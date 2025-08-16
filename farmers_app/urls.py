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

]