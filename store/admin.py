from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum, Avg
from django.urls import reverse
from .models import Category, Brand, Product, ProductImage, Review, Bundle, Variant, VariantImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order']


class VariantImageInline(admin.TabularInline):
    model = VariantImage
    extra = 1
    fields = ['image', 'alt_text', 'order']


class VariantInline(admin.TabularInline):
    model = Variant
    extra = 0
    fields = ['name', 'sku', 'price', 'stock', 'is_active', 'is_default']
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count', 'is_active', 'category_image', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 25
    
    def product_count(self, obj):
        count = obj.products.count()
        url = f'/admin/store/product/?category__id__exact={obj.id}'
        return format_html('<a href="{}">{} products</a>', url, count)
    product_count.short_description = 'Products'
    
    def category_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return '-'
    category_image.short_description = 'Image'
    
    actions = ['activate_categories', 'deactivate_categories']
    
    def activate_categories(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} categories activated.')
    activate_categories.short_description = 'Activate selected categories'
    
    def deactivate_categories(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} categories deactivated.')
    deactivate_categories.short_description = 'Deactivate selected categories'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count', 'brand_logo', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 25
    
    def product_count(self, obj):
        count = obj.products.count()
        url = f'/admin/store/product/?brand__id__exact={obj.id}'
        return format_html('<a href="{}">{} products</a>', url, count)
    product_count.short_description = 'Products'
    
    def brand_logo(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: contain; border-radius: 5px;" />', obj.logo.url)
        return '-'
    brand_logo.short_description = 'Logo'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_image', 'name', 'category', 'brand', 'formatted_price', 'stock_status', 'total_sold', 'is_available', 'is_featured', 'created_at']
    list_filter = ['category', 'brand', 'is_available', 'is_featured', 'is_new', 'is_top_rated', 'is_cannabis', 'created_at']
    search_fields = ['name', 'description', 'processor']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_available', 'is_featured']
    inlines = [ProductImageInline, VariantInline]
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    def product_image(self, obj):
        image = obj.images.filter(is_primary=True).first()
        if image:
            return format_html('<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 5px;" />', image.image.url)
        return '-'
    product_image.short_description = 'Image'
    
    def formatted_price(self, obj):
        if obj.original_price and obj.original_price > obj.price:
            return format_html(
                '<span style="color: #10b981; font-weight: bold;">KSh {}</span><br/><span style="text-decoration: line-through; color: #6b7280; font-size: 11px;">KSh {}</span>',
                obj.price, obj.original_price
            )
        return format_html('<span style="font-weight: bold;">KSh {}</span>', obj.price)
    formatted_price.short_description = 'Price'
    
    def stock_status(self, obj):
        if obj.stock == 0:
            return format_html('<span style="color: #ef4444; font-weight: bold;">⚠ Out of Stock</span>')
        elif obj.stock <= 10:
            return format_html('<span style="color: #f59e0b; font-weight: bold;">⚠ Low ({} left)</span>', obj.stock)
        return format_html('<span style="color: #10b981;">✓ In Stock ({})</span>', obj.stock)
    stock_status.short_description = 'Stock'
    
    def total_sold(self, obj):
        from orders.models import OrderItem
        sold = OrderItem.objects.filter(product=obj).aggregate(total=Sum('quantity'))['total'] or 0
        return f'{sold} sold'
    total_sold.short_description = 'Sales'
    
    actions = ['mark_as_featured', 'remove_from_featured', 'mark_out_of_stock', 'duplicate_product']
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} products marked as featured.')
    mark_as_featured.short_description = 'Mark as featured'
    
    def remove_from_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} products removed from featured.')
    remove_from_featured.short_description = 'Remove from featured'
    
    def mark_out_of_stock(self, request, queryset):
        updated = queryset.update(stock=0, is_available=False)
        self.message_user(request, f'{updated} products marked as out of stock.')
    mark_out_of_stock.short_description = 'Mark as out of stock'
    
    def duplicate_product(self, request, queryset):
        for product in queryset:
            product.pk = None
            product.name = f"{product.name} (Copy)"
            product.slug = f"{product.slug}-copy"
            product.save()
        self.message_user(request, f'{queryset.count()} products duplicated.')
    duplicate_product.short_description = 'Duplicate selected products'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'brand', 'name', 'slug', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'original_price', 'discount_percentage')
        }),
        ('Inventory', {
            'fields': ('stock', 'is_available')
        }),
        ('Specifications', {
            'fields': ('processor', 'ram', 'storage', 'screen_size', 'operating_system', 'color'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('features', 'whats_in_box', 'warranty_info'),
            'classes': ('collapse',)
        }),
        ('Cannabis / Compliance', {
            'fields': ('is_cannabis', 'cannabis_type', 'thc_percentage', 'cbd_percentage', 'unit_weight_g', 'package_amount', 'metrc_tag', 'lab_report', 'requires_age_verification'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Badges', {
            'fields': ('is_featured', 'is_new', 'is_top_rated')
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_primary', 'order']
    list_filter = ['is_primary']
    search_fields = ['product__name', 'alt_text']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_approved', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'user__username', 'title', 'comment']
    list_editable = ['is_approved']
    date_hierarchy = 'created_at'


@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    list_display = ['main_product', 'discount_percentage', 'is_active']
    list_filter = ['is_active']
    search_fields = ['main_product__name', 'title']
    filter_horizontal = ['accessory_products']


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'sku', 'effective_price', 'stock', 'is_active', 'is_default']
    search_fields = ['product__name', 'sku', 'name']
    list_filter = ['is_active', 'is_default']


@admin.register(VariantImage)
class VariantImageAdmin(admin.ModelAdmin):
    list_display = ['variant', 'order']
    search_fields = ['variant__product__name']
