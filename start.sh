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

case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*)
        echo "Windows detected."

        echo "Installing dependencies..."
        $PYTHON -m pip install -r requirements.txt

        echo "Preparing database..."
        $PYTHON manage.py migrate --noinput

        echo "Pick Vick running at http://127.0.0.1:8000"
        exec $PYTHON manage.py runserver 0.0.0.0:8000
        ;;

    *)
        echo "Linux detected."

        if [ ! -d ".venv" ]; then
            echo "Creating virtual environment..."
            $PYTHON -m venv .venv
        fi

        echo "Installing dependencies..."
        .venv/bin/python -m pip install -r requirements.txt

        echo "Preparing database..."
        .venv/bin/python manage.py migrate --noinput

        echo "Pick Vick running on port 8000"
        exec .venv/bin/gunicorn pick_vick.wsgi:application --bind 0.0.0.0:8000
        ;;
esac