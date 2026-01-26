from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from cart.cart import Cart
from .models import Order, OrderItem, ShippingMethod
from .forms import OrderCreateForm
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def checkout(request):
    """Checkout page"""
    cart = Cart(request)
    
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('store:home')
    
    # Get shipping methods
    shipping_methods = ShippingMethod.objects.filter(is_active=True)
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        shipping_method_id = request.POST.get('shipping_method')
        
        if form.is_valid() and shipping_method_id:
            order = form.save(commit=False)
            
            # Associate with user if logged in
            if request.user.is_authenticated:
                order.user = request.user
            
            # Calculate totals
            order.subtotal = cart.get_total_price()
            
            # Add shipping cost
            shipping_method = get_object_or_404(ShippingMethod, id=shipping_method_id)
            order.shipping_cost = shipping_method.cost
            
            # Calculate total (add tax if needed)
            order.total = order.subtotal + order.shipping_cost
            
            order.save()
            
            # Create order items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    product_name=item['product'].name,
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            # Clear cart
            cart.clear()
            
            # Store order ID in session for payment
            request.session['order_id'] = order.id
            
            # Redirect based on payment method
            if order.payment_method == 'card':
                return redirect('orders:payment', order_id=order.id)
            elif order.payment_method == 'mpesa':
                return redirect('orders:mpesa_payment', order_id=order.id)
            else:
                return redirect('orders:order_complete', order_id=order.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill form if user is logged in
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }
        form = OrderCreateForm(initial=initial_data)
    
    context = {
        'cart': cart,
        'form': form,
        'shipping_methods': shipping_methods,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'orders/checkout.html', context)


def payment(request, order_id):
    """Stripe payment page"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        try:
            # Create Stripe PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=int(order.total * 100),  # Amount in cents
                currency='usd',
                metadata={'order_id': order.id}
            )
            
            context = {
                'order': order,
                'client_secret': intent.client_secret,
                'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            }
            return render(request, 'orders/payment.html', context)
        
        except Exception as e:
            messages.error(request, f'Payment error: {str(e)}')
            return redirect('orders:checkout')
    
    context = {
        'order': order,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'orders/payment.html', context)


def payment_success(request, order_id):
    """Handle successful payment"""
    order = get_object_or_404(Order, id=order_id)
    order.is_paid = True
    order.paid_at = timezone.now()
    order.status = 'processing'
    order.save()
    
    return redirect('orders:order_complete', order_id=order.id)


def mpesa_payment(request, order_id):
    """M-Pesa payment page (placeholder)"""
    order = get_object_or_404(Order, id=order_id)
    
    # TODO: Integrate with M-Pesa API (Daraja)
    # For now, this is a placeholder
    
    context = {'order': order}
    return render(request, 'orders/mpesa_payment.html', context)


def order_complete(request, order_id):
    """Order completion page"""
    order = get_object_or_404(Order, id=order_id)
    
    context = {'order': order}
    return render(request, 'orders/order_complete.html', context)


@login_required
def order_history(request):
    """User's order history"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    
    context = {'orders': orders}
    return render(request, 'orders/order_history.html', context)


@login_required
def order_detail(request, order_number):
    """View specific order details"""
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        order_number=order_number,
        user=request.user
    )
    
    context = {'order': order}
    return render(request, 'orders/order_detail.html', context)
