
# CareerFlow AI 🚀

**CareerFlow AI** is a modern, secure, and AI-powered mock interview platform. It helps users practice interviews, get instant AI feedback, and improve their career readiness—all with a beautiful, intuitive interface.

**NEW:** Now powered by **Groq** (fast cloud AI) with **Ollama** as an optional fallback! Get interview feedback in **1-3 seconds** instead of 50-90 seconds. ⚡

---

## ✨ Features
- **AI-Powered Mock Interviews:** Upload your resume, set your target role, and get tailored interview questions with instant AI feedback.
  - **Groq** (recommended): Fast cloud AI, 1-3 second response times
  - **Ollama** (alternative): Local AI, offline support, free (uses your hardware)
- **Resume Parsing:** Extracts and analyzes your resume (PDF/DOCX) to generate relevant questions.
- **Modern, Responsive UI:** Beautiful Bootstrap 5 design, mobile-friendly, and intuitive.
- **Secure Authentication:** Login/signup with email or username, 2FA (two-factor authentication), password reset flow.
- **Admin Dashboard:** Django admin at `/admin/` (enable 2FA for staff in production).
- **Production-Ready:** Dockerized, Postgres support, static/media file handling, secure by default.

---

## 🚀 Quick Start

### Choose Your AI Provider

| Feature | Groq ⚡ | Ollama 🖥️ |
|---------|--------|---------|
| **Response Time** | 1-3 seconds | 50-90+ seconds |
| **Setup Time** | 2 minutes | 10+ minutes |
| **API Key** | Required (free) | Not needed |
| **Offline** | ❌ No | ✅ Yes |
| **Cost** | Free tier (~30 req/min) | Free (your hardware) |
| **Recommended** | ✅ Yes | For local dev |

---

## 📋 Prerequisites

```powershell
# You'll need:
# - Python 3.13+
# - Git
# - (For Groq) Free API key from https://console.groq.com
# - (For Ollama) Ollama installed from https://ollama.ai
```

---

## 🎯 Setup & Run

### Option 1: Local Development with Groq (Fastest - Recommended)

**Step 1: Get Groq API Key**
```
1. Visit: https://console.groq.com
2. Sign up (free)
3. Go to API Keys → Create New Key
4. Copy the key (looks like: gsk_...)
```

**Step 2: Clone & Setup Project**
```powershell
# Clone the repo
git clone <your-repo-url>
cd "CareerFlow AI"

# Create virtual environment (if not already done)
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Step 3: Configure Environment**
```powershell
# Copy example env file
cp .env.example .env

# Edit .env with:
AI_PROVIDER=groq
GROQ_API_KEY=gsk_your_actual_key_here
GROQ_MODEL=mistral-7b-instruct-v0.2
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Step 4: Initialize Database**
```powershell
# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create admin/superuser account
python manage.py createsuperuser
```

**Step 5: Run Tests (Optional)**
```powershell
# Verify AI service works with Groq
python test_ai_service.py

# You should see: [TEST 1] Status: ✓ AVAILABLE
```

**Step 6: Start Django Server**
```powershell
python manage.py runserver
```

**Step 7: Access Application**
- **Web App:** http://localhost:8000
- **Admin:** http://localhost:8000/admin/
- **Login:** Use superuser credentials

---

### Option 2: Local Development with Ollama (Offline)

**Step 1: Install & Start Ollama**
```powershell
# Download from: https://ollama.ai
# OR on Windows: Download installer and run

# In one terminal window, start Ollama:
ollama serve

# In another terminal, pull the Mistral model:
ollama pull mistral
```

**Step 2: Clone & Setup Project**
```powershell
# Clone the repo
git clone <your-repo-url>
cd "CareerFlow AI"

# Activate virtual environment
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Step 3: Configure Environment**
```powershell
# Edit .env with:
AI_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Step 4: Initialize Database & Run Server**
```powershell
# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

**Step 5: Access Application**
- **Web App:** http://localhost:8000
- **Admin:** http://localhost:8000/admin/

**⚠️ Note:** Feedback takes 50-90+ seconds with Ollama (CPU inference)

---

### Option 3: Docker Compose (All-in-One)

```powershell
# Make sure .env file exists with your settings:
cp .env.example .env
# Edit .env with your AI_PROVIDER choice and keys

