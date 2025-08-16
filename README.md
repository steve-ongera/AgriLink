# AgriLink 🌱 - Farmer-to-Buyer Digital Marketplace

**Developer:** Steve Ongera  
**Phone:** 0112284093  
**Version:** 1.0.0

## Overview

AgriLink is a comprehensive farmer-to-buyer digital marketplace that connects farmers directly with consumers, retailers, and transporters while eliminating exploitative middlemen. The platform integrates M-Pesa payments, WhatsApp ordering, SMS support for offline farmers, and real-time delivery tracking.

## 🎯 Key Features

### For Farmers
- **Digital Product Listing**: List produce with photos, prices, and quantities
- **SMS Integration**: List products via SMS for farmers without smartphones
- **Direct Payments**: Receive payments directly via M-Pesa
- **Order Management**: Track orders from placement to delivery
- **Rating System**: Build reputation through customer reviews
- **Wallet System**: Automatic earnings tracking and withdrawal

### For Buyers
- **Smart Search**: Find products by type, location, and price
- **Multiple Ordering**: Web platform, WhatsApp, or phone orders
- **Secure Payments**: M-Pesa integration with STK Push
- **Delivery Tracking**: Real-time updates on order status
- **Review System**: Rate farmers and transporters
- **Cart System**: Save items for later purchase

### For Transporters
- **Delivery Jobs**: Accept delivery requests in your area
- **Route Optimization**: Efficient pickup and delivery routes
- **Earnings Tracking**: Transparent payment system
- **Rating System**: Build reputation for more jobs
- **Vehicle Management**: Register multiple vehicles

## 🏗️ System Architecture

### User Types
1. **Farmers** - List and sell agricultural products
2. **Buyers** - Purchase products from farmers
3. **Transporters** - Handle deliveries
4. **Admins** - Manage the platform

### Core Models Structure

#### User Management
- `CustomUser` - Extended user model with user types
- `FarmerProfile` - Farmer-specific information
- `BuyerProfile` - Buyer-specific information  
- `TransporterProfile` - Transporter-specific information

#### Location System
- `County` - Kenya's 47 counties
- `SubCounty` - Sub-counties within counties
- `Ward` - Wards within sub-counties

#### Product Management
- `Category` - Main product categories (Crops, Livestock, etc.)
- `SubCategory` - Specific subcategories
- `Product` - Individual products with pricing and inventory
- `ProductImage` - Multiple images per product

#### Order Management
- `Order` - Main order entity
- `OrderItem` - Individual products in orders
- `Cart` / `CartItem` - Shopping cart functionality
- `WhatsAppOrder` - Orders placed via WhatsApp

#### Payment System
- `MpesaTransaction` - M-Pesa payment tracking
- `UserWallet` - User earnings and balances
- `WalletTransaction` - Transaction history
- `PlatformWallet` - Platform commission tracking

#### Communication & Support
- `Notification` - System notifications
- `SupportTicket` - Customer support
- `ContactMessage` - Contact form messages
- `SMSProductListing` - SMS-based product listings

#### Reviews & Ratings
- `FarmerReview` - Farmer reviews by buyers
- `TransporterReview` - Transporter reviews by buyers

#### Delivery & Logistics
- `DeliveryRoute` - Delivery route planning
- `DeliveryUpdate` - Real-time delivery tracking

## 🔄 Platform Workflow

### 1. User Registration
```
Farmer/Buyer/Transporter → Registration → Profile Setup → Verification
```

### 2. Product Listing (Farmers)
```
Web Platform:
Farmer Login → Add Product → Upload Photos → Set Price → Publish

SMS Platform:
Send SMS: "Tomatoes,50kg,80,Nakuru" → Auto-parsed → Product Created
```

### 3. Product Discovery (Buyers)
```
Search Products → Filter by Location/Price → View Details → Add to Cart
```

### 4. Order Placement
```
Web: Cart → Checkout → Payment
WhatsApp: Send Message → Bot Response → Confirm Order → Payment
Phone: Call Agent → Place Order → Payment
```

### 5. Payment Processing
```
M-Pesa STK Push → Payment Confirmation → Order Status Update → Automatic Split:
├── Farmer Payment (Product Cost)
├── Transporter Payment (Delivery Fee)  
└── Platform Commission (Service Fee)
```

