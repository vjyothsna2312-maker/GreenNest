from django.contrib import admin
from .models import Product, Order, OrderItem

admin.site.register(Product)
@admin.register(Order)

class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'full_name',
        'total_amount',
        'payment_status',
        'status',
        'created_at'
    )

    list_filter = (
        'payment_status',
        'status',
        'created_at'
    )

    search_fields = (
        'full_name',
        'user__username',
        'razorpay_payment_id'
    )

    def save_model(self, request, obj, form, change):

        if obj.payment_status != 'Paid':
            obj.status = 'Pending'

        super().save_model(request, obj, form, change)

admin.site.register(OrderItem)