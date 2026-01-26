from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Avg, Q, F
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json

from store.models import Product, Category
from orders.models import Order, OrderItem
from django.contrib.auth.models import User


@staff_member_required
def admin_dashboard(request):
    """Main admin dashboard with analytics"""
    
    # Date ranges
    today = timezone.now()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    last_year = today - timedelta(days=365)
    
    # === OVERVIEW STATS ===
    total_revenue = Order.objects.filter(is_paid=True).aggregate(
        total=Sum('total')
    )['total'] or Decimal('0.00')
    
    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    total_customers = User.objects.filter(is_staff=False).count()
    
    # Recent stats
    revenue_30_days = Order.objects.filter(
        is_paid=True, 
        created_at__gte=last_30_days
    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    orders_30_days = Order.objects.filter(created_at__gte=last_30_days).count()
    new_customers_30_days = User.objects.filter(
        is_staff=False,
        date_joined__gte=last_30_days
    ).count()
    
    # Average order value
    avg_order_value = Order.objects.filter(is_paid=True).aggregate(
        avg=Avg('total')
    )['avg'] or Decimal('0.00')
    
    # === SALES TRENDS (Last 30 days) ===
    daily_sales = Order.objects.filter(
        created_at__gte=last_30_days,
        is_paid=True
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        revenue=Sum('total'),
        orders=Count('id')
    ).order_by('date')
    
    sales_dates = [item['date'].strftime('%Y-%m-%d') for item in daily_sales]
    sales_revenue = [float(item['revenue']) for item in daily_sales]
    sales_orders = [item['orders'] for item in daily_sales]
    
    # === ORDER STATUS BREAKDOWN ===
    order_status_data = Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    status_labels = [item['status'].title() for item in order_status_data]
    status_counts = [item['count'] for item in order_status_data]
    
    # === TOP SELLING PRODUCTS ===
    top_products = OrderItem.objects.values(
        'product__name'
    ).annotate(
        total_sold=Sum('quantity'),
        revenue=Sum(F('price') * F('quantity'))
    ).order_by('-total_sold')[:10]
    
    # === TOP CATEGORIES ===
    top_categories = Category.objects.annotate(
        product_count=Count('products'),
        total_sold=Count('products__orderitem')
    ).order_by('-total_sold')[:5]
    
    # === RECENT ORDERS ===
    recent_orders = Order.objects.select_related('user').prefetch_related('items')[:10]
    
    # === LOW STOCK ALERTS ===
    low_stock_products = Product.objects.filter(
        stock__lte=10,
        is_available=True
    ).order_by('stock')[:10]
    
    # === REVENUE BY PAYMENT METHOD ===
    payment_methods = Order.objects.filter(is_paid=True).values(
        'payment_method'
    ).annotate(
        total=Sum('total'),
        count=Count('id')
    )
    
    payment_labels = [item['payment_method'].title() for item in payment_methods]
    payment_totals = [float(item['total']) for item in payment_methods]
    
    # === MONTHLY REVENUE (Last 12 months) ===
    monthly_revenue = Order.objects.filter(
        created_at__gte=last_year,
        is_paid=True
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        revenue=Sum('total')
    ).order_by('month')
    
    monthly_labels = [item['month'].strftime('%b %Y') for item in monthly_revenue]
    monthly_values = [float(item['revenue']) for item in monthly_revenue]
    
    # === CUSTOMER GROWTH ===
    customer_growth = User.objects.filter(
        is_staff=False,
        date_joined__gte=last_year
    ).annotate(
        month=TruncMonth('date_joined')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    customer_labels = [item['month'].strftime('%b %Y') for item in customer_growth]
    customer_counts = [item['count'] for item in customer_growth]
    
    context = {
        # Overview stats
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_customers': total_customers,
        'revenue_30_days': revenue_30_days,
        'orders_30_days': orders_30_days,
        'new_customers_30_days': new_customers_30_days,
        'avg_order_value': avg_order_value,
        
        # Charts data
        'sales_dates': json.dumps(sales_dates),
        'sales_revenue': json.dumps(sales_revenue),
        'sales_orders': json.dumps(sales_orders),
        'status_labels': json.dumps(status_labels),
        'status_counts': json.dumps(status_counts),
        'payment_labels': json.dumps(payment_labels),
        'payment_totals': json.dumps(payment_totals),
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_values': json.dumps(monthly_values),
        'customer_labels': json.dumps(customer_labels),
        'customer_counts': json.dumps(customer_counts),
        
        # Lists
        'top_products': top_products,
        'top_categories': top_categories,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
    }
    
    return render(request, 'admin/dashboard.html', context)


@staff_member_required
def analytics_view(request):
    """Detailed analytics page"""
    today = timezone.now()
    last_30_days = today - timedelta(days=30)
    
    # Conversion rate
    total_visitors = 1000  # You'd track this with Google Analytics or similar
    conversion_rate = (Order.objects.filter(created_at__gte=last_30_days).count() / total_visitors * 100) if total_visitors > 0 else 0
    
    # Return customer rate
    repeat_customers = User.objects.filter(
        is_staff=False,
        orders__created_at__gte=last_30_days
    ).annotate(
        order_count=Count('orders')
    ).filter(order_count__gt=1).count()
    
    total_customers = User.objects.filter(is_staff=False, orders__created_at__gte=last_30_days).distinct().count()
    return_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
    
    context = {
        'conversion_rate': round(conversion_rate, 2),
        'return_rate': round(return_rate, 2),
    }
    
    return render(request, 'admin/analytics.html', context)
