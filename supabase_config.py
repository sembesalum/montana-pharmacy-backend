#!/usr/bin/env python3
"""
Supabase Configuration Helper for Kipenzi Django App
"""

import os
import subprocess
import sys

def get_database_password():
    """Prompt user for database password"""
    print("🔐 Supabase Database Setup")
    print("=" * 40)
    print("You need to get your database password from Supabase:")
    print("1. Go to https://supabase.com/dashboard")
    print("2. Select your project: vumugefwfknpfihxnqhm")
    print("3. Go to Settings -> Database")
    print("4. Copy the password from the connection string")
    print()
    
    password = input("Enter your Supabase database password: ").strip()
    return password

def create_env_file(password):
    """Create .env file with Supabase configuration"""
    env_content = f"""# Django Settings
SECRET_KEY=django-insecure-5@iuiw798xppl64^4dhj7^x&sa)k-jy5k&30(67!=rs*s*eq!=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Supabase Configuration
SUPABASE_URL=https://vumugefwfknpfihxnqhm.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1bXVnZWZ3ZmtucGZpaHhucWhtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEwMzI4MTEsImV4cCI6MjA2NjYwODgxMX0.8X689kVNJB_XiFGM5k8ympvq3MIweLjlSzVL8S2quBQ

# Database (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres:{password}@db.vumugefwfknpfihxnqhm.supabase.co:5432/postgres
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with Supabase configuration")

def test_connection():
    """Test the database connection"""
    print("🔌 Testing database connection...")
    
    try:
        result = subprocess.run(
            ["python3", "manage.py", "check", "--database", "default"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Database connection successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Database connection failed: {e.stderr}")
        return False

def run_migrations():
    """Run Django migrations"""
    print("🔄 Running database migrations...")
    
    try:
        result = subprocess.run(
            ["python3", "manage.py", "migrate"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Migrations completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e.stderr}")
        return False

def create_superuser():
    """Create a superuser"""
    print("👤 Creating superuser...")
    
    try:
        # Use environment variables for superuser creation
        env = os.environ.copy()
        env['DJANGO_SUPERUSER_USERNAME'] = 'admin'
        env['DJANGO_SUPERUSER_EMAIL'] = 'admin@kipenzi.com'
        env['DJANGO_SUPERUSER_PASSWORD'] = 'admin123'
        
        result = subprocess.run(
            ["python3", "manage.py", "createsuperuser", "--noinput"],
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Superuser created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("Email: admin@kipenzi.com")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Superuser creation failed or was skipped: {e.stderr}")
        return False

def main():
    print("🚀 Kipenzi Django App - Supabase Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Get database password
    password = get_database_password()
    if not password:
        print("❌ Database password is required")
        sys.exit(1)
    
    # Create .env file
    create_env_file(password)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Test connection
    if not test_connection():
        print("❌ Cannot connect to Supabase database")
        print("Please check your password and try again")
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        print("❌ Failed to run migrations")
        sys.exit(1)
    
    # Create superuser
    create_superuser()
    
    print("\n🎉 Supabase setup completed successfully!")
    print("\nNext steps:")
    print("1. Test your app: python3 manage.py runserver")
    print("2. Visit http://localhost:8000/admin/ to access Django admin")
    print("3. Deploy to your chosen platform (Railway, Render, etc.)")
    print("\nYour Supabase project is ready at:")
    print("https://vumugefwfknpfihxnqhm.supabase.co")

if __name__ == "__main__":
    main() 