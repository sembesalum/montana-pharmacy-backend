# Production Demo Accounts Creation Guide

This guide explains how to create demo accounts for testing the pharmacy admin dashboard in production.

## Script: `create_production_demo_accounts.py`

This script creates 6 demo accounts with different roles for testing purposes.

## Prerequisites

1. **Django Environment Setup**
   - Ensure Django is installed and configured
   - Database migrations must be run (`python manage.py migrate`)
   - You must have database access

2. **Server Access**
   - SSH access to production server
   - Or run locally if connected to production database

## Usage

### Step 1: Navigate to Project Directory

```bash
cd /path/to/kipenzi_backend
```

### Step 2: Run the Script

```bash
python3 create_production_demo_accounts.py
```

Or if you're using a virtual environment:

```bash
source venv/bin/activate  # or your virtual environment activation command
python3 create_production_demo_accounts.py
```

### Step 3: Verify Output

The script will:
- ✅ Create/update demo accounts
- ✅ Display all credentials
- ✅ Show database statistics
- ✅ Provide next steps

## Demo Accounts Created

The script creates the following accounts:

| Role | Phone Number | Password | Business Type | Status |
|------|--------------|----------|---------------|--------|
| **SALES** | +255712345678 | Sales@2024 | pharmacist | ✅ Verified |
| **MARKETING** | +255987654321 | Marketing@2024 | marketing | ✅ Verified |
| **RECEIVER** | +255555123456 | Receiver@2024 | inventory | ✅ Verified |
| **MANAGER** | +255444987654 | Manager@2024 | pharmacy | ✅ Verified |
| **ACCOUNTANT** | +255333456789 | Accountant@2024 | accounting | ✅ Verified |
| **UNVERIFIED** | +255222111000 | Unverified@2024 | pharmacist | ⏳ Requires OTP |

## Account Permissions

### SALES
- Can sell products
- Can apply discounts
- Can record expenses
- Can view own sales only
- Can process refunds

### MARKETING
- Can sell products
- Can apply discounts
- Can place orders
- Can view sales reports
- Can manage sales
- Can create invoices

### RECEIVER
- Can add stock
- Can modify prices
- Can receive inventory
- Can view all products

### MANAGER
- **Full access** to all features
- Can manage users
- Can view all reports
- Can manage finances
- Can manage inventory

### ACCOUNTANT
- Can view sales reports
- Can view inventory value
- Can view cash flow
- Can view debts

### UNVERIFIED
- Requires OTP verification on first login
- Limited access until verified

## Troubleshooting

### Error: "Django Configuration Error"
- Make sure you're in the project root directory
- Check that `DJANGO_SETTINGS_MODULE` is set correctly
- Verify Django is installed: `pip list | grep Django`

### Error: "Database connection failed"
- Verify database credentials in settings
- Check database server is running
- Ensure migrations are applied: `python manage.py migrate`

### Error: "Account already exists"
- The script will update existing accounts automatically
- This is normal if you run the script multiple times

### Error: "Permission denied"
- Make sure the script is executable: `chmod +x create_production_demo_accounts.py`
- Or run with: `python3 create_production_demo_accounts.py`

## Security Notes

⚠️ **Important Security Considerations:**

1. **Change Passwords**: These are demo accounts with predictable passwords. Change them in production if needed.

2. **Remove After Testing**: Consider removing or disabling these accounts after testing is complete.

3. **OTP Verification**: The unverified account requires OTP verification, which tests the verification flow.

4. **Database Access**: Ensure only authorized personnel can run this script.

## Testing the Accounts

After running the script:

1. **Login to Dashboard**
   - Use the phone number and password from the output
   - For unverified account, you'll need to complete OTP verification

2. **Test Permissions**
   - Try accessing different sections based on role
   - Verify that permissions are correctly enforced

3. **Test Features**
   - Create sales (SALES, MARKETING, MANAGER)
   - Manage inventory (RECEIVER, MANAGER)
   - View reports (ACCOUNTANT, MANAGER)
   - Manage users (MANAGER only)

## Output Example

```
======================================================================
🚀 PRODUCTION DEMO ACCOUNTS CREATION SCRIPT
======================================================================
📅 Date: 2024-01-15 10:30:00
======================================================================

📝 Starting account creation process...

[1/6] Processing SALES account...
   Phone: +255712345678
   Business: Demo Sales Pharmacy
   ✅ Created successfully
----------------------------------------------------------------------

...

======================================================================
📊 CREATION SUMMARY
======================================================================
✅ New accounts created: 6
🔄 Existing accounts updated: 0
❌ Failed accounts: 0
======================================================================

======================================================================
🔐 DEMO ACCOUNT CREDENTIALS
======================================================================

Role: SALES
Phone Number: +255712345678
Password: Sales@2024
Business Name: Demo Sales Pharmacy
Status: ✅ Verified
Description: Sales staff account - can sell products and process transactions
----------------------------------------------------------------------

...
```

## Support

If you encounter any issues:
1. Check the error message in the script output
2. Verify database connectivity
3. Ensure all migrations are applied
4. Check Django settings configuration

## Script Features

- ✅ Automatic account creation/update
- ✅ Password hashing
- ✅ Verification status management
- ✅ Detailed output with credentials
- ✅ Database statistics
- ✅ Error handling and reporting
- ✅ Safe to run multiple times (updates existing accounts)

---

**Last Updated**: 2024-01-15
**Script Version**: 1.0

