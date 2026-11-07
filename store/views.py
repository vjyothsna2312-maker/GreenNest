from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from .models import Product, Order, OrderItem

from django.conf import settings
from django.db import transaction

import razorpay


# ---------------- HOME PAGE ----------------

def home(request):

    products = Product.objects.all()

    return render(request, 'store/home.html', {
        'products': products
    })


# ---------------- CATEGORY PAGE ----------------

def category(request, category_name):

    products = Product.objects.filter(
        category__iexact=category_name
    )

    return render(request, 'store/category.html', {
        'products': products,
        'category_name': category_name
    })


# ---------------- ADD TO CART ----------------

def add_to_cart(request, product_id):

    if request.method != 'POST':
        return redirect('home')

    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})

    product_id = str(product.id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    cart[product_id] = cart.get(product_id, 0) + quantity

    request.session['cart'] = cart

    return redirect('cart')


# ---------------- VIEW CART ----------------

def view_cart(request):

    cart = request.session.get('cart', {})

    cart_items = []
    total = 0

    for product_id, quantity in cart.items():

        product = get_object_or_404(Product, id=product_id)

        subtotal = product.price * quantity

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

        total += subtotal

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total
    })


# ---------------- REMOVE FROM CART ----------------

def remove_from_cart(request, product_id):

    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session['cart'] = cart

    return redirect('cart')


# ---------------- USER REGISTRATION ----------------

def register(request):

    if request.method == 'POST':

        form = UserCreationForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect('home')

    else:

        form = UserCreationForm()

    return render(request, 'store/register.html', {
        'form': form
    })


# ---------------- CHECKOUT ----------------

@login_required
def checkout(request):

    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart')

    cart_items = []
    total = 0

    # Calculate total from database product prices

    for product_id, quantity in cart.items():

        product = get_object_or_404(Product, id=product_id)

        quantity = int(quantity)

        if quantity < 1:
            return redirect('cart')

        subtotal = product.price * quantity

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

        total += subtotal

    # GET REQUEST: Display checkout form

    if request.method == 'GET':

        return render(request, 'store/checkout.html', {
            'cart_items': cart_items,
            'total': total
        })

    # POST REQUEST: Create or reuse pending order

    if request.method == 'POST':

        pending_order_id = request.session.get(
            'pending_order_id'
        )

        order = None

        if pending_order_id:

            order = Order.objects.filter(
                id=pending_order_id,
                user=request.user,
                payment_status='Pending'
            ).first()

        # Check whether existing order matches current cart

        if order:

            existing_items = {
                str(item.product_id): item.quantity
                for item in order.items.all()
            }

            current_items = {
                str(item['product'].id): item['quantity']
                for item in cart_items
            }

            same_cart = existing_items == current_items

            same_details = (
                order.full_name == request.POST.get('full_name')
                and order.address == request.POST.get('address')
                and order.city == request.POST.get('city')
                and order.pincode == request.POST.get('pincode')
                and order.phone == request.POST.get('phone')
            )

            if not same_cart or not same_details:
                order = None

        # Create a new order if no matching pending order exists

        if order is None:

            with transaction.atomic():

                order = Order.objects.create(
                    user=request.user,
                    full_name=request.POST.get('full_name'),
                    address=request.POST.get('address'),
                    city=request.POST.get('city'),
                    pincode=request.POST.get('pincode'),
                    phone=request.POST.get('phone'),
                    total_amount=total
                )

                for item in cart_items:

                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        quantity=item['quantity'],
                        price=item['product'].price
                    )

            request.session['pending_order_id'] = order.id

        # Connect to Razorpay

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        # Create Razorpay order only if one does not already exist

        if not order.razorpay_order_id:

            payment_data = {
                'amount': int(order.total_amount * 100),
                'currency': 'INR',
                'receipt': f'order_{order.id}'
            }

            try:

                razorpay_order = client.order.create(
                    data=payment_data
                )

                order.razorpay_order_id = razorpay_order['id']
                order.save()

            except Exception:

                return render(request, 'store/checkout.html', {
                    'cart_items': cart_items,
                    'total': total,
                    'error': 'Unable to connect to the payment service. Please try again.'
                })

        # Display Razorpay payment button

        return render(request, 'store/checkout.html', {
            'cart_items': cart_items,
            'total': order.total_amount,
            'order': order,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'razorpay_order_id': order.razorpay_order_id,
            'amount': int(order.total_amount * 100)
        })


# ---------------- VERIFY PAYMENT ----------------

@login_required
def verify_payment(request):

    if request.method != 'POST':
        return redirect('cart')

    payment_data = {
        'razorpay_order_id': request.POST.get('razorpay_order_id'),
        'razorpay_payment_id': request.POST.get('razorpay_payment_id'),
        'razorpay_signature': request.POST.get('razorpay_signature')
    }

    # Check required payment information

    if not all(payment_data.values()):
        return redirect('cart')

    order = get_object_or_404(
        Order,
        razorpay_order_id=payment_data['razorpay_order_id'],
        user=request.user
    )

    # Prevent processing an already-paid order again

    if order.payment_status == 'Paid':

        request.session['cart'] = {}
        request.session.pop('pending_order_id', None)

        return render(request, 'store/order_success.html', {
            'order': order
        })

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    try:

        # Verify Razorpay signature

        client.utility.verify_payment_signature(payment_data)

        # Fetch payment information from Razorpay

        payment = client.payment.fetch(
            payment_data['razorpay_payment_id']
        )

        # Verify payment belongs to this order

        if payment['order_id'] != order.razorpay_order_id:
            raise ValueError('Payment order mismatch')

        # Verify amount and currency

        if payment['amount'] != int(order.total_amount * 100):
            raise ValueError('Payment amount mismatch')

        if payment['currency'] != 'INR':
            raise ValueError('Payment currency mismatch')

        # Payment must be captured

        if payment['status'] != 'captured':

            return render(request, 'store/checkout.html', {
                'error': 'Payment has not been completed yet.',
                'cart_items': [],
                'total': order.total_amount,
                'order': order,
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'razorpay_order_id': order.razorpay_order_id,
                'amount': int(order.total_amount * 100)
            })

        # Update order after successful verification

        order.razorpay_payment_id = payment_data['razorpay_payment_id']

        order.payment_status = 'Paid'

        order.save()

        # Clear cart and pending order reference

        request.session['cart'] = {}

        request.session.pop('pending_order_id', None)

        return render(request, 'store/order_success.html', {
            'order': order
        })

    except razorpay.errors.SignatureVerificationError:

        error_message = 'Payment verification failed. Please try again.'

    except Exception:

        error_message = 'Unable to verify payment. Please contact support.'

    return render(request, 'store/checkout.html', {
        'error': error_message,
        'cart_items': [],
        'total': order.total_amount,
        'order': order,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': order.razorpay_order_id,
        'amount': int(order.total_amount * 100)
    })


# ---------------- MY ORDERS ----------------

@login_required
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'store/my_orders.html', {
        'orders': orders
    })