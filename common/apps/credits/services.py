from django.db import transaction
from django.core.exceptions import ValidationError
from .models import UserCredit, CreditTransaction, CreditAIOperation, CreditPricing
import logging
import uuid

logger = logging.getLogger(__name__)

class CreditService:
    """Service class for credit management"""
    @staticmethod
    def get_user_credits(user):
        """Get or create a user's credit account"""
        credit_account, _ = UserCredit.objects.get_or_create(user=user)
        return credit_account
    
    @staticmethod
    @transaction.atomic
    def add_credits(user, amount, transaction_type, description="", reference_id=None):
        """Add credits to a user's account"""
        if amount <= 0:
            raise ValidationError("Amount must be positive when adding credits")
        
        credit_account = CreditService.get_user_credits(user)
        
        # Update credit balance
        credit_account.balance += amount
        credit_account.lifetime_credits += amount
        credit_account.save()
        
        # Record transaction
        transaction = CreditTransaction.objects.create(
            user=user,
            amount=amount,
            transaction_type=transaction_type,
            description=description,
            reference_id=reference_id
        )
        
        logger.info(f"Added {amount} credits to user {user.username}, new balance: {credit_account.balance}")
        return credit_account, transaction
    
    @staticmethod
    @transaction.atomic
    def use_credits(user, amount, operation_type, input_data=None, ai_operation_id=None):
        """
        Use credits for an AI operation
        Returns (success, operation_id, message)
        """
        if amount < 0:
            raise ValidationError("Amount cannot be negative when using credits")
        
        # Handle free operations (0 credits)
        if amount == 0:
            # Create credit operation record for tracking purposes
            credit_operation = CreditAIOperation.objects.create(
                user=user,
                operation_type=operation_type,
                credits_used=0,
                status='pending',
                input_data=input_data,
                operation_id=ai_operation_id
            )
            
            # Record transaction for audit trail
            transaction = CreditTransaction.objects.create(
                user=user,
                amount=0,
                transaction_type='usage',
                description=f"Free usage for {operation_type}",
                reference_id=credit_operation.id
            )
            
            logger.info(f"Free usage for {operation_type}, user: {user.username}")
            return True, credit_operation.id, "Free operation completed successfully"
        
        credit_account = CreditService.get_user_credits(user)
        
        # Check if user has enough credits
        if credit_account.balance < amount:
            return False, None, "Insufficient credits"
        
        # Create credit operation record
        credit_operation = CreditAIOperation.objects.create(
            user=user,
            operation_type=operation_type,
            credits_used=amount,
            status='pending',
            input_data=input_data,
            operation_id=ai_operation_id
        )
        
        # Deduct credits
        credit_account.balance -= amount
        credit_account.save()
        
        # Record transaction
        transaction = CreditTransaction.objects.create(
            user=user,
            amount=-amount,
            transaction_type='usage',
            description=f"Used for {operation_type}",
            reference_id=credit_operation.id
        )
        
        logger.info(f"Used {amount} credits for {operation_type}, user: {user.username}, new balance: {credit_account.balance}")
        return True, credit_operation.id, "Credits used successfully"
    
    @staticmethod
    @transaction.atomic
    def refund_credits(operation_id):
        """Refund credits for a failed or cancelled operation"""
        try:
            credit_operation = CreditAIOperation.objects.select_for_update().get(id=operation_id)
            
            # Only refund if operation was not completed
            if credit_operation.status == 'completed':
                return False, "Cannot refund completed operations"
            
            # Check if already refunded
            if CreditTransaction.objects.filter(
                reference_id=credit_operation.id, 
                transaction_type='refund'
            ).exists():
                return False, "Operation already refunded"
            
            user = credit_operation.user
            amount = credit_operation.credits_used
            
            # Update operation status
            credit_operation.status = 'cancelled'
            credit_operation.save()
            
            # Add credits back to user
            credit_account = CreditService.get_user_credits(user)
            credit_account.balance += amount
            credit_account.save()
            
            # Record refund transaction
            transaction = CreditTransaction.objects.create(
                user=user,
                amount=amount,
                transaction_type='refund',
                description=f"Refund for {credit_operation.operation_type}",
                reference_id=credit_operation.id
            )
            
            logger.info(f"Refunded {amount} credits to user {user.username}, new balance: {credit_account.balance}")
            return True, "Credits refunded successfully"
            
        except CreditAIOperation.DoesNotExist:
            return False, "Operation not found"
        except Exception as e:
            logger.error(f"Error refunding credits: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def get_operation_cost(operation_type, units=1):
        """Calculate the cost of an operation based on pricing configuration"""
        try:
            pricing = CreditPricing.objects.get(operation_type=operation_type)
            total_cost = pricing.base_credits + (pricing.per_unit_credits * max(0, units - 1))
            return total_cost
        except CreditPricing.DoesNotExist:
            # Default costs if pricing not configured
            default_costs = {
                'transcription': 5,
                'analysis': 10,
                'summarization': 8,
                'image_generation': 15,
                'image_editing': 12
            }
            return default_costs.get(operation_type, 10)  # Default to 10 if not found
    
    @staticmethod
    def complete_operation(operation_id, result_data=None):
        """Mark an operation as completed with results"""
        try:
            operation = CreditAIOperation.objects.get(id=operation_id)
            operation.status = 'completed'
            operation.result_data = result_data
            operation.save()
            return True, "Operation completed"
        except CreditAIOperation.DoesNotExist:
            return False, "Operation not found"
        except Exception as e:
            logger.error(f"Error completing operation: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def fail_operation(operation_id, error_message):
        """Mark an operation as failed with error message"""
        try:
            operation = CreditAIOperation.objects.get(id=operation_id)
            operation.status = 'failed'
            operation.error_message = error_message
            operation.save()
            
            # Automatically refund credits for failed operations
            return CreditService.refund_credits(operation_id)
        except CreditAIOperation.DoesNotExist:
            return False, "Operation not found"
        except Exception as e:
            logger.error(f"Error marking operation as failed: {str(e)}")
            return False, str(e)
