from django.core.management.base import BaseCommand
from apps.authentication.models import User
from apps.credits.services import CreditService
import uuid


class Command(BaseCommand):
    help = 'Add credits to a user account'
    
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
            '--amount',
            type=int,
            required=True,
            help='Number of credits to add',
        )
        parser.add_argument(
            '--description',
            type=str,
            default='Manual credit addition',
            help='Description for the transaction',
        )
    
    def handle(self, *args, **options):
        """Add credits to a user's account"""
        
        user_id = options.get('user_id')
        username = options.get('username')
        email = options.get('email')
        amount = options['amount']
        description = options['description']
        
        # Validate that at least one identifier is provided
        if not any([user_id, username, email]):
            self.stdout.write(self.style.ERROR(
                'Please provide at least one of: --user-id, --username, or --email'
            ))
            return
        
        # Find the user
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
        
        # Check current balance
        credit_account = CreditService.get_user_credits(user)
        old_balance = credit_account.balance
        
        self.stdout.write(f'\nUser: {user.username} ({user.email})')
        self.stdout.write(f'User ID: {user.id}')
        self.stdout.write(f'Current balance: {old_balance} credits')
        
        # Add credits
        try:
            credit_account, transaction = CreditService.add_credits(
                user=user,
                amount=amount,
                transaction_type='bonus',
                description=description
            )
            
            self.stdout.write(self.style.SUCCESS(
                f'\n✓ Successfully added {amount} credits'
            ))
            self.stdout.write(f'New balance: {credit_account.balance} credits')
            self.stdout.write(f'Transaction ID: {transaction.id}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error adding credits: {str(e)}'))
