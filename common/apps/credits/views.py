from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from .models import (CreditPackage, UserCredit, CreditTransaction, 
                     CreditPricing, CreditPlan, UserSubscription)
from .serializers import (
    CreditPackageSerializer, UserCreditSerializer, CreditTransactionSerializer,
    CreditPricingSerializer, CreditBalanceSerializer,
    CreditUsageSerializer, CreditEstimateSerializer, CreditPlanSerializer,
    UserSubscriptionSerializer
)
from .services import CreditService
import logging

logger = logging.getLogger(__name__)

class CreditPackageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for credit packages
    """
    queryset = CreditPackage.objects.filter(is_active=True)
    serializer_class = CreditPackageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

class UserCreditViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for user credit balances
    """
    serializer_class = UserCreditSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return UserCredit.objects.all()
        return UserCredit.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def balance(self, request):
        """Get current user's credit balance"""
        credit_account = CreditService.get_user_credits(request.user)
        serializer = CreditBalanceSerializer({
            'balance': credit_account.balance,
            'lifetime_credits': credit_account.lifetime_credits
        })
        return Response(serializer.data)

class CreditTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for credit transactions
    """
    serializer_class = CreditTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return CreditTransaction.objects.all().order_by('-created_at')
        return CreditTransaction.objects.filter(user=user).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary of user's credit transactions"""
        user = request.user
        
        # Get totals by transaction type
        summary = CreditTransaction.objects.filter(user=user).values(
            'transaction_type'
        ).annotate(
            total=Sum('amount')
        ).order_by('transaction_type')
        
        return Response(summary)

 
class CreditPricingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for credit pricing configuration
    """
    queryset = CreditPricing.objects.all()
    serializer_class = CreditPricingSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

class CreditPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for credit subscription plans
    """
    queryset = CreditPlan.objects.filter(is_active=True).order_by('order')
    serializer_class = CreditPlanSerializer
    permission_classes = [permissions.AllowAny]  # Allow public access to view plans
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get the most popular plan"""
        try:
            plan = CreditPlan.objects.filter(is_active=True).first()
            if not plan:
                plan = CreditPlan.objects.filter(is_active=True).order_by('order').first()
            if plan:
                serializer = self.get_serializer(plan)
                return Response(serializer.data)
            return Response({"error": "No active plans found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error retrieving popular plan: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get plans grouped by type"""
        try:
            plan_types = dict(CreditPlan.PLAN_TYPES)
            result = {}
            
            for plan_type, display_name in plan_types.items():
                plans = CreditPlan.objects.filter(is_active=True, plan_type=plan_type).order_by('order')
                if plans.exists():
                    result[plan_type] = {
                        "name": display_name,
                        "plans": self.get_serializer(plans, many=True).data
                    }
            
            return Response(result)
        except Exception as e:
            logger.error(f"Error retrieving plans by type: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserSubscriptionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user subscriptions
    """
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return UserSubscription.objects.all().order_by('-created_at')
        return UserSubscription.objects.filter(user=user).order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Create a new subscription for the user"""
        # Add user to request data
        data = request.data.copy()
        data['user'] = request.user.id
        
        # Set start date to now if not provided
        if 'start_date' not in data:
            data['start_date'] = timezone.now().isoformat()
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            subscription = serializer.save()
            
            # If this is a paid plan with credits, add them to the user's account
            try:
                plan = subscription.plan
                if plan.credits > 0:
                    CreditService.add_credits(
                        user=request.user,
                        amount=plan.credits,
                        transaction_type='purchase',
                        description=f"Credits from {plan.name} plan subscription",
                        reference_id=subscription.id
                    )
            except Exception as e:
                logger.error(f"Error adding subscription credits: {str(e)}")
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a subscription"""
        subscription = self.get_object()
        
        # Only the owner can cancel their subscription
        if subscription.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        subscription.status = 'cancelled'
        subscription.auto_renew = False
        subscription.save()
        
        return Response({'status': 'cancelled', 'message': 'Subscription cancelled successfully'})
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get user's active subscription"""
        subscription = UserSubscription.objects.filter(
            user=request.user,
            status='active',
        ).order_by('-start_date').first()
        
        if subscription:
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        else:
            return Response({"message": "No active subscription found"}, status=status.HTTP_404_NOT_FOUND)
