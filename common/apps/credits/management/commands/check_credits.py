from django.core.management.base import BaseCommand
from apps.authentication.models import User
from apps.credits.services import CreditService
from apps.credits.models import CreditPricing
from apps.analytics.models import FeaturePricing
import uuid


class Command(BaseCommand):
    help = 'Check user credit balance and feature pricing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=str,
            help='User ID (UUID)',
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='User email',
        )
        parser.add_argument(
            '--feature',
            type=str,
            help='Feature name to check pricing (e.g., style_transfer)',
        )
    
    def handle(self, *args, **options):
        """Check user credit balance and optionally feature pricing"""
        
        user_id = options.get('user_id')
        username = options.get('username')
        email = options.get('email')
        feature_name = options.get('feature')
        
        # If a user identifier is provided, check their balance
        if any([user_id, username, email]):
            try:
                if user_id:
                    try:
                        user = User.objects.get(id=uuid.UUID(user_id))
                    except ValueError:
                        self.stdout.write(self.style.ERROR(f'Invalid user ID format: {user_id}'))
                        return
                elif username:
                    user = User.objects.get(username=username)
                else:
                    user = User.objects.get(email=email)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR('User not found'))
                return
            
            # Get credit balance
            credit_account = CreditService.get_user_credits(user)
            
            self.stdout.write(f'\n{"="*60}')
            self.stdout.write(f'USER CREDIT INFORMATION')
            self.stdout.write(f'{"="*60}')
            self.stdout.write(f'User: {user.username} ({user.email})')
            self.stdout.write(f'User ID: {user.id}')
            self.stdout.write(f'Current Balance: {credit_account.balance} credits')
            self.stdout.write(f'Lifetime Credits: {credit_account.lifetime_credits} credits')
            
            # Get recent transactions
            recent_transactions = user.credit_transactions.all().order_by('-created_at')[:5]
            if recent_transactions:
                self.stdout.write(f'\nRecent Transactions:')
                for txn in recent_transactions:
                    symbol = '+' if txn.amount > 0 else ''
                    self.stdout.write(
                        f'  {txn.created_at.strftime("%Y-%m-%d %H:%M")}: '
                        f'{symbol}{txn.amount} credits ({txn.transaction_type}) - {txn.description}'
                    )
        
        # If a feature is specified, show its pricing
        if feature_name:
            self.stdout.write(f'\n{"="*60}')
            self.stdout.write(f'FEATURE PRICING: {feature_name}')
            self.stdout.write(f'{"="*60}')
            
            # Check in FeaturePricing (analytics app)
            try:
                pricing = FeaturePricing.objects.get(feature_name=feature_name)
                self.stdout.write(f'Feature: {pricing.feature_name}')
                self.stdout.write(f'Description: {pricing.description}')
                self.stdout.write(f'Base Credits: {pricing.base_credits}')
                self.stdout.write(f'Per Unit Credits: {pricing.per_unit_credits}')
                self.stdout.write(f'Active: {pricing.is_active}')
                
                # Calculate example costs
                self.stdout.write(f'\nExample Costs:')
                for units in [1, 5, 10]:
                    cost = pricing.base_credits + (pricing.per_unit_credits * max(0, units - 1))
                    self.stdout.write(f'  {units} unit(s): {cost} credits')
                    
            except FeaturePricing.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'Feature "{feature_name}" not found in FeaturePricing'
                ))
            
            # Also check CreditPricing if it exists
            try:
                credit_pricing = CreditPricing.objects.get(operation_type=feature_name)
                self.stdout.write(f'\nCreditPricing:')
                self.stdout.write(f'Operation Type: {credit_pricing.operation_type}')
                self.stdout.write(f'Base Credits: {credit_pricing.base_credits}')
                self.stdout.write(f'Per Unit Credits: {credit_pricing.per_unit_credits}')
            except CreditPricing.DoesNotExist:
                pass
        
        # If no feature specified, show all available features
        elif not any([user_id, username, email]):
            self.stdout.write(f'\n{"="*60}')
            self.stdout.write(f'ALL AVAILABLE FEATURES')
            self.stdout.write(f'{"="*60}')
            
            features = FeaturePricing.objects.filter(is_active=True).order_by('feature_name')
            for feature in features:
                cost_1_unit = feature.base_credits
                self.stdout.write(
                    f'{feature.feature_name:30} | {cost_1_unit:3} credits | {feature.description}'
                )
        
        self.stdout.write(f'\n{"="*60}\n')