### 6. Delivery Assignment
```
Paid Order → Nearby Transporters Notified → Transporter Accepts → Route Created
```

### 7. Delivery Tracking
```
Pickup → In Transit → Near Destination → Delivered → Reviews
```

## 📱 Integration Systems

### M-Pesa Integration
- **STK Push**: Automatic payment prompts
- **Payment Verification**: Real-time payment confirmation
- **Automatic Payouts**: Split payments to farmers and transporters
- **B2C Payments**: Withdrawals to user accounts

### WhatsApp Integration
- **Order Processing**: Natural language order interpretation
- **Status Updates**: Automatic order status messages
- **Customer Support**: WhatsApp-based support
- **Marketing**: Broadcast messages to users

### SMS Integration (Africa's Talking)
- **Product Listings**: Farmers can list via SMS
- **Order Notifications**: SMS updates for all users
- **Payment Confirmations**: SMS receipts
- **Support**: SMS-based customer support

## 🗄️ Database Schema Highlights

### Key Relationships
```sql
-- Users and Profiles (One-to-One)
CustomUser ← FarmerProfile
CustomUser ← BuyerProfile  
CustomUser ← TransporterProfile

-- Products and Categories (Many-to-One)
Product → Category
Product → SubCategory
Product → FarmerProfile

-- Orders and Items (One-to-Many)
Order ← OrderItem
Order → BuyerProfile
Order → TransporterProfile

-- Location Hierarchy
County ← SubCounty ← Ward
```

### Important Indexes
- Product search by category and location
- Order lookup by status and date
- User lookup by phone number
- Geographic queries for nearby farmers/transporters

## 🚀 Setup Instructions

### Prerequisites
```bash
Python 3.9+
Django 4.2+
PostgreSQL 12+
Redis (for caching)
```

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# M-Pesa
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_SHORTCODE=your_shortcode
MPESA_PASSKEY=your_passkey

# Africa's Talking
AT_USERNAME=your_username
AT_API_KEY=your_api_key

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
WHATSAPP_NUMBER=whatsapp:+254XXXXXXXXX
```

### Installation
```bash
# Clone repository
git clone https://github.com/steveongera/agrilink.git
cd agrilink

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Database setup
python manage.py makemigrations
python manage.py migrate

# Load initial data
python manage.py loaddata fixtures/counties.json
python manage.py loaddata fixtures/categories.json

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

## 📊 Business Model

### Revenue Streams
1. **Commission**: 5% commission on each successful transaction
2. **Delivery Fees**: 10% of delivery charges
3. **Premium Listings**: Featured product placements
4. **Subscription**: Premium farmer accounts
5. **Advertising**: Banner ads for agricultural businesses

### Commission Structure
```
Order Total: KES 1,000
├── Farmer Receives: KES 920 (92%)
├── Platform Commission: KES 50 (5%)
├── Delivery Fee: KES 200 (20% for platform)
└── Transporter Receives: KES 160 (80% of delivery)
```

## 🔐 Security Features

### Data Protection
- User authentication and authorization
- Phone number verification
- Secure payment processing
- Data encryption at rest and in transit
- GDPR-compliant data handling

### Fraud Prevention
- Order verification system
- User rating and review system
- Transaction monitoring
- Suspicious activity detection
- Account verification requirements

## 📈 Analytics & Reporting

### Admin Dashboard
- Daily/Monthly sales reports
- User growth metrics
- Product performance analytics
- Geographic sales distribution
- Revenue and commission tracking

### Farmer Dashboard
- Sales performance
- Product views and engagement
- Customer reviews and ratings
- Earnings and payout history

### Buyer Dashboard
- Order history
- Favorite farmers and products
- Spending analytics
- Delivery performance

## 🎯 API Endpoints

### Authentication
```
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/verify-phone/
```

### Products
```
GET /api/products/
POST /api/products/
GET /api/products/{id}/
GET /api/products/search/?q=tomatoes&location=nairobi
```

### Orders
```
POST /api/orders/
GET /api/orders/{id}/
POST /api/orders/{id}/pay/
GET /api/orders/{id}/track/
```

### M-Pesa Callbacks
```
POST /api/mpesa/stk-callback/
POST /api/mpesa/b2c-callback/
```

## 🤝 Third-Party Integrations

