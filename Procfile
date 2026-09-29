web: python scripts/bootstrap.py && gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --access-logfile - --error-logfile - wsgi:app
