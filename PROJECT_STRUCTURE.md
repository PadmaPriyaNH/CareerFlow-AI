# CareerFlow AI - Project Structure & Documentation

## 📁 Directory Structure

```
CareerFlow AI/
├── 📄 Core Configuration
│   ├── manage.py                      # Django management script
│   ├── requirements.txt               # Python dependencies (with versions)
│   ├── .env.example                  # Environment template (copy to .env)
│   ├── .gitignore                    # Git exclusions
│   ├── .dockerignore                 # Docker exclusions
│   └── README.md                     # Main project documentation
│
├── 🐍 Django Project (config/)
│   ├── settings.py                   # Django settings (production-ready)
│   ├── urls.py                       # Main URL routing
│   ├── wsgi.py                       # WSGI app for deployment
│   └── asgi.py                       # ASGI app for async
│
├── 🎯 Apps
│   ├── accounts/                     # User authentication & profiles
│   │   ├── models.py                 # User models
│   │   ├── views.py                  # Auth views (login, signup, 2FA)
│   │   ├── forms.py                  # Auth forms
│   │   ├── urls.py / urls_two_factor.py
│   │   ├── admin.py                  # Admin configuration
│   │   ├── migrations/               # Database migrations
│   │   └── templates/                # Login, signup, profile templates
│   │
│   ├── interviews/                   # Main interview functionality
│   │   ├── models.py                 # Interview, Question, Answer models
│   │   ├── views.py                  # Interview flow views
│   │   ├── forms.py                  # Interview setup form
│   │   ├── urls.py                   # Interview URLs
│   │   ├── admin.py                  # Admin configuration
│   │   ├── services/
│   │   │   ├── ai_service.py        # ✨ NEW: Provider-agnostic AI service
│   │   │   └── ollama_engine.py     # ⚠️ DEPRECATED: Old Ollama service
│   │   ├── migrations/               # Database migrations
│   │   ├── templates/interviews/     # Interview templates (setup, room, feedback)
│   │   └── tests/                    # App-specific tests
│   │
│   └── core/                         # Dashboard & homepage
│       ├── models.py                 # Core models
│       ├── views.py                  # Dashboard views
│       ├── urls.py                   # Core URLs
│       ├── templates/                # Dashboard templates
│       └── static/                   # CSS, JS, images
│
├── 🧪 Testing
│   ├── tests/                        # Organized test suite
│   │   ├── __init__.py
│   │   └── test_ai_service.py       # Comprehensive AI service tests
│   ├── test_interview_flow.py        # ⚠️ Root level (consider moving)
│   ├── test_ai_service.py            # ⚠️ Root level (moved to tests/)
│   ├── test_ollama.py                # ⚠️ Old Ollama tests (deprecated)
│   ├── test_ollama_fallback.py       # ⚠️ Legacy fallback tests
│   ├── verify_fix.py                 # ⚠️ Old verification script
│   └── diagnose_ai_issue.py          # ⚠️ Old diagnostic script
│
├── 📚 Documentation
│   ├── README.md                     # Main documentation
│   ├── DIRECT_QUESTION_GENERATION.md # Context-based question generation
│   ├── GROQ_INTEGRATION.md           # Groq setup guide
│   ├── IMPLEMENTATION_COMPLETE.md    # Implementation summary
│   ├── QUICK_START.md                # Quick startup guide
│   ├── PROJECT_STRUCTURE.md          # This file
│   ├── AZURE_DEPLOYMENT_GUIDE.md     # Azure deployment
│   ├── AZURE_QUICK_REFERENCE.md      # Azure quick reference
│   ├── AZURE_README.md               # Azure information
│   ├── AZURE_COMPLETE_SETUP.md       # Complete Azure setup
│   ├── AZURE_FREE_DEPLOYMENT.md      # Azure free tier
│   ├── AZURE_FREE_QUICK_START.md     # Azure free quick start
│   ├── AZURE_TROUBLESHOOTING.md      # Azure troubleshooting
│   ├── DEPLOYMENT_COMPLETE.md        # Deployment completion info
│   ├── FREE_DEPLOYMENT_SUMMARY.md    # Free tier summary
│   └── INTERVIEW_FLOW_FIX.md         # Interview flow fixes
│
├── 🐳 Docker & Deployment
│   ├── Dockerfile                    # Development Docker image
│   ├── Dockerfile.prod               # Production Docker image
│   ├── docker-compose.yml            # Local development setup
│   ├── docker-compose.azure.yml      # Azure deployment setup
│   ├── entrypoint.sh                 # Container startup script
│   ├── deploy-azure.ps1              # Azure deployment script
│   ├── deploy-azure-free.ps1         # Azure free tier deploy script
│   └── start_all.ps1                 # Local startup script
│
├── 🔧 CI/CD
│   └── .github/workflows/
│       ├── ci.yml                    # GitHub Actions CI pipeline
│       └── azure-deploy.yml          # GitHub Actions Azure deploy
│
├── 📁 Database & Media
│   ├── db.sqlite3                    # SQLite database (dev only)
│   ├── media/                        # Uploaded resumes
│   │   └── resumes/                  # Resume files
│   └── staticfiles/                  # Collected static files
│
└── 📦 Virtual Environment & Cache
    ├── .venv/                        # Python virtual environment
    └── __pycache__/                  # Python cache (git-ignored)
```

