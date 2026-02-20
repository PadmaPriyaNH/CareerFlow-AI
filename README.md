
# CareerFlow AI 🚀

**CareerFlow AI** is a modern, secure, and AI-powered mock interview platform. It helps users practice interviews, get instant AI feedback, and improve their career readiness—all with a beautiful, intuitive interface.

---

## ✨ Features
- **AI-Powered Mock Interviews:** Upload your resume, set your target role, and get tailored interview questions and instant AI feedback (Ollama backend, local or cloud).
- **Resume Parsing:** Extracts and analyzes your resume (PDF/DOCX) to generate relevant questions.
- **Modern, Responsive UI:** Beautiful Bootstrap 5 design, mobile-friendly, and easy to use.
- **Secure Authentication:** Login/signup with email or username, 2FA (two-factor authentication), and robust password reset flow.
- Admin: Django admin available at `/admin/` (enable 2FA for staff in production).
- **Production-Ready:** Dockerized, supports Postgres, static/media file handling, and secure by default.

---

## 🚀 Quick Start

### Option 1: Complete Local Setup (Recommended for Development)

**Step 1: Install Ollama**
1. Download Ollama from [ollama.ai](https://ollama.ai)
2. Install and run it
3. Pull the Mistral model:
```bash
ollama pull mistral
```
4. Start Ollama service (it will run on `http://localhost:11434`):
```bash
ollama serve
```

**Step 2: Setup Django Project**
```bash
# 1. Activate virtual environment
.\.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment file
cp .env.example .env
# Edit .env and set: SECRET_KEY, DEBUG=True, ALLOWED_HOSTS=localhost,127.0.0.1

# 4. Run migrations
python manage.py migrate

# 5. Collect static files
python manage.py collectstatic --noinput

# 6. Create superuser (admin)
python manage.py createsuperuser
```

**Step 3: Start Django Server**
```bash
python manage.py runserver
```

**Step 4: Access the Application**
- **Web App:** http://localhost:8000
- **Admin:** http://localhost:8000/admin/
- **Login:** Use the superuser credentials you created

### Option 2: Docker Compose (All-in-One)
```bash
docker compose up --build
# App: http://localhost:8000
# Admin: http://localhost:8000/admin/
```

---

## ⚙️ Configuration
- **.env:** Copy `.env.example` to `.env` and set all required variables.
- **AI Model:**
  - Defaults to Ollama locally (`OLLAMA_HOST=http://localhost:11434`).
  - For local development, ensure the model is available: `ollama pull mistral` and make sure Ollama is running (`ollama serve`).
  - With Docker Compose, the `ollama` service is included and the web app points to `http://ollama:11434` automatically.
- **Database:** Uses SQLite by default, or Postgres via Docker/`DATABASE_URL`.
- **Static/Media:** Handled by Whitenoise and Django settings.

---

## 🛡️ Security & Best Practices
- 2FA (two-factor) for all users and admin.
- Admin at `/admin/`. You can change the admin URL by updating `config/urls.py` if desired.
- Strong password validation, secure cookies, HSTS, and SSL by default in production.
- All sensitive settings via environment variables.

---

## 🧪 Testing & CI
- Run tests: `python manage.py test`
- GitHub Actions CI: see `.github/workflows/ci.yml` (runs tests, migrations, linting)

---

## ☁️ Deploy to Azure (or any cloud)
1. Create an Azure Web App (Linux) or Web App for Containers.
2. Add your Azure Publish Profile as `AZURE_WEBAPP_PUBLISH_PROFILE` in GitHub repo secrets.
3. Set `AZURE_WEBAPP_NAME` secret to your web app name.
4. Push to `main` — GitHub Actions will build and deploy automatically.

**Production tips:**
- Use a managed Postgres DB and set `DATABASE_URL`.
- Set `DEBUG=False` and a strong `SECRET_KEY`.
- Set `ALLOWED_HOSTS` to your domain.
- Configure HTTPS and rotate secrets regularly.

---

## 📦 Optional: Azure Blob Storage for MEDIA
If you want uploaded MEDIA files (e.g., resumes) to be stored in Azure Blob Storage instead of local disk:

- Installation: already included in `requirements.txt` as `django-storages[azure]`.
- Set environment variables (in Azure App Settings or your `.env` file):
  - `USE_AZURE_STORAGE=True`
  - `AZURE_ACCOUNT_NAME=youraccount`
  - `AZURE_ACCOUNT_KEY=yourkey`
  - `AZURE_CONTAINER=media` (default)
  - `AZURE_CUSTOM_DOMAIN=youraccount.blob.core.windows.net` (optional; used to build MEDIA URLs)
- Static files continue to be served by WhiteNoise from the container image; only MEDIA is offloaded to Azure.

## 🤝 Contributing
Pull requests are welcome! Please open an issue to discuss major changes first.

---

## 📄 License
This project is licensed under the MIT License.

---
