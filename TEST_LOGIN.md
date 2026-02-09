# 🧪 Testing User Login

## Quick Test Methods

### Method 1: Simple Python Script (Recommended)

```bash
cd kipenzi_backend
python test_login_simple.py +255712345678 sales@123
```

Or with different phone formats:
```bash
python test_login_simple.py 0616107670 manager@123
python test_login_simple.py 255616107670 manager@123
```

### Method 2: Interactive Test Script

```bash
cd kipenzi_backend
python test_user_login.py
```

This will:
1. List all users in database
2. Ask for phone and password
3. Test database lookup
4. Test API login with different phone formats

### Method 3: Using cURL

```bash
curl -X POST https://geoclimatz.pythonanywhere.com/v1/hardware/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+255712345678",
    "password": "sales@123"
  }'
```

### Method 4: Using Python Requests

```python
import requests

response = requests.post(
    'https://geoclimatz.pythonanywhere.com/v1/hardware/login/',
    json={
        'phone_number': '+255712345678',
        'password': 'sales@123'
    }
)

print(response.json())
```

## Expected Responses

### ✅ Success (OTP Required)
```json
{
  "success": true,
  "message": "OTP sent to your phone number. Please verify to complete login.",
  "needs_otp": true,
  "phone_number": "+255712345678"
}
```

### ✅ Success (OTP Disabled)
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {...},
    "token": "..."
  }
}
```

### ❌ Failure
```json
{
  "success": false,
  "message": "Invalid phone number or password"
}
```

## Common Issues

### 1. "Invalid phone number or password"
- **Cause**: Phone number format mismatch or wrong password
- **Fix**: 
  - Check phone number format in database
  - Run `python fix_user_phone_numbers.py` to normalize
  - Verify password is correct

### 2. "User not found"
- **Cause**: Phone number doesn't exist in database
- **Fix**: Check if user was created properly

### 3. "Please verify your phone number first"
- **Cause**: User exists but `is_verified=False`
- **Fix**: This should no longer block login (after recent fixes)

## Testing OTP Verification

After successful login (OTP sent), test OTP verification:

```bash
curl -X POST https://geoclimatz.pythonanywhere.com/v1/hardware/login-verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+255712345678",
    "otp": "1234"
  }'
```

## Test Accounts

Common test accounts (if created):
- Phone: `+255712345678`, Password: `sales@123`
- Phone: `+255616107670`, Password: `manager@123`
- Phone: `+255987654321`, Password: `marketing@123`

## Debugging

Enable DEBUG mode in settings to see detailed error messages:
```python
DEBUG = True
```

Check server logs for:
- Phone number normalization
- Password verification
- User lookup attempts