---

## ⚠️ Files Marked for Cleanup

These files are in the root but should be organized or removed:

| File | Status | Action |
|------|--------|--------|
| `test_ai_service.py` | ⚠️ Duplicate | Move to `tests/` |
| `test_interview_flow.py` | ⚠️ Old | Move to `tests/` |
| `test_ollama.py` | ⚠️ Deprecated | Archive or remove |
| `test_ollama_fallback.py` | ⚠️ Deprecated | Archive or remove |
| `verify_fix.py` | ⚠️ Old | Remove (fix is complete) |
| `diagnose_ai_issue.py` | ⚠️ Old | Remove (issue resolved) |
| `start_all.ps1` | ℹ️ Helper | Keep, but document |
| Multiple AZURE_*.md files | ℹ️ Docs | Consider consolidating |

---

## 🚀 Key Files & What They Do

### Configuration
- **`config/settings.py`** - Django settings with production hardening, AI config, Azure storage support
- **`.env.example`** - Template for environment variables (copy to `.env`, never commit `.env`)
- **`requirements.txt`** - All Python dependencies with versions locked for reproducibility

### Application Code
- **`interviews/services/ai_service.py`** - ✨ Core: Provider-agnostic AI service (Groq/Ollama)
- **`interviews/models.py`** - Database models for interviews, questions, answers
- **`interviews/views.py`** - Interview flow: setup, room, feedback
- **`accounts/views.py`** - Authentication with 2FA support

### Testing
- **`tests/test_ai_service.py`** - Comprehensive AI service validation
- **Root test files** - Legacy tests (should be moved or removed)

### Deployment
- **`Dockerfile`** - Development container
- **`Dockerfile.prod`** - Production optimized container
- **`docker-compose.yml`** - Local development with all services
- **`.github/workflows/`** - CI/CD automation (tests + Azure deploy)

---

## 🔄 AI Provider Architecture

```
┌────────────────────────────────────────────┐
│   AIService (ai_service.py)               │
│   Provider-agnostic interface             │
└────────────────┬───────────────────────────┘
      ┌─────────┴────────────┐
      ▼                      ▼
┌──────────────┐      ┌──────────────────┐
│    Groq      │      │     Ollama       │
│  (Cloud)     │      │    (Local)       │
│  1-3 seconds │      │  50-90+ seconds  │
│   Free API   │      │   Free (CPU)     │
└──────────────┘      └──────────────────┘
```

### Methods in AIService
- `is_available()` - Health check (different for each provider)
- `evaluate_answer()` - Score and feedback on interview answers
- `generate_questions()` - Generate interview questions from skills
- `generate_questions_from_context()` - ✨ NEW: Full JD+Role+Resume context
- `parse_resume()` - Extract structured data from resumes

---

## 📋 Environment Configuration

### Required Variables (All)
```env
SECRET_KEY=your-secure-key
DEBUG=False (production)
ALLOWED_HOSTS=your-domain.com
AI_PROVIDER=groq  # or 'ollama'
```

### If Using Groq (Cloud - Recommended)
```env
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile
```

### If Using Ollama (Local)
```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral
```

