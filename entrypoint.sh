#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e
cd /app/backend

# Run database migrations. The --noinput flag is important for automation.

echo "Running migrations..."
/usr/local/bin/uv run python manage.py migrate --noinput

echo "Creating superuser if needed..."
/usr/local/bin/uv run python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
EOF

echo "Seeding database..."
/usr/local/bin/uv run python manage.py seed_inventory || echo "Seed data command not found or already seeded"

echo "Starting server..."
exec "$@"