### Payment Gateway
- **Safaricom M-Pesa**: Primary payment method
- **Airtel Money**: Secondary payment option
- **Bank Transfers**: For large transactions

### Communication
- **Africa's Talking**: SMS services
- **Twilio**: WhatsApp integration
- **Firebase**: Push notifications

### Maps & Location
- **Google Maps**: Location services
- **Mapbox**: Route optimization
- **OpenStreetMap**: Offline mapping

## 🛠️ Development Roadmap

### Phase 1 (MVP) ✅
- User registration and profiles
- Product listing and search
- Basic order management
- M-Pesa integration
- Admin dashboard

### Phase 2 (Current)
- WhatsApp integration
- SMS product listing
- Delivery tracking
- Review system
- Mobile app (React Native)

### Phase 3 (Planned)
- AI-powered crop recommendations
- Weather integration
- Bulk order management
- Export documentation
- Multi-language support

### Phase 4 (Future)
- IoT integration for farm monitoring
- Blockchain supply chain tracking
- Credit and insurance services
- International expansion

## 📞 Support & Contact

### Customer Support
- **Phone**: 0112284093
- **Email**: support@agrilink.co.ke
- **WhatsApp**: +254112284093
- **Support Hours**: 8 AM - 8 PM (EAT)

### Technical Support
- **Developer**: Steve Ongera
- **Email**: steve@agrilink.co.ke
- **GitHub**: [@steveongera](https://github.com/steveongera)

## 📄 License

This project is proprietary software developed for AgriLink Platform. All rights reserved.

---

## 🔧 Additional Technical Implementation

### Custom Django Commands

Create these management commands for platform maintenance:

```python
# management/commands/process_sms_listings.py
# Processes SMS product listings from Africa's Talking

# management/commands/update_analytics.py
# Updates daily analytics data

# management/commands/send_notifications.py
# Sends pending notifications via SMS/Email

# management/commands/process_payouts.py
# Processes automatic payouts to farmers and transporters
```

### Celery Tasks (Asynchronous Processing)

```python
# tasks.py
from celery import shared_task

@shared_task
def process_mpesa_payment(checkout_request_id):
    """Process M-Pesa payment confirmation"""
    pass

@shared_task
def send_order_notifications(order_id):
    """Send order notifications to all parties"""
    pass

@shared_task
def update_delivery_tracking(order_id, status):
    """Update delivery status and notify customer"""
    pass

@shared_task
def process_automatic_payouts():
    """Process daily payouts to users"""
    pass
```

### Custom Middlewares

```python
# middleware.py
class UserTypeMiddleware:
    """Redirect users based on their type"""
    
class LocationMiddleware:
    """Auto-detect user location for better experience"""
    
class AnalyticsMiddleware:
    """Track user interactions for analytics"""
```

### API Serializers Structure

```python
# serializers.py
from rest_framework import serializers

class ProductListSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source='farmer.farm_name')
    main_image = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    
class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
class FarmerProfileSerializer(serializers.ModelSerializer):
    rating = serializers.ReadOnlyField()
    total_products = serializers.SerializerMethodField()
```

## 🎨 Frontend Technologies

### Web Application Stack
```
React.js / Vue.js (Frontend)
├── State Management: Redux/Vuex
├── UI Framework: Tailwind CSS / Material-UI
├── Maps: Google Maps React
├── Charts: Chart.js / D3.js
└── PWA: Service Workers for offline support
```

### Mobile Application
```
React Native / Flutter
├── Navigation: React Navigation
├── State: Redux Toolkit
├── UI: Native Base / Flutter Material
├── Maps: React Native Maps
└── Push Notifications: Firebase
```

## 🧪 Testing Strategy

### Backend Testing
```python
# tests/test_models.py
class ProductModelTest(TestCase):
    def test_product_creation(self):
        # Test product model functionality
        
# tests/test_views.py
class OrderViewTest(APITestCase):
    def test_create_order(self):
        # Test order creation API
        
# tests/test_mpesa.py
class MpesaIntegrationTest(TestCase):
    def test_stk_push(self):
        # Test M-Pesa STK Push functionality
```

### Load Testing
```python
# locustfile.py
from locust import HttpUser, task, between

class AgriLinkUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def browse_products(self):
        self.client.get("/api/products/")
    
    @task
    def create_order(self):
        self.client.post("/api/orders/", json={
            "items": [{"product_id": 1, "quantity": 5}]
        })
```

## 🔄 Data Migration Scripts

### Initial Data Setup
```python
# management/commands/setup_initial_data.py
from django.core.management.base import BaseCommand
from agrilink.models import County, Category

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Create Kenya counties
        counties_data = [
            {"name": "Nairobi", "code": "047"},
            {"name": "Kiambu", "code": "022"},
            # ... all 47 counties
        ]
        
        # Create product categories
        categories_data = [
            {"name": "Cereals", "description": "Maize, wheat, rice, etc."},
            {"name": "Vegetables", "description": "Fresh vegetables"},
            # ... all categories
        ]
```

## 📦 Deployment Configuration

### Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "agrilink.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DEBUG=0
      - DATABASE_URL=postgresql://user:pass@db:5432/agrilink
      
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: agrilink
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data/
      
  redis:
    image: redis:6-alpine
    
  celery:
    build: .
    command: celery -A agrilink worker -l info
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

### Nginx Configuration
```nginx
# nginx.conf
server {
    listen 80;
    server_name agrilink.co.ke;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /var/www/agrilink/static/;
    }
    
    location /media/ {
        alias /var/www/agrilink/media/;
    }
}
```

## 🚀 Scaling Considerations

### Database Optimization
```python
# Database indexes for performance
class Meta:
    indexes = [
        models.Index(fields=['category', 'county', '-created_at']),
        models.Index(fields=['farmer', 'is_active']),
        models.Index(fields=['buyer', '-created_at']),
    ]
```

### Caching Strategy
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache frequently accessed data
from django.core.cache import cache

def get_featured_products():
    products = cache.get('featured_products')
    if not products:
        products = Product.objects.filter(is_featured=True)[:20]
        cache.set('featured_products', products, 3600)  # 1 hour
    return products
```

### Load Balancing
```python
# Use multiple database replicas
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'agrilink_primary',
        # ... primary database config
    },
    'replica1': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'agrilink_replica1',
        # ... replica database config
    }
}

