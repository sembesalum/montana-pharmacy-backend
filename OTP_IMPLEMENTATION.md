# OTP Implementation Guide

This document provides a complete OTP (One-Time Password) implementation that can be integrated into any Django backend project.

## Overview

The OTP implementation consists of:
1. **OTP Utility Module** - Handles OTP generation and SMS sending
2. **Verification Model** - Stores OTP codes in the database
3. **API Endpoints** - For sending and verifying OTP codes

## Features

- ✅ Generate random 4-digit OTP codes
- ✅ Send OTP via SMS using mShastra API
- ✅ Store OTP codes with expiration tracking
- ✅ Verify OTP codes with phone number validation
- ✅ Support for multiple verification types (Login, Registration, etc.)
- ✅ Automatic OTP expiration (5 minutes default)

---

## 1. Installation & Dependencies

Add these to your `requirements.txt`:

```txt
Django==4.1.1
djangorestframework==3.13.1
requests==2.27.1
```

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 2. Database Models

### Verification Model

Create a `Verification` model in your `users/models.py` (or appropriate app):

```python
from django.db import models
from django.utils import timezone
from datetime import timedelta

class Verification(models.Model):
    verification_id = models.CharField(max_length=50, primary_key=True)
    phone = models.CharField(max_length=15, blank=False, null=False)
    code = models.IntegerField(default=0, blank=False, null=False)
    verification_type = models.CharField(max_length=20, default="Login")
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True)
    
    # Optional: Link to your User/Agent model if needed
    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    
    verification = models.Manager()
    
    class Meta:
        db_table = "verification"
        indexes = [
            models.Index(fields=['phone', 'code']),
            models.Index(fields=['phone', 'verified']),
        ]
    
    def is_expired(self):
        """Check if OTP has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def save(self, *args, **kwargs):
        """Auto-set expiration time (5 minutes) when creating"""
        if not self.expires_at and not self.pk:
            self.expires_at = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)
```

**Migration:**
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 3. OTP Utility Module

Create `utils/otp_handler.py`:

```python
import requests
import json
import random
import uuid
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

# SMS API Configuration
SMS_API_URL = "https://mshastra.com/sendsms_api_json.aspx"
SMS_USERNAME = "YOUR_SMS_USERNAME"  # Replace with your credentials
SMS_PASSWORD = "YOUR_SMS_PASSWORD"  # Replace with your credentials
SMS_SENDER = "YourApp"  # Replace with your sender name

# OTP Configuration
OTP_LENGTH = 4
OTP_MIN = 1000
OTP_MAX = 9999
OTP_EXPIRY_MINUTES = 5


def generate_otp():
    """
    Generate a random OTP code
    
    Returns:
        int: Random 4-digit OTP code (1000-9999)
    """
    return random.randint(OTP_MIN, OTP_MAX)


def send_otp_sms(phone_number, otp_code, message_template=None):
    """
    Send OTP code via SMS using mShastra API
    
    Args:
        phone_number (str): Recipient phone number (with country code, e.g., "255694230173")
        otp_code (int): The OTP code to send
        message_template (str, optional): Custom message template. 
                                         Use {code} as placeholder for OTP.
    
    Returns:
        dict: API response with status and message
    """
    if message_template is None:
        message = f"Welcome To Your App!\nThank you for using our service.\nYour OTP is {otp_code}"
    else:
        message = message_template.format(code=otp_code)
    
    payload = json.dumps([{
        "user": SMS_USERNAME,
        "pwd": SMS_PASSWORD,
        "number": phone_number,
        "sender": SMS_SENDER,
        "msg": message,
        "language": "Unicode"
    }])
    
    headers = {
        'Content-Type': 'application/json',
        "accept": "application/json",
    }
    
    try:
        response = requests.post(SMS_API_URL, headers=headers, data=payload, timeout=10)
        json_response = response.json()
        return {
            "success": True,
            "response": json_response,
            "message": "OTP sent successfully"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to send OTP"
        }


def create_verification_record(phone, code, verification_type="Login", user=None):
    """
    Create a verification record in the database
    
    Args:
        phone (str): Phone number
        code (int): OTP code
        verification_type (str): Type of verification (Login, Registration, etc.)
        user: Optional user/agent object to link
    
    Returns:
        Verification: Created verification object
    """
    from users.models import Verification  # Adjust import path as needed
    
    verification = Verification()
    verification.verification_id = uuid.uuid4().hex
    verification.phone = phone
    verification.code = code
    verification.verification_type = verification_type
    verification.verified = False
    verification.expires_at = timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    
    if user:
        verification.user = user
    
    verification.save()
    return verification


def verify_otp(phone, code, verification_type="Login"):
    """
    Verify an OTP code
    
    Args:
        phone (str): Phone number
        code (int): OTP code to verify
        verification_type (str): Type of verification
    
    Returns:
        dict: Verification result with status and message
    """
    from users.models import Verification  # Adjust import path as needed
    
    try:
        # Find unverified OTP for this phone number
        verification = Verification.verification.filter(
            phone=phone,
            code=code,
            verification_type=verification_type,
            verified=False
        ).order_by('-created_at').first()
        
        if not verification:
            return {
                "success": False,
                "message": "Invalid OTP code"
            }
        
        # Check if expired
        if verification.is_expired():
            return {
                "success": False,
                "message": "OTP code has expired. Please request a new one."
            }
        
        # Mark as verified
        verification.verified = True
        verification.save()
        
        return {
            "success": True,
            "message": "OTP verified successfully",
            "verification": verification
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error verifying OTP: {str(e)}"
        }


def send_and_save_otp(phone, verification_type="Login", user=None):
    """
    Generate, send, and save OTP in one function
    
    Args:
        phone (str): Phone number
        verification_type (str): Type of verification
        user: Optional user object
    
    Returns:
        dict: Result with success status and message
    """
    # Generate OTP
    otp_code = generate_otp()
    
    # Send SMS
    sms_result = send_otp_sms(phone, otp_code)
    
    if not sms_result["success"]:
        return {
            "success": False,
            "message": "Failed to send OTP. Please try again."
        }
    
    # Save to database
    try:
        verification = create_verification_record(phone, otp_code, verification_type, user)
        return {
            "success": True,
            "message": "OTP sent successfully",
            "verification_id": verification.verification_id
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error saving OTP: {str(e)}"
        }
```

