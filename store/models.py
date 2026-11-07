from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=50)
    image = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

class Order(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
    max_length=20,
    choices=[
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    ],
    default='Pending'
)

    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)

    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)

    payment_status = models.CharField(max_length=20, default='Pending')


    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"


class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.product.name

    def __str__(self):
        return self.name