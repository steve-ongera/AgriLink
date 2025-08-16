from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta

from .models import *


# Custom User Admin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'user_type', 'is_verified', 'phone_number', 'created_at']
    list_filter = ['user_type', 'is_verified', 'is_active', 'is_staff', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    ordering = ['-created_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Profile Info', {
            'fields': ('user_type', 'phone_number', 'is_verified')
        }),
    )
    
    actions = ['verify_users', 'unverify_users']
    
    def verify_users(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} users were successfully verified.')
    verify_users.short_description = "Mark selected users as verified"
    
    def unverify_users(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} users were marked as unverified.')
    unverify_users.short_description = "Mark selected users as unverified"


# Location Models Admin
@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'subcounty_count', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['name']
    
    def subcounty_count(self, obj):
        return obj.subcounties.count()
    subcounty_count.short_description = 'Sub Counties'


@admin.register(SubCounty)
class SubCountyAdmin(admin.ModelAdmin):
    list_display = ['name', 'county', 'ward_count', 'created_at']
    list_filter = ['county']
    search_fields = ['name', 'county__name']
    ordering = ['county__name', 'name']
    
    def ward_count(self, obj):
        return obj.wards.count()
    ward_count.short_description = 'Wards'


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ['name', 'subcounty', 'county_name', 'created_at']
    list_filter = ['subcounty__county']
    search_fields = ['name', 'subcounty__name', 'subcounty__county__name']
    ordering = ['subcounty__county__name', 'subcounty__name', 'name']
    
    def county_name(self, obj):
        return obj.subcounty.county.name
    county_name.short_description = 'County'


# Profile Models Admin
@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ['farm_name', 'user_full_name', 'farm_type', 'county', 'farm_size', 'is_verified', 'total_sales', 'rating']
    list_filter = ['farm_type', 'county', 'is_verified', 'is_active', 'created_at']
    search_fields = ['farm_name', 'user__username', 'user__first_name', 'user__last_name', 'mpesa_number']
    readonly_fields = ['total_sales', 'rating', 'total_reviews']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'farm_name', 'farm_size', 'farm_type', 'description')
        }),
        ('Location', {
            'fields': ('county', 'subcounty', 'ward', 'specific_location')
        }),
        ('Contact & Banking', {
            'fields': ('mpesa_number', 'bank_account', 'bank_name')
        }),
        ('Farm Details', {
            'fields': ('years_experience', 'certifications')
        }),
        ('Stats', {
            'fields': ('total_sales', 'rating', 'total_reviews'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_verified', 'is_active')
        }),
    )
    
    actions = ['verify_farmers', 'deactivate_farmers']
    
    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_full_name.short_description = 'Farmer Name'
    
    def verify_farmers(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} farmers were successfully verified.')
    verify_farmers.short_description = "Verify selected farmers"
    
    def deactivate_farmers(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} farmers were deactivated.')
    deactivate_farmers.short_description = "Deactivate selected farmers"


@admin.register(BuyerProfile)
class BuyerProfileAdmin(admin.ModelAdmin):
    list_display = ['user_full_name', 'buyer_type', 'business_name', 'county', 'total_orders', 'total_spent']
    list_filter = ['buyer_type', 'county', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'business_name', 'mpesa_number']
    readonly_fields = ['total_orders', 'total_spent']
    ordering = ['-created_at']
    
    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_full_name.short_description = 'Buyer Name'


@admin.register(TransporterProfile)
class TransporterProfileAdmin(admin.ModelAdmin):
    list_display = ['user_full_name', 'vehicle_type', 'vehicle_registration', 'base_county', 'is_verified', 'is_available', 'rating']
    list_filter = ['vehicle_type', 'base_county', 'is_verified', 'is_available', 'is_active']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'vehicle_registration', 'driving_license']
    readonly_fields = ['total_deliveries', 'total_earnings', 'rating', 'total_reviews']
    filter_horizontal = ['service_counties']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'business_name')
        }),
        ('Vehicle Details', {
            'fields': ('vehicle_type', 'vehicle_registration', 'vehicle_capacity', 'driving_license', 'insurance_number')
        }),
        ('Service Area', {
            'fields': ('base_county', 'service_counties', 'max_distance')
        }),
        ('Rates', {
            'fields': ('rate_per_km', 'minimum_charge')
        }),
        ('Contact & Payment', {
            'fields': ('mpesa_number',)
        }),
        ('Stats', {
            'fields': ('total_deliveries', 'total_earnings', 'rating', 'total_reviews'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_verified', 'is_available', 'is_active')
        }),
    )
    
    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_full_name.short_description = 'Transporter Name'


