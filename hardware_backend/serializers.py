from rest_framework import serializers
from .models import (
    BusinessUser, ProductCategory, Brand, ProductType, 
    Product, Banner, HardwareOTP, Order, OrderItem
)
import random
import string

class BusinessUserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for business user registration"""
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = BusinessUser
        fields = [
            'business_type', 'business_name', 'phone_number', 
            'business_location', 'tin_number', 'password'
        ]
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if not value.startswith('+') and not value.isdigit():
            raise serializers.ValidationError("Phone number must be numeric or start with +")
        return value
    
    def validate_tin_number(self, value):
        """Validate TIN number"""
        if len(value) < 5:
            raise serializers.ValidationError("TIN number must be at least 5 characters")
        return value

class BusinessUserLoginSerializer(serializers.Serializer):
    """Serializer for business user login"""
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(max_length=128)

class BusinessUserSerializer(serializers.ModelSerializer):
    """Serializer for business user data"""
    class Meta:
        model = BusinessUser
        fields = [
            'user_id', 'business_type', 'business_name', 'phone_number',
            'business_location', 'tin_number', 'is_verified', 'created_at'
        ]
        read_only_fields = ['user_id', 'is_verified', 'created_at']

class OTPSerializer(serializers.Serializer):
    """Serializer for OTP verification"""
    phone_number = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=4)

class ProductCategorySerializer(serializers.ModelSerializer):
    """Serializer for product categories"""
    class Meta:
        model = ProductCategory
        fields = [
            'category_id', 'name', 'description', 'image', 
            'is_active', 'created_at'
        ]
        read_only_fields = ['category_id', 'created_at']

class BrandSerializer(serializers.ModelSerializer):
    """Serializer for brands"""
    class Meta:
        model = Brand
        fields = [
            'brand_id', 'name', 'description', 'logo', 
            'is_active', 'created_at'
        ]
        read_only_fields = ['brand_id', 'created_at']

class ProductTypeSerializer(serializers.ModelSerializer):
    """Serializer for product types"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category = ProductCategorySerializer(read_only=True)
    category_id = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = ProductType
        fields = [
            'type_id', 'name', 'category', 'category_id', 'category_name', 
            'description', 'image', 'is_active', 'created_at'
        ]
        read_only_fields = ['type_id', 'created_at']
    
    def create(self, validated_data):
        category_id = validated_data.pop('category_id')
        try:
            category = ProductCategory.objects.get(category_id=category_id)
            validated_data['category'] = category
            return super().create(validated_data)
        except ProductCategory.DoesNotExist:
            raise serializers.ValidationError({'category_id': 'Category not found'})
    
    def update(self, instance, validated_data):
        if 'category_id' in validated_data:
            category_id = validated_data.pop('category_id')
            try:
                category = ProductCategory.objects.get(category_id=category_id)
                validated_data['category'] = category
            except ProductCategory.DoesNotExist:
                raise serializers.ValidationError({'category_id': 'Category not found'})
        return super().update(instance, validated_data)

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    product_type_name = serializers.CharField(source='product_type.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'product_id', 'name', 'description', 'price', 'image',
            'category', 'category_name', 'brand', 'brand_name',
            'product_type', 'product_type_name', 'subtype', 'size',
            'color', 'material', 'weight', 'dimensions', 'is_active',
            'is_featured', 'stock_quantity', 'created_at'
        ]
        read_only_fields = ['product_id', 'created_at']

class BannerSerializer(serializers.ModelSerializer):
    """Serializer for banners"""
    class Meta:
        model = Banner
        fields = [
            'banner_id', 'title', 'image', 'description', 
            'link_url', 'is_active', 'order', 'created_at'
        ]
        read_only_fields = ['banner_id', 'created_at']

class HomePageSerializer(serializers.Serializer):
    """Serializer for home page data"""
    categories = ProductCategorySerializer(many=True)
    brands = BrandSerializer(many=True)
    banners = BannerSerializer(many=True)

class ProductsPageSerializer(serializers.Serializer):
    """Serializer for products page data"""
    product_types = ProductTypeSerializer(many=True)
    products = ProductSerializer(many=True)

