#!/bin/sh
set -e

echo "Aguardando banco de dados em $DB_HOST:$DB_PORT..."
while ! python -c "import socket; socket.create_connection(('$DB_HOST', int('$DB_PORT')), timeout=2)" 2>/dev/null; do
  sleep 1
done
echo "Banco disponível."

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py setup_groups

exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 60 \
  --access-logfile - \
  --error-logfile -
