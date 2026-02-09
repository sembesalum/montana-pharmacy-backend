from rest_framework import serializers
from .models import (
    BusinessUser, ProductCategory, Brand, ProductType, 
    Product, ProductBatch, Banner, HardwareOTP, Order, OrderItem,
    Customer, Shelf, ProductLocation, Sale, SaleItem, Expense,
    Invoice, InvoiceItem
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

class ProductBatchSerializer(serializers.ModelSerializer):
    """Serializer for product batches"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = ProductBatch
        fields = [
            'batch_id', 'product', 'product_name', 'batch_number', 'supplier',
            'cost_price', 'selling_price', 'quantity_received', 'quantity_remaining',
            'expiry_date', 'received_date', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['batch_id', 'received_date', 'created_at', 'updated_at']

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    product_type_name = serializers.CharField(source='product_type.name', read_only=True)
    batches = ProductBatchSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'product_id', 'name', 'description', 'price', 'image',
            'category', 'category_name', 'brand', 'brand_name',
            'product_type', 'product_type_name', 'subtype', 'size',
            'color', 'material', 'weight', 'dimensions', 'is_active',
            'is_featured', 'stock_quantity', 'minimum_stock', 'expiry_date', 'batches', 'created_at'
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


# New serializers for sales functionality
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'phone', 'email', 'address', 'created_at', 'updated_at']
        read_only_fields = ['customer_id', 'created_at', 'updated_at']


class CustomerSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'phone']

class UserAsCustomerSerializer(serializers.Serializer):
    """Serializer to convert BusinessUser to customer-like format"""
    customer_id = serializers.CharField()
    name = serializers.CharField()
    phone = serializers.CharField()


class ShelfSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelf
        fields = ['shelf_id', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['shelf_id', 'created_at', 'updated_at']


class ProductLocationSerializer(serializers.ModelSerializer):
    shelf_name = serializers.CharField(source='shelf.name', read_only=True)
    
    class Meta:
        model = ProductLocation
        fields = ['location_id', 'product', 'shelf', 'shelf_name', 'quantity', 'created_at', 'updated_at']
        read_only_fields = ['location_id', 'created_at', 'updated_at']


class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = ['sale_item_id', 'product', 'product_name', 'quantity', 'unit_price', 'total_price', 'created_at']
        read_only_fields = ['sale_item_id', 'total_price', 'created_at']


class ExpenseSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField(read_only=True)
    approved_by_name = serializers.SerializerMethodField(read_only=True)
    created_by = serializers.CharField(write_only=True, required=False, allow_null=True)
    approved_by = serializers.CharField(write_only=True, required=False, allow_null=True)
    created_by_id = serializers.SerializerMethodField(read_only=True)
    approved_by_id = serializers.SerializerMethodField(read_only=True)
    
    def get_created_by_name(self, obj):
        return obj.created_by.business_name if obj.created_by else None
    
    def get_approved_by_name(self, obj):
        return obj.approved_by.business_name if obj.approved_by else None
    
    def get_created_by_id(self, obj):
        return obj.created_by.user_id if obj.created_by else None
    
    def get_approved_by_id(self, obj):
        return obj.approved_by.user_id if obj.approved_by else None
    
    class Meta:
        model = Expense
        fields = [
            'expense_id', 'title', 'description', 'amount', 'category', 
            'status', 'expense_date', 'created_by', 'created_by_id', 'created_by_name',
            'approved_by', 'approved_by_id', 'approved_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['expense_id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        created_by_id = validated_data.pop('created_by', None)
        approved_by_id = validated_data.pop('approved_by', None)
        
        if created_by_id:
            try:
                created_by = BusinessUser.objects.get(user_id=created_by_id)
                validated_data['created_by'] = created_by
            except BusinessUser.DoesNotExist:
                pass
        
        if approved_by_id:
            try:
                approved_by = BusinessUser.objects.get(user_id=approved_by_id)
                validated_data['approved_by'] = approved_by
            except BusinessUser.DoesNotExist:
                pass
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        created_by_id = validated_data.pop('created_by', None)
        approved_by_id = validated_data.pop('approved_by', None)
        
        if created_by_id:
            try:
                created_by = BusinessUser.objects.get(user_id=created_by_id)
                validated_data['created_by'] = created_by
            except BusinessUser.DoesNotExist:
                pass
        
        if approved_by_id:
            try:
                approved_by = BusinessUser.objects.get(user_id=approved_by_id)
                validated_data['approved_by'] = approved_by
            except BusinessUser.DoesNotExist:
                pass
        
        return super().update(instance, validated_data)


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(required=False, allow_blank=True)
    customer_phone = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Sale
        fields = [
            'sale_id', 'customer', 'customer_name', 'customer_phone', 'total_amount', 
            'discount', 'payment_method', 'payment_status', 'salesperson', 
            'salesperson_name', 'sale_date', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['sale_id', 'sale_date', 'created_at', 'updated_at']


class CreateSaleSerializer(serializers.Serializer):
    customer_id = serializers.CharField(required=False, allow_blank=True)
    customer_name = serializers.CharField(required=False, allow_blank=True)
    customer_phone = serializers.CharField(required=False, allow_blank=True)
    items = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    payment_method = serializers.ChoiceField(choices=Sale.PAYMENT_METHOD_CHOICES, default='CASH')
    payment_status = serializers.ChoiceField(choices=Sale.PAYMENT_STATUS_CHOICES, default='PAID')
    discount = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    salesperson_name = serializers.CharField(required=False, allow_blank=True)
    salesperson = serializers.CharField(required=False, allow_blank=True)  # User ID
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required")
        
        for item in value:
            required_fields = ['product_id', 'quantity']
            for field in required_fields:
                if field not in item:
                    raise serializers.ValidationError(f"Missing required field: {field}")
            
            if item['quantity'] <= 0:
                raise serializers.ValidationError("Quantity must be greater than 0")
        
        return value
    
    def create(self, validated_data):
        from .models import Product, Customer, BusinessUser
        from decimal import Decimal
        
        # Get or create customer
        customer = None
        if validated_data.get('customer_id'):
            try:
                customer = Customer.objects.get(customer_id=validated_data['customer_id'])
            except Customer.DoesNotExist:
                pass
        
        # Get salesperson if user ID is provided
        salesperson = None
        if validated_data.get('salesperson'):
            try:
                salesperson = BusinessUser.objects.get(user_id=validated_data['salesperson'])
            except BusinessUser.DoesNotExist:
                pass
        
        # Get salesperson name
        salesperson_name = validated_data.get('salesperson_name', '')
        if not salesperson_name and salesperson:
            salesperson_name = salesperson.business_name
        
        # Create sale with initial total_amount as Decimal
        sale = Sale.objects.create(
            customer=customer,
            customer_name=validated_data.get('customer_name', '') or '',
            customer_phone=validated_data.get('customer_phone', '') or '',
            payment_method=validated_data.get('payment_method', 'CASH'),
            payment_status=validated_data.get('payment_status', 'PAID'),
            discount=Decimal(str(validated_data.get('discount', 0))),
            salesperson=salesperson,
            salesperson_name=salesperson_name,
            total_amount=Decimal('0.00')  # Will be calculated later
        )
        
        total_amount = 0
        
        # Create sale items
        for item_data in validated_data['items']:
            try:
                product = Product.objects.get(product_id=item_data['product_id'])
                
                # Check stock availability
                if product.stock_quantity < item_data['quantity']:
                    sale.delete()
                    raise serializers.ValidationError(f"Insufficient stock for {product.name}. Available: {product.stock_quantity}, Requested: {item_data['quantity']}")
                
                # Calculate total price
                from decimal import Decimal
                item_total_price = Decimal(str(product.price)) * Decimal(str(item_data['quantity']))
                
                # Create sale item
                sale_item = SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    product_name=product.name,
                    quantity=item_data['quantity'],
                    unit_price=product.price,
                    total_price=item_total_price
                )
                
                # Update product stock
                product.stock_quantity -= item_data['quantity']
                if product.stock_quantity < 0:
                    product.stock_quantity = 0
                product.save()
                
                total_amount += float(sale_item.total_price)
                
            except Product.DoesNotExist:
                sale.delete()
                raise serializers.ValidationError(f"Product with ID {item_data['product_id']} not found")
        
        # Update sale total (ensure discount is Decimal)
        discount_amount = Decimal(str(validated_data.get('discount', 0)))
        sale_total = Decimal(str(total_amount)) - discount_amount
        if sale_total < 0:
            sale_total = Decimal('0.00')
        sale.total_amount = sale_total
        sale.save()
        
        return sale


class ProductWithLocationSerializer(serializers.ModelSerializer):
    locations = ProductLocationSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='product_type.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'product_id', 'name', 'description', 'price', 'stock_quantity', 
            'minimum_stock', 'expiry_date', 'category_name', 'locations', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['product_id', 'created_at', 'updated_at']


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for invoice items"""
    product_id = serializers.CharField(source='product.product_id', read_only=True, allow_null=True)
    
    class Meta:
        model = InvoiceItem
        fields = [
            'invoice_item_id', 'product_id', 'product_name', 'product_description',
            'product_image', 'category', 'quantity', 'unit_price', 'total_price',
            'pack_type', 'created_at', 'updated_at'
        ]
        read_only_fields = ['invoice_item_id', 'created_at', 'updated_at']


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for invoices with items"""
    invoice_items = InvoiceItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_id = serializers.CharField(source='order.order_id', read_only=True, allow_null=True)
    
    class Meta:
        model = Invoice
        fields = [
            'invoice_id', 'invoice_number', 'order_id', 'invoice_date', 'due_date',
            'status', 'status_display', 'customer_name', 'customer_phone',
            'customer_address', 'customer_tin', 'subtotal', 'tax_amount',
            'shipping_amount', 'discount_amount', 'total_amount', 'payment_method',
            'payment_status', 'notes', 'terms_and_conditions', 'invoice_items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['invoice_id', 'invoice_number', 'created_at', 'updated_at']


class CreateInvoiceFromOrderSerializer(serializers.Serializer):
    """Serializer for creating invoice from order"""
    invoice_date = serializers.DateField(required=False)
    due_date = serializers.DateField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
    terms_and_conditions = serializers.CharField(required=False, allow_blank=True)


class UpdateInvoiceSerializer(serializers.ModelSerializer):
    """Serializer for updating invoices"""
    invoice_items = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    
    class Meta:
        model = Invoice
        fields = [
            'invoice_date', 'due_date', 'status', 'customer_name', 'customer_phone',
            'customer_address', 'customer_tin', 'shipping_amount', 'discount_amount',
            'payment_method', 'payment_status', 'notes', 'terms_and_conditions',
            'invoice_items'
        ]
    
    def validate_status(self, value):
        """Prevent editing paid or cancelled invoices"""
        if self.instance and self.instance.status in ['paid', 'cancelled']:
            if value != self.instance.status:
                raise serializers.ValidationError(
                    f"Cannot change status of {self.instance.status} invoice"
                )
        return value
    
    def update(self, instance, validated_data):
        invoice_items_data = validated_data.pop('invoice_items', None)
        
        # Update invoice fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update invoice items if provided
        if invoice_items_data is not None:
            # Delete existing items
            instance.invoice_items.all().delete()
            
            # Create new items
            for item_data in invoice_items_data:
                product_id = item_data.get('product_id')
                product = None
                if product_id:
                    try:
                        product = Product.objects.get(product_id=product_id)
                    except Product.DoesNotExist:
                        pass
                
                InvoiceItem.objects.create(
                    invoice=instance,
                    product=product,
                    product_name=item_data.get('product_name', ''),
                    product_description=item_data.get('product_description', ''),
                    product_image=item_data.get('product_image', ''),
                    category=item_data.get('category', ''),
                    quantity=item_data.get('quantity', 1),
                    unit_price=item_data.get('unit_price', 0),
                    pack_type=item_data.get('pack_type', 'Piece')
                )
        
        instance.save()
        return instance 