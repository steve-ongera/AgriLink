from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db.models import Q, Avg, Count, Sum, F
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import (
    Product, Category, SubCategory, ProductImage, FarmerProfile, 
    Order, OrderItem, Cart, CartItem, FarmerReview, CustomUser,
    County, SubCounty, Ward
)

def index(request):
    """
    Home page view displaying featured products, categories, and product tabs
    """
    # Get featured products (limit to 8)
    featured_products = Product.objects.filter(
        is_featured=True, 
        is_active=True,
        stock_status__in=['available', 'low_stock']
    ).select_related('category', 'subcategory', 'farmer').prefetch_related('images')[:8]
    
    # Add main_image property to featured products
    for product in featured_products:
        main_image = product.images.filter(is_main=True).first()
        if not main_image:
            main_image = product.images.first()
        product.main_image = main_image
        # Note: discount_percentage is already calculated as a property in the model
    
    # Get active categories with product count
    categories = Category.objects.filter(is_active=True).annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    ).order_by('sort_order', 'name')[:8]
    
    # Get products for tabs
    # Vegetables (assuming there's a category or subcategory for vegetables)
    vegetables = Product.objects.filter(
        Q(category__name__icontains='vegetables') | Q(subcategory__name__icontains='vegetables') | Q(category__name__icontains='crops'),
        is_active=True,
        stock_status__in=['available', 'low_stock']
    ).select_related('category', 'subcategory', 'farmer').prefetch_related('images')[:8]
    
    # Fruits
    fruits = Product.objects.filter(
        Q(category__name__icontains='fruits') | Q(subcategory__name__icontains='fruits'),
        is_active=True,
        stock_status__in=['available', 'low_stock']
    ).select_related('category', 'subcategory', 'farmer').prefetch_related('images')[:8]
    
    # New arrivals (products created in last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_products = Product.objects.filter(
        is_active=True,
        stock_status__in=['available', 'low_stock'],
        created_at__gte=thirty_days_ago
    ).select_related('category', 'subcategory', 'farmer').prefetch_related('images').order_by('-created_at')[:8]
    
    # Organic products
    organic_products = Product.objects.filter(
        is_organic=True,
        is_active=True,
        stock_status__in=['available', 'low_stock']
    ).select_related('category', 'subcategory', 'farmer').prefetch_related('images')[:8]
    
    # Add main_image to all product querysets
    for product_list in [vegetables, fruits, new_products, organic_products]:
        for product in product_list:
            main_image = product.images.filter(is_main=True).first()
            if not main_image:
                main_image = product.images.first()
            product.main_image = main_image
            # Note: discount_percentage is already calculated as a property in the model
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'vegetables': vegetables,
        'fruits': fruits,
        'new_products': new_products,
        'organic_products': organic_products,
    }
    
    return render(request, 'home.html', context)