# Product Models Admin
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'subcategory_count', 'product_count', 'is_active', 'sort_order']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['sort_order', 'name']
    
    def subcategory_count(self, obj):
        return obj.subcategories.count()
    subcategory_count.short_description = 'Sub Categories'
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'product_count', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'category__name']
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'farmer_name', 'category', 'price_display', 'available_quantity', 'stock_status', 'is_active', 'view_count']
    list_filter = ['category', 'subcategory', 'stock_status', 'quality_grade', 'is_active', 'is_featured', 'is_organic']
    search_fields = ['name', 'sku', 'farmer__farm_name', 'farmer__user__username']
    readonly_fields = [ 'sku', 'total_sold', 'view_count']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('farmer', 'name', 'slug', 'sku', 'description', 'short_description')
        }),
        ('Categorization', {
            'fields': ('category', 'subcategory')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price', 'minimum_order')
        }),
        ('Inventory', {
            'fields': ('available_quantity', 'low_stock_threshold', 'unit', 'stock_status')
        }),
        ('Product Details', {
            'fields': ('quality_grade', 'variety', 'harvest_date', 'expiry_date', 'farming_method')
        }),
        ('Features', {
            'fields': ('is_active', 'is_featured', 'is_organic', 'is_available_for_preorder')
        }),
        ('Stats', {
            'fields': ('total_sold', 'view_count'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_featured', 'mark_as_not_featured', 'mark_as_active', 'mark_as_inactive']
    
    def farmer_name(self, obj):
        return obj.farmer.farm_name
    farmer_name.short_description = 'Farm'
    
    def price_display(self, obj):
        if obj.discount_price:
            return format_html('<span style="text-decoration: line-through;">KES {}</span><br/><strong>KES {}</strong>', 
                             obj.price, obj.discount_price)
        return f'KES {obj.price}'
    price_display.short_description = 'Price'
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} products were marked as featured.')
    mark_as_featured.short_description = "Mark selected products as featured"
    
    def mark_as_not_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} products were unmarked as featured.')
    mark_as_not_featured.short_description = "Unmark selected products as featured"
    
    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} products were activated.')
    mark_as_active.short_description = "Activate selected products"
    
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} products were deactivated.')
    mark_as_inactive.short_description = "Deactivate selected products"