class ProductTypeWithProductsSerializer(serializers.ModelSerializer):
    """Serializer for product types with their products"""
    products = ProductSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = ProductType
        fields = [
            'type_id', 'name', 'category_name', 'description',
            'image', 'is_active', 'products'
        ]

class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items"""
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'order_item_id', 'product', 'quantity', 'unit_price', 
            'total_price', 'product_name', 'product_description', 
            'product_image', 'created_at'
        ]
        read_only_fields = ['order_item_id', 'total_price', 'created_at']

class OrderItemResponseSerializer(serializers.ModelSerializer):
    """Serializer for order items in response"""
    
    class Meta:
        model = OrderItem
        fields = [
            'product_id', 'product_name', 'product_image', 'category',
            'unit_price', 'quantity', 'pack_type', 'total_price'
        ]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['product_id'] = instance.product.product_id
        return data

class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders"""
    user = BusinessUserSerializer(read_only=True)
    order_items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'order_id', 'user', 'total_amount', 'subtotal', 'tax_amount', 
            'shipping_amount', 'delivery_address', 'delivery_phone', 
            'delivery_notes', 'status', 'status_display', 'tracking_number',
            'payment_method', 'payment_status', 'order_items', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['order_id', 'total_amount', 'subtotal', 'tax_amount', 
                           'shipping_amount', 'created_at', 'updated_at']

class OrderResponseSerializer(serializers.ModelSerializer):
    """Serializer for order response with new format"""
    items = OrderItemResponseSerializer(source='order_items', many=True, read_only=True)
    user_id = serializers.CharField(source='user.user_id', read_only=True)
    business_name = serializers.CharField(source='user.business_name', read_only=True)
    business_phone = serializers.CharField(source='user.phone_number', read_only=True)
    business_location = serializers.CharField(source='user.business_location', read_only=True)
    order_status = serializers.CharField(source='status', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'user_id', 'business_name', 'business_phone', 'business_location',
            'delivery_address', 'delivery_phone', 'delivery_notes',
            'payment_method', 'payment_timing', 'total_amount', 'partial_amount',
            'mobile_money_number', 'items'
        ]

class CreateOrderSerializer(serializers.ModelSerializer):
    """Serializer for creating orders"""
    order_items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    
    class Meta:
        model = Order
        fields = [
            'delivery_address', 'delivery_phone', 'delivery_notes',
            'payment_method', 'payment_timing', 'partial_amount',
            'mobile_money_number', 'order_items'
        ]
    
    def validate_order_items(self, value):
        """Validate order items"""
        if not value:
            raise serializers.ValidationError("Order must contain at least one item")
        
        for item in value:
            if 'product_id' not in item:
                raise serializers.ValidationError("Each item must have a product_id")
            if 'quantity' not in item:
                raise serializers.ValidationError("Each item must have a quantity")
            
            try:
                quantity = int(item['quantity'])
                if quantity <= 0:
                    raise serializers.ValidationError("Quantity must be greater than 0")
            except (ValueError, TypeError):
                raise serializers.ValidationError("Quantity must be a valid integer")
        
        return value
    
    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        user = self.context['request'].user
        
        # Create order
        order = Order.objects.create(
            user=user,
            **validated_data
        )
        
        # Create order items
        for item_data in order_items_data:
            try:
                product = Product.objects.get(product_id=item_data['product_id'])
                
                # Check stock availability
                if product.stock_quantity < item_data['quantity']:
                    raise serializers.ValidationError(
                        f"Insufficient stock for {product.name}. Available: {product.stock_quantity}"
                    )
                
                # Create order item
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item_data['quantity'],
                    unit_price=product.price,
                    product_name=product.name,
                    product_description=product.description,
                    product_image=product.image,
                    category=product.product_type.name,
                    pack_type=item_data.get('pack_type', 'Piece')
                )
                
                # Update product stock
                product.stock_quantity -= item_data['quantity']
                product.save()
                
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product with ID {item_data['product_id']} not found")
        
        # Calculate order totals
        order.calculate_totals()
        
        return order 