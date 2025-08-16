from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from decimal import Decimal
from PIL import Image
import uuid
from datetime import datetime, timedelta
from django.utils import timezone


# Custom User Model for different user types
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('farmer', 'Farmer'),
        ('buyer', 'Buyer'),
        ('transporter', 'Transporter'),
        ('admin', 'Admin'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='buyer')
    phone_number = models.CharField(
        max_length=15, 
        validators=[RegexValidator(r'^\+?254\d{9}$', 'Enter a valid Kenyan phone number')]
    )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.user_type})"


# Location Models
class County(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Counties"
        ordering = ['name']

    def __str__(self):
        return self.name


class SubCounty(models.Model):
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='subcounties')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Sub Counties"
        unique_together = ('county', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.county.name}"


class Ward(models.Model):
    subcounty = models.ForeignKey(SubCounty, on_delete=models.CASCADE, related_name='wards')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subcounty', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.subcounty.name}"


# User Profile Models
class FarmerProfile(models.Model):
    FARM_TYPE_CHOICES = [
        ('crops', 'Crop Farming'),
        ('livestock', 'Livestock'),
        ('poultry', 'Poultry'),
        ('dairy', 'Dairy Farming'),
        ('mixed', 'Mixed Farming'),
        ('organic', 'Organic Farming'),
        ('greenhouse', 'Greenhouse Farming'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='farmer_profile')
    farm_name = models.CharField(max_length=200)
    farm_size = models.DecimalField(max_digits=8, decimal_places=2, help_text='Size in acres')
    farm_type = models.CharField(max_length=20, choices=FARM_TYPE_CHOICES, default='crops')
    
    # Location
    county = models.ForeignKey(County, on_delete=models.CASCADE)
    subcounty = models.ForeignKey(SubCounty, on_delete=models.CASCADE)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE)
    specific_location = models.CharField(max_length=200, help_text='Village, estate, or landmark')
    
    # Contact & Banking
    mpesa_number = models.CharField(max_length=15, validators=[RegexValidator(r'^\+?254\d{9}$')])
    bank_account = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    
    # Farm details
    description = models.TextField(blank=True)
    years_experience = models.PositiveIntegerField(default=0)
    certifications = models.TextField(blank=True, help_text='Organic, GAP, etc.')
    
    # Profile stats
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.farm_name} - {self.user.get_full_name()}"

    @property
    def full_address(self):
        return f"{self.specific_location}, {self.ward.name}, {self.subcounty.name}, {self.county.name}"


class BuyerProfile(models.Model):
    BUYER_TYPE_CHOICES = [
        ('individual', 'Individual Consumer'),
        ('restaurant', 'Restaurant/Hotel'),
        ('retailer', 'Retailer/Shop'),
        ('processor', 'Food Processor'),
        ('exporter', 'Exporter'),
        ('institution', 'Institution (School, Hospital)'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='buyer_profile')
    buyer_type = models.CharField(max_length=20, choices=BUYER_TYPE_CHOICES, default='individual')
    business_name = models.CharField(max_length=200, blank=True)
    
    # Location
    county = models.ForeignKey(County, on_delete=models.CASCADE)
    subcounty = models.ForeignKey(SubCounty, on_delete=models.CASCADE)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE)
    delivery_address = models.TextField()
    
    # Contact & Payment
    mpesa_number = models.CharField(max_length=15, validators=[RegexValidator(r'^\+?254\d{9}$')])
    alternative_phone = models.CharField(max_length=15, blank=True)
    
    # Preferences
    preferred_products = models.TextField(blank=True, help_text='Comma-separated list')
    max_delivery_distance = models.PositiveIntegerField(default=50, help_text='Maximum delivery distance in km')
    
    # Stats
    total_orders = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.buyer_type})"


