#!/usr/bin/env python3
"""
Script to normalize phone numbers for existing users in the database.
This ensures all phone numbers are stored in a consistent format (+255XXXXXXXXX).
Run this script to fix phone number format mismatches that prevent login.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kipenzi.settings')
django.setup()

from hardware_backend.models import BusinessUser
from hardware_backend.views import normalize_phone_number

def fix_user_phone_numbers():
    """Normalize all user phone numbers to consistent format"""
    
    print("🔧 Fixing user phone numbers...")
    print("=" * 60)
    
    users = BusinessUser.objects.all()
    updated_count = 0
    errors = []
    
    for user in users:
        original_phone = user.phone_number
        normalized_phone = normalize_phone_number(original_phone)
        
        if original_phone != normalized_phone:
            try:
                # Check if normalized phone already exists (duplicate)
                existing_user = BusinessUser.objects.filter(phone_number=normalized_phone).exclude(user_id=user.user_id).first()
                
                if existing_user:
                    print(f"⚠️  Skipping {user.business_name} ({original_phone})")
                    print(f"   Normalized format {normalized_phone} already exists for user: {existing_user.business_name}")
                    errors.append(f"{user.business_name}: Duplicate phone number after normalization")
                else:
                    # Update phone number
                    user.phone_number = normalized_phone
                    user.save()
                    print(f"✅ Updated {user.business_name}")
                    print(f"   {original_phone} → {normalized_phone}")
                    updated_count += 1
            except Exception as e:
                print(f"❌ Error updating {user.business_name}: {str(e)}")
                errors.append(f"{user.business_name}: {str(e)}")
        else:
            print(f"✓ {user.business_name} ({original_phone}) - Already normalized")
    
    print("\n" + "=" * 60)
    print(f"✅ Successfully updated {updated_count} users")
    if errors:
        print(f"⚠️  {len(errors)} errors encountered:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("🎉 All phone numbers are now normalized!")
    
    return updated_count, len(errors)

if __name__ == '__main__':
    print("🚀 Phone Number Normalization Script")
    print("=" * 60)
    print("This script will normalize all user phone numbers to +255XXXXXXXXX format")
    print("=" * 60)
    
    response = input("\nContinue? (y/n): ").strip().lower()
    if response == 'y' or response == 'yes':
        updated, errors = fix_user_phone_numbers()
        if updated > 0:
            print(f"\n✅ Done! {updated} users updated.")
        else:
            print("\n✅ No updates needed - all phone numbers are already normalized.")
    else:
        print("❌ Cancelled by user.")
