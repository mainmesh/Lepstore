from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.db.models import Count, Sum
from orders.models import Order


class OrderInline(admin.TabularInline):
    model = Order
    extra = 0
    fields = ['order_number', 'status', 'total', 'created_at']
    readonly_fields = ['order_number', 'status', 'total', 'created_at']
    can_delete = False
    max_num = 5
    
    def has_add_permission(self, request, obj=None):
        return False


class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'full_name', 'customer_stats', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    inlines = [OrderInline]
    
    def full_name(self, obj):
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        return '-'
    full_name.short_description = 'Full Name'
    
    def customer_stats(self, obj):
        if obj.is_staff:
            return format_html('<span style="color: #667eea; font-weight: bold;">👤 Staff Member</span>')
        
        orders = obj.orders.all()
        total_orders = orders.count()
        total_spent = orders.filter(is_paid=True).aggregate(total=Sum('total'))['total'] or 0
        
        if total_orders == 0:
            return format_html('<span style="color: #6b7280;">No orders yet</span>')
        
        return format_html(
            '<span style="color: #10b981; font-weight: bold;">{} orders</span><br/>'
            '<span style="color: #6b7280; font-size: 11px;">KSh {} spent</span>',
            total_orders, total_spent
        )
    customer_stats.short_description = 'Customer Stats'


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

