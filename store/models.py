from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify


class Category(models.Model):
    """Product categories (Laptops, Tablets, Smartphones, Accessories)"""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('store:category_products', args=[self.slug])


class Brand(models.Model):
    """Product brands (Apple, Dell, HP, Samsung, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Main product model"""
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    description = models.TextField()
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percentage = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Inventory
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    is_available = models.BooleanField(default=True)
    
    # Specifications
    processor = models.CharField(max_length=200, blank=True)
    ram = models.CharField(max_length=50, blank=True)
    storage = models.CharField(max_length=50, blank=True)
    screen_size = models.CharField(max_length=50, blank=True)
    operating_system = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=50, blank=True)
    
    # Additional info
    features = models.TextField(blank=True, help_text="Key features, one per line")
    whats_in_box = models.TextField(blank=True, help_text="Items included, one per line")
    warranty_info = models.CharField(max_length=200, blank=True)
    
    # SEO
    meta_description = models.TextField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    # Badges
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_top_rated = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category', 'is_available']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Calculate discount percentage
        if self.original_price and self.original_price > self.price:
            self.discount_percentage = int(((self.original_price - self.price) / self.original_price) * 100)
        else:
            self.discount_percentage = 0
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])
    
    @property
    def is_on_sale(self):
        return self.original_price and self.original_price > self.price
    
    @property
    def savings(self):
        if self.is_on_sale:
            return self.original_price - self.price
        return 0
    
    @property
    def in_stock(self):
        return self.is_available and self.stock > 0
    
    @property
    def stock_status(self):
        if self.stock == 0:
            return 'Out of Stock'
        elif self.stock <= 5:
            return 'Low Stock'
        return 'In Stock'
    
    @property
    def average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0
    
    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()


class ProductImage(models.Model):
    """Multiple images for a product"""
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"Image for {self.product.name}"


class Review(models.Model):
    """Customer reviews"""
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_approved = models.BooleanField(default=True)
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}⭐)"


class Bundle(models.Model):
    """Product bundles for cross-selling"""
    main_product = models.ForeignKey(Product, related_name='bundles', on_delete=models.CASCADE)
    accessory_products = models.ManyToManyField(Product, related_name='bundled_with')
    title = models.CharField(max_length=200, default="Complete Your Setup")
    discount_percentage = models.IntegerField(default=15, validators=[MinValueValidator(0), MaxValueValidator(50)])
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Bundle for {self.main_product.name}"
    
    @property
    def total_price(self):
        accessories_price = sum(p.price for p in self.accessory_products.all())
        total = self.main_product.price + accessories_price
        return total * (1 - self.discount_percentage / 100)
    
    @property
    def savings(self):
        original_total = self.main_product.price + sum(p.price for p in self.accessory_products.all())
        return original_total - self.total_price