def product_detail(request, slug):
    """
    Product detail page view
    """
    # Get the product
    product = get_object_or_404(
        Product.objects.select_related('category', 'subcategory', 'farmer__user')
        .prefetch_related('images'),
        slug=slug,
        is_active=True
    )
    
    # Increment view count
    Product.objects.filter(id=product.id).update(view_count=F('view_count') + 1)
    
    # Get product images
    product_images = product.images.all().order_by('sort_order', 'created_at')
    main_image = product_images.filter(is_main=True).first()
    if not main_image:
        main_image = product_images.first()
    
    # Calculate pricing
    savings_amount = 0
    savings_percentage = 0
    if product.discount_price and product.discount_price < product.price:
        savings_amount = product.price - product.discount_price
        savings_percentage = round((savings_amount / product.price) * 100)
    
    # Get stock status info
    if product.stock_status == 'available':
        stock_info = {
            'class': 'success',
            'icon': 'check-circle',
            'text': 'In Stock'
        }
    elif product.stock_status == 'low_stock':
        stock_info = {
            'class': 'warning',
            'icon': 'exclamation-triangle',
            'text': 'Low Stock'
        }
    elif product.stock_status == 'sold_out':
        stock_info = {
            'class': 'danger',
            'icon': 'times-circle',
            'text': 'Out of Stock'
        }
    elif product.stock_status == 'harvesting':
        stock_info = {
            'class': 'info',
            'icon': 'clock',
            'text': 'Currently Harvesting'
        }
    else:
        stock_info = {
            'class': 'secondary',
            'icon': 'calendar',
            'text': 'Pre-Order Available'
        }
    
    # Get reviews
    reviews = FarmerReview.objects.filter(
        farmer=product.farmer,
        is_approved=True
    ).select_related('buyer__user').order_by('-created_at')
    
    # Calculate review stats
    total_reviews = reviews.count()
    if total_reviews > 0:
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        avg_rating = round(avg_rating, 1)
        
        # Calculate star distribution
        stars_full = int(avg_rating)
        stars_half = 1 if avg_rating - stars_full >= 0.5 else 0
        
        # Calculate rating percentages for breakdown
        rating_counts = {}
        for i in range(1, 6):
            rating_counts[i] = reviews.filter(rating=i).count()
        
        rating_percentages = {}
        for i in range(1, 6):
            rating_percentages[i] = round((rating_counts[i] / total_reviews) * 100) if total_reviews > 0 else 0
    else:
        avg_rating = 0
        stars_full = 0
        stars_half = 0
        rating_percentages = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    # Get related products (same category, different product)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True,
        stock_status__in=['available', 'low_stock']
    ).exclude(id=product.id).select_related('category', 'farmer').prefetch_related('images')[:4]
    
    # Add main_image to related products
    for related_product in related_products:
        related_main_image = related_product.images.filter(is_main=True).first()
        if not related_main_image:
            related_main_image = related_product.images.first()
        related_product.main_image = related_main_image
        # Note: discount_percentage is already calculated as a property in the model
    
    # Get frequently bought together products (mock implementation)
    # In a real scenario, you'd analyze order history
    frequently_bought = Product.objects.filter(
        category=product.category,
        is_active=True,
        stock_status__in=['available', 'low_stock']
    ).exclude(id=product.id).select_related('category', 'farmer').prefetch_related('images')[:4]
    
    # Add main_image to frequently bought products
    for freq_product in frequently_bought:
        freq_main_image = freq_product.images.filter(is_main=True).first()
        if not freq_main_image:
            freq_main_image = freq_product.images.first()
        freq_product.main_image = freq_main_image
        # Note: discount_percentage is already calculated as a property in the model
    
    # Get recently viewed products from session
    recently_viewed_ids = request.session.get('recently_viewed', [])
    if product.id in recently_viewed_ids:
        recently_viewed_ids.remove(product.id)
    recently_viewed_ids.insert(0, product.id)
    recently_viewed_ids = recently_viewed_ids[:10]  # Keep only last 10
    request.session['recently_viewed'] = recently_viewed_ids
    
    recently_viewed = Product.objects.filter(
        id__in=recently_viewed_ids,
        is_active=True
    ).exclude(id=product.id).select_related('category', 'farmer').prefetch_related('images')[:4]
    
    # Add main_image to recently viewed products
    for recent_product in recently_viewed:
        recent_main_image = recent_product.images.filter(is_main=True).first()
        if not recent_main_image:
            recent_main_image = recent_product.images.first()
        recent_product.main_image = recent_main_image
        # Note: discount_percentage is already calculated as a property in the model
    
    # WhatsApp integration
    whatsapp_number = "+254700000000"  # Replace with actual WhatsApp number from settings
    whatsapp_message = f"Hi! I'm interested in {product.name} (KSh {product.selling_price}). Is it available?"
    
    # Group attributes (if you have product attributes - this is a placeholder)
    grouped_attributes = {}  # Implement based on your product attribute model if you have one
    
    context = {
        'product': product,
        'main_image': main_image,
        'product_images': product_images,
        'savings_amount': savings_amount,
        'savings_percentage': savings_percentage,
        'stock_info': stock_info,
        'reviews': reviews[:10],  # Show first 10 reviews
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
        'stars_full': stars_full,
        'stars_half': stars_half,
        'rating_percentages': rating_percentages,
        'related_products': related_products,
        'frequently_bought': frequently_bought,
        'recently_viewed': recently_viewed,
        'whatsapp_number': whatsapp_number,
        'whatsapp_message': whatsapp_message,
        'grouped_attributes': grouped_attributes,
    }
    
    return render(request, 'product_detail.html', context)

