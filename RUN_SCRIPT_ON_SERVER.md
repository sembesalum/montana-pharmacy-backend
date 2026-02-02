# 🚀 How to Run create_accounts_via_api.py on Server

## Option 1: Run on PythonAnywhere Server (Recommended)

### Step 1: Access PythonAnywhere Console
1. Log in to [PythonAnywhere](https://www.pythonanywhere.com)
2. Go to **Consoles** tab
3. Click **Bash** to open a new console

### Step 2: Navigate to Your Project Directory
```bash
cd /home/yourusername/kipenzi_backend
# Replace 'yourusername' with your PythonAnywhere username
```

### Step 3: Ensure Python Environment is Active
```bash
# Check Python version
python3 --version

# If using virtual environment, activate it
source venv/bin/activate  # or your venv path
```

### Step 4: Install Required Dependencies (if not already installed)
```bash
pip install requests
# or install all requirements
pip install -r requirements.txt
```

### Step 5: Run the Script
```bash
python3 create_accounts_via_api.py
```

---

## Option 2: Run from Your Local Machine

You can also run the script from your local machine - it will make HTTP requests to the server:

### Step 1: Navigate to Project Directory
```bash
cd kipenzi_backend
```

### Step 2: Install Dependencies (if needed)
```bash
pip install requests
```

### Step 3: Run the Script
```bash
python3 create_accounts_via_api.py
```

---

## Option 3: Run via PythonAnywhere Tasks (Scheduled)

### Step 1: Go to Tasks Tab
1. Log in to PythonAnywhere
2. Go to **Tasks** tab
3. Click **Create a new task**

### Step 2: Configure Task
- **Command**: `cd /home/yourusername/kipenzi_backend && python3 create_accounts_via_api.py`
- **Schedule**: Choose when to run (one-time or recurring)
- **Description**: "Create/Update test accounts"

### Step 3: Save and Run
Click **Create** to save the task. It will run automatically at the scheduled time.

---

## 🔧 Troubleshooting

### Issue: "requests module not found"
**Solution:**
```bash
pip install requests
# or
pip3 install requests
```

### Issue: "Permission denied"
**Solution:**
```bash
chmod +x create_accounts_via_api.py
python3 create_accounts_via_api.py
```

### Issue: "Cannot connect to API"
**Check:**
1. Verify API_BASE_URL in the script is correct
2. Check if server is running: `curl https://geoclimatz.pythonanywhere.com/v1/hardware/`
3. Check network connectivity

### Issue: "Script runs but accounts not created"
**Check:**
1. Review error messages in script output
2. Verify phone numbers are in correct format (+255...)
3. Check if accounts already exist (script will skip them)
4. Verify TIN numbers are unique

---

## 📝 Before Running: Update Phone Numbers

If you need to update existing accounts, edit the `PHONE_UPDATE_MAP` in the script:

```python
PHONE_UPDATE_MAP = {
    'MANAGER': {
        '+255616107670': '+255616107671'  # Old → New
    }
}
```

---

## ✅ Expected Output

When successful, you should see:
```
🚀 Production Test Accounts Creator (API Method)
============================================================
🔍 Testing API connection...
✅ API is accessible

============================================================
🚀 Creating test accounts via API...
🌐 API URL: https://geoclimatz.pythonanywhere.com/v1/hardware
============================================================

[1/6] Creating SALES account...
Phone: +255712345678
Business: Demo Sales Pharmacy
Status Code: 201
✅ Successfully created SALES account

...

🎉 Account Creation Summary:
============================================================
✅ Successfully created/verified: 6 accounts
❌ Errors: 0 accounts
```

---

## 🎯 Quick Command Reference

```bash
# Navigate to project
cd /home/yourusername/kipenzi_backend

# Run script
python3 create_accounts_via_api.py

# Run with output saved to file
python3 create_accounts_via_api.py > account_creation_log.txt 2>&1

# Check script syntax
python3 -m py_compile create_accounts_via_api.py
```

---

## 📞 Need Help?

If you encounter issues:
1. Check PythonAnywhere console logs
2. Verify API endpoint is accessible
3. Ensure all dependencies are installed
4. Check script permissions

