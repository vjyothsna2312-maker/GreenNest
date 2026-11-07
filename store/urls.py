from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('category/<str:category_name>/', views.category, name='category'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('register/', views.register, name='register'),
    path('my-orders/', views.my_orders, name='my_orders'),
    
]