@require_POST
def add_to_cart(request, product_id):
    """
    Add product to cart
    """
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        quantity = int(request.POST.get('quantity', 1))
        
        # Check stock availability
        if not product.is_in_stock:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Product is out of stock'
                })
            else:
                messages.error(request, 'Product is out of stock')
                return redirect('product_detail', slug=product.slug)
        
        # Check quantity availability
        if quantity > product.available_quantity:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Only {product.available_quantity} units available'
                })
            else:
                messages.error(request, f'Only {product.available_quantity} units available')
                return redirect('product_detail', slug=product.slug)
        
        # Get or create cart
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(session_id=session_id)
        
        # If user is logged in and has buyer profile, associate cart
        if request.user.is_authenticated and hasattr(request.user, 'buyer_profile'):
            cart.buyer = request.user.buyer_profile
            cart.save()
        
        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        # Get updated cart total
        cart_total = cart.total_items
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to cart',
                'cart_total': cart_total
            })
        else:
            messages.success(request, f'{product.name} added to cart')
            return redirect('product_detail', slug=product.slug)
            
    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Error adding product to cart'
            })
        else:
            messages.error(request, 'Error adding product to cart')
            return redirect('product_detail', slug=product.slug)


def product_list(request):
    """
    Product listing page with comprehensive filters and sorting
    """
    # Base queryset
    products = Product.objects.filter(is_active=True).select_related(
        'category', 'subcategory', 'farmer__user'
    ).prefetch_related('images')
    
    # Initialize filter tracking
    has_filters = False
    
    # Search filter
    search_query = request.GET.get('q', '').strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(subcategory__name__icontains=search_query) |
            Q(farmer__farm_name__icontains=search_query) |
            Q(variety__icontains=search_query)
        )
        has_filters = True
    
    # Category filter
    current_category = request.GET.get('category')
    if current_category:
        products = products.filter(category__slug=current_category)
        has_filters = True
    
    # Subcategory filter
    current_subcategory = request.GET.get('subcategory')
    if current_subcategory:
        products = products.filter(subcategory__slug=current_subcategory)
        has_filters = True
    
    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            min_price = Decimal(min_price)
            products = products.filter(
                Q(discount_price__gte=min_price, discount_price__isnull=False) |
                Q(price__gte=min_price, discount_price__isnull=True)
            )
            has_filters = True
        except (ValueError, TypeError):
            min_price = None
    
    if max_price:
        try:
            max_price = Decimal(max_price)
            products = products.filter(
                Q(discount_price__lte=max_price, discount_price__isnull=False) |
                Q(price__lte=max_price, discount_price__isnull=True)
            )
            has_filters = True
        except (ValueError, TypeError):
            max_price = None
    
    # Stock status filter
    stock_status = request.GET.get('stock_status')
    if stock_status:
        products = products.filter(stock_status=stock_status)
        has_filters = True
    
    # Featured products filter
    featured = request.GET.get('featured')
    if featured:
        products = products.filter(is_featured=True)
        has_filters = True
    
    # Organic products filter
    organic = request.GET.get('organic')
    if organic:
        products = products.filter(is_organic=True)
        has_filters = True
    
    # Quality grade filter
    quality_grade = request.GET.get('quality_grade')
    if quality_grade:
        products = products.filter(quality_grade=quality_grade)
        has_filters = True
    
    # Farming method filter
    farming_method = request.GET.get('farming_method')
    if farming_method:
        products = products.filter(farming_method__icontains=farming_method)
        has_filters = True
    
    # County filter (farmer location)
    county = request.GET.get('county')
    if county:
        products = products.filter(farmer__county__slug=county)
        has_filters = True
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    sort_options = [
        ('-created_at', 'Newest First'),
        ('created_at', 'Oldest First'),
        ('name', 'Name A-Z'),
        ('-name', 'Name Z-A'),
        ('price', 'Price Low to High'),
        ('-price', 'Price High to Low'),
        ('-view_count', 'Most Popular'),
        ('-total_sold', 'Best Selling'),
        ('available_quantity', 'Stock Low to High'),
        ('-available_quantity', 'Stock High to Low'),
    ]
    
    # Apply sorting
    if sort_by == 'price':
        # Sort by actual selling price (considering discounts)
        products = products.extra(
            select={
                'selling_price': 'CASE WHEN discount_price IS NOT NULL AND discount_price < price THEN discount_price ELSE price END'
            }
        ).order_by('selling_price')
    elif sort_by == '-price':
        products = products.extra(
            select={
                'selling_price': 'CASE WHEN discount_price IS NOT NULL AND discount_price < price THEN discount_price ELSE price END'
            }
        ).order_by('-selling_price')
    else:
        products = products.order_by(sort_by)
    
    # Pagination
    items_per_page = int(request.GET.get('per_page', 12))
    per_page_options = [8, 12, 16, 24, 36]
    if items_per_page not in per_page_options:
        items_per_page = 12
    
    paginator = Paginator(products, items_per_page)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    # Add main_image to products
    for product in page_obj:
        main_image = product.images.filter(is_main=True).first()
        if not main_image:
            main_image = product.images.first()
        product.main_image = main_image
    
    # Get filter options
    # Categories with product count
    categories = Category.objects.filter(is_active=True).annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    ).order_by('sort_order', 'name')
    
    # Subcategories for current category
    subcategories = []
    if current_category:
        try:
            category = Category.objects.get(slug=current_category)
            subcategories = category.subcategories.filter(is_active=True).annotate(
                product_count=Count('products', filter=Q(products__is_active=True))
            ).order_by('name')
        except Category.DoesNotExist:
            pass
    
    # Counties with farmer count
    counties = County.objects.annotate(
        farmer_count=Count('farmerprofile', filter=Q(farmerprofile__is_active=True))
    ).filter(farmer_count__gt=0).order_by('name')
    
    # Stock status choices
    stock_status_choices = Product.STOCK_STATUS_CHOICES
    
    # Quality grade choices
    quality_grade_choices = Product.QUALITY_GRADE_CHOICES
    
    # Get unique farming methods
    farming_methods = Product.objects.filter(
        is_active=True, 
        farming_method__isnull=False
    ).exclude(farming_method='').values_list('farming_method', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'subcategories': subcategories,
        'counties': counties,
        'stock_status_choices': stock_status_choices,
        'quality_grade_choices': quality_grade_choices,
        'farming_methods': farming_methods,
        'sort_options': sort_options,
        'per_page_options': per_page_options,
        
        # Current filter values
        'search_query': search_query,
        'current_category': current_category,
        'current_subcategory': current_subcategory,
        'min_price': min_price,
        'max_price': max_price,
        'stock_status': stock_status,
        'county': county,
        'quality_grade': quality_grade,
        'farming_method': farming_method,
        'sort_by': sort_by,
        'items_per_page': items_per_page,
        'has_filters': has_filters,
        'total_products': paginator.count,
    }
    
    return render(request, 'product_list.html', context)

