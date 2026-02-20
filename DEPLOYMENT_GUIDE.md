# CareerFlow AI - Complete Deployment Guide

**Deploy to GitHub & Microsoft Azure in 30 minutes!**

---

## 📋 Prerequisites

- ✅ GitHub account (get one at github.com)
- ✅ Microsoft Azure account (free account: azure.microsoft.com/free)
- ✅ Azure CLI installed (`az --version`)
- ✅ Git installed (`git --version`)
- ✅ Groq API key (free from console.groq.com)
- ✅ Local project working with `python manage.py runserver`

---

## 🚀 Quick Deploy (All Steps)

### Step 1: Prepare Your GitHub Repository

```powershell
# Initialize git (if not already done)
git init
git config user.name "Your Name"
git config user.email "your@email.com"
git remote add origin https://github.com/YOUR_USERNAME/careerflow-ai.git

# Add all files EXCEPT .env
git add .
git commit -m "Initial commit: CareerFlow AI with Groq integration"

# Push to GitHub
git branch -M main
git push -u origin main
```

**Important:** Never commit `.env` file! The `.gitignore` prevents this automatically.

---

### Step 2: Create Azure Resources

```powershell
# 1. Login to Azure
az login

# 2. Create Resource Group
az group create --name careerflow-rg --location eastus

# 3. Create App Service Plan (Free Tier)
az appservice plan create `
  --name careerflow-plan `
  --resource-group careerflow-rg `
  --sku F1 `
  --is-linux

# 4. Create App Service
az webapp create `
  --name careerflow-ai `
  --resource-group careerflow-rg `
  --plan careerflow-plan `
  --runtime "python:3.11"

# 5. Create PostgreSQL Database (Optional - for production)
az postgres server create `
  --resource-group careerflow-rg `
  --name careerflow-db `
  --location eastus `
  --admin-user adminuser `
  --admin-password YourSecurePassword123 `
  --sku-name B_Gen5_1 `
  --storage-mb 51200

# 6. Configure app settings
az webapp config appsettings set `
  --resource-group careerflow-rg `
  --name careerflow-ai `
  --settings `
    SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" `
    DEBUG=False `
    ALLOWED_HOSTS=careerflow-ai.azurewebsites.net `
    AI_PROVIDER=groq `
    GROQ_API_KEY=gsk_YOUR_API_KEY_HERE `
    GROQ_MODEL=llama-3.3-70b-versatile
```

---

### Step 3: Enable GitHub Actions CI/CD

The project includes GitHub Actions workflows that automatically:
1. Run tests on every commit
2. Deploy to Azure on successful tests
3. Monitor deployment status

**Setup is automatic** - just push to GitHub!

The workflows are in:
- `.github/workflows/ci.yml` - Runs tests
- `.github/workflows/azure-deploy.yml` - Deploys to Azure

---

### Step 4: First Deployment

```powershell
# Push to GitHub (this triggers CI/CD automatically)
git push origin main

# Watch the deployment
# 1. Go to GitHub.com → Your Repo → Actions tab
# 2. Click the workflow run
# 3. Watch logs in real-time
# 4. Check Azure Portal for app status
```

---

### Step 5: Access Your Application

```
Web App: https://careerflow-ai.azurewebsites.net
Admin: https://careerflow-ai.azurewebsites.net/admin
```

Create superuser:
```powershell
az webapp remote-connection create `
  --resource-group careerflow-rg `
  --name careerflow-ai

# In the SSH connection:
python manage.py createsuperuser
```

---

## 🔧 Manual Deployment (If CI/CD Fails)

### Option A: Using deployment script

```powershell
.\deploy-azure.ps1
# or for free tier
.\deploy-azure-free.ps1
```

### Option B: Manual Azure CLI

```powershell
# 1. Build deployment package
$zipFile = "careerflow.zip"
$excludeFiles = @(".env", ".venv", "db.sqlite3", "*.pyc", "__pycache__", "node_modules", ".git")

