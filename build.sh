#!/usr/bin/env bash
# Render runs this script every time it deploys your app.
# Exit immediately if any command fails.
set -o errexit

echo "── Installing Python dependencies ──"
pip install -r requirements.txt

echo "── Collecting static files ──"
python manage.py collectstatic --no-input

echo "── Applying database migrations ──"
python manage.py migrate

echo "── Build complete ✓ ──"