# DevLog — Personal Developer Blog Platform

A full-featured personal blog built with **Django** and **Tailwind CSS**, styled with GitHub's dark mode color palette.

---

## Features

| Feature | Details |
|---|---|
| **Authentication** | Register, login, logout with password strength meter |
| **User Profiles** | Avatar upload, bio, social links (GitHub, Twitter, website), location |
| **Posts** | Create, read, edit, delete with Markdown-friendly editor |
| **Cover Images** | Optional image uploads per post with drag-and-drop preview |
| **Drafts** | Save posts as drafts before publishing |
| **View Counter** | Session-based unique view tracking per post |
| **Comments** | Authenticated users can comment; authors can delete comments |
| **Tags** | Tag posts and browse by topic |
| **Search** | Full-text search across titles, bodies, authors, and tags |
| **Dashboard** | Stats overview: views, posts, drafts, recent comments |
| **Reading Time** | Auto-calculated based on word count |
| **Pagination** | On home feed, tag pages, and profile pages |
| **Responsive** | Mobile-friendly layout throughout |

---

## Tech Stack

- **Backend:** Django 4.2
- **Styling:** Tailwind CSS (CDN), GitHub dark mode color system
- **Icons:** Feather Icons
- **Fonts:** Inter (body), JetBrains Mono (code)
- **Database:** SQLite (development) — swap for PostgreSQL in production
- **Media:** Django file uploads with Pillow

---

## Quick Start

### Option A — Using the setup script
```bash
chmod +x setup.sh
./setup.sh
```

### Option B — Manual setup
```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py makemigrations
python manage.py migrate

# 4. (Optional) Create admin user
python manage.py createsuperuser

# 5. Start server
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

---

## Project Structure

```
blog_project/
├── manage.py
├── requirements.txt
├── setup.sh
│
├── blog_project/               # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── blog/                       # Main application
│   ├── models.py               # Post, Profile, Comment, Tag
│   ├── views.py                # All view logic
│   ├── forms.py                # All form classes
│   ├── urls.py                 # URL routing
│   └── admin.py                # Admin configuration
│
├── templates/
│   ├── base.html               # Base layout with nav, footer, messages
│   ├── registration/
│   │   ├── login.html
│   │   └── register.html
│   └── blog/
│       ├── home.html           # Feed + sidebar
│       ├── post_detail.html    # Full post + comments
│       ├── post_form.html      # Create / edit post
│       ├── post_confirm_delete.html
│       ├── dashboard.html      # User dashboard
│       ├── profile.html        # Public profile
│       ├── profile_edit.html   # Edit profile
│       └── tag_posts.html      # Posts by tag
│
├── static/                     # CSS, JS, images
└── media/                      # User uploads (avatars, post images)
```

---

## Color System (GitHub Dark Mode)

| Variable | Hex | Usage |
|---|---|---|
| `canvas-default` | `#0d1117` | Page background |
| `canvas-overlay` | `#161b22` | Cards, modals |
| `canvas-subtle` | `#161b22` | Inputs, sidebars |
| `fg-default` | `#e6edf3` | Primary text |
| `fg-muted` | `#7d8590` | Secondary text |
| `border` | `#30363d` | All borders |
| `accent-fg` | `#58a6ff` | Links, tags |
| `accent-emphasis` | `#1f6feb` | Buttons, focus rings |
| `success-fg` | `#3fb950` | Published badge, success messages |
| `danger-fg` | `#f85149` | Errors, delete actions |

---

## Customization

### Change the site name
Edit `base.html` — search for `DevLog` and replace with your preferred name.

### Use PostgreSQL in production
In `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
Also install: `pip install psycopg2-binary`

### Environment variables (production)
Replace the hardcoded `SECRET_KEY` in `settings.py`:
```python
import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-key')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
```

---

## Admin Panel

Access the Django admin at **http://127.0.0.1:8000/admin/** after creating a superuser.
Manage posts, comments, tags, and user profiles from there.

---

## License

MIT — use freely for personal and commercial projects.