DATABASE_ROUTERS = ['agrilink.routers.DatabaseRouter']
```

## 🌍 Internationalization

### Multi-language Support
```python
# settings.py
LANGUAGES = [
    ('en', 'English'),
    ('sw', 'Kiswahili'),
    ('ka', 'Kikamba'),
    ('ku', 'Kikuyu'),
    ('lu', 'Luhya'),
]

USE_I18N = True
USE_L10N = True

# Translation strings
from django.utils.translation import gettext_lazy as _

class Product(models.Model):
    name = models.CharField(_('Product Name'), max_length=200)
    description = models.TextField(_('Description'))
```

### Currency Localization
```python
# Handle different currencies for future expansion
class CurrencyRate(models.Model):
    from_currency = models.CharField(max_length=3, default='KES')
    to_currency = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=10, decimal_places=4)
    updated_at = models.DateTimeField(auto_now=True)
```

## 🎯 Marketing Integration

### Referral System
```python
class ReferralProgram(models.Model):
    referrer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='referrals_made')
    referred = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='referral_source')
    referral_code = models.CharField(max_length=20, unique=True)
    reward_amount = models.DecimalField(max_digits=8, decimal_places=2, default=100)
    is_claimed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Loyalty Program
```python
class LoyaltyPoints(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    total_points = models.PositiveIntegerField(default=0)
    tier = models.CharField(max_length=20, choices=[
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ], default='bronze')
```

## 🔐 Advanced Security

### Rate Limiting
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='10/m', method='POST')
def create_order(request):
    # Limit order creation to prevent spam
    pass
```

### API Security
```python
# JWT Authentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

class ProductViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
```

## 📊 Advanced Analytics

### Custom Analytics Models
```python
class UserBehaviorAnalytics(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100)
    page_visited = models.CharField(max_length=200)
    time_spent = models.PositiveIntegerField()  # in seconds
    action_taken = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class ProductAnalytics(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0)
    cart_additions = models.PositiveIntegerField(default=0)
    purchases = models.PositiveIntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    date = models.DateField(auto_now_add=True)
```

This completes the comprehensive AgriLink platform documentation. The system is designed to be scalable, secure, and user-friendly while addressing the specific needs of the Kenyan agricultural market.