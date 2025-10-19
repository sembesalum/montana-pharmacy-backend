from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
import random
import string
import json
from django.db import models
from .utils import handle_image_upload

from .models import (
    BusinessUser, ProductCategory, Brand, ProductType, 
    Product, Banner, HardwareOTP, Order, OrderItem,
    Customer, Shelf, ProductLocation, Sale, SaleItem
)
from .serializers import (
    BusinessUserRegistrationSerializer, BusinessUserLoginSerializer,
    BusinessUserSerializer, OTPSerializer, ProductCategorySerializer,
    BrandSerializer, ProductTypeSerializer, ProductSerializer,
    BannerSerializer, HomePageSerializer, ProductsPageSerializer,
    ProductTypeWithProductsSerializer, OrderSerializer, CreateOrderSerializer,
    OrderItemSerializer, OrderResponseSerializer, OrderItemResponseSerializer,
    CustomerSerializer, CustomerSearchSerializer, ShelfSerializer,
    ProductLocationSerializer, SaleSerializer, SaleItemSerializer,
    CreateSaleSerializer, ProductWithLocationSerializer
)

def generate_otp():
    """Generate a 4-digit OTP"""
    return '1234'  # Default OTP for testing

def send_otp_sms(phone_number, otp):
    """
    Mock function to send OTP via SMS
    In production, integrate with SMS service like Twilio, AfricasTalking, etc.
    """
    # TODO: Integrate with actual SMS service
    print(f"Sending OTP {otp} to {phone_number}")
    return True

