# Azure Free Deployment - Quick Start Guide

## ⚡ 30-Minute FREE Deployment (Copy-Paste Ready!)

### What You Need
- Free Azure Account (https://azure.microsoft.com/free) ✓ $200 credit for 12 months
- Azure CLI (1 minute to install)
- Windows PowerShell or Terminal

### Total Cost: $0 for 12 months
- Web App (B1 tier): FREE
- PostgreSQL: FREE (1st month)
- Storage: FREE (5 GB)
- After 12 months: ~$5/month

---

## 🚀 Quick Start (3 Steps)

### Step 1: Login to Azure (2 min)
```powershell
az login
# Opens browser to log in with your free account
```

### Step 2: Run Deployment Script (5 min)
```powershell
cd "c:\Users\user\OneDrive\Desktop\CareerFlow AI"
.\deploy-azure-free.ps1
```

**The script will:**
✓ Create resource group
✓ Create PostgreSQL database (FREE for 1 month!)
✓ Create storage account (5 GB FREE)
✓ Create B1 app service (744 hours FREE/month)
✓ Show you all connection details

### Step 3: Configure & Deploy (15 min)

**Get storage key:**
```powershell
$ResourceGroup = "careerflow-free"
$StorageName = (az storage account list -g $ResourceGroup --query [0].name -o tsv)
az storage account keys list -n $StorageName -g $ResourceGroup
```

**Create .env file:**
```env
DEBUG=False
SECRET_KEY=django-insecure-your-secret-key
DATABASE_URL=postgresql://azureuser:PASSWORD@servername.postgres.database.azure.com:5432/careerflow?sslmode=require
AZURE_STORAGE_ACCOUNT_NAME=storageaccount
AZURE_STORAGE_ACCOUNT_KEY=your-storage-key
OLLAMA_HOST=http://localhost:11434
ALLOWED_HOSTS=careerflow-free-app.azurewebsites.net
```

**Build and deploy:**
```powershell
# Build production Docker image
docker build -f Dockerfile.prod -t careerflow:latest .

# Deploy to Azure
az webapp up `
  --name careerflow-free-app `
  --resource-group careerflow-free `
  --runtime PYTHON:3.11

# Run migrations (SSH to the app)
python manage.py migrate
python manage.py createsuperuser
```

**Visit your app:**
```
https://careerflow-free-app.azurewebsites.net
```

---

## 💰 What You Get Free

| Service | Free Amount | Value |
|---------|------------|-------|
| **Web App (B1)** | 744 hrs/month | ~$15/month |
| **PostgreSQL** | 50 GB storage | ~$50/month |
| **Storage** | 5 GB | ~$1/month |
| **Ollama** | Run locally | ~$20/month |
| **Total per month** | — | **~$86/month** |
| **Your cost** | **$0** | All FREE! |

**For 12 Months: You save ~$1,032!**

---

## ✅ Verification Checklist

After deployment, verify everything works:

```powershell
# 1. Check web app is running
curl https://careerflow-free-app.azurewebsites.net

# 2. Check admin panel
# Visit: https://careerflow-free-app.azurewebsites.net/admin

# 3. Check logs for errors
az webapp log tail --name careerflow-free-app --resource-group careerflow-free

# 4. Start Ollama locally for AI
ollama pull mistral
ollama serve

# 5. Test interview flow
# Login → Create interview → Upload resume → Generate questions
```

---

## 🛡️ Keep It Free - Important Limits

### ⚠️ DON'T Exceed These:

| Resource | Limit | When You Hit It | What Happens |
|----------|-------|----------------|--------------|
| App Service | 744 hours/month | Stop all apps | Charges start |
| PostgreSQL | 50 GB storage | Delete old data | Extra $1/GB |
| Storage | 5 GB | Delete resumes | Extra $0.024/GB |
| Data transfer | 100 GB/month | Heavy usage | $0.087/GB |
| Ollama (Azure) | 30 ACU-hrs/month | Run only locally | $0.0013/min |

### ✅ DO These:

✓ **Monitor daily** - Azure Portal → Cost Management + Billing
✓ **Set alerts** - Alert when spending > $100
✓ **Keep clean** - Delete old interview sessions monthly
✓ **Run Ollama locally** - Never use expensive Azure AI services
✓ **Use storage wisely** - Archive old resumes after 3 months

---

## 📊 Monitor Your Usage

```powershell
# Check what you're using
az monitor metrics list `
  --resource careerflow-free-app `
  --resource-group careerflow-free `
  --metric-names "Http5xx,Http4xx,CpuTime" `
  --output table

# View detailed billing
# https://portal.azure.com → Cost Management + Billing

# Set billing alerts
az monitor metrics alert create `
  --name "Budget Alert" `
  --resource-group careerflow-free `
  --condition "total > 100"  # Alert at $100 spent
```

---

## 🎯 Common Issues & Fixes

### "Resource already exists"
```powershell
# Use different name
.\deploy-azure-free.ps1 -AppName "mycareerflow2"
```

### "Storage account name already taken"
- Storage names are globally unique (must be 3-24 characters)
- Script auto-adds random suffix, should work automatically
- If not, use: `careerflow$(Get-Random 10000)`

### "Database creation failed"
- PostgreSQL names must be globally unique
- Try: `careerflow-db-$(Get-Random)`
- Check your existing resources

### "App won't start"
```powershell
# Check app logs
az webapp log tail --name careerflow-free-app --resource-group careerflow-free

# Most common: Missing DATABASE_URL
# Solution: Add to App Settings
az webapp config appsettings set `
  --name careerflow-free-app `
  --resource-group careerflow-free `
  --settings "DATABASE_URL=postgresql://..."
```

### "Ollama connection failed"
- By default, Ollama isn't deployed to Azure (saves cost!)
- Run Ollama on your local computer instead
- Or deploy separately using Container Instances

---

## 🔄 What Happens After 12 Months?

At month 13, your $200 free credit runs out. **You have options:**

### Option 1: Pay (Cheapest - Keep Everything)
```
App Service B1: $15/month
PostgreSQL: $50/month
Storage: $5/month (after 5GB)
Total: ~$70/month
```

### Option 2: Switch to Always-Free Tier (~$0)
```
App Service: Free Tier
PostgreSQL: Always-free tier
Storage: 5 GB (stays free)
Total: ~$5/month
```

### Option 3: Downsize
```
Scale down to smaller resources
Use different approach (serverless)
Total: $0-20/month
```

**Recommendation:** Option 2 (always-free tier) keeps you at ~$5/month!

---

## 📚 Files Created

This automation created:
- ✓ `deploy-azure-free.ps1` - Automated deployment script
- ✓ `AZURE_FREE_DEPLOYMENT.md` - Complete guide (this file)
- ✓ `Dockerfile.prod` - Production Docker image
- ✓ `docker-compose.azure.yml` - Local testing stack
- ✓ `.env.azure` - Configuration template

---

## 🎓 Learn More

- **Azure Free Account FAQ**: https://azure.microsoft.com/free/free-account-faq/
- **Free Services List**: https://azure.microsoft.com/free/services/
- **Cost Management**: https://azure.microsoft.com/pricing/calculator/
- **Microsoft Learn**: https://learn.microsoft.com/azure/

---

## ❓ Frequently Asked Questions

**Q: Will I be charged without my permission?**
A: No! Azure requires you to upgrade from free trial. You'll get multiple warnings.

**Q: Can I really deploy for $0?**
A: Yes! For 12 months with $200 free credit. After that, ~$5-70/month depending on tier.

**Q: What if I exceed limits?**
A: Azure will alert you. You can delete resources or pay. No surprise $1000 bills.

**Q: Can I use Mistral AI for free?**
A: Yes! Ollama (local) is free. Azure's AI services would cost extra (~$20/month).

**Q: How do I move to another cloud later?**
A: Your app is containerized (Docker). Works on any cloud!

**Q: What if I only need it for 3 months?**
A: Perfect! Destroy resources when done. Cost = $0.

---

## 🚀 You're Ready!

Run this command now:

```powershell
cd "c:\Users\user\OneDrive\Desktop\CareerFlow AI"
.\deploy-azure-free.ps1
```

**It will take 10-15 minutes to deploy everything to Azure!**

Questions? Check AZURE_FREE_DEPLOYMENT.md for the full guide.

---

**Last Updated:** February 2026
**Status:** Ready to deploy 🟢
**Cost:** FREE for 12 months 💰