# 2. Zip project (Windows)
Compress-Archive -Path .\ -DestinationPath $zipFile -Force

# 3. Deploy
az webapp deployment source config-zip `
  --resource-group careerflow-rg `
  --name careerflow-ai `
  --src $zipFile

# 4. Restart app
az webapp restart `
  --resource-group careerflow-rg `
  --name careerflow-ai
```

---

## 📊 Using PostgreSQL Database (Production)

The free tier SQLite works, but PostgreSQL is recommended for production.

### Create PostgreSQL

```powershell
# Create flexible server (cheaper than single server)
az postgres flexible-server create `
  --resource-group careerflow-rg `
  --name careerflow-db `
  --location eastus `
  --admin-user adminuser `
  --admin-password YourSecurePassword123 `
  --sku-name Standard_B1ms

# Create database
az postgres flexible-server db create `
  --resource-group careerflow-rg `
  --server-name careerflow-db `
  --database-name careerflow
```

### Connect to Database

Get connection string:
```powershell
az postgres flexible-server show-connection-string `
  --server-name careerflow-db `
  --admin-user adminuser `
  --database-name careerflow
```

In Azure Portal → App Settings, set:
```
DATABASE_URL=postgresql://adminuser:password@careerflow-db.postgres.database.azure.com:5432/careerflow
```

---

## 💾 Azure Blob Storage for Resumes

For production, store resumes in cloud storage:

### Create Storage Account

```powershell
# Create storage account
az storage account create `
  --name careerflowstorage `
  --resource-group careerflow-rg `
  --location eastus

# Get connection string
az storage account show-connection-string `
  --name careerflowstorage `
  --resource-group careerflow-rg
```

### Configure in App Settings

```powershell
az webapp config appsettings set `
  --resource-group careerflow-rg `
  --name careerflow-ai `
  --settings `
    USE_AZURE_STORAGE=True `
    AZURE_ACCOUNT_NAME=careerflowstorage `
    AZURE_ACCOUNT_KEY=YOUR_ACCOUNT_KEY `
    AZURE_CONTAINER=media
```

---

## 🔍 Monitoring & Troubleshooting

### View Application Logs

```powershell
# Stream logs in real-time
az webapp log tail `
  --resource-group careerflow-rg `
  --name careerflow-ai

# Or view in Portal:
# Azure Portal → careerflow-ai → Log stream
```

### Run Migrations

```powershell
# Connect via SSH
az webapp remote-connection create `
  --resource-group careerflow-rg `
  --name careerflow-ai

# In SSH session:
python manage.py migrate
python manage.py collectstatic --noinput
```

### Reset Database

```powershell
# In SSH session
python manage.py flush --noinput
python manage.py migrate
python manage.py createsuperuser
```

### Check App Health

```powershell
# Test endpoint
curl https://careerflow-ai.azurewebsites.net/health

# Or use Azure Portal:
# careerflow-ai → Overview → URL
```

---

## 🚨 Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| App crashes on startup | Migration not run | `az webapp remote-connection create` → `python manage.py migrate` |
| 500 errors | SECRET_KEY not set | Check App Settings in Portal |
| Groq not working | API key invalid | Update GROQ_API_KEY in App Settings |
| Resume upload fails | Azure storage not configured | Set USE_AZURE_STORAGE=True and credentials |
| Static files missing | Not collected | `python manage.py collectstatic` |

---

## 🔐 Security Checklist

✅ **Before Deployment:**
- [ ] Set strong `SECRET_KEY`
- [ ] Set `DEBUG=False`
- [ ] Set appropriate `ALLOWED_HOSTS`
- [ ] Use PostgreSQL (not SQLite)
- [ ] Enable HTTPS (automatic with Azure)
- [ ] Rotate `GROQ_API_KEY` quarterly
- [ ] Use Azure Key Vault for secrets (advanced)
- [ ] Enable diagnostic logs
- [ ] Set up monitoring alerts

---

## 📈 Performance Optimization

### Static Files
WhiteNoise handles static files - no additional setup needed.

