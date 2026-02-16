"""
URL configuration for lepstore project.
"""
from django.contrib import admin
from django.urls import path, include
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
    path('admin/', lep_admin.urls),
    # Keep the default admin available at /dj-admin/ if needed
    path('dj-admin/', admin.site.urls),
    # Keep admin dashboard view reachable
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('', include('store.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('accounts/', include('accounts.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
