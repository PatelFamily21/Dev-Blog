#!/bin/bash
# ─────────────────────────────────────────────
#  DevLog — Quick Setup Script
# ─────────────────────────────────────────────

set -e

echo ""
echo "  ██████╗ ███████╗██╗   ██╗██╗      ██████╗  ██████╗ "
echo "  ██╔══██╗██╔════╝██║   ██║██║     ██╔═══██╗██╔════╝ "
echo "  ██║  ██║█████╗  ██║   ██║██║     ██║   ██║██║  ███╗"
echo "  ██║  ██║██╔══╝  ╚██╗ ██╔╝██║     ██║   ██║██║   ██║"
echo "  ██████╔╝███████╗ ╚████╔╝ ███████╗╚██████╔╝╚██████╔╝"
echo "  ╚═════╝ ╚══════╝  ╚═══╝  ╚══════╝ ╚═════╝  ╚═════╝ "
echo ""
echo "  Personal Blog Platform — Setup"
echo "─────────────────────────────────────────────"

# 1. Create and activate virtual environment
echo ""
echo "→ Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
echo "→ Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# 3. Run migrations
echo "→ Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# 4. Create superuser (optional)
echo ""
echo "─────────────────────────────────────────────"
echo "  Would you like to create a superuser? (y/n)"
read -r CREATE_SU
if [[ "$CREATE_SU" == "y" || "$CREATE_SU" == "Y" ]]; then
  python manage.py createsuperuser
fi

# 5. Collect static files
echo "→ Collecting static files..."
python manage.py collectstatic --noinput --quiet 2>/dev/null || true

echo ""
echo "─────────────────────────────────────────────"
echo "  ✓ Setup complete!"
echo ""
echo "  Start the server:"
echo "    source venv/bin/activate"
echo "    python manage.py runserver"
echo ""
echo "  Then open: http://127.0.0.1:8000"
echo "─────────────────────────────────────────────"