### Media Files
Use Azure Blob Storage for scalability:
```
USE_AZURE_STORAGE=True
AZURE_ACCOUNT_NAME=...
AZURE_ACCOUNT_KEY=...
```

### Database
PostgreSQL much  faster than SQLite:
```
DATABASE_URL=postgresql://...
```

### Caching
Add Redis for interviews (optional):
```python
# Add to settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

---

## 🔄 GitHub Actions Workflow

The CI/CD pipeline automatically:

1. **Triggers on:** Push to main branch
2. **Runs:** Tests in Python 3.11 environment
3. **On Success:** Builds and deploys to Azure
4. **On Failure:** Sends notification (check Actions tab)

View workflow details:
- `.github/workflows/ci.yml`
- `.github/workflows/azure-deploy.yml`

---

## 🌐 Custom Domain

To use your own domain instead of `azurewebsites.net`:

```powershell
# 1. Point domain to Azure (update DNS records)
#    DNS CNAME: yoursite.com → careerflow-ai.azurewebsites.net

# 2. Add custom domain to Azure App
az webapp config hostname add `
  --resource-group careerflow-rg `
  --webapp-name careerflow-ai `
  --hostname yoursite.com

# 3. Add SSL certificate (automatic with Azure)
```

---

## 📝 Environment Variables Reference

### Required
```
SECRET_KEY=long-random-string
DEBUG=False
ALLOWED_HOSTS=careerflow-ai.azurewebsites.net OR yourdomain.com
AI_PROVIDER=groq
GROQ_API_KEY=gsk_...
```

### Optional but Recommended
```
DATABASE_URL=postgresql://user:pass@host/dbname
USE_AZURE_STORAGE=True
AZURE_ACCOUNT_NAME=...
AZURE_ACCOUNT_KEY=...
```

See `.env.example` for all options.

---

## 🎯 Deployment Scenarios

### Scenario 1: Free Azure Tier (SQLite + Groq)
```
Cost: $0/month
Setup: 15 minutes
Performance: Good (Groq is cloud-based)
Limit: 1GB free daily compute

Use: Dev/learning
```

### Scenario 2: Basic Production (PostgreSQL + Groq + Azure Storage)
```
Cost: ~$20-30/month
Setup: 30 minutes
Performance: Excellent
Limit: Enterprise-grade features

Use: Small team, production
```

### Scenario 3: Enterprise (dedicated apps, CDN, monitoring)
```
Cost: $100+/month
Setup: 1 hour
Performance: Maximum
Features: Auto-scaling, full monitoring

Use: Large scale, many users
```

---

## 📞 Getting Help

1. **GitHub Actions Failed?**
   - Go to GitHub → Actions tab
   - Click failed workflow
   - Check logs for error message

2. **App Crashing?**
   - View logs: `az webapp log tail ...`
   - Check App Settings in Portal
   - Verify database migrations ran

3. **Groq Not Working?**
   - Test locally: `python tests/test_ai_service.py`
   - Check API key in App Settings
   - Monitor Groq console at console.groq.com

4. **Database Issues?**
   - Verify DATABASE_URL format
   - Check PostgreSQL firewall rules
   - Run migrations manually via SSH

---

## ✨ Next Steps

After successful deployment:

1. ✅ Test all features at https://careerflow-ai.azurewebsites.net
2. ✅ Create admin user and customize settings
3. ✅ Upload a test resume and try an interview
4. ✅ Check metrics in Azure Portal
5. ✅ Set up monitoring and alerts
6. ✅ Plan capacity for expected users
7. ✅ Schedule regular database backups

---

## 🎉 You're Done!

Your CareerFlow AI application is live on Azure! 🚀

- 🌐 Web: https://careerflow-ai.azurewebsites.net
- 👨‍💼 Admin: https://careerflow-ai.azurewebsites.net/admin
- 📊 Metrics: Azure Portal → careerflow-ai app
- 📝 Logs: Azure Portal → Log stream

**Feedback?** Edit this guide and submit a pull request!

---

*Last updated: February 2026*
