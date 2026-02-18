#!/bin/sh
set -e

# Wait for the database defined by DATABASE_URL to be available (if present)
if [ -n "$DATABASE_URL" ]; then
  echo "Waiting for database..."
  python - <<'PY'
import os, time, sys
from urllib.parse import urlparse
try:
    import psycopg2
except Exception as e:
    print('psycopg2 not available:', e)
    sys.exit(0)
url = urlparse(os.getenv('DATABASE_URL'))
host = url.hostname or 'db'
port = url.port or 5432
user = url.username
password = url.password
dbname = url.path.lstrip('/') or 'postgres'
for i in range(60):
    try:
        conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=dbname, connect_timeout=3)
        conn.close()
        print('Database is available')
        break
    except Exception as exc:
        print('DB not ready, retrying...', exc)
        time.sleep(1)
else:
    print('Timed out waiting for the database', file=sys.stderr)
    sys.exit(1)
PY
fi

# Run migrations and collectstatic
python manage.py migrate --noinput
python manage.py collectstatic --noinput || true

# Exec the container CMD
exec "$@"
