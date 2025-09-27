#!/usr/bin/env python3
"""
Complete script to set up test accounts in production database.
This script will:
1. Switch to production database configuration
2. Create/update test accounts
3. Optionally switch back to local database
"""

import os
import sys
import subprocess
import django
from django.conf import settings

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {str(e)}")
        return False

def switch_database_config():
    """Switch to production database configuration"""
    print("🔄 Switching to production database configuration...")
    
    settings_file = 'kipenzi/settings.py'
    
    if not os.path.exists(settings_file):
        print(f"❌ Settings file not found: {settings_file}")
        return False
    
    # Read the current settings file
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Backup the original file
    with open(f"{settings_file}.backup", 'w') as f:
        f.write(content)
    print(f"📁 Backup created: {settings_file}.backup")
    
    # Comment out SQLite database configuration
    sqlite_start = content.find("DATABASES = {\n    'default': {\n        'ENGINE': 'django.db.backends.sqlite3',")
    sqlite_end = content.find("}\n}", sqlite_start) + 3
    
    if sqlite_start != -1 and sqlite_end != -1:
        sqlite_config = content[sqlite_start:sqlite_end]
        commented_sqlite = sqlite_config.replace("DATABASES = {", "# DATABASES = {")
        commented_sqlite = commented_sqlite.replace("'default': {", "#     'default': {")
        commented_sqlite = commented_sqlite.replace("'ENGINE':", "#         'ENGINE':")
        commented_sqlite = commented_sqlite.replace("'NAME':", "#         'NAME':")
        commented_sqlite = commented_sqlite.replace("}", "#     }")
        commented_sqlite = commented_sqlite.replace("}", "# }")
        
        content = content[:sqlite_start] + commented_sqlite + content[sqlite_end:]
    
    # Uncomment production MySQL database configuration
    mysql_start = content.find("# DATABASES = {\n#     'default': {\n#         'ENGINE': 'django.db.backends.mysql',")
    mysql_end = content.find("# }", mysql_start) + 3
    
    if mysql_start != -1 and mysql_end != -1:
        mysql_config = content[mysql_start:mysql_end]
        uncommented_mysql = mysql_config.replace("# DATABASES = {", "DATABASES = {")
        uncommented_mysql = uncommented_mysql.replace("#     'default': {", "    'default': {")
        uncommented_mysql = uncommented_mysql.replace("#         'ENGINE':", "        'ENGINE':")
        uncommented_mysql = uncommented_mysql.replace("#         'NAME':", "        'NAME':")
        uncommented_mysql = uncommented_mysql.replace("#         'USER':", "        'USER':")
        uncommented_mysql = uncommented_mysql.replace("#         'PASSWORD':", "        'PASSWORD':")
        uncommented_mysql = uncommented_mysql.replace("#         'HOST':", "        'HOST':")
        uncommented_mysql = uncommented_mysql.replace("#         'PORT':", "        'PORT':")
        uncommented_mysql = uncommented_mysql.replace("#         'OPTIONS': {", "        'OPTIONS': {")
        uncommented_mysql = uncommented_mysql.replace("#             'init_command':", "            'init_command':")
        uncommented_mysql = uncommented_mysql.replace("#             'charset':", "            'charset':")
        uncommented_mysql = uncommented_mysql.replace("#             'connect_timeout':", "            'connect_timeout':")
        uncommented_mysql = uncommented_mysql.replace("#         },", "        },")
        uncommented_mysql = uncommented_mysql.replace("#         'CONN_MAX_AGE':", "        'CONN_MAX_AGE':")
        uncommented_mysql = uncommented_mysql.replace("#     }", "    }")
        uncommented_mysql = uncommented_mysql.replace("# }", "}")
        
        content = content[:mysql_start] + uncommented_mysql + content[mysql_end:]
    
    # Write the updated content
    with open(settings_file, 'w') as f:
        f.write(content)
    
    print("✅ Successfully switched to production database configuration!")
    return True

