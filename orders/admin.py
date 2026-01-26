from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.urls import reverse
from .models import Order, OrderItem, ShippingMethod


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'product_name', 'price', 'quantity', 'subtotal']
    readonly_fields = ['subtotal']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number_link', 'customer_info', 'items_count', 'status_badge', 'payment_badge', 'formatted_total', 'created_at']
    list_filter = ['status', 'is_paid', 'created_at', 'payment_method']
    search_fields = ['order_number', 'first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'paid_at', 'order_summary']
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    def order_number_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.pk])
        return format_html('<a href="{}" style="font-weight: bold; color: #667eea;">{}</a>', url, obj.order_number)
    order_number_link.short_description = 'Order #'
    
    def customer_info(self, obj):
        return format_html(
            '<strong>{}</strong><br/><span style="color: #6b7280; font-size: 12px;">{}</span><br/><span style="color: #6b7280; font-size: 11px;">{}</span>',
            obj.full_name, obj.email, obj.phone
        )
    customer_info.short_description = 'Customer'
    
    def items_count(self, obj):
        count = obj.items.count()
        return format_html('<span style="background: #e0e7ff; color: #4338ca; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;">{} items</span>', count)
    items_count.short_description = 'Items'
    
    def status_badge(self, obj):
        colors = {
            'pending': ('#fef3c7', '#92400e'),
            'processing': ('#dbeafe', '#1e40af'),
            'shipped': ('#e0e7ff', '#4338ca'),
            'delivered': ('#d1fae5', '#065f46'),
            'cancelled': ('#fee2e2', '#991b1b'),
        }
        bg, fg = colors.get(obj.status, ('#f3f4f6', '#374151'))
        return format_html(
            '<span style="background: {}; color: {}; padding: 6px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; display: inline-block;">{}</span>',
            bg, fg, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def payment_badge(self, obj):
        if obj.is_paid:
            return format_html(
                '<span style="color: #10b981; font-weight: bold;">✓ Paid</span><br/><span style="color: #6b7280; font-size: 11px;">{}</span>',
                obj.get_payment_method_display()
            )
        return format_html('<span style="color: #ef4444; font-weight: bold;">✗ Unpaid</span>')
    payment_badge.short_description = 'Payment'
    
    def formatted_total(self, obj):
        return format_html('<span style="font-weight: bold; font-size: 14px; color: #1f2937;">KSh {}</span>', obj.total)
    formatted_total.short_description = 'Total'
    
    def order_summary(self, obj):
        items_html = '<br/>'.join([f"• {item.quantity}x {item.product_name} - KSh {item.subtotal}" for item in obj.items.all()])
        return format_html(
            '<div style="background: #f9fafb; padding: 15px; border-radius: 8px;">{}</div>',
            items_html
        )
    order_summary.short_description = 'Order Summary'
    
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_paid']
    
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} orders marked as processing.')
    mark_as_processing.short_description = 'Mark as processing'
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} orders marked as shipped.')
    mark_as_shipped.short_description = 'Mark as shipped'
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} orders marked as delivered.')
    mark_as_delivered.short_description = 'Mark as delivered'
    
    def mark_as_paid(self, request, queryset):
        from django.utils import timezone
        updated = 0
        for order in queryset:
            if not order.is_paid:
                order.is_paid = True
                order.paid_at = timezone.now()
                order.save()
                updated += 1
        self.message_user(request, f'{updated} orders marked as paid.')
    mark_as_paid.short_description = 'Mark as paid'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'created_at', 'updated_at')
        }),
        ('Customer Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('address', 'city', 'postal_code', 'country')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_id', 'is_paid', 'paid_at')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'shipping_cost', 'tax', 'total')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'price', 'quantity', 'subtotal']
    list_filter = ['order__created_at']
    search_fields = ['order__order_number', 'product_name']


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'cost', 'estimated_days', 'is_active']
    list_filter = ['is_active']
    list_editable = ['cost', 'is_active']
