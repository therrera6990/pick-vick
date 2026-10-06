#!/usr/bin/env bash
set -e

echo "Starting Pick Vick..."

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

echo "Installing dependencies..."
$PYTHON -m pip install -r requirements.txt

echo "Preparing database..."
$PYTHON manage.py migrate --noinput

echo "Pick Vick running at http://127.0.0.1:8000"

# Gunicorn is for Linux. Windows uses Django's development server.
case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*)
        echo "Windows detected - using Django development server."
        exec $PYTHON manage.py runserver 0.0.0.0:8000
        ;;
    *)
        echo "Linux detected - using Gunicorn."
        exec $PYTHON -m gunicorn pick_vick.wsgi:application --bind 0.0.0.0:8000
        ;;
esac