# Start all services
docker compose up --build

# Access:
# - App: http://localhost:8000
# - Admin: http://localhost:8000/admin/
```

**With Groq in Docker:**
```yaml
# .env for Docker:
AI_PROVIDER=groq
GROQ_API_KEY=gsk_your_key
GROQ_MODEL=mistral-7b-instruct-v0.2
DEBUG=False
SECRET_KEY=your-long-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

**With Ollama in Docker:**
```yaml
# .env for Docker with Ollama:
AI_PROVIDER=ollama
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=mistral
DEBUG=False
SECRET_KEY=your-long-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## ⚙️ Configuration

### Environment Variables

```env
# AI Provider Selection
AI_PROVIDER=groq              # or 'ollama'

# For Groq (Cloud AI)
GROQ_API_KEY=gsk_...          # Get from https://console.groq.com
GROQ_MODEL=mistral-7b-instruct-v0.2  # or other Groq models

# For Ollama (Local AI)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral          # or other Ollama models

# Django Settings
DEBUG=True                     # False for production
SECRET_KEY=your-secret-key    # Generate: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional - defaults to SQLite)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# 2FA (optional)
TWO_FACTOR_ENABLED=True
```

### File Structure
```
.
├── manage.py                 # Django management
├── requirements.txt          # Python dependencies
├── .env.example             # Example environment file
├── Dockerfile               # Docker image configuration
├── docker-compose.yml       # Docker Compose for local dev
├── config/                  # Django settings
├── interviews/              # Interview app
│   ├── models.py           # Interview & Answer models
│   ├── views.py            # Interview views
│   ├── services/
│   │   └── ai_service.py   # Provider-agnostic AI service (NEW)
│   └── templates/
├── accounts/                # User authentication
│   ├── models.py
│   ├── views.py
│   └── templates/
├── core/                    # Dashboard & home
└── media/                   # User uploads (resumes)
```

### Database
- **Development:** SQLite (default, no setup needed)
- **Production:** PostgreSQL (via `DATABASE_URL` env var)

### Static & Media Files
- **Static:** WhiteNoise handles in development and production
- **Media:** Local disk by default, or Azure Blob Storage (set `USE_AZURE_STORAGE=True`)


---

## 🛡️ Security & Best Practices

### Development
- ✅ Use `.env` for all secrets (never commit it!)
- ✅ Keep `DEBUG=True` only in development
- ✅ Use random `SECRET_KEY` (run: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- ✅ Enable 2FA (two-factor authentication) for all user accounts
- ✅ Change the admin URL from `/admin/` if desired (edit `config/urls.py`)

### Production
- ✅ Set `DEBUG=False`
- ✅ Generate strong `SECRET_KEY`
- ✅ Use HTTPS/SSL
- ✅ Set appropriate `ALLOWED_HOSTS`
- ✅ Use managed database (PostgreSQL on Azure, AWS RDS, etc.)
- ✅ Store secrets in Azure Key Vault or environment configuration (never in code)
- ✅ Rotate API keys regularly (especially Groq keys)
- ✅ Enable HSTS, secure cookies, and CSRF protection (Django defaults)
- ✅ Keep dependencies updated: `pip install --upgrade -r requirements.txt`

### Groq API Key Safety
- 🔐 Never commit `.env` file to Git
- 🔐 Never expose API key in logs or error messages
- 🔐 Rotate keys quarterly
- 🔐 Monitor usage in Groq console (free tier limits)
- 🔐 Use environment variables in production, not hardcoded values

---

## 🧪 Testing

### Run Django Tests
```powershell
# Test all apps
python manage.py test

# Test specific app
python manage.py test interviews

# Test with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Test AI Service
```powershell
# Verify AI provider works (Groq or Ollama)
python test_ai_service.py

# Should output:
# [TEST 1] AI Provider: GROQ (or OLLAMA)
# [TEST 1] Status: ✓ AVAILABLE
# [TEST 2] Testing Resume Parsing... ✓
# [TEST 3] Testing Answer Evaluation... ✓
# [TEST 4] Testing Question Generation... ✓
```

