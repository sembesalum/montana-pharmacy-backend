# OTP Implementation Package

A complete, ready-to-use OTP (One-Time Password) implementation for Django backends.

## 📦 What's Included

This package contains everything needed to implement OTP functionality:

1. **`utils/otp_handler.py`** - Core OTP utility functions
2. **`users/views/otp_views_example.py`** - Example API views/endpoints
3. **`users/models_otp_example.py`** - Example database models
4. **`OTP_IMPLEMENTATION.md`** - Complete documentation
5. **`OTP_QUICK_START.md`** - Quick setup guide

## 🚀 Quick Start

1. **Update SMS credentials** in `utils/otp_handler.py`:
   ```python
   SMS_USERNAME = 'YOUR_USERNAME'
   SMS_PASSWORD = 'YOUR_PASSWORD'
   SMS_SENDER = 'YourApp'
   ```

2. **Add/Update Verification model** (see `users/models_otp_example.py`)

3. **Copy API views** from `users/views/otp_views_example.py` to your views

4. **Add URLs** to your `urls.py`:
   ```python
   path('send-otp/', send_otp),
   path('verify-otp/', verify_otp_code),
   ```

5. **Test it!**

For detailed instructions, see **`OTP_QUICK_START.md`**

## 📚 Documentation

- **Quick Start**: `OTP_QUICK_START.md` - Get started in 5 minutes
- **Full Guide**: `OTP_IMPLEMENTATION.md` - Complete documentation with all features

## 🔑 Key Features

- ✅ Generate random 4-digit OTP codes
- ✅ Send OTP via SMS (mShastra API)
- ✅ Store OTPs in database with expiration
- ✅ Verify OTP codes
- ✅ Rate limiting support
- ✅ Automatic expiration (5 minutes)
- ✅ One-time use (can't reuse verified OTP)

## 📱 API Endpoints

### Send OTP
```
POST /api/users/send-otp/
Body: {"phone": "255694230173", "verification_type": "Login"}
```

### Verify OTP
```
POST /api/users/verify-otp/
Body: {"phone": "255694230173", "otp": "1234", "verification_type": "Login"}
```

## 🛠️ Customization

All configuration options are in `utils/otp_handler.py`:
- OTP length (default: 4 digits)
- Expiration time (default: 5 minutes)
- SMS message template
- API credentials

## 📋 Requirements

- Django 4.1.1+
- Django REST Framework
- requests library
- MySQL/PostgreSQL database

## 🔧 Integration Steps

1. **Copy files** to your project
2. **Update credentials** in `otp_handler.py`
3. **Run migrations** for Verification model
4. **Add views** to your views.py
5. **Add URLs** to your urls.py
6. **Test endpoints**

## 📝 File Structure

```
your-project/
├── utils/
│   └── otp_handler.py          # Core OTP functions
├── users/
│   ├── models.py                # Add Verification model here
│   ├── views/
│   │   └── otp_views_example.py # Example API views
│   └── urls.py                  # Add OTP endpoints
├── OTP_IMPLEMENTATION.md        # Full documentation
├── OTP_QUICK_START.md          # Quick setup guide
└── OTP_README.md               # This file
```

## 🎯 Usage Example

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

## ⚠️ Important Notes

1. **SMS Credentials**: Update `SMS_USERNAME`, `SMS_PASSWORD`, and `SMS_SENDER` in `otp_handler.py`
2. **Model Structure**: The handler works with your existing Verification model structure
3. **Phone Format**: Use international format (e.g., "255694230173" for Tanzania)
4. **Rate Limiting**: Consider implementing rate limiting in production
5. **Security**: Always use HTTPS in production

## 🐛 Troubleshooting

See `OTP_IMPLEMENTATION.md` section 11 for common issues and solutions.

## 📞 Support

For questions or issues:
1. Check `OTP_IMPLEMENTATION.md` for detailed documentation
2. Review `OTP_QUICK_START.md` for setup issues
3. Check Django and DRF documentation

## 📄 License

This implementation is provided as-is for integration purposes.

---

**Ready to use!** Just update the credentials and you're good to go! 🚀

