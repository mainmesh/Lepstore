from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _


class LepAdminSite(AdminSite):
    site_header = "LepStore Admin"
    site_title = "LepStore Admin"
    index_title = "Welcome to LepStore Admin"
    login_template = 'admin/login.html'
    index_template = 'admin/custom_index.html'


# Create an instance to use in urls
lep_admin = LepAdminSite(name='lep_admin')


# Transfer existing registrations from the default admin site so models remain available
def transfer_registrations():
    # Copy registrations without removing from the default site
    for model, model_admin in list(admin.site._registry.items()):
        try:
            lep_admin.register(model, model_admin.__class__)
        except admin.sites.AlreadyRegistered:
            pass


transfer_registrations()
