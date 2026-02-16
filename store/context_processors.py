from .models import Category


def categories(request):
    """Expose active categories to all templates for header/footer navigation."""
    cats = Category.objects.filter(is_active=True).order_by('name')
    return {
        'site_categories': cats,
    }