class TransporterProfile(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ('motorcycle', 'Motorcycle'),
        ('tuk_tuk', 'Tuk Tuk'),
        ('pickup', 'Pickup Truck'),
        ('van', 'Van'),
        ('truck', 'Truck'),
        ('lorry', 'Lorry'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='transporter_profile')
    business_name = models.CharField(max_length=200, blank=True)
    
    # Vehicle details
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES)
    vehicle_registration = models.CharField(max_length=20, unique=True)
    vehicle_capacity = models.DecimalField(max_digits=8, decimal_places=2, help_text='Capacity in kg')
    
    # Location & Coverage
    base_county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='transporters')
    service_counties = models.ManyToManyField(County, related_name='available_transporters')
    max_distance = models.PositiveIntegerField(default=100, help_text='Maximum delivery distance in km')
    
    # Rates
    rate_per_km = models.DecimalField(max_digits=6, decimal_places=2)
    minimum_charge = models.DecimalField(max_digits=8, decimal_places=2, default=200)
    
    # Contact & Payment
    mpesa_number = models.CharField(max_length=15, validators=[RegexValidator(r'^\+?254\d{9}$')])
    
    # Documents
    driving_license = models.CharField(max_length=50)
    insurance_number = models.CharField(max_length=100, blank=True)
    
    # Stats
    total_deliveries = models.PositiveIntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.vehicle_type} ({self.vehicle_registration})"


# Product Category Models (Enhanced)
class Category(models.Model):
    """Main product categories like Crops, Livestock, Fertilizers, etc."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Font awesome icon class')
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class SubCategory(models.Model):
    """Subcategories like Vegetables, Fruits, Dairy Cows, etc."""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Sub Categories"
        unique_together = ('category', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# Enhanced Product Model
class Product(models.Model):
    """Enhanced product model for farm produce"""
    STOCK_STATUS_CHOICES = [
        ('available', 'Available'),
        ('low_stock', 'Low Stock'),
        ('sold_out', 'Sold Out'),
        ('harvesting', 'Currently Harvesting'),
        ('pre_order', 'Pre-Order (Future Harvest)'),
    ]

    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('ltr', 'Liter'),
        ('ml', 'Milliliter'),
        ('pc', 'Piece'),
        ('dozen', 'Dozen'),
        ('bag', 'Bag (90kg)'),
        ('crate', 'Crate'),
        ('bunch', 'Bunch'),
        ('sack', 'Sack'),
        ('ton', 'Ton'),
        ('acre', 'Per Acre'),
    ]

    QUALITY_GRADE_CHOICES = [
        ('premium', 'Premium Grade'),
        ('grade_a', 'Grade A'),
        ('grade_b', 'Grade B'),
        ('standard', 'Standard'),
        ('organic', 'Certified Organic'),
    ]

    # Basic Information
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    sku = models.CharField(max_length=100, unique=True, help_text='Stock Keeping Unit')
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    
    # Categorization
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products', blank=True, null=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    minimum_order = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    
    # Inventory
    available_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_status = models.CharField(max_length=20, choices=STOCK_STATUS_CHOICES, default='available')
    low_stock_threshold = models.DecimalField(max_digits=8, decimal_places=2, default=10)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='kg')
    
    # Product Quality & Details
    quality_grade = models.CharField(max_length=20, choices=QUALITY_GRADE_CHOICES, default='standard')
    variety = models.CharField(max_length=100, blank=True, help_text='e.g., Sukuma Wiki, Improved Kienyeji')
    
    # Farming Details
    harvest_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    farming_method = models.CharField(max_length=100, blank=True, help_text='Organic, Conventional, etc.')
    
    # Product Features
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_organic = models.BooleanField(default=False)
    is_available_for_preorder = models.BooleanField(default=False)
    
    # Stats
    total_sold = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    view_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['farmer', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} - {self.farmer.farm_name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.farmer.farm_name}")
            self.slug = base_slug
            
        if not self.sku:
            self.sku = f"FARM-{uuid.uuid4().hex[:8].upper()}"
        
        # Update stock status based on quantity
        if self.available_quantity == 0:
            self.stock_status = 'sold_out'
        elif self.available_quantity <= self.low_stock_threshold:
            self.stock_status = 'low_stock'
        else:
            self.stock_status = 'available'
            
        super().save(*args, **kwargs)

    @property
    def selling_price(self):
        """Return discount price if available, otherwise regular price"""
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.discount_price and self.discount_price < self.price:
            return round(((self.price - self.discount_price) / self.price) * 100)
        return 0

    @property
    def is_in_stock(self):
        return self.stock_status in ['available', 'low_stock']


class ProductImage(models.Model):
    """Multiple images for each product"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'created_at']

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"

    def save(self, *args, **kwargs):
        # If this is set as main image, unset others
        if self.is_main:
            ProductImage.objects.filter(product=self.product, is_main=True).update(is_main=False)
        
        super().save(*args, **kwargs)
        
        # Resize image if too large
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size)
                img.save(self.image.path)


