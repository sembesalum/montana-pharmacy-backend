#!/bin/bash

echo "🔍 Apache & Django Troubleshooting Script"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  This script should be run with sudo for full diagnostics"
fi

echo ""
echo "1. Checking Apache status..."
sudo systemctl status apache2 --no-pager -l

echo ""
echo "2. Checking Apache configuration..."
sudo apache2ctl configtest

echo ""
echo "3. Checking Apache error logs..."
sudo tail -20 /var/log/apache2/error.log

echo ""
echo "4. Checking Apache access logs..."
sudo tail -10 /var/log/apache2/access.log

echo ""
echo "5. Checking file permissions..."
PROJECT_DIR="/home/ubuntu/django/kipenzi"
VENV_DIR="/home/ubuntu/django/venv"

echo "Project directory permissions:"
ls -la "$PROJECT_DIR" | head -5

echo ""
echo "WSGI file permissions:"
ls -la "$PROJECT_DIR/kipenzi/wsgi.py"

echo ""
echo "Virtual environment permissions:"
ls -la "$VENV_DIR" | head -5

echo ""
echo "6. Checking if WSGI module is loaded..."
sudo apache2ctl -M | grep wsgi

echo ""
echo "7. Checking Apache user..."
ps aux | grep -E '[a]pache|[h]ttpd' | head -3

echo ""
echo "8. Testing Django application..."
cd "$PROJECT_DIR"
echo "Current directory: $(pwd)"
echo "Python version: $(python3 --version)"
echo "Django check:"
sudo -u ubuntu python3 manage.py check

echo ""
echo "9. Checking environment variables..."
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo "PYTHONPATH: $PYTHONPATH"

echo ""
echo "10. Testing WSGI application directly..."
cd "$PROJECT_DIR"
sudo -u ubuntu python3 -c "
import os
import sys
sys.path.insert(0, '/home/ubuntu/django/kipenzi')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kipenzi.settings')
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    print('✅ WSGI application loads successfully')
except Exception as e:
    print(f'❌ WSGI application failed to load: {e}')
"

echo ""
echo "11. Checking if mod_wsgi is installed..."
python3 -c "import mod_wsgi; print('✅ mod_wsgi is installed')" 2>/dev/null || echo "❌ mod_wsgi not found in Python"

echo ""
echo "12. Checking Apache modules..."
sudo apache2ctl -M | grep -E "(wsgi|headers|deflate)"

echo ""
echo "🔧 Quick fixes to try:"
echo "1. Run: sudo chmod +x fix_apache_permissions.sh && sudo ./fix_apache_permissions.sh"
echo "2. Check: sudo tail -f /var/log/apache2/error.log"
echo "3. Restart Apache: sudo systemctl restart apache2"
echo "4. Test: curl -I http://54.86.138.123/" 