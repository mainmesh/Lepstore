from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from importlib import import_module
from django.apps import apps


class LepAdminSite(AdminSite):
    site_header = "LepStore Admin"
    site_title = "LepStore Admin"
    index_title = "Welcome to LepStore Admin"
    login_template = 'admin/login.html'
    index_template = 'admin/custom_index.html'


# Create an instance to use in urls
# Register the custom admin under the standard `admin` namespace so built-in
# admin template reverses (e.g. `admin:app_list`) resolve correctly.
lep_admin = LepAdminSite(name='admin')


# Ensure each app's admin module is imported so registrations are populated
def import_all_app_admins():
    for app_config in apps.get_app_configs():
        module_name = f"{app_config.name}.admin"
        try:
            import_module(module_name)
        except ModuleNotFoundError:
            # some apps don't have an admin module
            continue


# Transfer existing registrations from the default admin site so models remain available
def transfer_registrations():
    # Copy registrations without removing from the default site
    for model, model_admin in list(admin.site._registry.items()):
        try:
            lep_admin.register(model, model_admin.__class__)
        except admin.sites.AlreadyRegistered:
            pass


# Unregister models from the default admin to avoid exposing the default admin interface
def unregister_default_admin():
    for model in list(admin.site._registry.keys()):
        try:
            admin.site.unregister(model)
        except Exception:
            # ignore models that cannot be unregistered
            pass


import_all_app_admins()
transfer_registrations()
unregister_default_admin()
