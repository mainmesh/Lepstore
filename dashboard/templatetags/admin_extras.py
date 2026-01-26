from django import template
from store.models import Product
from orders.models import Order
from django.contrib.auth.models import User

register = template.Library()


@register.inclusion_tag('admin/partials/quick_stats.html')
def admin_quick_stats():
    """Return small counts for display on the admin index page."""
    return {
        'total_products': Product.objects.count(),
        'total_orders': Order.objects.count(),
        'total_customers': User.objects.filter(is_staff=False).count(),
    }