### Manual Testing Checklist
- [ ] Create account and 2FA
- [ ] Upload resume (PDF or DOCX)
- [ ] Answer sample interview question
- [ ] Verify AI feedback appears in <3s (Groq) or <90s (Ollama)
- [ ] Check score ranges 0-10 with feedback
- [ ] Test on mobile (responsive design)
- [ ] Try wrong credentials (error handling)
- [ ] Admin login and user management

---

## ☁️ Deploy to Azure

### Quick Deploy (Manual)

```powershell
# Prerequisites:
# - Azure account with subscription
# - Azure CLI installed (az login)

# 1. Create resource group
az group create --name careerflow-rg --location eastus

# 2. Create App Service plan (free tier)
az appservice plan create -g careerflow-rg -n careerflow-plan --sku F1 --is-linux

# 3. Create web app
az webapp create -g careerflow-rg -p careerflow-plan -n careerflow-ai --runtime "python|3.11"

# 4. Configure environment variables
az webapp config appsettings set -g careerflow-rg -n careerflow-ai --settings \
  AI_PROVIDER=groq \
  GROQ_API_KEY=gsk_your_key \
  GROQ_MODEL=mistral-7b-instruct-v0.2 \
  DEBUG=False \
  SECRET_KEY=your-long-secret-key \
  ALLOWED_HOSTS=careerflow-ai.azurewebsites.net

# 5. Deploy code
az webapp deployment source config-zip -g careerflow-rg -n careerflow-ai --src <your-zip-file>
```

### Automated Deploy (GitHub Actions)

1. Add Azure publish profile as `AZURE_WEBAPP_PUBLISH_PROFILE` secret in GitHub
2. Push to `main` branch — GitHub Actions automatically deploys
3. Set environment variables in Azure Portal (App Configuration)

### Production Configuration

In **Azure Portal → App Settings**, set these variables:

```env
AI_PROVIDER=groq
GROQ_API_KEY=gsk_your_actual_key
GROQ_MODEL=mistral-7b-instruct-v0.2
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=careerflow-ai.azurewebsites.net
DATABASE_URL=postgresql://user:pass@server.postgres.database.azure.com:5432/dbname
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=strong_password
DJANGO_SUPERUSER_EMAIL=admin@example.com
```

### Using Azure Database for PostgreSQL

```powershell
# 1. Create PostgreSQL server
az postgres flexible-server create -g careerflow-rg -n careerflow-db

# 2. Create database
az postgres flexible-server db create -g careerflow-rg -s careerflow-db -d careerflowdb

# 3. Set DATABASE_URL in App Settings:
postgresql://username:password@careerflow-db.postgres.database.azure.com:5432/careerflowdb

# 4. Run migrations on server (via SSH or app startup script)
```

---

## 📦 Optional: Azure Blob Storage for Resumes

Store uploaded resume files in Azure Blob Storage instead of local disk:

```env
# Enable Azure Storage
USE_AZURE_STORAGE=True
AZURE_ACCOUNT_NAME=youraccount
AZURE_ACCOUNT_KEY=yourkey
AZURE_CONTAINER=media
AZURE_CUSTOM_DOMAIN=youraccount.blob.core.windows.net
```

**Note:** Static files (CSS, JS) are served by WhiteNoise; only MEDIA files go to Azure Blob Storage.

---

## 🔄 How It Works

### Interview Flow
```
1. User creates account & sets up 2FA
   ↓
2. User uploads resume (PDF/DOCX)
   ↓
3. AI parses resume → extracts skills, experience
   ↓
4. User enters target role & job description
   ↓
5. AI generates 10 tailored interview questions
   ↓
6. User answers questions one by one
   ↓
7. For each answer:
   - Sent to Groq (1-3s) or Ollama (50-90s)
   - AI scores 0-10 with detailed feedback
   - Feedback displayed to user
   ↓
8. Interview complete → overall score & summary
```

