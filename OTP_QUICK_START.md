# OTP Implementation - Quick Start Guide

This is a quick reference guide for integrating the OTP system into your Django backend.

## 📋 Prerequisites

- Django 4.1.1+
- Django REST Framework
- Python 3.8+
- MySQL/PostgreSQL database

## 🚀 Quick Setup (5 Steps)

### Step 1: Copy the OTP Handler

The `utils/otp_handler.py` file is already created. Just update the SMS credentials:

```python
# In utils/otp_handler.py, update these:
SMS_USERNAME = 'YOUR_SMS_USERNAME'
SMS_PASSWORD = 'YOUR_SMS_PASSWORD'
SMS_SENDER = 'YourAppName'
```

### Step 2: Create/Update Verification Model

If you don't have a Verification model, add this to your `users/models.py`:

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
    
    verification = models.Manager()
    
    class Meta:
        db_table = "verification"
        indexes = [
            models.Index(fields=['phone', 'code']),
        ]
    
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def save(self, *args, **kwargs):
        if not self.expires_at and not self.pk:
            self.expires_at = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)
```

Then run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Add API Views

Copy the views from `users/views/otp_views_example.py` to your `users/views.py` or import them:

```python
# In users/views/__init__.py or views.py
from .otp_views_example import send_otp, verify_otp_code, resend_otp
```

Or add directly to your `users/views.py`:

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from utils.otp_handler import send_and_save_otp, verify_otp
import re

@api_view(['POST'])
def send_otp(request):
    phone = request.data.get('phone', '').strip()
    verification_type = request.data.get('verification_type', 'Login')
    
    if not phone:
        return Response({"message": "Phone required"}, status=400)
    
    result = send_and_save_otp(phone, verification_type)
    
    if result["success"]:
        return Response({"message": result["message"]}, status=200)
    return Response({"message": result["message"]}, status=500)

@api_view(['POST'])
def verify_otp_code(request):
    phone = request.data.get('phone', '').strip()
    otp = request.data.get('otp', '').strip()
    verification_type = request.data.get('verification_type', 'Login')
    
    if not phone or not otp:
        return Response({"message": "Phone and OTP required"}, status=400)
    
    result = verify_otp(phone, int(otp), verification_type)
    
    if result["success"]:
        return Response({"message": result["message"], "verified": True}, status=200)
    return Response({"message": result["message"], "verified": False}, status=400)
```

### Step 4: Add URLs

Add to your `users/urls.py`:

```python
from django.urls import path
from users.views import send_otp, verify_otp_code

urlpatterns = [
    path('send-otp/', send_otp, name='send_otp'),
    path('verify-otp/', verify_otp_code, name='verify_otp'),
]
```

### Step 5: Test It!

```bash
# Send OTP
curl -X POST http://localhost:8000/api/users/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "255694230173"}'

# Verify OTP (use the code you received)
curl -X POST http://localhost:8000/api/users/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "255694230173", "otp": "1234"}'
```

## 📱 Frontend Integration

### JavaScript/React Example

```javascript
// Send OTP
const sendOTP = async (phone) => {
  const response = await fetch('/api/users/send-otp/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone, verification_type: 'Login' })
  });
  const data = await response.json();
  return data;
};

// Verify OTP
const verifyOTP = async (phone, otp) => {
  const response = await fetch('/api/users/verify-otp/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone, otp, verification_type: 'Login' })
  });
  const data = await response.json();
  return data;
};
```

## 🔧 Configuration Options

### Change OTP Expiry Time

In `utils/otp_handler.py`:
```python
OTP_EXPIRY_MINUTES = 10  # Change from 5 to 10 minutes
```

### Change OTP Length

In `utils/otp_handler.py`:
```python
OTP_LENGTH = 6
OTP_MIN = 100000
OTP_MAX = 999999
```

### Custom SMS Message

```python
custom_msg = "Your code is {code}. Valid for 5 min."
send_otp_sms(phone, otp_code, custom_msg)
```

## 🛡️ Security Features

- ✅ OTP expires after 5 minutes
- ✅ One-time use (can't reuse verified OTP)
- ✅ Rate limiting (3 requests per 10 minutes)
- ✅ Phone number validation

## 📝 API Endpoints

### POST `/api/users/send-otp/`
**Request:**
```json
{
  "phone": "255694230173",
  "verification_type": "Login"
}
```

**Response:**
```json
{
  "message": "OTP sent successfully",
  "status": "success"
}
```

### POST `/api/users/verify-otp/`
**Request:**
```json
{
  "phone": "255694230173",
  "otp": "1234",
  "verification_type": "Login"
}
```

**Response:**
```json
{
  "message": "OTP verified successfully",
  "status": "success",
  "verified": true
}
```

## ❓ Common Issues

**OTP not received?**
- Check SMS API credentials
- Verify phone number format (include country code)
- Check SMS account balance

**OTP expired immediately?**
- Check server timezone: `USE_TZ = True` in settings.py
- Verify database timezone matches server

**Database errors?**
- Run migrations: `python manage.py migrate`
- Check model field types

## 📚 Full Documentation

See `OTP_IMPLEMENTATION.md` for complete documentation with advanced features.

## 🎯 Next Steps

1. Update SMS credentials in `utils/otp_handler.py`
2. Run migrations
3. Test with curl or Postman
4. Integrate with your frontend
5. Add rate limiting if needed
6. Set up cleanup cron job for expired OTPs

---

**That's it!** Your OTP system is ready to use. 🎉

