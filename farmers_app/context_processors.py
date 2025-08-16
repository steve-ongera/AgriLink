from django.db.models import Count
from .models import Category, Cart, CartItem
from django.db.models import Max, Min
from django.db import models

def categories(request):
    """
    Context processor to make categories available across all templates
    """
    categories = Category.objects.filter(is_active=True).annotate(
        product_count=Count('products', filter=models.Q(products__is_active=True))
    ).order_by('name')
    
    return {
        'global_categories': categories,
    }

def cart_context(request):
    """
    Context processor to make cart information available across all templates
    """
    cart_items_count = 0
    cart_total = 0
    
    try:
        # For authenticated users, try to get cart by customer
        if request.user.is_authenticated:
            try:
                customer = request.user.customer
                cart = Cart.objects.filter(customer=customer).first()
            except AttributeError:
                # User doesn't have a customer profile
                cart = None
        else:
            # For anonymous users, use session
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
            
            cart = Cart.objects.filter(session_id=session_id).first()
        
        if cart:
            # Method 1: If you have a total_items property/method on your Cart model
            if hasattr(cart, 'total_items'):
                cart_items_count = cart.total_items
            else:
                # Method 2: Count cart items through related CartItem model
                cart_items_count = cart.cartitem_set.aggregate(
                    total=models.Sum('quantity')
                )['total'] or 0
            
            # Calculate total amount
            if hasattr(cart, 'total_amount'):
                cart_total = cart.total_amount
            else:
                # Calculate total from cart items
                cart_total = sum(
                    item.quantity * item.product.price 
                    for item in cart.cartitem_set.all()
                )
                
    except Exception as e:
        # Log the error for debugging
        print(f"Cart context processor error: {e}")
        cart_items_count = 0
        cart_total = 0
    
    return {
        'cart_items_count': cart_items_count,
        'cart_total': cart_total,
    }