from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.index, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:category_slug>/', views.category_products, name='category_products'),
    path('contact/', views.contact_view, name='contact'),
    path('about-us/', views.about_us_view, name='about_us'),

    # Cart operations
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/count/', views.cart_count, name='cart_count'),
    
    # Checkout process
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/process/', views.process_checkout, name='process_checkout'),

]