# Order Management System
class Order(models.Model):
    """Enhanced orders with M-Pesa integration"""
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid - Awaiting Pickup'),
        ('assigned', 'Driver Assigned'),
        ('picked_up', 'Picked Up from Farm'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('cash', 'Cash on Delivery'),
        ('bank', 'Bank Transfer'),
    ]

    # Order identification
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    buyer = models.ForeignKey(BuyerProfile, on_delete=models.CASCADE, related_name='orders')
    
    # Delivery details
    delivery_address = models.TextField()
    delivery_phone = models.CharField(max_length=15)
    delivery_county = models.ForeignKey(County, on_delete=models.CASCADE)
    delivery_notes = models.TextField(blank=True)
    
    # Financial details
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    service_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)  # Platform fee
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='mpesa')
    
    # Assigned transporter
    transporter = models.ForeignKey(
        TransporterProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='deliveries'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_confirmed_at = models.DateTimeField(blank=True, null=True)
    picked_up_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    estimated_delivery = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} - {self.buyer.user.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"AG{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    @property
    def total_items(self):
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    @property
    def unique_farmers(self):
        """Get list of farmers involved in this order"""
        return set(item.product.farmer for item in self.items.all())


class OrderItem(models.Model):
    """Individual items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE)  # For easy farmer payouts
    
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Product details at time of order (for record keeping)
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.order_number} - {self.product_name} x {self.quantity}"

    def save(self, *args, **kwargs):
        self.product_name = self.product.name
        self.product_sku = self.product.sku
        self.unit = self.product.unit
        self.farmer = self.product.farmer
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


# M-Pesa Payment Integration
class MpesaTransaction(models.Model):
    """Track M-Pesa payments"""
    TRANSACTION_TYPE_CHOICES = [
        ('payment', 'Customer Payment'),
        ('payout_farmer', 'Farmer Payout'),
        ('payout_transporter', 'Transporter Payout'),
        ('refund', 'Refund'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='mpesa_transactions', null=True, blank=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    
    # M-Pesa details
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    merchant_request_id = models.CharField(max_length=100, blank=True)
    checkout_request_id = models.CharField(max_length=100, blank=True)
    mpesa_receipt_number = models.CharField(max_length=100, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    response_code = models.CharField(max_length=10, blank=True)
    response_description = models.TextField(blank=True)
    
    # Additional data
    account_reference = models.CharField(max_length=100, blank=True)
    transaction_desc = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"M-Pesa {self.transaction_type} - KES {self.amount} - {self.status}"


# SMS Integration for Offline Farmers
class SMSProductListing(models.Model):
    """Handle product listings via SMS"""
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name='sms_listings')
    phone_number = models.CharField(max_length=15)
    message_content = models.TextField()
    
    # Parsed data
    product_name = models.CharField(max_length=200, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=20, blank=True)
    
    # Processing status
    is_processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True)
    created_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"SMS from {self.phone_number} - {self.product_name}"


# Review System
class FarmerReview(models.Model):
    """Reviews for farmers"""
    RATING_CHOICES = [(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)]
    
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name='reviews')
    buyer = models.ForeignKey(BuyerProfile, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='farmer_reviews')
    
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField(blank=True)
    
    # Review aspects
    product_quality = models.PositiveIntegerField(choices=RATING_CHOICES, null=True, blank=True)
    communication = models.PositiveIntegerField(choices=RATING_CHOICES, null=True, blank=True)
    packaging = models.PositiveIntegerField(choices=RATING_CHOICES, null=True, blank=True)
    
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('farmer', 'buyer', 'order')

    def __str__(self):
        return f"{self.farmer.farm_name} - {self.rating} stars by {self.buyer.user.get_full_name()}"


class TransporterReview(models.Model):
    """Reviews for transporters"""
    RATING_CHOICES = [(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)]
    
    transporter = models.ForeignKey(TransporterProfile, on_delete=models.CASCADE, related_name='reviews')
    buyer = models.ForeignKey(BuyerProfile, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transporter_reviews')
    
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField(blank=True)
    
    # Review aspects
    timeliness = models.PositiveIntegerField(choices=RATING_CHOICES, null=True, blank=True)
    communication = models.PositiveIntegerField(choices=RATING_CHOICES, null=True, blank=True)
    care_of_goods = models.PositiveIntegerField(choices=RATING_CHOICES, null=True, blank=True)
    
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('transporter', 'buyer', 'order')

    def __str__(self):
        return f"{self.transporter.user.get_full_name()} - {self.rating} stars"


# WhatsApp Integration
class WhatsAppOrder(models.Model):
    """Handle orders placed via WhatsApp"""
    phone_number = models.CharField(max_length=15)
    customer_name = models.CharField(max_length=200, blank=True)
    message_content = models.TextField()
    
    # Location
    delivery_location = models.TextField(blank=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Parsed order data
    parsed_products = models.JSONField(blank=True, null=True)  # Store parsed product requests
    estimated_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Processing status
    is_processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True)
    created_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    
    # WhatsApp bot response
    bot_response = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"WhatsApp Order from {self.phone_number} - {self.customer_name}"


# Cart System (for web users)
class Cart(models.Model):
    """Shopping cart for website visitors"""
    session_id = models.CharField(max_length=100, unique=True)
    buyer = models.ForeignKey(BuyerProfile, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.session_id}"
    
    @property
    def total_items(self):
        """Return total number of items in cart"""
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0
    
    @property
    def total_amount(self):
        """Return total amount of cart"""
        return sum(
            item.quantity * item.product.selling_price
            for item in self.items.all()
        )

    @property
    def delivery_fee_estimate(self):
        """Estimate delivery fee based on cart contents"""
        if not self.buyer:
            return Decimal('0.00')
        
        # Group items by farmer to estimate multiple pickup points
        farmers = set(item.product.farmer for item in self.items.all())
        base_fee = Decimal('200.00')  # Base delivery fee
        
        # Add extra fee for multiple farmers
        if len(farmers) > 1:
            base_fee += Decimal('100.00') * (len(farmers) - 1)
            
        return base_fee


class CartItem(models.Model):
    """Items in shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.cart.session_id} - {self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.quantity * self.product.selling_price


# Notification System
class Notification(models.Model):
    """System notifications for users"""
    NOTIFICATION_TYPE_CHOICES = [
        ('order_placed', 'Order Placed'),
        ('order_confirmed', 'Order Confirmed'),
        ('payment_received', 'Payment Received'),
        ('driver_assigned', 'Driver Assigned'),
        ('pickup_scheduled', 'Pickup Scheduled'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('review_request', 'Review Request'),
        ('payout_received', 'Payout Received'),
        ('new_message', 'New Message'),
        ('system_alert', 'System Alert'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related objects
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_sent_sms = models.BooleanField(default=False)
    is_sent_email = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"


# Support & Communication
class SupportTicket(models.Model):
    """Customer support tickets"""
    TICKET_STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    ticket_number = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='support_tickets')
    
    subject = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=TICKET_STATUS_CHOICES, default='open')
    
    # Related objects
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_tickets'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket #{self.ticket_number} - {self.subject}"


class SupportMessage(models.Model):
    """Messages within support tickets"""
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    attachment = models.FileField(upload_to='support_attachments/', blank=True, null=True)
    
    is_internal = models.BooleanField(default=False)  # Staff-only messages
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.ticket.ticket_number} - Message by {self.sender.username}"


# Analytics & Reporting
class PlatformAnalytics(models.Model):
    """Daily analytics for the platform"""
    date = models.DateField(unique=True)
    
    # User metrics
    total_farmers = models.PositiveIntegerField(default=0)
    total_buyers = models.PositiveIntegerField(default=0)
    total_transporters = models.PositiveIntegerField(default=0)
    new_registrations = models.PositiveIntegerField(default=0)
    
    # Product metrics
    total_products = models.PositiveIntegerField(default=0)
    new_products = models.PositiveIntegerField(default=0)
    active_products = models.PositiveIntegerField(default=0)
    
    # Order metrics
    total_orders = models.PositiveIntegerField(default=0)
    completed_orders = models.PositiveIntegerField(default=0)
    cancelled_orders = models.PositiveIntegerField(default=0)
    
    # Financial metrics
    gross_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    platform_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    farmer_payouts = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transporter_payouts = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Analytics for {self.date}"


# System Configuration
class SystemConfiguration(models.Model):
    """System-wide configuration settings"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key}: {self.value[:50]}"

    class Meta:
        ordering = ['key']


# Newsletter & Marketing
class Newsletter(models.Model):
    """Newsletter subscriptions"""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    user_type = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    interests = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class MarketingCampaign(models.Model):
    """Marketing campaigns"""
    CAMPAIGN_TYPE_CHOICES = [
        ('email', 'Email Campaign'),
        ('sms', 'SMS Campaign'),
        ('push', 'Push Notification'),
        ('whatsapp', 'WhatsApp Broadcast'),
    ]
    
    name = models.CharField(max_length=200)
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPE_CHOICES)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    
    # Targeting
    target_user_type = models.CharField(max_length=20, blank=True)
    target_counties = models.ManyToManyField(County, blank=True)
    
    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    scheduled_at = models.DateTimeField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    
    # Stats
    total_recipients = models.PositiveIntegerField(default=0)
    total_sent = models.PositiveIntegerField(default=0)
    total_delivered = models.PositiveIntegerField(default=0)
    total_opened = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.campaign_type})"


# Contact & Feedback
class ContactMessage(models.Model):
    """Contact form messages"""
    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('product', 'Product Information'),
        ('order', 'Order Inquiry'),
        ('technical', 'Technical Support'),
        ('partnership', 'Partnership'),
        ('farmer_onboarding', 'Farmer Registration'),
        ('transporter_onboarding', 'Transporter Registration'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    user_type = models.CharField(max_length=20, blank=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    message = models.TextField()
    
    is_read = models.BooleanField(default=False)
    is_responded = models.BooleanField(default=False)
    response = models.TextField(blank=True)
    responded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    responded_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"


# Logistics & Delivery Tracking
class DeliveryRoute(models.Model):
    """Delivery routes for orders"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery_route')
    transporter = models.ForeignKey(TransporterProfile, on_delete=models.CASCADE)
    
    # Route details
    pickup_locations = models.JSONField()  # List of farmer locations
    delivery_location = models.TextField()
    estimated_distance = models.DecimalField(max_digits=8, decimal_places=2, help_text='Distance in km')
    estimated_duration = models.PositiveIntegerField(help_text='Duration in minutes')
    
    # Status tracking
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Route for Order #{self.order.order_number}"


class DeliveryUpdate(models.Model):
    """Real-time delivery updates"""
    UPDATE_TYPE_CHOICES = [
        ('assigned', 'Driver Assigned'),
        ('pickup_started', 'Pickup Started'),
        ('pickup_completed', 'Pickup Completed'),
        ('in_transit', 'In Transit'),
        ('near_destination', 'Near Destination'),
        ('delivered', 'Delivered'),
        ('exception', 'Delivery Exception'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='delivery_updates')
    update_type = models.CharField(max_length=20, choices=UPDATE_TYPE_CHOICES)
    message = models.TextField()
    location = models.CharField(max_length=200, blank=True)
    
    # GPS coordinates (optional)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_number} - {self.update_type}"


# Financial Management
class PlatformWallet(models.Model):
    """Platform wallet for commission and fees"""
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_commission_earned = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_fees_collected = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_payouts_made = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Platform Wallet - Balance: KES {self.balance}"


class UserWallet(models.Model):
    """User wallet for farmers and transporters"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_withdrawn = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # M-Pesa details
    mpesa_number = models.CharField(max_length=15, blank=True)
    auto_withdraw_enabled = models.BooleanField(default=False)
    minimum_balance_for_withdrawal = models.DecimalField(max_digits=8, decimal_places=2, default=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Wallet - Balance: KES {self.balance}"


class WalletTransaction(models.Model):
    """Wallet transaction history"""
    TRANSACTION_TYPE_CHOICES = [
        ('credit_sale', 'Credit from Sale'),
        ('credit_delivery', 'Credit from Delivery'),
        ('debit_withdrawal', 'Withdrawal'),
        ('debit_fee', 'Platform Fee'),
        ('refund', 'Refund'),
    ]
    
    wallet = models.ForeignKey(UserWallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    
    # Related objects
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    mpesa_transaction = models.ForeignKey(MpesaTransaction, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Balance after transaction
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.wallet.user.username} - {self.transaction_type} - KES {self.amount}"