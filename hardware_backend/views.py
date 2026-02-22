from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta, datetime, date
from decimal import Decimal
import random
import string
import json
import requests
from django.db import models
from django.conf import settings
from .utils import handle_image_upload

from .models import (
    BusinessUser, ProductCategory, Brand, ProductType, 
    Product, ProductBatch, Banner, HardwareOTP, Order, OrderItem,
    Customer, Shelf, ProductLocation, Sale, SaleItem, Expense,
    Invoice, InvoiceItem
)
from .serializers import (
    BusinessUserRegistrationSerializer, BusinessUserLoginSerializer,
    BusinessUserSerializer, OTPSerializer, ProductCategorySerializer,
    BrandSerializer, ProductTypeSerializer, ProductSerializer, ProductBatchSerializer,
    BannerSerializer, HomePageSerializer, ProductsPageSerializer,
    ProductTypeWithProductsSerializer, OrderSerializer, CreateOrderSerializer,
    OrderItemSerializer, OrderResponseSerializer, OrderItemResponseSerializer,
    CustomerSerializer, CustomerSearchSerializer, ShelfSerializer,
    ProductLocationSerializer, SaleSerializer, SaleItemSerializer,
    CreateSaleSerializer, ProductWithLocationSerializer, ExpenseSerializer,
    InvoiceSerializer, InvoiceItemSerializer, CreateInvoiceFromOrderSerializer,
    UpdateInvoiceSerializer
)

def generate_otp():
    """Generate a 4-digit OTP - defaults to 1234 for development"""
    # Check if we should use default OTP (for development/testing)
    use_default_otp = getattr(settings, 'USE_DEFAULT_OTP', True)  # Default to True for development
    
    if use_default_otp or settings.DEBUG:
        # Return default OTP for easy testing
        return '1234'
    
    # Generate random 4-digit OTP (1000-9999) for production
    otp = random.randint(1000, 9999)
    return str(otp)