# Order Management Admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['total_price', 'product_name', 'product_sku', 'unit', 'farmer']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'buyer_name', 'status', 'total_amount', 'payment_method', 'transporter_name', 'created_at']
    list_filter = ['status', 'payment_method', 'delivery_county', 'created_at']
    search_fields = ['order_number', 'buyer__user__username', 'buyer__user__first_name', 'buyer__user__last_name']
    readonly_fields = ['order_number', 'subtotal', 'total_amount', 'total_items']
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'buyer', 'status', 'payment_method')
        }),
        ('Delivery Details', {
            'fields': ('delivery_address', 'delivery_phone', 'delivery_county', 'delivery_notes')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'delivery_fee', 'service_fee', 'total_amount')
        }),
        ('Assignment', {
            'fields': ('transporter',)
        }),
        ('Timestamps', {
            'fields': ('payment_confirmed_at', 'picked_up_at', 'delivered_at', 'estimated_delivery'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_paid', 'assign_transporter', 'mark_as_delivered']
    
    def buyer_name(self, obj):
        return obj.buyer.user.get_full_name() or obj.buyer.user.username
    buyer_name.short_description = 'Buyer'
    
    def transporter_name(self, obj):
        return obj.transporter.user.get_full_name() if obj.transporter else 'Not Assigned'
    transporter_name.short_description = 'Transporter'
    
    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = 'Items'
    
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status='paid', payment_confirmed_at=timezone.now())
        self.message_user(request, f'{updated} orders were marked as paid.')
    mark_as_paid.short_description = "Mark selected orders as paid"
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered', delivered_at=timezone.now())
        self.message_user(request, f'{updated} orders were marked as delivered.')
    mark_as_delivered.short_description = "Mark selected orders as delivered"


@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_type', 'phone_number', 'amount', 'status', 'mpesa_receipt_number', 'created_at']
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = ['phone_number', 'mpesa_receipt_number', 'merchant_request_id', 'checkout_request_id']
    readonly_fields = ['merchant_request_id', 'checkout_request_id', 'response_code', 'response_description']
    ordering = ['-created_at']


# Review System Admin
@admin.register(FarmerReview)
class FarmerReviewAdmin(admin.ModelAdmin):
    list_display = ['farmer_name', 'buyer_name', 'rating', 'title', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['farmer__farm_name', 'buyer__user__username', 'title', 'comment']
    readonly_fields = ['farmer', 'buyer', 'order']
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def farmer_name(self, obj):
        return obj.farmer.farm_name
    farmer_name.short_description = 'Farmer'
    
    def buyer_name(self, obj):
        return obj.buyer.user.get_full_name() or obj.buyer.user.username
    buyer_name.short_description = 'Buyer'
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} reviews were approved.')
    approve_reviews.short_description = "Approve selected reviews"
    
    def disapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} reviews were disapproved.')
    disapprove_reviews.short_description = "Disapprove selected reviews"


@admin.register(TransporterReview)
class TransporterReviewAdmin(admin.ModelAdmin):
    list_display = ['transporter_name', 'buyer_name', 'rating', 'title', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['transporter__user__username', 'buyer__user__username', 'title', 'comment']
    readonly_fields = ['transporter', 'buyer', 'order']
    
    def transporter_name(self, obj):
        return obj.transporter.user.get_full_name() or obj.transporter.user.username
    transporter_name.short_description = 'Transporter'
    
    def buyer_name(self, obj):
        return obj.buyer.user.get_full_name() or obj.buyer.user.username
    buyer_name.short_description = 'Buyer'


# Communication & Integration Admin
@admin.register(SMSProductListing)
class SMSProductListingAdmin(admin.ModelAdmin):
    list_display = ['farmer_name', 'phone_number', 'product_name', 'is_processed', 'created_at']
    list_filter = ['is_processed', 'created_at']
    search_fields = ['farmer__farm_name', 'phone_number', 'product_name']
    readonly_fields = ['message_content', 'processing_error']
    
    def farmer_name(self, obj):
        return obj.farmer.farm_name if obj.farmer else 'Unknown'
    farmer_name.short_description = 'Farmer'


@admin.register(WhatsAppOrder)
class WhatsAppOrderAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'phone_number', 'county', 'estimated_total', 'is_processed', 'created_at']
    list_filter = ['is_processed', 'county', 'created_at']
    search_fields = ['customer_name', 'phone_number']
    readonly_fields = ['message_content', 'parsed_products', 'bot_response']


# Cart System Admin
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'buyer_name', 'total_items', 'total_amount', 'created_at']
    search_fields = ['session_id', 'buyer__user__username']
    readonly_fields = ['total_items', 'total_amount']
    
    def buyer_name(self, obj):
        return obj.buyer.user.get_full_name() if obj.buyer else 'Anonymous'
    buyer_name.short_description = 'Buyer'


# Notification System Admin
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'is_sent_sms', 'created_at']
    list_filter = ['notification_type', 'is_read', 'is_sent_sms', 'is_sent_email', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f'{updated} notifications were marked as read.')
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f'{updated} notifications were marked as unread.')
    mark_as_unread.short_description = "Mark selected notifications as unread"


# Support System Admin
class SupportMessageInline(admin.TabularInline):
    model = SupportMessage
    readonly_fields = ['sender', 'created_at']
    extra = 1


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'user', 'subject', 'priority', 'status', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['ticket_number', 'user__username', 'subject']
    readonly_fields = ['ticket_number']
    inlines = [SupportMessageInline]
    
    fieldsets = (
        ('Ticket Information', {
            'fields': ('ticket_number', 'user', 'subject', 'description')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'assigned_to')
        }),
        ('Related Order', {
            'fields': ('order',)
        }),
    )


