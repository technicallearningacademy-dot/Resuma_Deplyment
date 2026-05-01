import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

email = 'admin@admin.com'
password = 'adminpassword'

if not User.objects.filter(email=email).exists():
    print(f"Creating superuser {email}...")
    User.objects.create_superuser(email=email, password=password)
    print("Superuser created successfully.")
else:
    print(f"Superuser {email} already exists.")
