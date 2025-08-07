#!/bin/bash

# Django i18n No-Prefix Example Project Setup Script

echo "======================================"
echo "Django i18n No-Prefix Demo Setup"
echo "======================================"

# Change to example_project directory
cd "$(dirname "$0")"

# Run migrations
echo ""
echo "Running migrations..."
python manage.py migrate

# Create superuser (optional)
echo ""
echo "Do you want to create a superuser? (y/n)"
read -r create_superuser
if [ "$create_superuser" = "y" ]; then
    python manage.py createsuperuser
fi

# Collect static files
echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || true

# Make messages for translations
echo ""
echo "Creating translation files..."
python manage.py makemessages -l ko -l ja --ignore=venv --ignore=.venv 2>/dev/null || true

# Compile messages
echo ""
echo "Compiling translation files..."
python manage.py compilemessages 2>/dev/null || true

# Start the development server
echo ""
echo "======================================"
echo "Starting development server..."
echo "Visit http://localhost:8000 to see the demo"
echo "Admin: http://localhost:8000/admin"
echo "======================================"
echo ""

python manage.py runserver
