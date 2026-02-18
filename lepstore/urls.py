"""
URL configuration for lepstore project.
"""
from django.contrib import admin
from django.urls import path, include
from store import views as store_views
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from dashboard.views import admin_dashboard
from .custom_admin import lep_admin

# Use custom admin site (lep_admin) as primary admin at /admin/
lep_admin.index_template = 'admin/custom_index.html'
lep_admin.site_header = "LepStore Admin Dashboard"
lep_admin.site_title = "LepStore Admin"
lep_admin.index_title = "Welcome to LepStore Admin"
urlpatterns = [
    # Register the custom admin urls under the `lep_admin` namespace so
    # templates that reverse `lep_admin:...` will resolve correctly.
    path('admin/', include((lep_admin.urls[0], lep_admin.name), namespace=lep_admin.name)),
    # Keep admin dashboard view reachable
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    # Root-level contact alias (no namespace) to satisfy templates reversing 'contact'
    path('contact/', store_views.contact, name='contact'),
    path('', include('store.urls')),

    # Favicons served from static — add redirects at site root to avoid 404s on Vercel
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'images/favicon.png')),
    path('favicon.png', RedirectView.as_view(url=settings.STATIC_URL + 'images/favicon.png')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('accounts/', include('accounts.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
