import os
import sys

# Full path to the project root (same directory as manage.py)
project_root = '/home/wamahosp/repositories/learning-management-system/lms'
sys.path.insert(0, project_root)

# Path to the Django project package (where settings.py lives)
sys.path.insert(0, os.path.join(project_root, 'lms'))

# Set environment variable for Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')

# Import Django's WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