### AI Provider Selection
```
Application starts
   ↓
Check AI_PROVIDER env variable
   ├─ If "groq" → Load Groq ChatGroq with GROQ_API_KEY
   └─ If "ollama" → Load Ollama ChatOllama with OLLAMA_HOST
   ↓
User submits answer
   ↓
AIService checks if provider available (API call or HTTP check)
   ├─ If available → Evaluate with selected provider
   └─ If unavailable → Fall back to default feedback
   ↓
Return score + feedback to user
```

---

## 📚 Documentation

- **[GROQ_INTEGRATION.md](GROQ_INTEGRATION.md)** — Complete Groq setup guide, troubleshooting
- **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** — What was implemented and how
- **[AZURE_QUICK_REFERENCE.md](AZURE_QUICK_REFERENCE.md)** — Azure deployment reference
- **Code Comments** — All source code is well-documented
- **Docstrings** — All functions have clear docstrings

---

## 🤝 Contributing

Pull requests welcome! Please:
1. Create a new branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Run tests: `python manage.py test`
4. Commit: `git commit -am 'Add feature'`
5. Push: `git push origin feature/your-feature`
6. Open a Pull Request

---

## ❓ FAQ

**Q: Which AI provider should I use?**
A: **Groq** for production (1-3s, cloud). **Ollama** for local dev/offline (free but slower on CPU).

**Q: Do I need both Groq and Ollama?**
A: No, choose one. Set `AI_PROVIDER` and provide either `GROQ_API_KEY` or `OLLAMA_HOST`.

**Q: How much does Groq cost?**
A: Free tier ~30 requests/minute. Perfect for personal projects. Pay-as-you-go at scale.

**Q: Can I switch providers easily?**
A: Yes! Just change `AI_PROVIDER=groq` to `AI_PROVIDER=ollama` in `.env` and restart.

**Q: Will my code break if I switch?**
A: No! The `AIService` abstraction handles both providers transparently.

**Q: How do I get a Groq API key?**
A: Visit https://console.groq.com → Sign up (free) → API Keys → Create Key

**Q: Can I use different Groq models?**
A: Yes, set `GROQ_MODEL=mixtral-8x7b-32768` or any Groq-supported model.

**Q: Does this work on Azure Free Tier (F1)?**
A: Yes! Groq handles the heavy LLM work; Django just needs a basic App Service.

**Q: What if Groq goes down?**
A: Fallback to default questions and neutral 6/10 score (graceful degradation).

**Q: How do I test locally before deploying?**
A: Run `python test_ai_service.py` to verify AI service works with your provider.

**Q: Can I use Azure storage for resume uploads?**
A: Yes, set `USE_AZURE_STORAGE=True` and configure Azure Blob Storage credentials.

**Q: How do I enable/disable 2FA for users?**
A: In Django admin → Users → Edit user → Check "2FA Enabled"

**Q: What Python version is required?**
A: Python 3.11+ (tested with 3.11, 3.12, 3.13)

---

## 📦 Dependencies

Key packages:
- **Django 6.0+** — Web framework
- **LangChain** — LLM abstraction layer
- **langchain-groq** — Groq provider
- **langchain-ollama** — Ollama provider
- **django-cors-headers** — CORS support
- **python-decouple** — Environment variable management
- **django-storages[azure]** — Azure Blob Storage support
- **psycopg2** — PostgreSQL driver
- **whitenoise** — Static file serving

See `requirements.txt` for full list.

---

## 🚀 Performance Tips

### For Groq (Default)
- ✅ Response times: 1-3 seconds
- ✅ No GPU needed
- ✅ No local setup required
- ✅ Works on free Azure tier

### For Ollama (Alternative)
- ✅ Offline support
- ✅ No API key needed
- ⚠️ Requires GPU for fast inference (CPU is slow)
- ⚠️ Takes 50-90+ seconds per answer on CPU

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

---

## 🎉 Ready to Go!

Your CareerFlow AI platform is now ready for deployment. Choose your AI provider, configure `.env`, and start conducting AI-powered interviews! 🚀

For questions or issues, see [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) or check our troubleshooting guides.