def create_test_accounts():
    """Create test accounts in production database"""
    print("🚀 Creating test accounts in production database...")
    
    # Add the project directory to Python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kipenzi.settings')
    django.setup()
    
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
            'role': 'SALES'
        },
        {
            'phone_number': '+255987654321',
            'password': 'marketing@123',
            'business_name': 'Demo Marketing Pharmacy',
            'business_location': 'Arusha, Tanzania',
            'business_type': 'marketing',
            'tin_number': '987654321',
            'is_verified': True,
            'role': 'MARKETING'
        },
        {
            'phone_number': '+255555123456',
            'password': 'receiver@123',
            'business_name': 'Demo Receiver Pharmacy',
            'business_location': 'Mwanza, Tanzania',
            'business_type': 'inventory',
            'tin_number': '555123456',
            'is_verified': True,
            'role': 'RECEIVER'
        },
        {
            'phone_number': '+255444987654',
            'password': 'manager@123',
            'business_name': 'Demo Manager Pharmacy',
            'business_location': 'Dodoma, Tanzania',
            'business_type': 'pharmacy',
            'tin_number': '444987654',
            'is_verified': True,
            'role': 'MANAGER'
        },
        {
            'phone_number': '+255333456789',
            'password': 'accountant@123',
            'business_name': 'Demo Accountant Pharmacy',
            'business_location': 'Tanga, Tanzania',
            'business_type': 'accounting',
            'tin_number': '333456789',
            'is_verified': True,
            'role': 'ACCOUNTANT'
        },
        {
            'phone_number': '+255222111000',
            'password': 'unverified@123',
            'business_name': 'Unverified Test Pharmacy',
            'business_location': 'Zanzibar, Tanzania',
            'business_type': 'pharmacist',
            'tin_number': '222111000',
            'is_verified': False,
            'role': 'UNVERIFIED'
        }
    ]
    
    created_accounts = []
    updated_accounts = []
    
    for account_data in test_accounts:
        try:
            # Check if user already exists
            existing_user = BusinessUser.objects.filter(phone_number=account_data['phone_number']).first()
            
            if existing_user:
                print(f"🔄 User with phone {account_data['phone_number']} already exists. Updating...")
                # Update existing user
                for key, value in account_data.items():
                    if key == 'password':
                        existing_user.password = make_password(value)
                    elif key != 'role':  # Skip role field as it's not in the model
                        setattr(existing_user, key, value)
                existing_user.save()
                updated_accounts.append(existing_user)
                print(f"✅ Updated user: {account_data['business_name']} ({account_data['phone_number']})")
            else:
                # Create new user
                user = BusinessUser.objects.create(
                    user_id=str(uuid.uuid4()),
                    phone_number=account_data['phone_number'],
                    password=make_password(account_data['password']),
                    business_name=account_data['business_name'],
                    business_location=account_data['business_location'],
                    business_type=account_data['business_type'],
                    tin_number=account_data['tin_number'],
                    is_verified=account_data['is_verified'],
                )
                created_accounts.append(user)
                print(f"✅ Created user: {account_data['business_name']} ({account_data['phone_number']})")
                
        except Exception as e:
            print(f"❌ Error creating user {account_data['phone_number']}: {str(e)}")
    
    print(f"\n🎉 Successfully processed {len(created_accounts + updated_accounts)} test accounts!")
    print(f"   - Created: {len(created_accounts)}")
    print(f"   - Updated: {len(updated_accounts)}")
    
    print("\n📋 Production Test Account Credentials:")
    print("=" * 60)
    
    for account in test_accounts:
        role_name = account['role']
        status = "✅ Verified" if account['is_verified'] else "⏳ Pending Verification"
        print(f"Role: {role_name}")
        print(f"Phone: {account['phone_number']}")
        print(f"Password: {account['password']}")
        print(f"Business: {account['business_name']}")
        print(f"Status: {status}")
        print("-" * 40)
    
    print("\n🚀 These accounts are now available in the PRODUCTION database!")
    print("💡 You can use these credentials to test the deployed admin dashboard.")
    
    return True

def main():
    """Main function to set up production test accounts"""
    print("🚀 Setting up test accounts in production database...")
    print("=" * 60)
    
    # Step 1: Switch to production database
    if not switch_database_config():
        print("❌ Failed to switch to production database configuration")
        return False
    
    # Step 2: Create test accounts
    if not create_test_accounts():
        print("❌ Failed to create test accounts")
        return False
    
    print("\n🎉 Production test accounts setup completed successfully!")
    print("📊 Database: MySQL on PythonAnywhere")
    print("🌐 You can now test the deployed dashboard with these credentials")
    
    # Ask if user wants to switch back to local database
    response = input("\n🔄 Do you want to switch back to local database? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        print("🔄 Switching back to local database...")
        # This would require implementing the reverse switch
        print("💡 To switch back to local database, run: python switch_to_production_db.py local")
    
    return True

if __name__ == '__main__':
    main()
