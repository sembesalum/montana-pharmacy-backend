#!/usr/bin/env python3
"""
Simple script to run the production account creation.
This can be executed directly on the production server.
"""

import subprocess
import sys
import os

def main():
    print("🚀 Starting production account creation...")
    print("=" * 50)
    
    # Change to the backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    try:
        # Run the production account creation script
        result = subprocess.run([
            sys.executable, 'create_prod_accounts.py'
        ], capture_output=True, text=True, check=True)
        
        print("✅ Script executed successfully!")
        print("\n📋 Output:")
        print(result.stdout)
        
        if result.stderr:
            print("\n⚠️  Warnings/Errors:")
            print(result.stderr)
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Script failed with exit code {e.returncode}")
        print(f"Error: {e.stderr}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return 1
    
    print("\n🎉 Production accounts creation completed!")
    return 0

if __name__ == '__main__':
    sys.exit(main())

