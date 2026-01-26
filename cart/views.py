from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from store.models import Product
from .cart import Cart


def cart_detail(request):
    """Display the cart"""
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})


@require_POST
def cart_add(request, product_id):
    """Add a product to the cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    quantity = int(request.POST.get('quantity', 1))
    
    # Check stock availability
    current_quantity = cart.get_product_quantity(product)
    if current_quantity + quantity > product.stock:
        messages.error(request, f'Sorry, only {product.stock} items available in stock.')
        return redirect('store:product_detail', slug=product.slug)
    
    cart.add(product=product, quantity=quantity, override_quantity=False)
    messages.success(request, f'{product.name} added to your cart.')
    
    # Redirect based on POST parameter
    if request.POST.get('buy_now'):
        return redirect('cart:cart_detail')
    return redirect(request.META.get('HTTP_REFERER', 'store:home'))


@require_POST
def cart_remove(request, product_id):
    """Remove a product from the cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, f'{product.name} removed from your cart.')
    return redirect('cart:cart_detail')


@require_POST
def cart_update(request, product_id):
    """Update product quantity in cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        cart.remove(product)
        messages.success(request, f'{product.name} removed from your cart.')
    elif quantity > product.stock:
        messages.error(request, f'Sorry, only {product.stock} items available in stock.')
    else:
        cart.add(product=product, quantity=quantity, override_quantity=True)
        messages.success(request, 'Cart updated successfully.')
    
    return redirect('cart:cart_detail')
