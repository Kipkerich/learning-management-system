import os
import django
from django.contrib.auth.models import User

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms.settings")
django.setup()

if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@gmail.com", "Super@123")
    print("Superuser created successfully")
else:
    print("Superuser already exists")