def send_otp_sms(phone_number, otp):
    """
    Send OTP via SMS using mShastra API
    Falls back to console print in development if SMS credentials are not configured
    """
    # Get SMS configuration from settings
    sms_username = getattr(settings, 'SMS_USERNAME', None)
    sms_password = getattr(settings, 'SMS_PASSWORD', None)
    sms_sender = getattr(settings, 'SMS_SENDER', 'YourApp')
    sms_api_url = getattr(settings, 'SMS_API_URL', 'https://mshastra.com/sendsms_api_json.aspx')
    
    # Check if SMS credentials are configured
    if not sms_username or sms_username == 'YOUR_SMS_USERNAME' or not sms_password or sms_password == 'YOUR_SMS_PASSWORD':
        # Fallback to console print in development
        print(f"[DEV MODE] OTP {otp} for {phone_number} (SMS not configured)")
        return True
    
    # Prepare phone number (ensure it doesn't have + prefix for SMS API)
    phone_clean = phone_number.replace('+', '').replace(' ', '')
    
    # Prepare SMS message
    message = f"Welcome To Pharmacy Mkononi!\nThank you for using our service.\nYour OTP is {otp}"
    
    # Prepare payload for mShastra API
    payload = json.dumps([{
        "user": sms_username,
        "pwd": sms_password,
        "number": phone_clean,
        "sender": sms_sender,
        "msg": message,
        "language": "Unicode"
    }])
    
    headers = {
        'Content-Type': 'application/json',
        "accept": "application/json",
    }
    
    try:
        # Send SMS via API
        response = requests.post(sms_api_url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        json_response = response.json()
        
        # Check if SMS was sent successfully
        # mShastra API typically returns success status in response
        print(f"SMS sent successfully to {phone_number}: {json_response}")
        return True
    except requests.exceptions.RequestException as e:
        # Log error but don't fail - fallback to console in development
        print(f"Failed to send SMS to {phone_number}: {str(e)}")
        if settings.DEBUG:
            print(f"[DEV MODE] OTP {otp} for {phone_number}")
            return True
        return False
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        if settings.DEBUG:
            print(f"[DEV MODE] OTP {otp} for {phone_number}")
            return True
        return False

def normalize_phone_number(phone_number):
    """Normalize phone number to consistent format (+255XXXXXXXXX)"""
    if not phone_number:
        return phone_number
    
    phone = phone_number.strip()
    
    # Remove any spaces, dashes, or other characters
    phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Normalize to +255 format
    if phone.startswith('0'):
        # Remove leading 0 and add +255 (Tanzania country code)
        phone = f"+255{phone[1:]}"
    elif phone.startswith('255'):
        # Add + prefix if missing
        phone = f"+{phone}"
    elif not phone.startswith('+'):
        # Add + prefix if missing
        phone = f"+{phone}"
    
    return phone

@api_view(['POST'])
@permission_classes([AllowAny])
def register_business_user(request):
    """Register a new business user"""
    try:
        serializer = BusinessUserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            # Normalize phone number to ensure consistency
            phone_number = serializer.validated_data['phone_number']
            normalized_phone = normalize_phone_number(phone_number)
            tin_number = serializer.validated_data['tin_number']
            
            # Check if user already exists with normalized phone
            if BusinessUser.objects.filter(phone_number=normalized_phone).exists():
                return Response({
                    'success': False,
                    'message': 'User with this phone number already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Also check with original phone number format (in case normalization differs)
            if normalized_phone != phone_number and BusinessUser.objects.filter(phone_number=phone_number).exists():
                return Response({
                    'success': False,
                    'message': 'User with this phone number already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if BusinessUser.objects.filter(tin_number=tin_number).exists():
                return Response({
                    'success': False,
                    'message': 'User with this TIN number already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update serializer data with normalized phone
            serializer.validated_data['phone_number'] = normalized_phone
            
            # Create user
            user = serializer.save()
            
            # Generate and send OTP (use normalized phone)
            otp = generate_otp()
            HardwareOTP.objects.update_or_create(
                phone_number=normalized_phone,
                defaults={'otp': otp, 'is_used': False}
            )
            
            # Send OTP via SMS
            send_otp_sms(normalized_phone, otp)
            
            return Response({
                'success': True,
                'message': 'Registration successful. Please verify your phone number with the OTP sent.',
                'user_id': user.user_id,
                'phone_number': normalized_phone
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
    """Login business user with phone number and password - sends OTP for verification"""
    try:
        serializer = BusinessUserLoginSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number'].strip()
            password = serializer.validated_data['password']
            
            # Check if OTP login is enabled
            enable_otp_login = getattr(settings, 'ENABLE_OTP_LOGIN', True)
            
            # Normalize phone number - handle different formats
            normalized_phone = normalize_phone_number(phone_number)
            
            # Try to find user with multiple phone number formats
            user = None
            phone_variants = [
                normalized_phone,  # +255616107670
                phone_number,     # Original format
                normalized_phone[1:] if normalized_phone.startswith('+') else f"+{normalized_phone}",  # Without + or with +
            ]
            
            # Remove duplicates
            phone_variants = list(dict.fromkeys(phone_variants))
            
            for phone_variant in phone_variants:
                try:
                    user = BusinessUser.objects.get(phone_number=phone_variant)
                    break  # Found user, exit loop
                except BusinessUser.DoesNotExist:
                    continue
            
            # If still not found, try case-insensitive search (in case of any whitespace issues)
            if not user:
                # Try with Q object for case-insensitive search
                from django.db.models import Q
                users = BusinessUser.objects.filter(
                    Q(phone_number__iexact=normalized_phone) |
                    Q(phone_number__iexact=phone_number) |
                    Q(phone_number__iexact=normalized_phone.replace('+', ''))
                )
                if users.exists():
                    user = users.first()
            
            # If user not found, return error with helpful debug info (only in development)
            if not user:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"User not found. Input: {phone_number}, Normalized: {normalized_phone}, Tried: {phone_variants}")
                
                # In production, don't expose debug info
                debug_info = {}
                if settings.DEBUG:
                    debug_info = {
                        'input_phone': phone_number,
                        'normalized_phone': normalized_phone,
                        'tried_variants': phone_variants[:5]
                    }
                
                return Response({
                    'success': False,
                    'message': 'Invalid phone number or password',
                    **debug_info
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check password
            password_valid = user.check_password(password)
            if not password_valid:
                # Log for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Password check failed for user {user.phone_number} (user_id: {user.user_id})")
                
                return Response({
                    'success': False,
                    'message': 'Invalid phone number or password'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Require admin approval before login (mobile app users)
            if not user.is_verified:
                return Response({
                    'success': False,
                    'message': 'Please Wait for the approval before Login'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # If OTP login is disabled, return token directly (backward compatibility)
            if not enable_otp_login:
                import hashlib
                import time
                token_data = f"{user.user_id}:{user.phone_number}:{int(time.time())}"
                token = hashlib.sha256(token_data.encode()).hexdigest()
                
                user_serializer = BusinessUserSerializer(user)
                return Response({
                    'success': True,
                    'message': 'Login successful',
                    'data': {
                        'user': user_serializer.data,
                        'token': token
                    }
                }, status=status.HTTP_200_OK)
            
            # OTP login is enabled - generate and send OTP
            # Generate OTP
            otp = generate_otp()
            
            # Use the user's actual phone number from database (to ensure consistency)
            otp_phone = user.phone_number
            
            # Delete existing OTP for this phone number (if any)
            HardwareOTP.objects.filter(phone_number=otp_phone).delete()
            
            # Create new OTP record
            HardwareOTP.objects.create(
                phone_number=otp_phone,
                otp=otp,
                is_used=False
            )
            
            # Send OTP via SMS
            send_otp_sms(otp_phone, otp)
            
            # Return response indicating OTP is required (user is already approved at this point)
            return Response({
                'success': True,
                'message': 'OTP sent to your phone number. Please verify to complete login.',
                'needs_otp': True,
                'phone_number': otp_phone
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
            
            # Check if OTP is expired using model method
            if otp_obj.is_expired():
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
def login_verify_otp(request):
    """Verify OTP to complete login after password verification"""
    try:
        phone_number = request.data.get('phone_number', '').strip()
        otp = request.data.get('otp', '').strip()
        
        if not phone_number:
            return Response({
                'success': False,
                'message': 'Phone number is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not otp:
            return Response({
                'success': False,
                'message': 'OTP is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Normalize phone number - handle different formats
        normalized_phone = normalize_phone_number(phone_number)
        
        # Check if OTP exists - try multiple phone formats
        otp_obj = None
        phone_variants = [
            normalized_phone,
            phone_number,
            normalized_phone[1:] if normalized_phone.startswith('+') else f"+{normalized_phone}",
        ]
        
        # Remove duplicates
        phone_variants = list(dict.fromkeys(phone_variants))
        
        for phone_variant in phone_variants:
            try:
                otp_obj = HardwareOTP.objects.get(phone_number=phone_variant)
                break
            except HardwareOTP.DoesNotExist:
                continue
        
        if not otp_obj:
            return Response({
                'success': False,
                'message': 'No OTP found for this phone number. Please request a new one.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if OTP is expired
        if otp_obj.is_expired():
            return Response({
                'success': False,
                'message': 'OTP has expired. Please request a new one.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if OTP is already used
        if otp_obj.is_used:
            return Response({
                'success': False,
                'message': 'OTP has already been used. Please request a new one.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify OTP code
        if otp_obj.otp != otp:
            return Response({
                'success': False,
                'message': 'Invalid OTP code'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()
        
        # Get user - try multiple phone formats (use the phone from OTP record)
        otp_phone = otp_obj.phone_number
        user = None
        
        phone_variants = [
            otp_phone,  # Phone stored in OTP record
            normalized_phone,
            phone_number,
            normalized_phone[1:] if normalized_phone.startswith('+') else f"+{normalized_phone}",
        ]
        
        # Remove duplicates
        phone_variants = list(dict.fromkeys(phone_variants))
        
        for phone_variant in phone_variants:
            try:
                user = BusinessUser.objects.get(phone_number=phone_variant)
                break
            except BusinessUser.DoesNotExist:
                continue
        
        # If still not found, try case-insensitive search
        if not user:
            from django.db.models import Q
            users = BusinessUser.objects.filter(
                Q(phone_number__iexact=otp_phone) |
                Q(phone_number__iexact=normalized_phone) |
                Q(phone_number__iexact=phone_number)
            )
            if users.exists():
                user = users.first()
        
        if not user:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Require admin approval before login (do not auto-verify; only dashboard can approve)
        if not user.is_verified:
            return Response({
                'success': False,
                'message': 'Please Wait for the approval before Login'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Generate authentication token
        import hashlib
        import time
        token_data = f"{user.user_id}:{user.phone_number}:{int(time.time())}"
        token = hashlib.sha256(token_data.encode()).hexdigest()
        
        # Return user data with token
        user_serializer = BusinessUserSerializer(user)
        return Response({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': user_serializer.data,
                'token': token
            }
        }, status=status.HTTP_200_OK)
        
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
        phone_number = request.data.get('phone_number', '').strip()
        if not phone_number:
            return Response({
                'success': False,
                'message': 'Phone number is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Normalize phone number - handle different formats
        normalized_phone = phone_number
        if normalized_phone.startswith('0'):
            # Remove leading 0 and add +255 (Tanzania country code)
            normalized_phone = f"+255{normalized_phone[1:]}"
        elif normalized_phone.startswith('255'):
            # Add + prefix if missing
            normalized_phone = f"+{normalized_phone}"
        elif not normalized_phone.startswith('+'):
            # Add + prefix if missing
            normalized_phone = f"+{normalized_phone}"
        
        # Check if user exists (try normalized first, then original)
        user = None
        try:
            user = BusinessUser.objects.get(phone_number=normalized_phone)
        except BusinessUser.DoesNotExist:
            try:
                user = BusinessUser.objects.get(phone_number=phone_number)
            except BusinessUser.DoesNotExist:
                pass
        
        if not user:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Use normalized phone for OTP
        otp_phone = normalized_phone if user.phone_number == normalized_phone else user.phone_number
        
        # Generate new OTP
        otp = generate_otp()
        
        # Delete existing OTP and create new one to ensure fresh timestamp
        HardwareOTP.objects.filter(phone_number=otp_phone).delete()
        HardwareOTP.objects.create(
            phone_number=otp_phone,
            otp=otp,
            is_used=False
        )
        
        # Send OTP via SMS
        send_otp_sms(otp_phone, otp)
        
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
    """Get home page data - categories, brands, and banners
    
    This endpoint is used by the mobile app to fetch categories.
    Response format: { success: true, data: { categories: [...], brands: [...], banners: [...] } }
    Categories are accessible at body['data']['categories']
    """
    try:
        # Get active categories, ordered by name for consistent ordering
        categories = ProductCategory.objects.filter(is_active=True).order_by('name')
        categories_serializer = ProductCategorySerializer(categories, many=True)
        
        # Get active brands, ordered by name
        brands = Brand.objects.filter(is_active=True).order_by('name')
        brands_serializer = BrandSerializer(brands, many=True)
        
        # Get active banners, ordered by order field and creation date
        banners = Banner.objects.filter(is_active=True).order_by('order', '-created_at')
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
        
        # Get active categories, ordered by name for consistent ordering
        categories = ProductCategory.objects.filter(is_active=True).order_by('name')
        categories_serializer = ProductCategorySerializer(categories, many=True)
        
        # Get active brands, ordered by name
        brands = Brand.objects.filter(is_active=True).order_by('name')
        brands_serializer = BrandSerializer(brands, many=True)
        
        # Get active banners, ordered by order field and creation date
        banners = Banner.objects.filter(is_active=True).order_by('order', '-created_at')
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
        
        # Extract shelf_id for product location (required)
        shelf_id = data.pop('shelf_id', None) or data.pop('shelf', None)
        if not shelf_id:
            return Response({
                'success': False,
                'message': 'Shelf location is required. Please select a shelf where the product will be located.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate shelf exists
        try:
            shelf = Shelf.objects.get(shelf_id=shelf_id)
        except Shelf.DoesNotExist:
            return Response({
                'success': False,
                'message': f'Shelf with ID "{shelf_id}" not found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"🔍 DEBUG: Final data before serializer: {data}")
        print(f"🔍 DEBUG: Data types: {[(k, type(v).__name__) for k, v in data.items()]}")
        
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            product = serializer.save()
            print(f"🔍 DEBUG: Product created successfully: {product.product_id}")
            
            # Create product location on the specified shelf
            try:
                # Get quantity from stock_quantity or use 0
                quantity = int(data.get('stock_quantity', 0)) if data.get('stock_quantity') else 0
                
                ProductLocation.objects.create(
                    product=product,
                    shelf=shelf,
                    quantity=quantity
                )
                print(f"🔍 DEBUG: Product location created: {product.name} on {shelf.name}")
            except Exception as loc_error:
                print(f"⚠️ WARNING: Failed to create product location: {str(loc_error)}")
                # Don't fail the product creation if location creation fails
                # The location can be added later
            
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

# Shelf Admin Views
@api_view(['GET'])
@permission_classes([AllowAny])
def admin_get_all_shelves(request):
    """Admin: Get all shelves (including inactive)"""
    try:
        shelves = Shelf.objects.all().order_by('name')
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
def admin_create_shelf(request):
    """Admin: Create a new shelf"""
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
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to create shelf: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])
def admin_update_shelf(request, shelf_id):
    """Admin: Update a shelf"""
    try:
        try:
            shelf = Shelf.objects.get(shelf_id=shelf_id)
        except Shelf.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Shelf not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ShelfSerializer(shelf, data=request.data, partial=True)
        if serializer.is_valid():
            updated_shelf = serializer.save()
            return Response({
                'success': True,
                'message': 'Shelf updated successfully',
                'data': ShelfSerializer(updated_shelf).data
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
            'message': f'Failed to update shelf: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def admin_delete_shelf(request, shelf_id):
    """Admin: Delete a shelf"""
    try:
        try:
            shelf = Shelf.objects.get(shelf_id=shelf_id)
        except Shelf.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Shelf not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        shelf.delete()
        return Response({
            'success': True,
            'message': 'Shelf deleted successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to delete shelf: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@permission_classes([AllowAny])
def admin_toggle_shelf_status(request, shelf_id):
    """Admin: Toggle shelf active status"""
    try:
        try:
            shelf = Shelf.objects.get(shelf_id=shelf_id)
        except Shelf.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Shelf not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        shelf.is_active = not shelf.is_active
        shelf.save()
        
        return Response({
            'success': True,
            'message': f'Shelf {"activated" if shelf.is_active else "deactivated"} successfully',
            'data': ShelfSerializer(shelf).data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to toggle shelf status: {str(e)}'
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


@api_view(['PUT', 'PATCH'])
@permission_classes([AllowAny])
def admin_update_user(request, user_id):
    """Admin: Update a business user's basic details (name, phone, role, status)"""
    try:
        try:
            user = BusinessUser.objects.get(user_id=user_id)
        except BusinessUser.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

        data = request.data

        # Update business name
        name = data.get('name')
        if name is not None:
            user.business_name = name

        # Update phone number with normalization and uniqueness check
        phone = data.get('phone') or data.get('phone_number')
        if phone is not None:
            normalized_phone = normalize_phone_number(phone)
            if BusinessUser.objects.exclude(user_id=user_id).filter(phone_number=normalized_phone).exists():
                return Response({
                    'success': False,
                    'message': 'Phone number already exists for another user'
                }, status=status.HTTP_400_BAD_REQUEST)
            user.phone_number = normalized_phone

        # Update role (business_type) from frontend role value
        role = data.get('role') or data.get('business_type')
        if role is not None:
            # Store as lowercased business type for consistency
            user.business_type = str(role).lower()

        # Update status -> map to is_verified
        status_value = data.get('status')
        if status_value is not None:
            # Treat "active" as verified, others as not verified
            user.is_verified = (str(status_value).lower() == 'active')

        user.save()

        return Response({
            'success': True,
            'message': 'User updated successfully',
            'data': BusinessUserSerializer(user).data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to update user: {str(e)}'
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
        # Get user; if not found, return empty list instead of 404
        try:
            user = BusinessUser.objects.get(user_id=user_id)
        except BusinessUser.DoesNotExist:
            return Response({
                'success': True,
                'message': 'No orders found for this user',
                'data': []
            }, status=status.HTTP_200_OK)

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
    """Get all customers - includes both Customer and BusinessUser"""
    try:
        # Get all customers
        customers = Customer.objects.all().order_by('-created_at')
        customer_serializer = CustomerSerializer(customers, many=True)
        results = list(customer_serializer.data)
        
        # Also get all BusinessUsers (users) and convert to customer format
        users = BusinessUser.objects.all().order_by('-created_at')
        for user in users:
            results.append({
                'customer_id': f"USER-{user.user_id}",  # Prefix to distinguish from regular customers
                'name': user.business_name,
                'phone': user.phone_number,
                'email': None,  # BusinessUser doesn't have email in the model
                'address': user.business_location,
                'created_at': user.created_at.isoformat() if user.created_at else timezone.now().isoformat(),
                'updated_at': user.updated_at.isoformat() if user.updated_at else timezone.now().isoformat(),
            })
        
        return Response({
            'success': True,
            'data': results
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch customers: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_customers(request):
    """Search customers by name or phone - includes both Customer and BusinessUser"""
    try:
        query = request.GET.get('q', '').strip()
        
        if not query:
            return Response({
                'success': True,
                'data': []
            }, status=status.HTTP_200_OK)
        
        # Search in Customer model
        customers = Customer.objects.filter(
            models.Q(name__icontains=query) | 
            models.Q(phone__icontains=query)
        ).order_by('name')[:10]
        
        customer_serializer = CustomerSearchSerializer(customers, many=True)
        results = list(customer_serializer.data)
        
        # Also search in BusinessUser model (users)
        users = BusinessUser.objects.filter(
            models.Q(business_name__icontains=query) | 
            models.Q(phone_number__icontains=query)
        ).order_by('business_name')[:10]
        
        # Convert BusinessUser to customer-like format
        for user in users:
            results.append({
                'customer_id': f"USER-{user.user_id}",  # Prefix to distinguish from regular customers
                'name': user.business_name,
                'phone': user.phone_number,
            })
        
        # Remove duplicates based on phone number and limit to 10 total
        seen_phones = set()
        unique_results = []
        for item in results:
            phone = item.get('phone', '')
            if phone and phone not in seen_phones:
                seen_phones.add(phone)
                unique_results.append(item)
                if len(unique_results) >= 10:
                    break
        
        return Response({
            'success': True,
            'data': unique_results
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
    """Get all customers - includes both Customer and BusinessUser"""
    try:
        # Get all customers
        customers = Customer.objects.all().order_by('-created_at')
        customer_serializer = CustomerSerializer(customers, many=True)
        results = list(customer_serializer.data)
        
        # Also get all BusinessUsers (users) and convert to customer format
        users = BusinessUser.objects.all().order_by('-created_at')
        for user in users:
            results.append({
                'customer_id': f"USER-{user.user_id}",  # Prefix to distinguish from regular customers
                'name': user.business_name,
                'phone': user.phone_number,
                'email': None,  # BusinessUser doesn't have email in the model
                'address': user.business_location,
                'created_at': user.created_at.isoformat() if user.created_at else timezone.now().isoformat(),
                'updated_at': user.updated_at.isoformat() if user.updated_at else timezone.now().isoformat(),
            })
        
        return Response({
            'success': True,
            'data': results
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch customers: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_customers(request):
    """Search customers by name or phone - includes both Customer and BusinessUser"""
    try:
        query = request.GET.get('q', '').strip()
        
        if not query:
            return Response({
                'success': True,
                'data': []
            }, status=status.HTTP_200_OK)
        
        # Search in Customer model
        customers = Customer.objects.filter(
            models.Q(name__icontains=query) | 
            models.Q(phone__icontains=query)
        ).order_by('name')[:10]
        
        customer_serializer = CustomerSearchSerializer(customers, many=True)
        results = list(customer_serializer.data)
        
        # Also search in BusinessUser model (users)
        users = BusinessUser.objects.filter(
            models.Q(business_name__icontains=query) | 
            models.Q(phone_number__icontains=query)
        ).order_by('business_name')[:10]
        
        # Convert BusinessUser to customer-like format
        for user in users:
            results.append({
                'customer_id': f"USER-{user.user_id}",  # Prefix to distinguish from regular customers
                'name': user.business_name,
                'phone': user.phone_number,
            })
        
        # Remove duplicates based on phone number and limit to 10 total
        seen_phones = set()
        unique_results = []
        for item in results:
            phone = item.get('phone', '')
            if phone and phone not in seen_phones:
                seen_phones.add(phone)
                unique_results.append(item)
                if len(unique_results) >= 10:
                    break
        
        return Response({
            'success': True,
            'data': unique_results
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


# Product Batch Management APIs
@api_view(['POST'])
@permission_classes([AllowAny])
def create_product_batch(request, product_id):
    """Create a new product batch"""
    try:
        if not product_id:
            return Response({
                'success': False,
                'message': 'Product ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create batch
        batch = ProductBatch.objects.create(
            product=product,
            batch_number=request.data.get('batch_number'),
            supplier=request.data.get('supplier'),
            cost_price=request.data.get('cost_price'),
            selling_price=request.data.get('selling_price'),
            quantity_received=request.data.get('quantity_received'),
            quantity_remaining=request.data.get('quantity_received'),
            expiry_date=request.data.get('expiry_date'),
            is_active=True
        )
        
        # Update product stock
        product.stock_quantity += batch.quantity_received
        product.save()
        
        return Response({
            'success': True,
            'message': 'Batch created successfully',
            'data': ProductBatchSerializer(batch).data
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to create batch: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_batches(request, product_id):
    """Get all batches for a product"""
    try:
        try:
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        batches = ProductBatch.objects.filter(product=product).order_by('-received_date')
        serializer = ProductBatchSerializer(batches, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch batches: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@permission_classes([AllowAny])
def update_product_batch(request, batch_id):
    """Update a product batch"""
    try:
        try:
            batch = ProductBatch.objects.get(batch_id=batch_id)
        except ProductBatch.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Batch not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if 'batch_number' in request.data:
            batch.batch_number = request.data['batch_number']
        if 'supplier' in request.data:
            batch.supplier = request.data['supplier']
        if 'cost_price' in request.data:
            batch.cost_price = request.data['cost_price']
        if 'selling_price' in request.data:
            batch.selling_price = request.data['selling_price']
        if 'quantity_remaining' in request.data:
            batch.quantity_remaining = request.data['quantity_remaining']
        if 'expiry_date' in request.data:
            batch.expiry_date = request.data['expiry_date']
        if 'is_active' in request.data:
            batch.is_active = request.data['is_active']
        
        batch.save()
        
        return Response({
            'success': True,
            'message': 'Batch updated successfully',
            'data': ProductBatchSerializer(batch).data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to update batch: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_product_batch(request, batch_id):
    """Delete a product batch"""
    try:
        try:
            batch = ProductBatch.objects.get(batch_id=batch_id)
        except ProductBatch.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Batch not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        product = batch.product
        product.stock_quantity -= batch.quantity_remaining
        if product.stock_quantity < 0:
            product.stock_quantity = 0
        product.save()
        
        batch.delete()
        
        return Response({
            'success': True,
            'message': 'Batch deleted successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to delete batch: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Expense Management APIs
@api_view(['GET'])
@permission_classes([AllowAny])
def admin_get_all_expenses(request):
    """Admin: Get all expenses"""
    try:
        expenses = Expense.objects.all().select_related('created_by', 'approved_by').order_by('-created_at')
        serializer = ExpenseSerializer(expenses, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch expenses: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_create_expense(request):
    """Admin: Create a new expense"""
    try:
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            expense = serializer.save()
            return Response({
                'success': True,
                'message': 'Expense created successfully',
                'data': ExpenseSerializer(expense).data
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
            'message': f'Failed to create expense: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])
def admin_update_expense(request, expense_id):
    """Admin: Update an expense"""
    try:
        try:
            expense = Expense.objects.get(expense_id=expense_id)
        except Expense.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Expense not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ExpenseSerializer(expense, data=request.data, partial=True)
        if serializer.is_valid():
            updated_expense = serializer.save()
            return Response({
                'success': True,
                'message': 'Expense updated successfully',
                'data': ExpenseSerializer(updated_expense).data
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
            'message': f'Failed to update expense: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def admin_delete_expense(request, expense_id):
    """Admin: Delete an expense"""
    try:
        try:
            expense = Expense.objects.get(expense_id=expense_id)
        except Expense.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Expense not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        expense.delete()
        return Response({
            'success': True,
            'message': 'Expense deleted successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to delete expense: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@permission_classes([AllowAny])
def admin_update_expense_status(request, expense_id):
    """Admin: Update expense status"""
    try:
        try:
            expense = Expense.objects.get(expense_id=expense_id)
        except Expense.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Expense not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        new_status = request.data.get('status')
        if not new_status:
            return Response({
                'success': False,
                'message': 'status is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if new_status not in ['PENDING', 'APPROVED', 'REJECTED']:
            return Response({
                'success': False,
                'message': 'Invalid status. Valid options: PENDING, APPROVED, REJECTED'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        expense.status = new_status
        
        # Set approved_by if status is being changed to APPROVED or REJECTED
        if new_status in ['APPROVED', 'REJECTED']:
            user_id = request.data.get('approved_by')
            if user_id:
                try:
                    user = BusinessUser.objects.get(user_id=user_id)
                    expense.approved_by = user
                except BusinessUser.DoesNotExist:
                    pass
        
        expense.save()
        
        return Response({
            'success': True,
            'message': f'Expense status updated to {new_status}',
            'data': ExpenseSerializer(expense).data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to update expense status: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Financial Overview API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_financial_overview(request):
    """Get financial overview including cash flow and debts"""
    try:
        from django.utils import timezone
        from datetime import timedelta
        from decimal import Decimal
        
        # Get period filter from query params
        period = request.GET.get('period', 'this_month')
        today = timezone.now().date()
        
        # Calculate date range based on period
        if period == 'today':
            start_date = today
            end_date = today
        elif period == 'this_week':
            start_date = today - timedelta(days=today.weekday())
            end_date = today
        elif period == 'this_month':
            start_date = today.replace(day=1)
            end_date = today
        elif period == 'last_month':
            if today.month == 1:
                start_date = today.replace(year=today.year - 1, month=12, day=1)
            else:
                start_date = today.replace(month=today.month - 1, day=1)
            end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        elif period == 'this_year':
            start_date = today.replace(month=1, day=1)
            end_date = today
        else:
            start_date = None
            end_date = None
        
        # Get income from sales (PAID sales only)
        sales_query = Sale.objects.filter(payment_status='PAID')
        if start_date and end_date:
            sales_query = sales_query.filter(sale_date__date__gte=start_date, sale_date__date__lte=end_date)
        
        total_income = sales_query.aggregate(
            total=models.Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        # Get expenses (APPROVED expenses only)
        expenses_query = Expense.objects.filter(status='APPROVED')
        if start_date and end_date:
            expenses_query = expenses_query.filter(expense_date__gte=start_date, expense_date__lte=end_date)
        
        total_expenses = expenses_query.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        
        net_cash_flow = total_income - total_expenses
        
        # Build transactions list from sales and expenses
        transactions = []
        
        # Add sales as income transactions
        for sale in sales_query.order_by('-sale_date')[:50]:  # Limit to 50 most recent
            transactions.append({
                'id': f"SALE-{sale.sale_id}",
                'type': 'INCOME',
                'description': f"Sale to {sale.customer_name or 'Walk-in Customer'}",
                'amount': float(sale.total_amount),
                'date': sale.sale_date.isoformat(),
                'category': 'Sales',
            })
        
        # Add expenses as expense transactions
        for expense in expenses_query.order_by('-expense_date')[:50]:  # Limit to 50 most recent
            transactions.append({
                'id': f"EXP-{expense.expense_id}",
                'type': 'EXPENSE',
                'description': expense.title,
                'amount': float(expense.amount),
                'date': expense.expense_date.isoformat() + 'T00:00:00Z',
                'category': expense.category,
            })
        
        # Sort transactions by date (most recent first)
        transactions.sort(key=lambda x: x['date'], reverse=True)
        transactions = transactions[:50]  # Limit to 50 most recent overall
        
        # Get debts from orders (unpaid or partially paid orders)
        debts = []
        unpaid_orders = Order.objects.filter(
            models.Q(payment_status__in=['pending', 'unpaid', 'partial']) |
            models.Q(payment_status='pay_on_delivery', status__in=['confirmed', 'processing', 'shipped', 'delivered'])
        ).exclude(status='cancelled')
        
        for order in unpaid_orders:
            # Calculate amount owed
            if order.partial_amount:
                amount_owed = float(order.total_amount - order.partial_amount)
            else:
                amount_owed = float(order.total_amount)
            
            # Determine status
            if order.partial_amount and order.partial_amount > 0:
                debt_status = 'PARTIAL'
            else:
                # Check if overdue (assuming due date is 30 days after order)
                due_date = order.created_at.date() + timedelta(days=30)
                if today > due_date:
                    debt_status = 'OVERDUE'
                else:
                    debt_status = 'PENDING'
            
            debts.append({
                'debt_id': f"DEBT-{order.order_id}",
                'customer_name': order.user.business_name,
                'customer_phone': order.delivery_phone,
                'amount_owed': amount_owed,
                'original_amount': float(order.total_amount),
                'due_date': (order.created_at.date() + timedelta(days=30)).isoformat() + 'T00:00:00Z',
                'status': debt_status,
                'created_date': order.created_at.isoformat(),
            })
        
        return Response({
            'success': True,
            'data': {
                'cash_flow': {
                    'total_income': float(total_income),
                    'total_expenses': float(total_expenses),
                    'net_cash_flow': float(net_cash_flow),
                    'transactions': transactions,
                },
                'debts': debts,
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch financial overview: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Reports & Analytics API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_reports_analytics(request):
    """Get reports and analytics data including sales, products, and employee performance"""
    try:
        from django.utils import timezone
        from datetime import timedelta
        from decimal import Decimal
        
        # Get date range from query params
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        
        if start_date_str and end_date_str:
            try:
                start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Default to last 30 days
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
        
        # Get sales data
        sales_query = Sale.objects.filter(
            sale_date__date__gte=start_date,
            sale_date__date__lte=end_date
        ).select_related('customer', 'salesperson').prefetch_related('items__product')
        
        sales_data = []
        for sale in sales_query:
            items = []
            for item in sale.items.all():
                items.append({
                    'product_id': item.product.product_id if item.product else '',
                    'product_name': item.product_name,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'total': float(item.total_price),
                })
            
            sales_data.append({
                'id': sale.sale_id,
                'date': sale.sale_date.date().isoformat(),
                'customer_name': sale.customer_name or (sale.customer.name if sale.customer else 'Walk-in Customer'),
                'customer_phone': sale.customer_phone or (sale.customer.phone if sale.customer else ''),
                'items': items,
                'total_amount': float(sale.total_amount),
                'payment_method': sale.payment_method,
                'payment_status': sale.payment_status,
                'employee': sale.salesperson_name or (sale.salesperson.business_name if sale.salesperson else 'Unknown'),
            })
        
        # Get product performance data
        products_data = []
        product_sales_map = {}
        
        # Aggregate sales by product
        for sale in sales_query:
            for item in sale.items.all():
                product_id = item.product.product_id if item.product else None
                if not product_id:
                    continue
                
                if product_id not in product_sales_map:
                    product = item.product
                    product_sales_map[product_id] = {
                        'id': product_id,
                        'name': product.name,
                        'category': product.category.name if product.category else 'Uncategorized',
                        'stock': product.stock_quantity,
                        'price': float(product.price),
                        'cost': 0,  # Cost not available in model, default to 0
                        'sales_count': 0,
                        'revenue': 0,
                    }
                
                product_sales_map[product_id]['sales_count'] += item.quantity
                product_sales_map[product_id]['revenue'] += float(item.total_price)
        
        products_data = list(product_sales_map.values())
        products_data.sort(key=lambda x: x['revenue'], reverse=True)
        
        # Get employee performance data
        employee_map = {}
        
        for sale in sales_query:
            employee_name = sale.salesperson_name or (sale.salesperson.business_name if sale.salesperson else 'Unknown')
            
            if employee_name not in employee_map:
                employee_map[employee_name] = {
                    'name': employee_name,
                    'sales_count': 0,
                    'total_revenue': 0,
                    'avg_sale_value': 0,
                }
            
            employee_map[employee_name]['sales_count'] += 1
            employee_map[employee_name]['total_revenue'] += float(sale.total_amount)
        
        # Calculate averages
        for emp in employee_map.values():
            if emp['sales_count'] > 0:
                emp['avg_sale_value'] = emp['total_revenue'] / emp['sales_count']
        
        employees_data = list(employee_map.values())
        employees_data.sort(key=lambda x: x['total_revenue'], reverse=True)
        
        return Response({
            'success': True,
            'data': {
                'sales': sales_data,
                'products': products_data,
                'employees': employees_data,
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch reports data: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Invoice Management Views
@api_view(['POST'])
@permission_classes([AllowAny])
def create_invoice_from_order(request, order_id):
    """Create an invoice from an order"""
    try:
        # Get order
        try:
            order = Order.objects.select_related('user').prefetch_related('order_items__product').get(order_id=order_id)
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if invoice already exists for this order
        if hasattr(order, 'invoice'):
            return Response({
                'success': False,
                'message': 'Invoice already exists for this order',
                'invoice_id': order.invoice.invoice_id
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate request data
        serializer = CreateInvoiceFromOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get invoice date (default to today)
        invoice_date = serializer.validated_data.get('invoice_date', date.today())
        due_date = serializer.validated_data.get('due_date')
        
        # Calculate due date if not provided (default to 30 days from invoice date)
        if not due_date:
            due_date = invoice_date + timedelta(days=30)
        
        # Create invoice
        invoice = Invoice.objects.create(
            order=order,
            invoice_date=invoice_date,
            due_date=due_date,
            customer_name=order.user.business_name,
            customer_phone=order.user.phone_number,
            customer_address=order.delivery_address,
            customer_tin=order.user.tin_number,
            subtotal=order.subtotal,
            tax_amount=order.tax_amount,
            shipping_amount=order.shipping_amount,
            total_amount=order.total_amount,
            payment_method=order.payment_method,
            payment_status=order.payment_status,
            notes=serializer.validated_data.get('notes', ''),
            terms_and_conditions=serializer.validated_data.get('terms_and_conditions', ''),
            status='draft'
        )
        
        # Generate invoice number
        invoice.generate_invoice_number()
        
        # Create invoice items from order items
        for order_item in order.order_items.all():
            InvoiceItem.objects.create(
                invoice=invoice,
                product=order_item.product,
                product_name=order_item.product_name,
                product_description=order_item.product_description,
                product_image=order_item.product_image,
                category=order_item.category,
                quantity=order_item.quantity,
                unit_price=order_item.unit_price,
                total_price=order_item.total_price,
                pack_type=order_item.pack_type
            )
        
        # Serialize and return
        invoice_serializer = InvoiceSerializer(invoice)
        
        return Response({
            'success': True,
            'message': 'Invoice created successfully from order',
            'data': invoice_serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to create invoice: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_invoices(request):
    """Get all invoices"""
    try:
        invoices = Invoice.objects.select_related('order', 'order__user').prefetch_related('invoice_items__product').all()
        invoices_serializer = InvoiceSerializer(invoices, many=True)
        
        return Response({
            'success': True,
            'data': invoices_serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch invoices: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_invoice_details(request, invoice_id):
    """Get invoice details"""
    try:
        try:
            invoice = Invoice.objects.select_related('order', 'order__user').prefetch_related('invoice_items__product').get(invoice_id=invoice_id)
        except Invoice.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invoice not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        invoice_serializer = InvoiceSerializer(invoice)
        
        return Response({
            'success': True,
            'data': invoice_serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch invoice details: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@permission_classes([AllowAny])
def update_invoice(request, invoice_id):
    """Update an invoice"""
    try:
        try:
            invoice = Invoice.objects.get(invoice_id=invoice_id)
        except Invoice.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invoice not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if invoice can be edited
        if invoice.status in ['paid', 'cancelled']:
            return Response({
                'success': False,
                'message': f'Cannot edit invoice with status: {invoice.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update invoice
        serializer = UpdateInvoiceSerializer(invoice, data=request.data, partial=True)
        if serializer.is_valid():
            updated_invoice = serializer.save()
            
            # Recalculate totals
            updated_invoice.calculate_totals()
            
            # Update the related order if it exists
            if updated_invoice.order:
                order = updated_invoice.order
                
                # Update order delivery information from invoice customer info
                order.delivery_address = updated_invoice.customer_address
                order.delivery_phone = updated_invoice.customer_phone
                
                # Update order payment information
                if updated_invoice.payment_method:
                    order.payment_method = updated_invoice.payment_method
                if updated_invoice.payment_status:
                    order.payment_status = updated_invoice.payment_status
                
                # Update order items to match invoice items
                # First, delete existing order items
                order.order_items.all().delete()
                
                # Create new order items from invoice items
                for invoice_item in updated_invoice.invoice_items.all():
                    # Get the product if it exists
                    product = invoice_item.product
                    
                    # OrderItem requires a product, so if invoice item doesn't have one,
                    # we need to find a product by name or create a dummy one
                    # For now, we'll try to find by name, or use the first product as fallback
                    if not product and invoice_item.product_name:
                        try:
                            # Try to find product by name
                            product = Product.objects.filter(name__icontains=invoice_item.product_name).first()
                        except:
                            pass
                    
                    # If still no product, we can't create OrderItem without it
                    # So we'll skip items without products or use a default
                    if not product:
                        # Skip items without products - they can't be added to orders
                        continue
                    
                    # Create order item
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=invoice_item.product_name,
                        product_description=invoice_item.product_description or '',
                        product_image=invoice_item.product_image or '',
                        category=invoice_item.category or '',
                        quantity=invoice_item.quantity,
                        unit_price=invoice_item.unit_price,
                        total_price=invoice_item.total_price,
                        pack_type=invoice_item.pack_type
                    )
                
                # Update order totals to match invoice totals
                order.subtotal = updated_invoice.subtotal
                order.tax_amount = updated_invoice.tax_amount
                order.shipping_amount = updated_invoice.shipping_amount
                order.total_amount = updated_invoice.total_amount
                
                # Save the order
                order.save()
            
            invoice_serializer = InvoiceSerializer(updated_invoice)
            
            return Response({
                'success': True,
                'message': 'Invoice and related order updated successfully',
                'data': invoice_serializer.data
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
            'message': f'Failed to update invoice: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_invoice(request, invoice_id):
    """Delete an invoice"""
    try:
        try:
            invoice = Invoice.objects.get(invoice_id=invoice_id)
        except Invoice.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invoice not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if invoice can be deleted
        if invoice.status in ['paid', 'sent']:
            return Response({
                'success': False,
                'message': f'Cannot delete invoice with status: {invoice.status}. Only draft or cancelled invoices can be deleted.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        invoice_id_str = invoice.invoice_id
        invoice_number = invoice.invoice_number
        
        # Delete invoice (cascade will delete invoice items)
        invoice.delete()
        
        return Response({
            'success': True,
            'message': 'Invoice deleted successfully',
            'deleted_invoice': {
                'invoice_id': invoice_id_str,
                'invoice_number': invoice_number
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to delete invoice: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
