#!/usr/bin/env python3
"""
Setup script for deploying Kipenzi Django app with Supabase
"""

import os
import secrets
import subprocess
import sys

def generate_secret_key():
    """Generate a new Django secret key"""
    return ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50))

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        return None

def main():
    print("🚀 Kipenzi Django App - Supabase Deployment Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: Please run this script from the project root directory (where manage.py is located)")
        sys.exit(1)
    
    # Generate secret key
    secret_key = generate_secret_key()
    print(f"✅ Generated new Django secret key")
    
    # Create .env file if it doesn't exist
    env_file = '.env'
    if not os.path.exists(env_file):
        print("📝 Creating .env file...")
        with open(env_file, 'w') as f:
            f.write(f"# Django Settings\n")
            f.write(f"SECRET_KEY={secret_key}\n")
            f.write(f"DEBUG=True\n")
            f.write(f"ALLOWED_HOSTS=localhost,127.0.0.1\n")
            f.write(f"\n")
            f.write(f"# Database (Supabase PostgreSQL)\n")
            f.write(f"# Replace with your actual Supabase database URL\n")
            f.write(f"DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres\n")
        print(f"✅ Created {env_file} file")
    else:
        print(f"⚠️  {env_file} file already exists")
    
    # Install dependencies
    print("📦 Installing dependencies...")
    if run_command("pip install -r requirements.txt"):
        print("✅ Dependencies installed successfully")
    else:
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Check if DATABASE_URL is set
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("\n⚠️  DATABASE_URL not set. You need to:")
        print("1. Create a Supabase project at https://supabase.com")
        print("2. Get your database connection string")
        print("3. Set the DATABASE_URL environment variable")
        print("\nExample:")
        print("export DATABASE_URL='postgresql://postgres:password@db.xxx.supabase.co:5432/postgres'")
        
        # Ask if user wants to continue with local MySQL
        response = input("\nDo you want to continue with local MySQL for development? (y/n): ")
        if response.lower() != 'y':
            print("Setup incomplete. Please set DATABASE_URL and run again.")
            sys.exit(1)
    else:
        print("✅ DATABASE_URL is configured")
        
        # Run migrations
        print("🔄 Running database migrations...")
        if run_command("python manage.py migrate"):
            print("✅ Migrations completed successfully")
        else:
            print("❌ Failed to run migrations")
            sys.exit(1)
        
        # Create superuser
        print("\n👤 Creating superuser...")
        print("Please enter the details for your admin user:")
        if run_command("python manage.py createsuperuser --noinput"):
            print("✅ Superuser created successfully")
        else:
            print("⚠️  Superuser creation failed or was skipped")
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Update your .env file with your actual Supabase database URL")
    print("2. Test your app locally: python manage.py runserver")
    print("3. Follow the deployment guide in DEPLOYMENT.md")
    print("\nFor deployment options:")
    print("- Railway: https://railway.app")
    print("- Render: https://render.com")
    print("- Heroku: https://heroku.com")

if __name__ == "__main__":
    main() 