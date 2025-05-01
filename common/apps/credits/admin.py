from django.contrib import admin
from .models import (CreditPackage, UserCredit, CreditTransaction,  
                      CreditPricing, PlanFeature, CreditPlan, PlanFeatureAssociation, 
                      UserSubscription)

@admin.register(CreditPackage)
class CreditPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'credits', 'price', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(UserCredit)
class UserCreditAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'lifetime_credits', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('lifetime_credits',)

@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'transaction_type', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user__username', 'user__email', 'description')
    readonly_fields = ('created_at',)

@admin.register(CreditPricing)
class CreditPricingAdmin(admin.ModelAdmin):
    list_display = ('operation_type', 'base_credits', 'per_unit_credits')
    list_filter = ('operation_type',)
    search_fields = ('operation_type', 'description')

@admin.register(PlanFeature)
class PlanFeatureAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description')

class PlanFeatureInline(admin.TabularInline):
    model = PlanFeatureAssociation
    extra = 1
    autocomplete_fields = ['feature']

@admin.register(CreditPlan)
class CreditPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'display_price', 'price_suffix', 'credits', 'is_popular', 'is_active', 'order')
    list_filter = ('plan_type', 'is_popular', 'is_active')
    search_fields = ('name', 'description', 'tagline')
    inlines = [PlanFeatureInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'plan_type', 'description', 'tagline')
        }),
        ('Pricing', {
            'fields': ('price', 'display_price', 'price_suffix', 'credits')
        }),
        ('Display Options', {
            'fields': ('is_popular', 'is_custom', 'is_active', 'order')
        }),
    )

@admin.register(PlanFeatureAssociation)
class PlanFeatureAssociationAdmin(admin.ModelAdmin):
    list_display = ('plan', 'feature', 'custom_description')
    list_filter = ('plan',)
    search_fields = ('plan__name', 'feature__name', 'custom_description')
    autocomplete_fields = ['plan', 'feature']

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date', 'auto_renew')
    list_filter = ('status', 'auto_renew', 'plan')
    search_fields = ('user__username', 'user__email', 'plan__name')
    readonly_fields = ('created_at',)
    date_hierarchy = 'start_date'
