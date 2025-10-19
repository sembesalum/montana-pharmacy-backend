from django.db import models
import uuid
from django.contrib.auth.hashers import make_password, check_password
from decimal import Decimal

def generate_uuid():
    """Generate a UUID string for model primary keys"""
    return str(uuid.uuid4())

class BusinessUser(models.Model):
    """Business user model for hardware delivery app"""

    
    user_id = models.CharField(max_length=50, primary_key=True, default=generate_uuid)
    business_type = models.CharField(max_length=20)
    business_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15, unique=True)
    business_location = models.CharField(max_length=500)
    tin_number = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "business_users"
    
    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def __str__(self):
        return f"{self.business_name} ({self.phone_number})"

class ProductCategory(models.Model):
    """Product categories like machines, aluminium, etc."""
    category_id = models.CharField(max_length=50, primary_key=True, default=generate_uuid)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "product_categories"
        verbose_name_plural = "Product Categories"
    
    def __str__(self):
        return self.name

class Brand(models.Model):
    """Product brands"""
    brand_id = models.CharField(max_length=50, primary_key=True, default=generate_uuid)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    logo = models.CharField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "brands"
    
    def __str__(self):
        return self.name

class ProductType(models.Model):
    """Product types within categories"""
    type_id = models.CharField(max_length=50, primary_key=True, default=generate_uuid)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='product_types')
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "product_types"
        unique_together = ['name', 'category']
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"

class Product(models.Model):
    """Product model with all required fields"""
    product_id = models.CharField(max_length=50, primary_key=True, default=generate_uuid)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.CharField(max_length=500, blank=True, null=True)
    
    # Relationships
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name='products')
    
    # Product specifications
    subtype = models.CharField(max_length=100, blank=True, null=True)
    size = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    material = models.CharField(max_length=100, blank=True, null=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    dimensions = models.CharField(max_length=200, blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    stock_quantity = models.IntegerField(default=0)
    minimum_stock = models.IntegerField(default=10)
    expiry_date = models.DateField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "products"
    
    def __str__(self):
        return self.name

class Banner(models.Model):
    """Banner images for home page"""
    banner_id = models.CharField(max_length=50, primary_key=True, default=generate_uuid)
    title = models.CharField(max_length=200)
    image = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    link_url = models.CharField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "banners"
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title

class HardwareOTP(models.Model):
    """OTP model for hardware app verification"""
    phone_number = models.CharField(max_length=15, primary_key=True)
    otp = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    class Meta:
        db_table = "hardware_otps"
    
    def __str__(self):
        return f"OTP for {self.phone_number}"

class Order(models.Model):
    """Order model for user purchases"""
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    order_id = models.CharField(max_length=50, primary_key=True, default=generate_uuid)
    user = models.ForeignKey(BusinessUser, on_delete=models.CASCADE, related_name='orders')
    
    # Order details
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    shipping_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Delivery information
    delivery_address = models.TextField()
    delivery_phone = models.CharField(max_length=15)
    delivery_notes = models.TextField(blank=True, null=True)
    
    # Order status and tracking
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Payment information
    PAYMENT_METHOD_CHOICES = [
        ('cash_on_delivery', 'Cash on Delivery'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    PAYMENT_TIMING_CHOICES = [
        ('pay_now', 'Pay Now'),
        ('pay_on_delivery', 'Pay on Delivery'),
    ]
    
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='cash_on_delivery')
    payment_timing = models.CharField(max_length=20, choices=PAYMENT_TIMING_CHOICES, default='pay_on_delivery')
    payment_status = models.CharField(max_length=20, default='pending')
    partial_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    mobile_money_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Order number for display
    order_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "orders"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_id} - {self.user.business_name}"
    
    def generate_order_number(self):
        """Generate a human-readable order number"""
        if not self.order_number:
            # Format: ORD-YYYYMMDD-XXXX (e.g., ORD-20240101-0001)
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            # Get the count of orders for today
            today_orders = Order.objects.filter(created_at__date=datetime.now().date()).count()
            self.order_number = f"ORD-{date_str}-{today_orders + 1:04d}"
            self.save()
        return self.order_number
    
    def calculate_totals(self):
        """Calculate order totals from order items"""
        subtotal = sum(item.total_price for item in self.order_items.all())
        self.subtotal = subtotal
        
        # Calculate tax (assuming 18% VAT)
        self.tax_amount = subtotal * Decimal('0.18')
        
        # Calculate shipping (free for orders over 100,000, otherwise 5,000)
        if subtotal >= Decimal('100000.00'):
            self.shipping_amount = Decimal('0.00')
        else:
            self.shipping_amount = Decimal('5000.00')
        
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_amount
        self.save()

class OrderItem(models.Model):
    """Individual items in an order"""
    order_item_id = models.CharField(max_length=50, primary_key=True, default=generate_uuid)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Item details
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Product snapshot (in case product details change later)
    product_name = models.CharField(max_length=200)
    product_description = models.TextField()
    product_image = models.CharField(max_length=500, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    
    PACK_TYPE_CHOICES = [
        ('Piece', 'Piece'),
        ('Dozen', 'Dozen'),
    ]
    pack_type = models.CharField(max_length=10, choices=PACK_TYPE_CHOICES, default='Piece')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "order_items"
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name} - Order {self.order.order_id}"
    
    def save(self, *args, **kwargs):
        # Calculate total price
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Customer(models.Model):
    customer_id = models.CharField(max_length=50, primary_key=True, default=generate_uuid)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "customers"
    
    def __str__(self):
        return f"{self.name} - {self.phone}"


class Shelf(models.Model):
    shelf_id = models.CharField(max_length=50, primary_key=True, default=generate_uuid)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "shelves"
    
    def __str__(self):
        return self.name


class ProductLocation(models.Model):
    location_id = models.CharField(max_length=50, primary_key=True, default=generate_uuid)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='locations')
    shelf = models.ForeignKey(Shelf, on_delete=models.CASCADE, related_name='products')
    quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "product_locations"
        unique_together = ['product', 'shelf']
    
    def __str__(self):
        return f"{self.product.name} - {self.shelf.name}"


class Sale(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('UNPAID', 'Unpaid'),
        ('PARTIAL', 'Partially Paid'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('MOBILE_MONEY', 'Mobile Money'),
        ('BANK_TRANSFER', 'Bank Transfer'),
    ]
    
    sale_id = models.CharField(max_length=50, primary_key=True, default=generate_uuid)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    customer_name = models.CharField(max_length=200, blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='CASH')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PAID')
    salesperson = models.ForeignKey(BusinessUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    salesperson_name = models.CharField(max_length=200, blank=True, null=True)
    sale_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "sales"
        ordering = ['-sale_date']
    
    def __str__(self):
        return f"Sale {self.sale_id} - {self.customer_name or 'Walk-in'} - TSh {self.total_amount}"


class SaleItem(models.Model):
    sale_item_id = models.CharField(max_length=50, primary_key=True, default=generate_uuid)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sale_items')
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "sale_items"
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name} - Sale {self.sale.sale_id}"
    
    def save(self, *args, **kwargs):
        # Calculate total price
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
