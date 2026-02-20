# CareerFlow AI - Quick Start Guide

## 🎯 Complete Setup in 5 Steps

### Prerequisites
- Python 3.8+ installed
- Ollama installed from [ollama.ai](https://ollama.ai)
- Git (optional)

---

## Step 1: Start Ollama Service (Terminal 1)

```powershell
# This starts the AI backend
ollama serve
```

**Expected Output:**
```
2026/02/20 13:00:00 routes.go:1055: INFO server config env="map[OLLAMA_NUM_GPU:1 OLLAMA_ORIGINS:* OLLAMA_SECURITY:false]"
```

**Wait for this message:** `Listening on 127.0.0.1:11434`

---

## Step 2: Pull Mistral Model (Terminal 2)

```powershell
ollama pull mistral
```

**This downloads the AI model (takes 5-10 minutes first time)**

---

## Step 3: Setup Python Environment (Terminal 3)

```powershell
# Navigate to project folder
cd "C:\Users\user\OneDrive\Desktop\CareerFlow AI"

# Activate virtual environment
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 4: Setup Database & Configuration

```powershell
# Create/update database
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create admin user (follow prompts)
python manage.py createsuperuser
```

---

## Step 5: Start Django Server (Terminal 3)

```powershell
python manage.py runserver
```

**Expected Output:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

## 🎉 You're Ready!

| Component | URL | Status |
|-----------|-----|--------|
| **Web App** | http://localhost:8000 | ✅ Running |
| **Admin** | http://localhost:8000/admin/ | ✅ Running |
| **Ollama AI** | http://localhost:11434 | ✅ Running |

---

## 📋 Terminal Setup (Recommended)

Open **4 PowerShell windows** simultaneously:

### Terminal 1: Ollama Service
```powershell
ollama serve
```

### Terminal 2: Model Download (First Time Only)
```powershell
ollama pull mistral
```

### Terminal 3: Django Server
```powershell
cd "C:\Users\user\OneDrive\Desktop\CareerFlow AI"
.\.venv\Scripts\activate
python manage.py runserver
```

### Terminal 4: Monitoring (Optional)
```powershell
# Monitor Django logs or run tests
cd "C:\Users\user\OneDrive\Desktop\CareerFlow AI"
.\.venv\Scripts\activate
python manage.py test
```

---

## 🧪 Test the Setup

1. Open http://localhost:8000
2. Create a user account
3. Upload a resume (PDF/DOCX)
4. Click "Start Interview"
5. Answer a question
6. **You should get AI feedback within 30-50 seconds**

---

## ⚠️ Troubleshooting

### Ollama Not Starting
```powershell
# Check if port 11434 is in use
netstat -ano | findstr :11434

# Kill process if needed
taskkill /PID <PID> /F

# Restart Ollama
ollama serve
```

### Django Migration Error
```powershell
# Reset database
del db.sqlite3
python manage.py migrate
```

### Model Not Found Error
```powershell
# Ensure model is downloaded
ollama pull mistral

# Verify with
curl -s http://localhost:11434/api/tags | python -m json.tool
```

### Port Already in Use
```powershell
# Use different port
python manage.py runserver 8001
```

---

## 📚 Environment Configuration

Edit `.env` file:

```env
# Django
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral

# Database
DB_NAME=db.sqlite3
```

---

## 🚀 Next Steps

- Upload a resume (PDF or DOCX)
- Set target job role
- Start an interview
- Get AI feedback on your answers
- Check `/admin/` to see response analytics

Happy interviewing! 🎉