def category_products(request, slug):
    """
    Products by category
    """
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    products = Product.objects.filter(
        category=category,
        is_active=True
    ).select_related('category', 'subcategory', 'farmer').prefetch_related('images')
    
    # Apply additional filters
    subcategory_slug = request.GET.get('subcategory')
    if subcategory_slug:
        products = products.filter(subcategory__slug=subcategory_slug)
    
    # Sort products
    sort_by = request.GET.get('sort', '-created_at')
    products = products.order_by(sort_by)
    
    # Add main_image to products
    for product in products:
        main_image = product.images.filter(is_main=True).first()
        if not main_image:
            main_image = product.images.first()
        product.main_image = main_image
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    # Get subcategories for this category
    subcategories = category.subcategories.filter(is_active=True)
    
    context = {
        'category': category,
        'products': products,
        'subcategories': subcategories,
        'current_subcategory': subcategory_slug,
    }
    
    return render(request, 'category_products.html', context)


 

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactMessage

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Save message to DB
        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message
        )

        messages.success(request, "Your message has been sent successfully!")
        return redirect('contact')  # Redirect to avoid re-submission

    return render(request, 'contact.html')


def about_us_view(request):
    return render(request, 'about.html')

from django.shortcuts import render

def custom_page_not_found(request, exception):
    return render(request, '404.html', status=404)

def custom_server_error(request):
    return render(request, '500.html', status=500)
