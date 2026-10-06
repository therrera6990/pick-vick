#!/usr/bin/env bash
set -e

echo "Updating system..."
apt-get update

echo "Installing Python, pip, nginx, and rsync..."
apt-get install -y python3 python3-pip python3-venv nginx rsync

echo "Creating application directory..."
mkdir -p /var/www/pick-vick
chown -R ubuntu:ubuntu /var/www/pick-vick

echo "Installing nginx configuration..."
cp /home/ubuntu/deploy/nginx-pick-vick.conf /etc/nginx/sites-available/pick-vick

ln -sf /etc/nginx/sites-available/pick-vick /etc/nginx/sites-enabled/pick-vick

rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl restart nginx
systemctl enable nginx

echo "Installing systemd service..."
cp /home/ubuntu/deploy/pick-vick.service /etc/systemd/system/pick-vick.service

systemctl daemon-reload
systemctl enable pick-vick.service

echo "EC2 setup complete."