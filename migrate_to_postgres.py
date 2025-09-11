#!/usr/bin/env python3
"""
Migration script to help move from MySQL to PostgreSQL for Supabase deployment
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        return None

def check_postgresql_compatibility():
    """Check for potential PostgreSQL compatibility issues"""
    print("🔍 Checking for PostgreSQL compatibility issues...")
    
    # Check for MySQL-specific imports
    mysql_issues = []
    
    # Search for PyMySQL usage
    if run_command("grep -r 'PyMySQL' . --include='*.py' --exclude-dir=venv --exclude-dir=__pycache__"):
        mysql_issues.append("PyMySQL import found - will need to be removed for PostgreSQL")
    
    # Search for MySQL-specific field types
    if run_command("grep -r 'models.TextField' . --include='*.py' --exclude-dir=venv --exclude-dir=__pycache__"):
        mysql_issues.append("Text fields found - these should work fine with PostgreSQL")
    
    # Check for custom SQL queries
    if run_command("grep -r 'raw(' . --include='*.py' --exclude-dir=venv --exclude-dir=__pycache__"):
        mysql_issues.append("Raw SQL queries found - may need PostgreSQL syntax updates")
    
    if mysql_issues:
        print("⚠️  Potential compatibility issues found:")
        for issue in mysql_issues:
            print(f"   - {issue}")
    else:
        print("✅ No obvious compatibility issues found")
    
    return mysql_issues

def backup_mysql_data():
    """Create a backup of MySQL data"""
    print("💾 Creating MySQL data backup...")
    
    backup_file = "mysql_backup.sql"
    
    # Create backup command
    backup_cmd = f"mysqldump -u root -p3102001Prosper kipenzi > {backup_file}"
    
    if run_command(backup_cmd):
        print(f"✅ MySQL backup created: {backup_file}")
        return backup_file
    else:
        print("❌ Failed to create MySQL backup")
        return None

def test_postgresql_connection():
    """Test PostgreSQL connection"""
    print("🔌 Testing PostgreSQL connection...")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        return False
    
    # Test connection using Django
    test_cmd = "python manage.py check --database default"
    if run_command(test_cmd):
        print("✅ PostgreSQL connection successful")
        return True
    else:
        print("❌ PostgreSQL connection failed")
        return False

def run_postgresql_migrations():
    """Run migrations on PostgreSQL database"""
    print("🔄 Running PostgreSQL migrations...")
    
    # Run migrations
    if run_command("python manage.py migrate"):
        print("✅ PostgreSQL migrations completed")
        return True
    else:
        print("❌ PostgreSQL migrations failed")
        return False

def main():
    print("🔄 Kipenzi - MySQL to PostgreSQL Migration Helper")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Step 1: Check compatibility
    issues = check_postgresql_compatibility()
    
    # Step 2: Check if DATABASE_URL is set
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("\n❌ DATABASE_URL not set. Please:")
        print("1. Create a Supabase project")
        print("2. Get your database connection string")
        print("3. Set: export DATABASE_URL='your-connection-string'")
        sys.exit(1)
    
    # Step 3: Test PostgreSQL connection
    if not test_postgresql_connection():
        print("\n❌ Cannot connect to PostgreSQL database")
        print("Please check your DATABASE_URL and try again")
        sys.exit(1)
    
    # Step 4: Create MySQL backup
    backup_file = backup_mysql_data()
    
    # Step 5: Run PostgreSQL migrations
    if not run_postgresql_migrations():
        print("\n❌ Failed to run PostgreSQL migrations")
        print("Please check your database schema and try again")
        sys.exit(1)
    
    print("\n🎉 Migration setup completed!")
    print("\nNext steps:")
    print("1. Test your app with PostgreSQL: python manage.py runserver")
    print("2. If everything works, you can deploy to your hosting platform")
    print("3. If you encounter issues, check the compatibility issues above")
    
    if backup_file:
        print(f"\n📁 MySQL backup saved as: {backup_file}")
        print("You can use this to restore data if needed")

if __name__ == "__main__":
    main() 