# Analytics Admin
@admin.register(PlatformAnalytics)
class PlatformAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_farmers', 'total_buyers', 'total_orders', 'gross_sales', 'platform_commission']
    list_filter = ['date']
    readonly_fields = ['date', 'total_farmers', 'total_buyers', 'total_transporters', 'new_registrations',
                      'total_products', 'new_products', 'active_products', 'total_orders', 'completed_orders',
                      'cancelled_orders', 'gross_sales', 'platform_commission', 'farmer_payouts', 'transporter_payouts']
    ordering = ['-date']


# Financial Management Admin
@admin.register(UserWallet)
class UserWalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'total_earned', 'total_withdrawn', 'auto_withdraw_enabled']
    list_filter = ['auto_withdraw_enabled', 'user__user_type']
    search_fields = ['user__username', 'mpesa_number']
    readonly_fields = ['balance', 'total_earned', 'total_withdrawn']


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet_user', 'transaction_type', 'amount', 'balance_after', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['wallet__user__username', 'description']
    readonly_fields = ['balance_after']
    
    def wallet_user(self, obj):
        return obj.wallet.user.username
    wallet_user.short_description = 'User'


# System Configuration Admin
@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ['key', 'value_preview', 'description', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['key', 'description']
    
    def value_preview(self, obj):
        return obj.value[:50] + '...' if len(obj.value) > 50 else obj.value
    value_preview.short_description = 'Value'


# Marketing Admin
@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'user_type', 'location', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_active', 'created_at']
    search_fields = ['email', 'name']


@admin.register(MarketingCampaign)
class MarketingCampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'campaign_type', 'target_user_type', 'total_recipients', 'total_sent', 'sent_at']
    list_filter = ['campaign_type', 'target_user_type', 'is_active']
    search_fields = ['name', 'subject']
    filter_horizontal = ['target_counties']
    readonly_fields = ['total_recipients', 'total_sent', 'total_delivered', 'total_opened']


# Contact & Feedback Admin
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'user_type', 'county', 'is_read', 'is_responded', 'created_at']
    list_filter = ['subject', 'user_type', 'county', 'is_read', 'is_responded', 'created_at']
    search_fields = ['name', 'email', 'phone', 'message']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'user_type', 'county')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Response', {
            'fields': ('is_read', 'is_responded', 'response', 'responded_by', 'responded_at')
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_responded']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} messages were marked as read.')
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_responded(self, request, queryset):
        updated = queryset.update(is_responded=True, responded_at=timezone.now())
        self.message_user(request, f'{updated} messages were marked as responded.')
    mark_as_responded.short_description = "Mark selected messages as responded"


# Delivery Tracking Admin
@admin.register(DeliveryRoute)
class DeliveryRouteAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'transporter_name', 'estimated_distance', 'estimated_duration', 'started_at', 'completed_at']
    list_filter = ['transporter', 'started_at', 'completed_at']
    search_fields = ['order__order_number', 'transporter__user__username']
    readonly_fields = ['pickup_locations']
    
    def order_number(self, obj):
        return obj.order.order_number
    order_number.short_description = 'Order'
    
    def transporter_name(self, obj):
        return obj.transporter.user.get_full_name() or obj.transporter.user.username
    transporter_name.short_description = 'Transporter'


@admin.register(DeliveryUpdate)
class DeliveryUpdateAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'update_type', 'message', 'location', 'created_at']
    list_filter = ['update_type', 'created_at']
    search_fields = ['order__order_number', 'message', 'location']
    readonly_fields = ['created_at']
    
    def order_number(self, obj):
        return obj.order.order_number
    order_number.short_description = 'Order'


# Register remaining models with basic admin
admin.site.register(ProductImage)
admin.site.register(OrderItem)
admin.site.register(CartItem)
admin.site.register(SupportMessage)
admin.site.register(PlatformWallet)

# Customize admin site headers
admin.site.site_header = "Agricultural Marketplace Admin"
admin.site.site_title = "AgriMarket Admin"
admin.site.index_title = "Welcome to Agricultural Marketplace Administration"