#!/usr/bin/env bash
set -o errexit

echo "=== Installing dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

# Ensure staticfiles directory exists
mkdir -p src/staticfiles

echo "=== Collecting static files ==="
python src/manage.py collectstatic --noinput

echo "=== Applying migrations ==="
python src/manage.py migrate --noinput

echo "=== Importing initial FPL data (optional) ==="
python src/manage.py import_fpl_data || echo "Skipping import_fpl_data"

echo "=== Creating superuser if none exists ==="
# Move into src so Python can find your Django project
cd src

python - <<'PY'
import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fantasy_project.settings")
django.setup()

User = get_user_model()
username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "adminpass")

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser created:", username)
else:
    print("Superuser already exists.")
PY

# Return to repo root
cd ..

echo "=== Build script completed ==="
