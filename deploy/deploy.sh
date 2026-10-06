#!/usr/bin/env bash
set -e

HOST=""
KEY=""

while getopts "h:i:" opt; do
    case $opt in
        h) HOST="$OPTARG" ;;
        i) KEY="$OPTARG" ;;
        *)
            echo "Usage: $0 -h <PUBLIC-IP> -i <KEY.pem>"
            exit 1
            ;;
    esac
done

if [ -z "$HOST" ] || [ -z "$KEY" ]; then
    echo "Usage: $0 -h <PUBLIC-IP> -i <KEY.pem>"
    exit 1
fi

echo "Deploying Pick Vick to $HOST..."

echo "Copying files to EC2..."
rsync -avz \
    --exclude ".git" \
    --exclude ".env" \
    --exclude "*.pem" \
    --exclude "__pycache__" \
    -e "ssh -i \"$KEY\"" \
    ./ ubuntu@"$HOST":/var/www/pick-vick/

echo "Installing dependencies..."
ssh -i "$KEY" ubuntu@"$HOST" \
    "cd /var/www/pick-vick && python3 -m pip install -r requirements.txt --break-system-packages"

echo "Running migrations..."
ssh -i "$KEY" ubuntu@"$HOST" \
    "cd /var/www/pick-vick && python3 manage.py migrate --noinput"

echo "Restarting Pick Vick..."
ssh -i "$KEY" ubuntu@"$HOST" \
    "sudo systemctl restart pick-vick.service"

echo "Checking site..."
sleep 3

if curl -f "http://$HOST/" >/dev/null 2>&1; then
    echo "Deployment successful!"
    echo "Open: http://$HOST/"
else
    echo "Deployment finished, but the site check failed."
    echo "Check with: sudo systemctl status pick-vick.service"
    exit 1
fi