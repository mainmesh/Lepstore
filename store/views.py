from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Brand, Review, Bundle


def home(request):
    """Homepage with featured products and categories"""
    featured_products = Product.objects.filter(
        is_featured=True, 
        is_available=True
    ).select_related('category', 'brand').prefetch_related('images')[:8]
    
    top_rated = Product.objects.filter(
        is_top_rated=True,
        is_available=True
    ).select_related('category', 'brand').prefetch_related('images')[:6]
    
    new_arrivals = Product.objects.filter(
        is_new=True,
        is_available=True
    ).select_related('category', 'brand').prefetch_related('images')[:6]
    
    categories = Category.objects.filter(is_active=True)
    
    # Deals/Sale products
    sale_products = Product.objects.filter(
        is_available=True,
        discount_percentage__gt=0
    ).select_related('category', 'brand').prefetch_related('images')[:6]
    
    context = {
        'featured_products': featured_products,
        'top_rated': top_rated,
        'new_arrivals': new_arrivals,
        'categories': categories,
        'sale_products': sale_products,
    }
    return render(request, 'store/home.html', context)


def product_list(request):
    """Product listing with filtering and sorting"""
    products = Product.objects.filter(is_available=True).select_related('category', 'brand').prefetch_related('images')
    
    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Brand filter
    brand_slugs = request.GET.getlist('brand')
    if brand_slugs:
        products = products.filter(brand__slug__in=brand_slugs)
    
    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Processor filter
    processors = request.GET.getlist('processor')
    if processors:
        processor_query = Q()
        for proc in processors:
            processor_query |= Q(processor__icontains=proc)
        products = products.filter(processor_query)
    
    # RAM filter
    ram_options = request.GET.getlist('ram')
    if ram_options:
        ram_query = Q()
        for ram in ram_options:
            ram_query |= Q(ram__icontains=ram)
        products = products.filter(ram_query)
    
    # Storage filter
    storage_options = request.GET.getlist('storage')
    if storage_options:
        storage_query = Q()
        for storage in storage_options:
            storage_query |= Q(storage__icontains=storage)
        products = products.filter(storage_query)
    
    # Rating filter
    min_rating = request.GET.get('rating')
    if min_rating:
        # This is simplified - in production, you'd want to annotate with avg rating
        products = products.filter(is_top_rated=True)
    
    # Search query
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(processor__icontains=query)
        )
    
    # Sorting
    sort = request.GET.get('sort', 'default')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'rating':
        products = products.filter(is_top_rated=True)
    else:
        products = products.order_by('-is_featured', '-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'brands': brands,
        'current_category': category_slug,
        'current_sort': sort,
        'query': query,
        'total_products': paginator.count,
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    """Product detail page with reviews and bundles"""
    product = get_object_or_404(
        Product.objects.select_related('category', 'brand').prefetch_related('images', 'reviews'),
        slug=slug
    )
    
    # Get approved reviews
    reviews = product.reviews.filter(is_approved=True).select_related('user').order_by('-created_at')
    
    # Get bundle recommendations
    bundles = Bundle.objects.filter(
        main_product=product,
        is_active=True
    ).prefetch_related('accessory_products__images')
    
    # Related products (same category, exclude current)
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id).select_related('category', 'brand').prefetch_related('images')[:4]
    
    # Check if user has purchased this product
    user_purchased = False
    if request.user.is_authenticated:
        from orders.models import OrderItem
        user_purchased = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__status='delivered'
        ).exists()
    
    context = {
        'product': product,
        'reviews': reviews,
        'bundles': bundles,
        'related_products': related_products,
        'user_purchased': user_purchased,
    }
    return render(request, 'store/product_detail.html', context)


def category_products(request, slug):
    """Products by category"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(
        category=category,
        is_available=True
    ).select_related('category', 'brand').prefetch_related('images')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'total_products': paginator.count,
    }
    return render(request, 'store/category_products.html', context)


@login_required
def add_review(request, slug):
    """Add a product review"""
    product = get_object_or_404(Product, slug=slug)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        title = request.POST.get('title')
        comment = request.POST.get('comment')
        
        if not all([rating, title, comment]):
            messages.error(request, 'All fields are required.')
            return redirect('store:product_detail', slug=slug)
        
        # Check if user already reviewed
        if Review.objects.filter(product=product, user=request.user).exists():
            messages.warning(request, 'You have already reviewed this product.')
            return redirect('store:product_detail', slug=slug)
        
        # Check if user purchased this product
        from orders.models import OrderItem
        purchased = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__status='delivered'
        ).exists()
        
        Review.objects.create(
            product=product,
            user=request.user,
            rating=int(rating),
            title=title,
            comment=comment,
            is_verified_purchase=purchased
        )
        
        messages.success(request, 'Thank you for your review!')
        return redirect('store:product_detail', slug=slug)
    
    return redirect('store:product_detail', slug=slug)


def search(request):
    """Search products"""
    query = request.GET.get('q', '')
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(processor__icontains=query),
            is_available=True
        ).select_related('category', 'brand').prefetch_related('images').distinct()
    else:
        products = Product.objects.none()
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'page_obj': page_obj,
        'total_results': paginator.count,
    }
    return render(request, 'store/search_results.html', context)


def contact(request):
    """Simple contact page to avoid missing reverse errors."""
    # Minimal contact info page; can be expanded later with a form.
    context = {
        'phone': '+254754102950',
        'email': 'support@lepstore.example',
    }
    return render(request, 'store/contact.html', context)


def shipping_info(request):
    """Static shipping information page referenced from the site header."""
    context = {
        'title': 'Shipping Information',
        'delivery_times': 'Local deliveries: 1-3 business days. International: 7-21 business days.',
        'rates_note': 'Shipping rates vary by weight and destination. See individual product pages for estimates.',
    }
    return render(request, 'store/shipping_info.html', context)


def health(request):
    """Lightweight health endpoint used by deploy checks."""
    return HttpResponse('OK', status=200)
