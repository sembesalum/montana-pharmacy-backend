#!/bin/bash

# Fix Apache permissions for Django application
# Run this script as root or with sudo

echo "🔧 Fixing Apache permissions for Django application..."

# Set the project directory
PROJECT_DIR="/home/ubuntu/django/kipenzi"
VENV_DIR="/home/ubuntu/django/venv"

# Check if directories exist
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Project directory $PROJECT_DIR does not exist"
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment directory $VENV_DIR does not exist"
    exit 1
fi

# Get the Apache user (usually www-data on Ubuntu)
APACHE_USER=$(ps aux | grep -E '[a]pache|[h]ttpd' | awk '{print $1}' | head -1)
if [ -z "$APACHE_USER" ]; then
    APACHE_USER="www-data"
fi

echo "📁 Setting directory permissions..."

# Set ownership to ubuntu user but give Apache group access
sudo chown -R ubuntu:www-data "$PROJECT_DIR"
sudo chown -R ubuntu:www-data "$VENV_DIR"

# Set directory permissions (755 for directories)
sudo find "$PROJECT_DIR" -type d -exec chmod 755 {} \;
sudo find "$VENV_DIR" -type d -exec chmod 755 {} \;

# Set file permissions (644 for files)
sudo find "$PROJECT_DIR" -type f -exec chmod 644 {} \;
sudo find "$VENV_DIR" -type f -exec chmod 644 {} \;

# Make manage.py executable
sudo chmod +x "$PROJECT_DIR/manage.py"

# Make wsgi.py readable by Apache
sudo chmod 644 "$PROJECT_DIR/kipenzi/wsgi.py"

# Add Apache user to ubuntu group (if it exists)
if getent group ubuntu > /dev/null 2>&1; then
    sudo usermod -a -G ubuntu "$APACHE_USER"
fi

# Create static directory if it doesn't exist
sudo mkdir -p "$PROJECT_DIR/static"
sudo chown ubuntu:www-data "$PROJECT_DIR/static"
sudo chmod 755 "$PROJECT_DIR/static"

# Collect static files
echo "📦 Collecting static files..."
cd "$PROJECT_DIR"
sudo -u ubuntu python3 manage.py collectstatic --noinput

echo "✅ Permissions fixed!"
echo "🔄 Restarting Apache..."
sudo systemctl restart apache2

echo "📋 Summary of changes:"
echo "- Set ownership to ubuntu:www-data"
echo "- Set directory permissions to 755"
echo "- Set file permissions to 644"
echo "- Made manage.py executable"
echo "- Collected static files"
echo "- Restarted Apache"

echo ""
echo "🔍 To check if it's working:"
echo "1. Check Apache error logs: sudo tail -f /var/log/apache2/error.log"
echo "2. Check Apache access logs: sudo tail -f /var/log/apache2/access.log"
echo "3. Test your application: curl http://your-domain.com/" 