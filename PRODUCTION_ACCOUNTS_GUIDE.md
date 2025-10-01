# 🚀 Production Test Accounts Creation Guide

## 📋 **Overview**
This guide explains how to create test accounts in the production database for the pharmacy admin dashboard.

## 🎯 **Test Accounts to Create**

| Role | Phone | Password | Business Name | Status |
|------|-------|----------|---------------|--------|
| SALES | +255712345678 | sales@123 | Demo Sales Pharmacy | ✅ Verified |
| MARKETING | +255987654321 | marketing@123 | Demo Marketing Pharmacy | ✅ Verified |
| RECEIVER | +255555123456 | receiver@123 | Demo Receiver Pharmacy | ✅ Verified |
| MANAGER | +255444987654 | manager@123 | Demo Manager Pharmacy | ✅ Verified |
| ACCOUNTANT | +255333456789 | accountant@123 | Demo Accountant Pharmacy | ✅ Verified |
| UNVERIFIED | +255222111000 | unverified@123 | Unverified Test Pharmacy | ⏳ Pending |

## 🔧 **Method 1: Using Python Scripts (Recommended)**

### **Step 1: Prepare the Scripts**
The following scripts are already created:
- `create_prod_accounts.py` - Main script using production settings
- `settings_production.py` - Production database configuration
- `run_prod_accounts.py` - Simple runner script

### **Step 2: Run on Production Server**
```bash
# SSH into your production server
ssh your-username@geoclimatz.pythonanywhere.com

# Navigate to your project directory
cd /home/geoclimatz/your-project-directory/kipenzi_backend

# Make scripts executable
chmod +x create_prod_accounts.py
chmod +x run_prod_accounts.py

# Run the account creation script
python3 create_prod_accounts.py
```

### **Step 3: Verify Creation**
The script will output:
- ✅ Created/Updated user confirmations
- 📋 Complete credentials list
- 📊 Database statistics

## 🔧 **Method 2: Using Django Shell**

### **Step 1: Access Django Shell on Production**
```bash
# On production server
cd /home/geoclimatz/your-project-directory/kipenzi_backend
python3 manage.py shell
```

### **Step 2: Run Account Creation Code**
```python
from hardware_backend.models import BusinessUser
from django.contrib.auth.hashers import make_password
import uuid

# Test accounts data
test_accounts = [
    {
        'phone_number': '+255712345678',
        'password': 'sales@123',
        'business_name': 'Demo Sales Pharmacy',
        'business_location': 'Dar es Salaam, Tanzania',
        'business_type': 'pharmacist',
        'tin_number': '123456789',
        'is_verified': True,
    },
    {
        'phone_number': '+255987654321',
        'password': 'marketing@123',
        'business_name': 'Demo Marketing Pharmacy',
        'business_location': 'Arusha, Tanzania',
        'business_type': 'marketing',
        'tin_number': '987654321',
        'is_verified': True,
    },
    {
        'phone_number': '+255555123456',
        'password': 'receiver@123',
        'business_name': 'Demo Receiver Pharmacy',
        'business_location': 'Mwanza, Tanzania',
        'business_type': 'inventory',
        'tin_number': '555123456',
        'is_verified': True,
    },
    {
        'phone_number': '+255444987654',
        'password': 'manager@123',
        'business_name': 'Demo Manager Pharmacy',
        'business_location': 'Dodoma, Tanzania',
        'business_type': 'pharmacy',
        'tin_number': '444987654',
        'is_verified': True,
    },
    {
        'phone_number': '+255333456789',
        'password': 'accountant@123',
        'business_name': 'Demo Accountant Pharmacy',
        'business_location': 'Tanga, Tanzania',
        'business_type': 'accounting',
        'tin_number': '333456789',
        'is_verified': True,
    },
    {
        'phone_number': '+255222111000',
        'password': 'unverified@123',
        'business_name': 'Unverified Test Pharmacy',
        'business_location': 'Zanzibar, Tanzania',
        'business_type': 'pharmacist',
        'tin_number': '222111000',
        'is_verified': False,
    }
]

# Create accounts
for account_data in test_accounts:
    try:
        # Check if user exists
        existing_user = BusinessUser.objects.filter(phone_number=account_data['phone_number']).first()
        
        if existing_user:
            print(f"Updating existing user: {account_data['phone_number']}")
            for key, value in account_data.items():
                if key == 'password':
                    existing_user.password = make_password(value)
                else:
                    setattr(existing_user, key, value)
            existing_user.save()
        else:
            print(f"Creating new user: {account_data['phone_number']}")
            BusinessUser.objects.create(
                user_id=str(uuid.uuid4()),
                phone_number=account_data['phone_number'],
                password=make_password(account_data['password']),
                business_name=account_data['business_name'],
                business_location=account_data['business_location'],
                business_type=account_data['business_type'],
                tin_number=account_data['tin_number'],
                is_verified=account_data['is_verified'],
            )
        print(f"✅ Success: {account_data['business_name']}")
    except Exception as e:
        print(f"❌ Error: {account_data['phone_number']} - {str(e)}")

# Verify creation
total_users = BusinessUser.objects.count()
print(f"\n📊 Total users in database: {total_users}")
```

## 🔧 **Method 3: Using Django Admin**

### **Step 1: Access Django Admin**
1. Go to: `https://geoclimatz.pythonanywhere.com/admin/`
2. Login with your superuser credentials

### **Step 2: Create Users Manually**
1. Navigate to "Hardware Backend" → "Business Users"
2. Click "Add Business User"
3. Fill in the details for each test account
4. Save each user

## 🧪 **Testing the Accounts**

### **Step 1: Test Login**
1. Go to your frontend dashboard
2. Use the test credentials to login
3. Verify each role has appropriate access

### **Step 2: Verify Permissions**
- **SALES**: Can view products, orders
- **MARKETING**: Can view analytics, reports
- **RECEIVER**: Can manage inventory
- **MANAGER**: Can create products, manage all
- **ACCOUNTANT**: Can view financial reports
- **UNVERIFIED**: Should require OTP verification

## 🔍 **Troubleshooting**

### **Common Issues**

#### **1. Database Connection Error**
```bash
# Check if MySQL is running
sudo service mysql status

# Check database credentials in settings
python3 manage.py dbshell
```

#### **2. Permission Denied**
```bash
# Make scripts executable
chmod +x *.py

# Check file ownership
ls -la *.py
```

#### **3. Import Errors**
```bash
# Install requirements
pip3 install -r requirements.txt

# Check Python path
python3 -c "import sys; print(sys.path)"
```

## 📊 **Verification Commands**

### **Check Database Connection**
```bash
python3 manage.py dbshell
```

### **List All Users**
```bash
python3 manage.py shell -c "from hardware_backend.models import BusinessUser; print([f'{u.phone_number} - {u.business_name}' for u in BusinessUser.objects.all()])"
```

### **Check User Count**
```bash
python3 manage.py shell -c "from hardware_backend.models import BusinessUser; print(f'Total users: {BusinessUser.objects.count()}')"
```

## 🎯 **Expected Results**

After successful execution, you should see:
- ✅ 6 test accounts created/updated
- 📋 Complete credentials list
- 📊 Database statistics
- 🚀 Ready for frontend testing

## 🚀 **Next Steps**

1. **Create the accounts** using any method above
2. **Test login** with each role
3. **Verify permissions** work correctly
4. **Update frontend** if needed
5. **Deploy to production** when ready

**Your production test accounts are now ready!** 🎉

