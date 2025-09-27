#!/usr/bin/env python3
"""
Script to switch Django settings to use production database.
This will uncomment the production database configuration and comment out SQLite.
"""

import os
import re

def switch_to_production_db():
    """Switch settings.py to use production MySQL database"""
    
    settings_file = 'kipenzi/settings.py'
    
    if not os.path.exists(settings_file):
        print(f"❌ Settings file not found: {settings_file}")
        return False
    
    print("🔄 Switching to production database configuration...")
    
    # Read the current settings file
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Backup the original file
    with open(f"{settings_file}.backup", 'w') as f:
        f.write(content)
    print(f"📁 Backup created: {settings_file}.backup")
    
    # Comment out SQLite database configuration
    sqlite_pattern = r"(DATABASES = \{\s*'default': \{\s*'ENGINE': 'django\.db\.backends\.sqlite3',\s*'NAME': BASE_DIR / 'db\.sqlite3',\s*\}\s*\})"
    sqlite_replacement = r"# \1"
    content = re.sub(sqlite_pattern, sqlite_replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Uncomment production MySQL database configuration
    mysql_pattern = r"# (DATABASES = \{\s*'default': \{\s*'ENGINE': 'django\.db\.backends\.mysql',\s*'NAME': 'geoclimatz\$default',\s*'USER': 'geoclimatz',\s*'PASSWORD': 'salumroot',\s*'HOST': 'geoclimatz\.mysql\.pythonanywhere-services\.com',\s*'PORT': '3306',\s*'OPTIONS': \{\s*'init_command': \"SET sql_mode='STRICT_TRANS_TABLES'\",\s*'charset': 'utf8mb4',\s*'connect_timeout': 30,\s*\}\s*,\s*'CONN_MAX_AGE': 300,\s*\}\s*\})"
    mysql_replacement = r"\1"
    content = re.sub(mysql_pattern, mysql_replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Write the updated content
    with open(settings_file, 'w') as f:
        f.write(content)
    
    print("✅ Successfully switched to production database configuration!")
    print("📊 Database: MySQL on PythonAnywhere")
    print("🔗 Host: geoclimatz.mysql.pythonanywhere-services.com")
    print("📝 Database: geoclimatz$default")
    
    return True

def switch_to_local_db():
    """Switch settings.py back to local SQLite database"""
    
    settings_file = 'kipenzi/settings.py'
    
    if not os.path.exists(settings_file):
        print(f"❌ Settings file not found: {settings_file}")
        return False
    
    print("🔄 Switching back to local database configuration...")
    
    # Read the current settings file
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Comment out production MySQL database configuration
    mysql_pattern = r"(DATABASES = \{\s*'default': \{\s*'ENGINE': 'django\.db\.backends\.mysql',\s*'NAME': 'geoclimatz\$default',\s*'USER': 'geoclimatz',\s*'PASSWORD': 'salumroot',\s*'HOST': 'geoclimatz\.mysql\.pythonanywhere-services\.com',\s*'PORT': '3306',\s*'OPTIONS': \{\s*'init_command': \"SET sql_mode='STRICT_TRANS_TABLES'\",\s*'charset': 'utf8mb4',\s*'connect_timeout': 30,\s*\}\s*,\s*'CONN_MAX_AGE': 300,\s*\}\s*\})"
    mysql_replacement = r"# \1"
    content = re.sub(mysql_pattern, mysql_replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Uncomment SQLite database configuration
    sqlite_pattern = r"# (DATABASES = \{\s*'default': \{\s*'ENGINE': 'django\.db\.backends\.sqlite3',\s*'NAME': BASE_DIR / 'db\.sqlite3',\s*\}\s*\})"
    sqlite_replacement = r"\1"
    content = re.sub(sqlite_pattern, sqlite_replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Write the updated content
    with open(settings_file, 'w') as f:
        f.write(content)
    
    print("✅ Successfully switched back to local database configuration!")
    print("📊 Database: SQLite (local)")
    
    return True

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'local':
        switch_to_local_db()
    else:
        switch_to_production_db()
