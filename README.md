# KukujeshiStocker

Inventory, POS, and online storefront for small retailers — track stock, sell in person or online, and reconcile automatically.

## Tech Stack
- **Frontend:** React (Vite), Redux Toolkit, React Query, Tailwind CSS v4
- **Backend:** Django 5.2 LTS, Django REST Framework, JWT auth
- **Database:** PostgreSQL (prod) / SQLite (dev)
- **Payments:** Paystack
- **File storage:** Cloudinary

## Backend Setup
```bash
cd backend
python -m venv venv
source venv/Scripts/activate   # Git Bash on Windows
pip install -r requirements.txt
cp .env.example .env           # then fill in real values
python manage.py migrate
python manage.py runserver
```

## Frontend Setup
_Coming in Phase 4._