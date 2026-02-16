"""
URL configuration for lepstore project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from dashboard.views import admin_dashboard

# Custom admin URL configuration
admin.site.index_template = 'admin/custom_index.html'
admin.site.site_header = "LepStore Admin Dashboard"
admin.site.site_title = "LepStore Admin"
admin.site.index_title = "Welcome to LepStore Admin"
urlpatterns = [
    path('admin/', admin_dashboard, name='admin_dashboard'),
    path('dj-admin/', admin.site.urls),
    # Keep legacy admin login URL working by redirecting to the real admin login
    path('admin/login/', RedirectView.as_view(url='/dj-admin/login/', query_string=True, permanent=False)),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('', include('store.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('accounts/', include('accounts.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
