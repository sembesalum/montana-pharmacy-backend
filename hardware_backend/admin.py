from django.contrib import admin
from .models import (
    BusinessUser, ProductCategory, Brand, ProductType, 
    Product, ProductBatch, Banner, HardwareOTP, Order, OrderItem
)

@admin.register(BusinessUser)
class BusinessUserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'business_name', 'phone_number', 'business_type', 'is_verified', 'created_at']
    list_filter = ['business_type', 'is_verified', 'created_at']
    search_fields = ['business_name', 'phone_number', 'tin_number']
    readonly_fields = ['user_id', 'created_at', 'updated_at']
    ordering = ['-created_at']

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['category_id', 'name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['category_id', 'created_at', 'updated_at']
    ordering = ['name']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['brand_id', 'name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['brand_id', 'created_at', 'updated_at']
    ordering = ['name']

@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ['type_id', 'name', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'category__name']
    readonly_fields = ['type_id', 'created_at', 'updated_at']
    ordering = ['category__name', 'name']

@admin.register(ProductBatch)
class ProductBatchAdmin(admin.ModelAdmin):
    list_display = ['batch_id', 'product', 'batch_number', 'supplier', 'quantity_received', 'quantity_remaining', 'expiry_date', 'is_active']
    list_filter = ['is_active', 'expiry_date', 'received_date']
    search_fields = ['batch_number', 'supplier', 'product__name']
    readonly_fields = ['batch_id', 'received_date', 'created_at', 'updated_at']
    ordering = ['-received_date']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'name', 'category', 'brand', 'price', 'is_active', 'is_featured', 'stock_quantity']
    list_filter = ['category', 'brand', 'product_type', 'is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'description', 'category__name', 'brand__name']
    readonly_fields = ['product_id', 'created_at', 'updated_at']
    list_editable = ['price', 'is_active', 'is_featured', 'stock_quantity']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'price', 'image')
        }),
        ('Relationships', {
            'fields': ('category', 'brand', 'product_type')
        }),
        ('Specifications', {
            'fields': ('subtype', 'size', 'color', 'material', 'weight', 'dimensions')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'stock_quantity')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['banner_id', 'title', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['banner_id', 'created_at', 'updated_at']
    list_editable = ['is_active', 'order']
    ordering = ['order', '-created_at']

@admin.register(HardwareOTP)
class HardwareOTPAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'otp', 'is_used', 'created_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['phone_number']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order_item_id', 'order', 'product_name', 'quantity', 'unit_price', 'total_price']
    list_filter = ['created_at']
    search_fields = ['product_name', 'order__order_id']
    readonly_fields = ['order_item_id', 'total_price', 'created_at']
    ordering = ['-created_at']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'total_amount', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['order_id', 'user__business_name', 'user__phone_number', 'tracking_number']
    readonly_fields = ['order_id', 'total_amount', 'subtotal', 'tax_amount', 'shipping_amount', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'user', 'status', 'tracking_number')
        }),
        ('Financial Information', {
            'fields': ('total_amount', 'subtotal', 'tax_amount', 'shipping_amount', 'payment_method', 'payment_status')
        }),
        ('Delivery Information', {
            'fields': ('delivery_address', 'delivery_phone', 'delivery_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