@api_view(['POST'])
@permission_classes([AllowAny])
def register_business_user(request):
    """Register a new business user"""
    try:
        serializer = BusinessUserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            # Check if user already exists
            phone_number = serializer.validated_data['phone_number']
            tin_number = serializer.validated_data['tin_number']
            
            if BusinessUser.objects.filter(phone_number=phone_number).exists():
                return Response({
                    'success': False,
                    'message': 'User with this phone number already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if BusinessUser.objects.filter(tin_number=tin_number).exists():
                return Response({
                    'success': False,
                    'message': 'User with this TIN number already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create user
            user = serializer.save()
            
            # Generate and send OTP
            otp = generate_otp()
            HardwareOTP.objects.update_or_create(
                phone_number=phone_number,
                defaults={'otp': otp, 'is_used': False}
            )
            
            # Send OTP via SMS
            send_otp_sms(phone_number, otp)
            
            return Response({
                'success': True,
                'message': 'Registration successful. Please verify your phone number with the OTP sent.',
                'user_id': user.user_id,
                'phone_number': phone_number
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Registration failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_business_user(request):
    """Login business user"""
    try:
        serializer = BusinessUserLoginSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            password = serializer.validated_data['password']
            
            # Find user by phone number
            try:
                user = BusinessUser.objects.get(phone_number=phone_number)
            except BusinessUser.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Invalid phone number or password'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check password
            if not user.check_password(password):
                return Response({
                    'success': False,
                    'message': 'Invalid phone number or password'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check if user is verified
            if not user.is_verified:
                return Response({
                    'success': False,
                    'message': 'Please verify your phone number first',
                    'needs_verification': True
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Generate a simple token for authentication
            # In production, use JWT tokens
            import hashlib
            import time
            token_data = f"{user.user_id}:{user.phone_number}:{int(time.time())}"
            token = hashlib.sha256(token_data.encode()).hexdigest()
            
            # Return user data with token in the expected format
            user_serializer = BusinessUserSerializer(user)
            return Response({
                'success': True,
                'message': 'Login successful',
                'data': {
                    'user': user_serializer.data,
                    'token': token
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Login failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """Verify OTP for user registration"""
    try:
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            otp = serializer.validated_data['otp']
            
            # Check if OTP exists and is valid
            try:
                otp_obj = HardwareOTP.objects.get(phone_number=phone_number)
            except HardwareOTP.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'No OTP found for this phone number'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if OTP is expired (15 minutes)
            if timezone.now() - otp_obj.created_at > timedelta(minutes=15):
                return Response({
                    'success': False,
                    'message': 'OTP has expired. Please request a new one.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if OTP is already used
            if otp_obj.is_used:
                return Response({
                    'success': False,
                    'message': 'OTP has already been used'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify OTP
            if otp_obj.otp != otp:
                return Response({
                    'success': False,
                    'message': 'Invalid OTP'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark OTP as used
            otp_obj.is_used = True
            otp_obj.save()
            
            # Update user verification status
            try:
                user = BusinessUser.objects.get(phone_number=phone_number)
                user.is_verified = True
                user.save()
                
                # Generate a simple token for authentication
                import hashlib
                import time
                token_data = f"{user.user_id}:{user.phone_number}:{int(time.time())}"
                token = hashlib.sha256(token_data.encode()).hexdigest()
                
                # Return user details with token in the expected format
                user_serializer = BusinessUserSerializer(user)
                return Response({
                    'success': True,
                    'message': 'Phone number verified successfully',
                    'data': {
                        'user': user_serializer.data,
                        'token': token
                    }
                }, status=status.HTTP_200_OK)
            except BusinessUser.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'User not found'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'OTP verification failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def resend_otp(request):
    """Resend OTP to user"""
    try:
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({
                'success': False,
                'message': 'Phone number is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user exists
        try:
            user = BusinessUser.objects.get(phone_number=phone_number)
        except BusinessUser.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate new OTP
        otp = generate_otp()
        
        # Delete existing OTP and create new one to ensure fresh timestamp
        HardwareOTP.objects.filter(phone_number=phone_number).delete()
        HardwareOTP.objects.create(
            phone_number=phone_number,
            otp=otp,
            is_used=False
        )
        
        # Send OTP via SMS
        send_otp_sms(phone_number, otp)
        
        return Response({
            'success': True,
            'message': 'OTP sent successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to resend OTP: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def home_page(request):
    """Get home page data - categories, brands, and banners"""
    try:
        # Get active categories
        categories = ProductCategory.objects.filter(is_active=True)
        categories_serializer = ProductCategorySerializer(categories, many=True)
        
        # Get active brands
        brands = Brand.objects.filter(is_active=True)
        brands_serializer = BrandSerializer(brands, many=True)
        
        # Get active banners
        banners = Banner.objects.filter(is_active=True)
        banners_serializer = BannerSerializer(banners, many=True)
        
        return Response({
            'success': True,
            'data': {
                'categories': categories_serializer.data,
                'brands': brands_serializer.data,
                'banners': banners_serializer.data
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch home page data: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def home_page_with_user(request):
    """Get personalized home page data with user context"""
    try:
        user_id = request.data.get('user_id')
        
        # Get active categories
        categories = ProductCategory.objects.filter(is_active=True)
        categories_serializer = ProductCategorySerializer(categories, many=True)
        
        # Get active brands
        brands = Brand.objects.filter(is_active=True)
        brands_serializer = BrandSerializer(brands, many=True)
        
        # Get active banners
        banners = Banner.objects.filter(is_active=True)
        banners_serializer = BannerSerializer(banners, many=True)
        
        # Initialize response data
        response_data = {
            'categories': categories_serializer.data,
            'brands': brands_serializer.data,
            'banners': banners_serializer.data
        }
        
        # If user_id is provided, add personalized content
        if user_id:
            try:
                user = BusinessUser.objects.get(user_id=user_id)
                user_serializer = BusinessUserSerializer(user)
                
                # Add user data to response
                response_data['user'] = user_serializer.data
                
                # You can add personalized content here based on user preferences
                # For example: favorite categories, recent purchases, etc.
                
            except BusinessUser.DoesNotExist:
                # User not found, but still return basic home page data
                pass
        
        return Response({
            'success': True,
            'data': response_data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch home page data: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def products_page(request):
    """Get products page data - product types and products"""
    try:
        # Get all active product types with their products
        product_types = ProductType.objects.filter(is_active=True).prefetch_related('products')
        
        # Group products by product type
        product_types_data = []
        for product_type in product_types:
            products = product_type.products.filter(is_active=True)
            product_type_data = ProductTypeWithProductsSerializer(product_type).data
            product_type_data['products'] = ProductSerializer(products, many=True).data
            product_types_data.append(product_type_data)
        
        return Response({
            'success': True,
            'data': {
                'product_types': product_types_data
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch products data: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def products_page_with_user(request):
    """Get personalized products page data with user context"""
    try:
        user_id = request.data.get('user_id')
        category_filter = request.data.get('category_id')
        brand_filter = request.data.get('brand_id')
        
        # Get all active product types with their products
        product_types = ProductType.objects.filter(is_active=True).prefetch_related('products')
        
        # Apply filters if provided
        if category_filter:
            product_types = product_types.filter(category_id=category_filter)
        
        # Group products by product type
        product_types_data = []
        for product_type in product_types:
            products = product_type.products.filter(is_active=True)
            
            # Apply brand filter if provided
            if brand_filter:
                products = products.filter(brand_id=brand_filter)
            
            product_type_data = ProductTypeWithProductsSerializer(product_type).data
            product_type_data['products'] = ProductSerializer(products, many=True).data
            product_types_data.append(product_type_data)
        
        # Initialize response data
        response_data = {
            'product_types': product_types_data
        }
        
        # If user_id is provided, add user context
        if user_id:
            try:
                user = BusinessUser.objects.get(user_id=user_id)
                user_serializer = BusinessUserSerializer(user)
                
                # Add user data to response
                response_data['user'] = user_serializer.data
                
                # You can add personalized product recommendations here
                # For example: recently viewed products, favorites, etc.
                
            except BusinessUser.DoesNotExist:
                # User not found, but still return products data
                pass
        
        return Response({
            'success': True,
            'data': response_data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch products data: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def products_by_category(request, category_id):
    """Get products filtered by category"""
    try:
        # Get products for specific category
        products = Product.objects.filter(
            category_id=category_id,
            is_active=True
        ).select_related('category', 'brand', 'product_type')
        
        products_serializer = ProductSerializer(products, many=True)
        
        return Response({
            'success': True,
            'data': {
                'products': products_serializer.data
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch products: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def products_by_brand(request, brand_id):
    """Get products filtered by brand"""
    try:
        # Get products for specific brand
        products = Product.objects.filter(
            brand_id=brand_id,
            is_active=True
        ).select_related('category', 'brand', 'product_type')
        
        products_serializer = ProductSerializer(products, many=True)
        
        return Response({
            'success': True,
            'data': {
                'products': products_serializer.data
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch products: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def product_detail(request, product_id):
    """Get detailed information about a specific product"""
    try:
        # Get specific product
        try:
            product = Product.objects.select_related('category', 'brand', 'product_type').get(
                product_id=product_id,
                is_active=True
            )
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        product_serializer = ProductSerializer(product)
        
        return Response({
            'success': True,
            'data': {
                'product': product_serializer.data
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch product details: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def search_products(request):
    """Search products by name or description"""
    try:
        query = request.GET.get('q', '').strip()
        if not query:
            return Response({
                'success': False,
                'message': 'Search query is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Search products by name or description
        products = Product.objects.filter(
            is_active=True,
            name__icontains=query
        ) | Product.objects.filter(
            is_active=True,
            description__icontains=query
        )
        
        products = products.select_related('category', 'brand', 'product_type').distinct()
        products_serializer = ProductSerializer(products, many=True)
        
        return Response({
            'success': True,
            'data': {
                'products': products_serializer.data,
                'query': query,
                'count': products.count()
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Search failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def get_business_user_data(request):
    """Get business user data by user_id"""
    try:
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({
                'success': False,
                'message': 'user_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = BusinessUser.objects.get(user_id=user_id)
        serializer = BusinessUserSerializer(user)
        return Response({
            'success': True,
            'message': 'User data fetched successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    except BusinessUser.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch user data: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Admin Management Views
@api_view(['GET'])
@permission_classes([AllowAny])
def admin_get_all_products(request):
    """Admin: Get all products (including inactive)"""
    try:
        products = Product.objects.select_related('category', 'brand', 'product_type').all()
        products_serializer = ProductSerializer(products, many=True)
        
        return Response({
            'success': True,
            'data': products_serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch products: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_create_product(request):
    """Admin: Create a new product"""
    try:
        # Handle both JSON and FormData requests
        if request.content_type and 'application/json' in request.content_type:
            data = request.data.copy()
        else:
            # Handle FormData - extract data from POST
            data = {}
            for key, value in request.POST.items():
                data[key] = value
        
        # Handle image upload if provided
        image_file = request.FILES.get('image')
        
        # Remove image field from data if no file is uploaded
        if 'image' in data and not image_file:
            del data['image']
        
        if image_file:
            image_url = handle_image_upload(image_file, 'products')
            if image_url:
                data['image'] = image_url
            else:
                return Response({
                    'success': False,
                    'message': 'Failed to upload image'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Convert names to IDs for foreign key fields
        if 'category' in data and data['category']:
            try:
                category = ProductCategory.objects.get(name=data['category'])
                data['category'] = category.category_id
            except ProductCategory.DoesNotExist:
                return Response({
                    'success': False,
                    'message': f'Category "{data["category"]}" not found'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if 'brand' in data and data['brand']:
            try:
                brand = Brand.objects.get(name=data['brand'])
                data['brand'] = brand.brand_id
            except Brand.DoesNotExist:
                return Response({
                    'success': False,
                    'message': f'Brand "{data["brand"]}" not found'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if 'product_type' in data and data['product_type']:
            try:
                product_type = ProductType.objects.get(name=data['product_type'])
                data['product_type'] = product_type.type_id
            except ProductType.DoesNotExist:
                return Response({
                    'success': False,
                    'message': f'Product type "{data["product_type"]}" not found'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"🔍 DEBUG: Final data before serializer: {data}")
        print(f"🔍 DEBUG: Data types: {[(k, type(v).__name__) for k, v in data.items()]}")
        
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            product = serializer.save()
            print(f"🔍 DEBUG: Product created successfully: {product.product_id}")
            return Response({
                'success': True,
                'message': 'Product created successfully',
                'data': ProductSerializer(product).data
            }, status=status.HTTP_201_CREATED)
        else:
            print(f"🔍 DEBUG: Validation failed: {serializer.errors}")
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to create product: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])
def admin_update_product(request, product_id):
    """Admin: Update a product"""
    try:
        try:
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Handle image upload if provided
        image_file = request.FILES.get('image')
        data = request.data.copy()
        
        # Remove image field from data if no file is uploaded
        if 'image' in data and not image_file:
            del data['image']
        
        if image_file:
            image_url = handle_image_upload(image_file, 'products', product.image)
            if image_url:
                data['image'] = image_url
            else:
                return Response({
                    'success': False,
                    'message': 'Failed to upload image'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ProductSerializer(product, data=data, partial=True)
        if serializer.is_valid():
            updated_product = serializer.save()
            return Response({
                'success': True,
                'message': 'Product updated successfully',
                'data': ProductSerializer(updated_product).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to update product: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def admin_delete_product(request, product_id):
    """Admin: Delete a product"""
    try:
        try:
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        product.delete()
        return Response({
            'success': True,
            'message': 'Product deleted successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to delete product: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@permission_classes([AllowAny])
def admin_toggle_product_status(request, product_id):
    """Admin: Toggle product active status"""
    try:
        try:
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        product.is_active = not product.is_active
        product.save()
        
        return Response({
            'success': True,
            'message': f'Product {"activated" if product.is_active else "deactivated"} successfully',
            'data': ProductSerializer(product).data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to toggle product status: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Category Admin Views
@api_view(['GET'])
@permission_classes([AllowAny])
def admin_get_all_categories(request):
    """Admin: Get all categories (including inactive)"""
    try:
        categories = ProductCategory.objects.all()
        categories_serializer = ProductCategorySerializer(categories, many=True)
        
        return Response({
            'success': True,
            'data': categories_serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch categories: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_create_category(request):
    """Admin: Create a new category"""
    try:
        # Handle image upload if provided
        image_file = request.FILES.get('image')
        data = request.data.copy()
        
        # Remove image field from data if no file is uploaded
        if 'image' in data and not image_file:
            del data['image']
        
        if image_file:
            image_url = handle_image_upload(image_file, 'categories')
            if image_url:
                data['image'] = image_url
            else:
                return Response({
                    'success': False,
                    'message': 'Failed to upload image'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ProductCategorySerializer(data=data)
        if serializer.is_valid():
            category = serializer.save()
            return Response({
                'success': True,
                'message': 'Category created successfully',
                'data': ProductCategorySerializer(category).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to create category: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])
def admin_update_category(request, category_id):
    """Admin: Update a category"""
    try:
        try:
            category = ProductCategory.objects.get(category_id=category_id)
        except ProductCategory.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Category not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Handle image upload if provided
        image_file = request.FILES.get('image')
        data = request.data.copy()
        
        # Remove image field from data if no file is uploaded
        if 'image' in data and not image_file:
            del data['image']
        
        if image_file:
            image_url = handle_image_upload(image_file, 'categories', category.image)
            if image_url:
                data['image'] = image_url
            else:
                return Response({
                    'success': False,
                    'message': 'Failed to upload image'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ProductCategorySerializer(category, data=data, partial=True)
        if serializer.is_valid():
            updated_category = serializer.save()
            return Response({
                'success': True,
                'message': 'Category updated successfully',
                'data': ProductCategorySerializer(updated_category).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to update category: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def admin_delete_category(request, category_id):
    """Admin: Delete a category"""
    try:
        try:
            category = ProductCategory.objects.get(category_id=category_id)
        except ProductCategory.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Category not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        category.delete()
        return Response({
            'success': True,
            'message': 'Category deleted successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to delete category: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@permission_classes([AllowAny])
def admin_toggle_category_status(request, category_id):
    """Admin: Toggle category active status"""
    try:
        try:
            category = ProductCategory.objects.get(category_id=category_id)
        except ProductCategory.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Category not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        category.is_active = not category.is_active
        category.save()
        
        return Response({
            'success': True,
            'message': f'Category {"activated" if category.is_active else "deactivated"} successfully',
            'data': ProductCategorySerializer(category).data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to toggle category status: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Brand Admin Views
@api_view(['GET'])
@permission_classes([AllowAny])
def admin_get_all_brands(request):
    """Admin: Get all brands (including inactive)"""
    try:
        brands = Brand.objects.all()
        brands_serializer = BrandSerializer(brands, many=True)
        
        return Response({
            'success': True,
            'data': brands_serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch brands: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_create_brand(request):
    """Admin: Create a new brand"""
    try:
        # Handle image upload if provided
        image_file = request.FILES.get('logo')
        data = request.data.copy()
        
        if image_file:
            image_url = handle_image_upload(image_file, 'brands')
            if image_url:
                data['logo'] = image_url
            else:
                return Response({
                    'success': False,
                    'message': 'Failed to upload logo'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = BrandSerializer(data=data)
        if serializer.is_valid():
            brand = serializer.save()
            return Response({
                'success': True,
                'message': 'Brand created successfully',
                'data': BrandSerializer(brand).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to create brand: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])
def admin_update_brand(request, brand_id):
    """Admin: Update a brand"""
    try:
        try:
            brand = Brand.objects.get(brand_id=brand_id)
        except Brand.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Brand not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Handle image upload if provided
        image_file = request.FILES.get('logo')
        data = request.data.copy()
        
        if image_file:
            image_url = handle_image_upload(image_file, 'brands', brand.logo)
            if image_url:
                data['logo'] = image_url
            else:
                return Response({
                    'success': False,
                    'message': 'Failed to upload logo'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = BrandSerializer(brand, data=data, partial=True)
        if serializer.is_valid():
            updated_brand = serializer.save()
            return Response({
                'success': True,
                'message': 'Brand updated successfully',
                'data': BrandSerializer(updated_brand).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to update brand: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def admin_delete_brand(request, brand_id):
    """Admin: Delete a brand"""
    try:
        try:
            brand = Brand.objects.get(brand_id=brand_id)
        except Brand.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Brand not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        brand.delete()
        return Response({
            'success': True,
            'message': 'Brand deleted successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to delete brand: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@permission_classes([AllowAny])
def admin_toggle_brand_status(request, brand_id):
    """Admin: Toggle brand active status"""
    try:
        try:
            brand = Brand.objects.get(brand_id=brand_id)
        except Brand.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Brand not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        brand.is_active = not brand.is_active
        brand.save()
        
        return Response({
            'success': True,
            'message': f'Brand {"activated" if brand.is_active else "deactivated"} successfully',
            'data': BrandSerializer(brand).data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to toggle brand status: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Product Type Admin Views
@api_view(['GET'])
@permission_classes([AllowAny])
def admin_get_all_product_types(request):
    """Admin: Get all product types (including inactive)"""
    try:
        product_types = ProductType.objects.select_related('category').all()
        product_types_serializer = ProductTypeSerializer(product_types, many=True)
        
        return Response({
            'success': True,
            'data': product_types_serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch product types: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_create_product_type(request):
    """Admin: Create a new product type"""
    try:
        # Handle image upload if provided
        image_file = request.FILES.get('image')
        data = request.data.copy()
        
        if image_file:
            image_url = handle_image_upload(image_file, 'product_types')
            if image_url:
                data['image'] = image_url
            else:
                return Response({
                    'success': False,
                    'message': 'Failed to upload image'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ProductTypeSerializer(data=data)
        if serializer.is_valid():
            product_type = serializer.save()
            return Response({
                'success': True,
                'message': 'Product type created successfully',
                'data': ProductTypeSerializer(product_type).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to create product type: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])
def admin_update_product_type(request, product_type_id):
    """Admin: Update a product type"""
    try:
        try:
            product_type = ProductType.objects.get(type_id=product_type_id)
        except ProductType.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product type not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Handle image upload if provided
        image_file = request.FILES.get('image')
        data = request.data.copy()
        
        if image_file:
            image_url = handle_image_upload(image_file, 'product_types', product_type.image)
            if image_url:
                data['image'] = image_url
            else:
                return Response({
                    'success': False,
                    'message': 'Failed to upload image'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ProductTypeSerializer(product_type, data=data, partial=True)
        if serializer.is_valid():
            updated_product_type = serializer.save()
            return Response({
                'success': True,
                'message': 'Product type updated successfully',
                'data': ProductTypeSerializer(updated_product_type).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to update product type: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def admin_delete_product_type(request, product_type_id):
    """Admin: Delete a product type"""
    try:
        try:
            product_type = ProductType.objects.get(type_id=product_type_id)
        except ProductType.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product type not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        product_type.delete()
        return Response({
            'success': True,
            'message': 'Product type deleted successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to delete product type: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@permission_classes([AllowAny])
def admin_toggle_product_type_status(request, product_type_id):
    """Admin: Toggle product type active status"""
    try:
        try:
            product_type = ProductType.objects.get(type_id=product_type_id)
        except ProductType.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product type not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        product_type.is_active = not product_type.is_active
        product_type.save()
        
        return Response({
            'success': True,
            'message': f'Product type {"activated" if product_type.is_active else "deactivated"} successfully',
            'data': ProductTypeSerializer(product_type).data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to toggle product type status: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Banner Admin Views
@api_view(['GET'])
@permission_classes([AllowAny])
def admin_get_all_banners(request):
    """Admin: Get all banners (including inactive)"""
    try:
        banners = Banner.objects.all()
        banners_serializer = BannerSerializer(banners, many=True)
        
        return Response({
            'success': True,
            'data': banners_serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch banners: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_create_banner(request):
    """Admin: Create a new banner"""
    try:
        # Handle image upload if provided
        image_file = request.FILES.get('image')
        data = request.data.copy()
        
        if image_file:
            image_url = handle_image_upload(image_file, 'banners')
            if image_url:
                data['image'] = image_url
            else:
                return Response({
                    'success': False,
                    'message': 'Failed to upload image'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = BannerSerializer(data=data)
        if serializer.is_valid():
            banner = serializer.save()
            return Response({
                'success': True,
                'message': 'Banner created successfully',
                'data': BannerSerializer(banner).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to create banner: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])
def admin_update_banner(request, banner_id):
    """Admin: Update a banner"""
    try:
        try:
            banner = Banner.objects.get(banner_id=banner_id)
        except Banner.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Banner not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Handle image upload if provided
        image_file = request.FILES.get('image')
        data = request.data.copy()
        
        if image_file:
            image_url = handle_image_upload(image_file, 'banners', banner.image)
            if image_url:
                data['image'] = image_url
            else:
                return Response({
                    'success': False,
                    'message': 'Failed to upload image'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = BannerSerializer(banner, data=data, partial=True)
        if serializer.is_valid():
            updated_banner = serializer.save()
            return Response({
                'success': True,
                'message': 'Banner updated successfully',
                'data': BannerSerializer(updated_banner).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to update banner: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def admin_delete_banner(request, banner_id):
    """Admin: Delete a banner"""
    try:
        try:
            banner = Banner.objects.get(banner_id=banner_id)
        except Banner.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Banner not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Delete image from S3 if it exists
        if banner.image:
            from .utils import delete_image_from_s3
            delete_image_from_s3(banner.image)
        
        banner.delete()
        return Response({
            'success': True,
            'message': 'Banner deleted successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to delete banner: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@permission_classes([AllowAny])
def admin_toggle_banner_status(request, banner_id):
    """Admin: Toggle banner active status"""
    try:
        try:
            banner = Banner.objects.get(banner_id=banner_id)
        except Banner.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Banner not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        banner.is_active = not banner.is_active
        banner.save()
        
        return Response({
            'success': True,
            'message': f'Banner {"activated" if banner.is_active else "deactivated"} successfully',
            'data': BannerSerializer(banner).data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to toggle banner status: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# User Admin Views
@api_view(['GET'])
@permission_classes([AllowAny])
def admin_get_all_users(request):
    """Admin: Get all business users (including unverified)"""
    try:
        users = BusinessUser.objects.all()
        users_serializer = BusinessUserSerializer(users, many=True)
        return Response({
            'success': True,
            'data': users_serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch users: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@permission_classes([AllowAny])
def admin_toggle_user_verification(request, user_id):
    """Admin: Toggle user verification status"""
    try:
        try:
            user = BusinessUser.objects.get(user_id=user_id)
        except BusinessUser.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        user.is_verified = not user.is_verified
        user.save()
        return Response({
            'success': True,
            'message': f'User {"verified" if user.is_verified else "unverified"} successfully',
            'data': BusinessUserSerializer(user).data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to toggle user verification: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def admin_delete_user(request, user_id):
    """Admin: Delete a business user"""
    try:
        try:
            user = BusinessUser.objects.get(user_id=user_id)
        except BusinessUser.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({
            'success': True,
            'message': 'User deleted successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to delete user: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# User Profile Management Views
@api_view(['PUT'])
@permission_classes([AllowAny])
def update_user_profile(request, user_id):
    """Update user profile details"""
    try:
        # Get user
        try:
            user = BusinessUser.objects.get(user_id=user_id)
        except BusinessUser.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get current password for verification
        current_password = request.data.get('current_password')
        if not current_password:
            return Response({
                'success': False,
                'message': 'Current password is required for profile updates'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify current password
        if not user.check_password(current_password):
            return Response({
                'success': False,
                'message': 'Current password is incorrect'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Prepare data for update (exclude password field)
        update_data = {}
        allowed_fields = ['business_name', 'business_type', 'business_location', 'tin_number']
        
        for field in allowed_fields:
            if field in request.data:
                update_data[field] = request.data[field]
        
        # Check for unique constraints
        if 'phone_number' in request.data:
            phone_number = request.data['phone_number']
            if phone_number != user.phone_number:
                if BusinessUser.objects.filter(phone_number=phone_number).exists():
                    return Response({
                        'success': False,
                        'message': 'Phone number already exists'
                    }, status=status.HTTP_400_BAD_REQUEST)
                update_data['phone_number'] = phone_number
        
        if 'tin_number' in request.data:
            tin_number = request.data['tin_number']
            if tin_number != user.tin_number:
                if BusinessUser.objects.filter(tin_number=tin_number).exists():
                    return Response({
                        'success': False,
                        'message': 'TIN number already exists'
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update user
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.save()
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'data': BusinessUserSerializer(user).data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to update profile: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_user_password(request, user_id):
    """Update user password"""
    try:
        # Get user
        try:
            user = BusinessUser.objects.get(user_id=user_id)
        except BusinessUser.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get password data
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        # Validate required fields
        if not current_password:
            return Response({
                'success': False,
                'message': 'Current password is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not new_password:
            return Response({
                'success': False,
                'message': 'New password is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not confirm_password:
            return Response({
                'success': False,
                'message': 'Password confirmation is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify current password
        if not user.check_password(current_password):
            return Response({
                'success': False,
                'message': 'Current password is incorrect'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if new password matches confirmation
        if new_password != confirm_password:
            return Response({
                'success': False,
                'message': 'New password and confirmation do not match'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate new password length
        if len(new_password) < 6:
            return Response({
                'success': False,
                'message': 'New password must be at least 6 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if new password is different from current
        if user.check_password(new_password):
            return Response({
                'success': False,
                'message': 'New password must be different from current password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update password
        user.password = new_password
        user.save()
        
        return Response({
            'success': True,
            'message': 'Password updated successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to update password: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Order Management Views
@api_view(['POST'])
@permission_classes([AllowAny])
def create_order(request):
    """Create a new order for a user"""
    try:
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({
                'success': False,
                'message': 'user_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user
        try:
            user = BusinessUser.objects.get(user_id=user_id)
        except BusinessUser.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create a mock request context for the serializer
        mock_request = type('MockRequest', (), {'user': user})()
        
        serializer = CreateOrderSerializer(data=request.data, context={'request': mock_request})
        if serializer.is_valid():
            order = serializer.save()
            # Generate order number
            order_number = order.generate_order_number()
            
            # Prepare response data
            response_data = {
                'success': True,
                'message': 'Order created successfully',
                'order_id': order.order_id,
                'order_number': order_number,
                'total_amount': float(order.total_amount),
                'order_status': order.status.upper(),
                'created_at': order.created_at.isoformat() + 'Z'
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to create order: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_order_details_new_format(request, order_id):
    """Get order details in new format"""
    try:
        # Get order
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize order in new format
        order_serializer = OrderResponseSerializer(order)
        
        return Response({
            'success': True,
            'data': order_serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to get order details: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_orders(request, user_id):
    """Get all orders for a specific user"""
    try:
        # Get user
        try:
            user = BusinessUser.objects.get(user_id=user_id)
        except BusinessUser.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get user's orders
        orders = Order.objects.filter(user=user).prefetch_related('order_items__product')
        orders_serializer = OrderSerializer(orders, many=True)
        
        return Response({
            'success': True,
            'data': orders_serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch orders: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_order_details(request, order_id):
    """Get detailed information about a specific order"""
    try:
        # Get order
        try:
            order = Order.objects.select_related('user').prefetch_related('order_items__product').get(order_id=order_id)
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        order_serializer = OrderSerializer(order)
        
        return Response({
            'success': True,
            'data': order_serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch order details: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@permission_classes([AllowAny])
def update_order_status(request, order_id):
    """Update order status (for admin use)"""
    try:
        # Get order
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        new_status = request.data.get('status')
        if not new_status:
            return Response({
                'success': False,
                'message': 'status is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate status
        valid_statuses = [choice[0] for choice in Order.ORDER_STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response({
                'success': False,
                'message': f'Invalid status. Valid options: {", ".join(valid_statuses)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update status
        order.status = new_status
        
        # Update tracking number if provided
        tracking_number = request.data.get('tracking_number')
        if tracking_number:
            order.tracking_number = tracking_number
        
        order.save()
        
        return Response({
            'success': True,
            'message': f'Order status updated to {new_status}',
            'data': OrderSerializer(order).data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to update order status: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def cancel_order(request, order_id):
    """Cancel an order"""
    try:
        # Get order
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if order can be cancelled
        if order.status in ['delivered', 'cancelled', 'refunded']:
            return Response({
                'success': False,
                'message': f'Order cannot be cancelled in {order.status} status'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Cancel order
        order.status = 'cancelled'
        order.save()
        
        # Restore product stock
        for item in order.order_items.all():
            product = item.product
            product.stock_quantity += item.quantity
            product.save()
        
        return Response({
            'success': True,
            'message': 'Order cancelled successfully',
            'data': OrderSerializer(order).data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to cancel order: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_order(request, order_id):
    """Delete an order permanently"""
    try:
        # Get order
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if order can be deleted
        if order.status in ['delivered', 'shipped']:
            return Response({
                'success': False,
                'message': f'Order cannot be deleted in {order.status} status. Only pending, confirmed, processing, or cancelled orders can be deleted.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Store order details for response
        order_data = {
            'order_id': order.order_id,
            'order_number': order.order_number,
            'user_id': order.user.user_id,
            'business_name': order.user.business_name,
            'total_amount': float(order.total_amount),
            'status': order.status,
            'created_at': order.created_at.isoformat() + 'Z'
        }
        
        # Restore product stock before deletion
        for item in order.order_items.all():
            product = item.product
            product.stock_quantity += item.quantity
            product.save()
        
        # Delete the order (this will also delete order items due to CASCADE)
        order.delete()
        
        return Response({
            'success': True,
            'message': 'Order deleted successfully',
            'deleted_order': order_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to delete order: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Admin Order Management Views
@api_view(['GET'])
@permission_classes([AllowAny])
def admin_get_all_orders(request):
    """Admin: Get all orders"""
    try:
        orders = Order.objects.select_related('user').prefetch_related('order_items__product').all()
        orders_serializer = OrderSerializer(orders, many=True)
        
        return Response({
            'success': True,
            'data': orders_serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch orders: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def admin_get_orders_by_status(request, status):
    """Admin: Get orders filtered by status"""
    try:
        # Validate status
        valid_statuses = [choice[0] for choice in Order.ORDER_STATUS_CHOICES]
        if status not in valid_statuses:
            return Response({
                'success': False,
                'message': f'Invalid status. Valid options: {", ".join(valid_statuses)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        orders = Order.objects.filter(status=status).select_related('user').prefetch_related('order_items__product')
        orders_serializer = OrderSerializer(orders, many=True)
        
        return Response({
            'success': True,
            'data': orders_serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch orders: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Customer Management APIs
@api_view(['GET'])
@permission_classes([AllowAny])
def get_customers(request):
    """Get all customers"""
    try:
        customers = Customer.objects.all().order_by('-created_at')
        serializer = CustomerSerializer(customers, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch customers: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_customers(request):
    """Search customers by name or phone"""
    try:
        query = request.GET.get('q', '').strip()
        
        if not query:
            return Response({
                'success': True,
                'data': []
            }, status=status.HTTP_200_OK)
        
        customers = Customer.objects.filter(
            models.Q(name__icontains=query) | 
            models.Q(phone__icontains=query)
        ).order_by('name')[:10]
        
        serializer = CustomerSearchSerializer(customers, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to search customers: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_customer(request):
    """Create a new customer"""
    try:
        serializer = CustomerSerializer(data=request.data)
        
        if serializer.is_valid():
            customer = serializer.save()
            return Response({
                'success': True,
                'message': 'Customer created successfully',
                'data': CustomerSerializer(customer).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to create customer: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Shelf Management APIs
@api_view(['GET'])
@permission_classes([AllowAny])
def get_shelves(request):
    """Get all shelves"""
    try:
        shelves = Shelf.objects.filter(is_active=True).order_by('name')
        serializer = ShelfSerializer(shelves, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch shelves: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_shelf(request):
    """Create a new shelf"""
    try:
        serializer = ShelfSerializer(data=request.data)
        
        if serializer.is_valid():
            shelf = serializer.save()
            return Response({
                'success': True,
                'message': 'Shelf created successfully',
                'data': ShelfSerializer(shelf).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to create shelf: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Products with Locations API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_products_with_locations(request):
    """Get all products with their locations"""
    try:
        products = Product.objects.filter(is_active=True).prefetch_related('locations__shelf')
        serializer = ProductWithLocationSerializer(products, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch products: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Sales Management APIs
@api_view(['GET'])
@permission_classes([AllowAny])
def get_sales(request):
    """Get all sales"""
    try:
        sales = Sale.objects.all().prefetch_related('items__product').order_by('-sale_date')
        serializer = SaleSerializer(sales, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch sales: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_sale(request):
    """Create a new sale"""
    try:
        serializer = CreateSaleSerializer(data=request.data)
        
        if serializer.is_valid():
            sale = serializer.save()
            return Response({
                'success': True,
                'message': 'Sale created successfully',
                'data': SaleSerializer(sale).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to create sale: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sales_by_salesperson(request, salesperson_id):
    """Get sales by specific salesperson"""
    try:
        sales = Sale.objects.filter(salesperson_id=salesperson_id).prefetch_related('items__product').order_by('-sale_date')
        serializer = SaleSerializer(sales, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch sales: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_sale_payment_status(request, sale_id):
    """Update sale payment status"""
    try:
        try:
            sale = Sale.objects.get(sale_id=sale_id)
        except Sale.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Sale not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        payment_status = request.data.get('payment_status')
        if not payment_status:
            return Response({
                'success': False,
                'message': 'Payment status is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        valid_statuses = [choice[0] for choice in Sale.PAYMENT_STATUS_CHOICES]
        if payment_status not in valid_statuses:
            return Response({
                'success': False,
                'message': f'Invalid payment status. Valid options: {", ".join(valid_statuses)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        sale.payment_status = payment_status
        sale.save()
        
        return Response({
            'success': True,
            'message': 'Payment status updated successfully',
            'data': SaleSerializer(sale).data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to update payment status: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Inventory Alert APIs
@api_view(['GET'])
@permission_classes([AllowAny])
def get_low_stock_products(request):
    """Get products with low stock"""
    try:
        products = Product.objects.filter(
            is_active=True,
            stock_quantity__lte=models.F('minimum_stock')
        ).order_by('stock_quantity')
        
        serializer = ProductWithLocationSerializer(products, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch low stock products: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_expiring_products(request):
    """Get products expiring soon (within 30 days)"""
    try:
        from datetime import datetime, timedelta
        
        # Get products expiring within 30 days
        expiry_threshold = datetime.now().date() + timedelta(days=30)
        
        products = Product.objects.filter(
            is_active=True,
            expiry_date__lte=expiry_threshold,
            expiry_date__gte=datetime.now().date()
        ).order_by('expiry_date')
        
        serializer = ProductWithLocationSerializer(products, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch expiring products: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Customer Management APIs
@api_view(['GET'])
@permission_classes([AllowAny])
def get_customers(request):
    """Get all customers"""
    try:
        customers = Customer.objects.all().order_by('-created_at')
        serializer = CustomerSerializer(customers, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch customers: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_customers(request):
    """Search customers by name or phone"""
    try:
        query = request.GET.get('q', '').strip()
        
        if not query:
            return Response({
                'success': True,
                'data': []
            }, status=status.HTTP_200_OK)
        
        customers = Customer.objects.filter(
            models.Q(name__icontains=query) | 
            models.Q(phone__icontains=query)
        ).order_by('name')[:10]
        
        serializer = CustomerSearchSerializer(customers, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to search customers: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_customer(request):
    """Create a new customer"""
    try:
        serializer = CustomerSerializer(data=request.data)
        
        if serializer.is_valid():
            customer = serializer.save()
            return Response({
                'success': True,
                'message': 'Customer created successfully',
                'data': CustomerSerializer(customer).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to create customer: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Shelf Management APIs
@api_view(['GET'])
@permission_classes([AllowAny])
def get_shelves(request):
    """Get all shelves"""
    try:
        shelves = Shelf.objects.filter(is_active=True).order_by('name')
        serializer = ShelfSerializer(shelves, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch shelves: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_shelf(request):
    """Create a new shelf"""
    try:
        serializer = ShelfSerializer(data=request.data)
        
        if serializer.is_valid():
            shelf = serializer.save()
            return Response({
                'success': True,
                'message': 'Shelf created successfully',
                'data': ShelfSerializer(shelf).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to create shelf: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Products with Locations API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_products_with_locations(request):
    """Get all products with their locations"""
    try:
        products = Product.objects.filter(is_active=True).prefetch_related('locations__shelf')
        serializer = ProductWithLocationSerializer(products, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch products: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Sales Management APIs
@api_view(['GET'])
@permission_classes([AllowAny])
def get_sales(request):
    """Get all sales"""
    try:
        sales = Sale.objects.all().prefetch_related('items__product').order_by('-sale_date')
        serializer = SaleSerializer(sales, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch sales: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_sale(request):
    """Create a new sale"""
    try:
        serializer = CreateSaleSerializer(data=request.data)
        
        if serializer.is_valid():
            sale = serializer.save()
            return Response({
                'success': True,
                'message': 'Sale created successfully',
                'data': SaleSerializer(sale).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to create sale: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sales_by_salesperson(request, salesperson_id):
    """Get sales by specific salesperson"""
    try:
        sales = Sale.objects.filter(salesperson_id=salesperson_id).prefetch_related('items__product').order_by('-sale_date')
        serializer = SaleSerializer(sales, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch sales: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_sale_payment_status(request, sale_id):
    """Update sale payment status"""
    try:
        try:
            sale = Sale.objects.get(sale_id=sale_id)
        except Sale.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Sale not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        payment_status = request.data.get('payment_status')
        if not payment_status:
            return Response({
                'success': False,
                'message': 'Payment status is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        valid_statuses = [choice[0] for choice in Sale.PAYMENT_STATUS_CHOICES]
        if payment_status not in valid_statuses:
            return Response({
                'success': False,
                'message': f'Invalid payment status. Valid options: {", ".join(valid_statuses)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        sale.payment_status = payment_status
        sale.save()
        
        return Response({
            'success': True,
            'message': 'Payment status updated successfully',
            'data': SaleSerializer(sale).data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to update payment status: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Inventory Alert APIs
@api_view(['GET'])
@permission_classes([AllowAny])
def get_low_stock_products(request):
    """Get products with low stock"""
    try:
        products = Product.objects.filter(
            is_active=True,
            stock_quantity__lte=models.F('minimum_stock')
        ).order_by('stock_quantity')
        
        serializer = ProductWithLocationSerializer(products, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch low stock products: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_expiring_products(request):
    """Get products expiring soon (within 30 days)"""
    try:
        from datetime import datetime, timedelta
        
        # Get products expiring within 30 days
        expiry_threshold = datetime.now().date() + timedelta(days=30)
        
        products = Product.objects.filter(
            is_active=True,
            expiry_date__lte=expiry_threshold,
            expiry_date__gte=datetime.now().date()
        ).order_by('expiry_date')
        
        serializer = ProductWithLocationSerializer(products, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch expiring products: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
