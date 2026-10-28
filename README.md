# Tour & Travel Management API (FastAPI)

Run locally:
    python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    cp .env.example .env     # then export the variables, or set them in your shell
    uvicorn app.main:app --reload
Open http://127.0.0.1:8000/docs  -> click "Authorize" after calling /auth/login.

Deploy: see render.yaml (Render web service) + a Neon Postgres DATABASE_URL.
Tables and the first admin (ADMIN_USERNAME / ADMIN_PASSWORD) are created automatically on first start.
