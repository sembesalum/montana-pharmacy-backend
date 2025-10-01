# 🚀 Quick Start: Production Test Accounts

## ⚡ **Fastest Method (Recommended)**

### **1. Run the Script**
```bash
cd kipenzi_backend
python3 create_prod_accounts.py
```

### **2. That's it!** 
The script will create all 6 test accounts in your production database.

## 📋 **Test Account Credentials**

| Role | Phone | Password | Status |
|------|-------|----------|--------|
| **SALES** | +255712345678 | sales@123 | ✅ Verified |
| **MARKETING** | +255987654321 | marketing@123 | ✅ Verified |
| **RECEIVER** | +255555123456 | receiver@123 | ✅ Verified |
| **MANAGER** | +255444987654 | manager@123 | ✅ Verified |
| **ACCOUNTANT** | +255333456789 | accountant@123 | ✅ Verified |
| **UNVERIFIED** | +255222111000 | unverified@123 | ⏳ Pending |

## 🌐 **Test Your Dashboard**

1. **Frontend URL**: Your deployed Vercel app
2. **Backend URL**: https://geoclimatz.pythonanywhere.com
3. **Login** with any of the credentials above
4. **Test** each role's permissions

## 🔧 **Alternative Methods**

### **Method 2: Django Shell**
```bash
python3 manage.py shell
# Then run the Python code from PRODUCTION_ACCOUNTS_GUIDE.md
```

### **Method 3: Django Admin**
1. Go to: https://geoclimatz.pythonanywhere.com/admin/
2. Create users manually

## ✅ **Verification**

After running the script, you should see:
- ✅ 6 accounts created/updated
- 📊 Database statistics
- 🎉 Ready for testing!

## 🆘 **Need Help?**

Check the detailed guide: `PRODUCTION_ACCOUNTS_GUIDE.md`

**Ready to test your production dashboard!** 🚀