---

## 4. API Views/Endpoints

Create or update `users/views/otp_views.py`:

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from utils.otp_handler import send_and_save_otp, verify_otp
import re


@api_view(['POST'])
def send_otp(request):
    """
    Send OTP to phone number
    
    Request Body:
        {
            "phone": "255694230173",
            "verification_type": "Login"  // Optional, defaults to "Login"
        }
    
    Response:
        {
            "message": "OTP sent successfully",
            "status": "success"
        }
    """
    try:
        data = request.data
        phone = data.get('phone', '').strip()
        verification_type = data.get('verification_type', 'Login')
        
        # Validate phone number
        if not phone:
            return Response(
                {"message": "Phone number is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Basic phone validation (adjust regex as needed)
        if not re.match(r'^\+?[1-9]\d{9,14}$', phone.replace(' ', '')):
            return Response(
                {"message": "Invalid phone number format"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Optional: Check if user exists (adjust based on your User model)
        # from users.models import User
        # user = None
        # if User.objects.filter(phone=phone).exists():
        #     user = User.objects.get(phone=phone)
        
        # Send OTP
        result = send_and_save_otp(phone, verification_type, user=None)
        
        if result["success"]:
            return Response(
                {"message": result["message"], "status": "success"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": result["message"], "status": "error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    except Exception as e:
        return Response(
            {"message": f"Error sending OTP: {str(e)}", "status": "error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def verify_otp_code(request):
    """
    Verify OTP code
    
    Request Body:
        {
            "phone": "255694230173",
            "otp": "1234",
            "verification_type": "Login"  // Optional, defaults to "Login"
        }
    
    Response (Success):
        {
            "message": "OTP verified successfully",
            "status": "success",
            "verified": true
        }
    
    Response (Error):
        {
            "message": "Invalid OTP code",
            "status": "error",
            "verified": false
        }
    """
    try:
        data = request.data
        phone = data.get('phone', '').strip()
        otp = data.get('otp', '').strip()
        verification_type = data.get('verification_type', 'Login')
        
        # Validate inputs
        if not phone:
            return Response(
                {"message": "Phone number is required", "status": "error", "verified": False},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not otp:
            return Response(
                {"message": "OTP code is required", "status": "error", "verified": False},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate OTP format (should be numeric)
        if not otp.isdigit():
            return Response(
                {"message": "OTP must be numeric", "status": "error", "verified": False},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify OTP
        result = verify_otp(phone, int(otp), verification_type)
        
        if result["success"]:
            return Response(
                {
                    "message": result["message"],
                    "status": "success",
                    "verified": True
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "message": result["message"],
                    "status": "error",
                    "verified": False
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except Exception as e:
        return Response(
            {
                "message": f"Error verifying OTP: {str(e)}",
                "status": "error",
                "verified": False
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
```

---

## 5. URL Configuration

Add to your `users/urls.py`:

```python
from django.urls import path
from users.views.otp_views import send_otp, verify_otp_code

urlpatterns = [
    path('send-otp/', send_otp, name='send_otp'),
    path('verify-otp/', verify_otp_code, name='verify_otp'),
]
```

---

## 6. Configuration

### Update SMS Credentials

Edit `utils/otp_handler.py` and replace:
- `SMS_USERNAME` - Your mShastra username
- `SMS_PASSWORD` - Your mShastra password
- `SMS_SENDER` - Your sender name (must be approved by mShastra)

### Optional: Environment Variables

For better security, use environment variables:

```python
import os
from django.conf import settings

SMS_USERNAME = os.getenv('SMS_USERNAME', 'YOUR_DEFAULT_USERNAME')
SMS_PASSWORD = os.getenv('SMS_PASSWORD', 'YOUR_DEFAULT_PASSWORD')
SMS_SENDER = os.getenv('SMS_SENDER', 'YourApp')
```

---

## 7. Usage Examples

### Frontend/Client Integration

#### Send OTP:
```javascript
// JavaScript/React Example
const sendOTP = async (phoneNumber) => {
  try {
    const response = await fetch('https://your-api.com/api/users/send-otp/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        phone: phoneNumber,
        verification_type: 'Login'
      })
    });
    
    const data = await response.json();
    console.log(data.message);
  } catch (error) {
    console.error('Error:', error);
  }
};
```

#### Verify OTP:
```javascript
const verifyOTP = async (phoneNumber, otpCode) => {
  try {
    const response = await fetch('https://your-api.com/api/users/verify-otp/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        phone: phoneNumber,
        otp: otpCode,
        verification_type: 'Login'
      })
    });
    
    const data = await response.json();
    if (data.verified) {
      console.log('OTP verified successfully!');
      // Proceed with login/registration
    } else {
      console.error(data.message);
    }
  } catch (error) {
    console.error('Error:', error);
  }
};
```

### Python/Backend Usage:

```python
from utils.otp_handler import send_and_save_otp, verify_otp

# Send OTP
result = send_and_save_otp("255694230173", "Login")
if result["success"]:
    print("OTP sent!")

# Verify OTP
result = verify_otp("255694230173", 1234, "Login")
if result["success"]:
    print("OTP verified!")
```

---

## 8. Testing

### Test OTP Sending:
```bash
curl -X POST http://localhost:8000/api/users/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "255694230173", "verification_type": "Login"}'
```

### Test OTP Verification:
```bash
curl -X POST http://localhost:8000/api/users/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "255694230173", "otp": "1234", "verification_type": "Login"}'
```

---

## 9. Security Considerations

1. **Rate Limiting**: Implement rate limiting to prevent OTP spam
2. **OTP Expiration**: OTPs expire after 5 minutes (configurable)
3. **One-Time Use**: Once verified, OTP cannot be reused
4. **Phone Validation**: Validate phone number format before sending
5. **Error Messages**: Don't reveal if phone number exists in system
6. **HTTPS**: Always use HTTPS in production

### Rate Limiting Example:

```python
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def send_otp_with_rate_limit(request):
    phone = request.data.get('phone')
    cache_key = f'otp_rate_limit_{phone}'
    
    # Check rate limit (max 3 requests per 10 minutes)
    attempts = cache.get(cache_key, 0)
    if attempts >= 3:
        return Response(
            {"message": "Too many OTP requests. Please try again later."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    # Increment counter
    cache.set(cache_key, attempts + 1, 600)  # 10 minutes
    
    # Send OTP...
    # ... rest of your code
```

---

## 10. Customization Options

### Change OTP Length:
```python
# In utils/otp_handler.py
OTP_LENGTH = 6
OTP_MIN = 100000
OTP_MAX = 999999
```

### Change Expiration Time:
```python
# In utils/otp_handler.py
OTP_EXPIRY_MINUTES = 10  # 10 minutes instead of 5
```

### Custom SMS Template:
```python
custom_message = "Your verification code is {code}. Valid for 5 minutes."
send_otp_sms(phone, otp_code, custom_message)
```

---

## 11. Troubleshooting

### OTP Not Received:
1. Check SMS API credentials
2. Verify phone number format (include country code)
3. Check SMS API account balance
4. Verify sender name is approved

### OTP Expired Immediately:
1. Check server timezone settings
2. Verify `USE_TZ = True` in settings.py
3. Check database timezone

### Database Errors:
1. Run migrations: `python manage.py migrate`
2. Check model field types match
3. Verify foreign key relationships if using user linking

---

## 12. Support

For issues or questions:
- Check Django REST Framework documentation
- Verify SMS API (mShastra) documentation
- Review Django models and migrations

---

## License

This implementation is provided as-is for integration purposes.