### For Production Database
```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### For Azure Deployment
```env
USE_AZURE_STORAGE=True
AZURE_ACCOUNT_NAME=...
AZURE_ACCOUNT_KEY=...
```

---

## 🧪 Running Tests

### Run all tests
```bash
pytest tests/ -v
python tests/test_ai_service.py
```

### Run Django tests
```bash
python manage.py test
```

### Test AI service specifically
```bash
python tests/test_ai_service.py
```

---

## 🐳 Docker Commands

### Development
```bash
docker-compose up --build
```

### Production
```bash
docker build -f Dockerfile.prod -t careerflow:latest .
docker run -e SECRET_KEY=... -e DEBUG=False careerflow:latest
```

---

## 📦 Dependencies

### Core
- Django 6.0+ - Web framework
- LangChain - AI abstraction layer
- langchain-groq - Groq provider
- langchain-ollama - Ollama provider

### Authentication
- django-two-factor-auth - 2FA
- django-otp - One-time passwords
- qrcode - QR code generation

### Database
- psycopg2 - PostgreSQL driver
- dj-database-url - Parse DATABASE_URL

### Production
- gunicorn - WSGI server
- whitenoise - Static file serving
- django-cors-headers - CORS support

### Optional
- django-storages[azure] - Azure Blob Storage

See `requirements.txt` for versions.

---

## ✅ Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate strong `SECRET_KEY`
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Use PostgreSQL (not SQLite)
- [ ] Set `GROQ_API_KEY` or configure Ollama
- [ ] Enable HTTPS/SSL
- [ ] Configure Azure storage if needed
- [ ] Run migrations: `python manage.py migrate`
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Run tests: `pytest tests/`
- [ ] Check security: `python manage.py check --deploy`

---

## 🚀 Deployment Paths

1. **Local Development**
   - Copy `.env.example` to `.env`
   - Set `AI_PROVIDER=groq` and add `GROQ_API_KEY`
   - Run: `python manage.py runserver`

2. **Docker Local**
   - Run: `docker-compose up --build`

3. **GitHub + Azure (Automated CI/CD)**
   - Push to GitHub
   - GitHub Actions runs tests automatically
   - On success, deploys to Azure App Service
   - See: `.github/workflows/azure-deploy.yml`

4. **Manual Azure Deployment**
   - Use: `deploy-azure.ps1` or `deploy-azure-free.ps1`
   - Set environment variables in Azure Portal

---

## 📚 Documentation Map

| Document | Purpose |
|----------|---------|
| `README.md` | Getting started, features, setup options |
| `QUICK_START.md` | Fast 5-minute setup |
| `GROQ_INTEGRATION.md` | Groq setup, models, costs |
| `DIRECT_QUESTION_GENERATION.md` | Context-aware question generation |
| `AZURE_DEPLOYMENT_GUIDE.md` | Full Azure setup |
| `AZURE_QUICK_REFERENCE.md` | Quick Azure commands |
| `PROJECT_STRUCTURE.md` | This file - project organization |

---

## 🎯 Quick References

### Start Local Dev
```bash
.venv\Scripts\activate
python manage.py runserver
```

### Start with Docker
```bash
docker-compose up
```

### Test AI Service
```bash
python tests/test_ai_service.py
```

### Deploy to Azure
```bash
.\deploy-azure.ps1
# or
.\deploy-azure-free.ps1 (free tier)
```

---

## 🔐 Security Notes

- ✅ Never commit `.env` file
- ✅ Never hardcode `SECRET_KEY`
- ✅ Use Azure Key Vault for production secrets
- ✅ Enable HTTPS with SSL certificates
- ✅ Rotate API keys quarterly
- ✅ Use secure, long passwords
- ✅ Enable 2FA for all users
- ✅ Monitor logs for suspicious activity

---

## 📞 Support & Troubleshooting

- **Groq Issues**: Check `GROQ_INTEGRATION.md` and `AZURE_TROUBLESHOOTING.md`
- **Ollama Issues**: Ensure `ollama serve` is running
- **Database Issues**: Check `DATABASE_URL` format
- **Azure Issues**: See `AZURE_TROUBLESHOOTING.md`
- **Test Failures**: Run `pytest tests/ -v` for detailed output

---

## 🎉 Project Status

✅ **Fully Functional**
- Resume parsing with AI
- Interview question generation (standard + context-aware)
- Answer evaluation with scoring
- Beautiful responsive UI
- 2FA authentication
- Production-ready deployment

✅ **Production Ready**
- Proper settings for deployment
- Docker support (dev + prod)
- GitHub Actions CI/CD
- Azure deployment tested
- Security hardening enabled

---

This document last updated: February 2026
