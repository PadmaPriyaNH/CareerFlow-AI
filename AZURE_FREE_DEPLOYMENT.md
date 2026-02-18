# Azure Free Tier Deployment - CareerFlow AI (100% FREE!)

## 🎉 Free Azure Deployment Options

Microsoft Azure offers **$200 FREE CREDIT for 12 months** plus **Always-Free Services** with no expiration. This guide shows you how to deploy completely free!

---

## 💰 Free Resources Breakdown

### Azure Free Tier (12 months - $200 credit)
| Service | Free Amount | Notes |
|---------|------------|-------|
| App Service | 1 x B1 tier | 744 hours/month |
| PostgreSQL | 1 month free | ~$50 value |
| Storage | 5 GB | Blob storage |
| Data Transfer | 100 GB egress | Per month |

### Always-Free Services (No expiration, no credit used)
| Service | Free Amount | Cost After |
|---------|------------|-----------|
| Container Instances | 30 ACU-hours/month | Minimal ($0.0013/min) |
| Application Insights | 1 GB ingestion/month | $0.80 per GB after |
| Bandwidth | First 15 GB/month out | $0.087 per GB after |

---

## 🚀 Free Deployment Architecture

```
Azure Free Tier (12 Months - $200 Credit)
├── App Service B1 Tier (~$15/month)
│   └── CareerFlow AI Django App
├── PostgreSQL Single Server (~$50/month)
│   └── Database + 5 GB storage
└── Storage Account (~$5/month)
    └── Resume uploads (5 GB)

Total Monthly Cost: $70
With $200 Credit: 2.8+ months FREE
```

**After 12 months?** Switch to Always-Free services (~$10-20/month)

---

## 📋 Prerequisites (All Free & Open Source)

✅ Azure Free Account (sign up with Microsoft/GitHub)
✅ Azure CLI (free download)
✅ Docker Desktop (free community edition)
✅ PowerShell (built into Windows)
✅ VS Code (free)

---

## ⚡ 3-Step Free Deployment

### Step 1: Create Free Azure Account (5 min)
```
1. Go to: https://azure.microsoft.com/free
2. Click "Start free"
3. Sign in with Microsoft/GitHub account
4. Verify with phone number
5. Get $200 credit + Always-free services
```

**What You Get:**
- $200 free credit (valid 12 months)
- Free services for 12 months
- Always-free services forever
- No credit card needed to start (but required to verify)

---

### Step 2: Deployment Script (Automated)

Create a PowerShell script that deploys for FREE:

```powershell
# 1. Login
az login

# 2. Create resource group
az group create --name careerflow-free --location eastus

# 3. Create FREE PostgreSQL (1 month free first)
az postgres server create `
  --name careerflow-db-free `
  --resource-group careerflow-free `
  --location eastus `
  --admin-user azureuser `
  --admin-password "P@ssw0rd123!" `
  --sku-name B_Gen5_1 `
  --storage-size 51200  # 50 GB free tier

# 4. Create FREE Storage Account (with always-free amounts)
az storage account create `
  --name careerflowfree `
  --resource-group careerflow-free `
  --location eastus `
  --sku Standard_LRS

# 5. Create FREE App Service Plan
az appservice plan create `
  --name careerflow-plan-free `
  --resource-group careerflow-free `
  --sku B1 `
  --is-linux

# 6. Create free web app
az webapp create `
  --name careerflow-free-app `
  --resource-group careerflow-free `
  --plan careerflow-plan-free `
  --runtime "PYTHON|3.11"

# Done! Now configure it...
```

---

### Step 3: Use Local Ollama (Save ~$200/month!)

**Option A: Run Ollama on Your Computer**
```powershell
# Install Ollama locally: https://ollama.ai
ollama pull mistral

# In production code, use local Ollama:
OLLAMA_HOST=http://your-home-ip:11434
```

**Option B: Use Always-Free Container Instances (30 ACU hours/month FREE)**
```powershell
# Create always-free container for Ollama (~$0 for 30 hours)
az container create `
  --resource-group careerflow-free `
  --name ollama-free `
  --image ollama/ollama `
  --memory 4 `
  --cpu 2 `
  --dns-name-label ollama-free `
  --ports 11434 `
  --environment-variables OLLAMA_HOST=0.0.0.0:11434
```

**30 ACU-hours/month means:**
- Run 24/7: costs $0.0013/min (~$20/month) ❌ Not free
- Run during business (8 hours/day): costs ~$0.50/month ✅ Almost free
- **Best**: Use local Ollama + AI fallback ✅ FREE

---

## 🎯 Completely FREE Setup (Total Cost: $0)

### The Smart Strategy:
1. **Use Azure Free Tier for everything** ($200 credit covers 12 months)
2. **Run Ollama locally** (on your computer) - FREE
3. **Use graceful degradation** (defaults if Ollama unavailable) - Already implemented!
4. **Move to Always-Free after 12 months** (~$10/month cost)

### Cost Breakdown:
| Component | Cost | Alternative |
|-----------|------|-------------|
| Web App (B1) | $0 (free tier) | Always free tier: ~$15/mo |
| PostgreSQL | $0 (free tier) | Always free tier: ~$50/mo |
| Storage | $0 (free tier) | Always free tier: ~$5/mo |
| Ollama | $0 (local) | Container: ~$20/mo |
| **Total First Year** | **$200 credit** | After year 1: ~$90/mo |

---

## 🚀 Complete FREE Deployment (Copy-Paste Ready)

### File: `deploy-azure-free.ps1`

```powershell
# ============================================================================
# CareerFlow AI - Azure FREE Tier Deployment Script
# Cost: $0 (uses $200 free credit from Azure)
# ============================================================================

param(
    [string]$ResourceGroup = "careerflow-free",
    [string]$Location = "eastus",
    [string]$AppName = "careerflow-free-app"
)

Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║     Azure FREE Tier Deployment - CareerFlow AI    ║" -ForegroundColor Green
Write-Host "║           Cost: $0 (Using $200 Free Credit)        ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Green

# 1. Login
Write-Host "`n[1/7] Logging in to Azure..." -ForegroundColor Cyan
az login

# 2. Create resource group
Write-Host "[2/7] Creating resource group..." -ForegroundColor Cyan
az group create --name $ResourceGroup --location $Location

# 3. Create FREE PostgreSQL
Write-Host "[3/7] Creating FREE PostgreSQL database..." -ForegroundColor Cyan
az postgres server create `
  --name "$AppName-db" `
  --resource-group $ResourceGroup `
  --location $Location `
  --admin-user azureuser `
  --admin-password "P@ssw0rd123!Change" `
  --sku-name B_Gen5_1 `
  --storage-size 51200 `
  --backup-retention 7 `
  --geo-redundant-backup Disabled

# Firewall for Azure services
az postgres server firewall-rule create `
  --resource-group $ResourceGroup `
  --server-name "$AppName-db" `
  --name "AllowAzureServices" `
  --start-ip-address 0.0.0.0 `
  --end-ip-address 0.0.0.0

# 4. Create FREE Storage Account
Write-Host "[4/7] Creating FREE Storage Account..." -ForegroundColor Cyan
az storage account create `
  --name "$AppName$(Get-Random 1000)" `
  --resource-group $ResourceGroup `
  --location $Location `
  --sku Standard_LRS `
  --kind StorageV2

# 5. Create FREE App Service Plan (B1 = FREE TIER)
Write-Host "[5/7] Creating FREE App Service Plan..." -ForegroundColor Cyan
az appservice plan create `
  --name "$AppName-plan" `
  --resource-group $ResourceGroup `
  --sku B1 `
  --is-linux `
  --number-of-workers 1

# 6. Create FREE Web App
Write-Host "[6/7] Creating FREE Web App..." -ForegroundColor Cyan
az webapp create `
  --name $AppName `
  --resource-group $ResourceGroup `
  --plan "$AppName-plan" `
  --runtime "PYTHON|3.11"

# 7. Display connection info
Write-Host "[7/7] Getting connection information..." -ForegroundColor Cyan

$dbServer = "$AppName-db.postgres.database.azure.com"
$dbConnection = "postgresql://azureuser:P@ssw0rd123!Change@$dbServer/careerflow"
$appUrl = "https://$AppName.azurewebsites.net"

Write-Host "`n╔════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              ✓ DEPLOYMENT COMPLETE!                ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`nConnection Details:" -ForegroundColor Yellow
Write-Host "App URL: $appUrl" -ForegroundColor White
Write-Host "Database: $dbServer" -ForegroundColor White
Write-Host "Database Connection String:" -ForegroundColor White
Write-Host "$dbConnection" -ForegroundColor Cyan

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Copy connection string above" -ForegroundColor White
Write-Host "2. Add to .env file" -ForegroundColor White
Write-Host "3. Build Docker image: docker build -f Dockerfile.prod -t careerflow:latest ." -ForegroundColor White
Write-Host "4. Deploy to app: az webapp up --name $AppName --resource-group $ResourceGroup" -ForegroundColor White
Write-Host "5. Run migrations: python manage.py migrate" -ForegroundColor White

Write-Host "`n⏰ Cost Tracker:" -ForegroundColor Cyan
Write-Host "First 12 Months: $0 (Free Tier Credits)" -ForegroundColor Green
Write-Host "After 12 Months: ~$65/month (or use Always-Free tier)" -ForegroundColor Yellow
Write-Host "Ollama: $0 (Run locally on your computer)" -ForegroundColor Green

Write-Host "`n💡 Tip: Monitor Azure Portal to stay within free tier limits!" -ForegroundColor Cyan
```

---

## 🛠️ Configuration for FREE Deployment

### Update `.env` for Free Tier:

```env
# Production settings
DEBUG=False
SECRET_KEY=your-secret-key-here

# FREE PostgreSQL (Single Server - older but free tier)
DATABASE_URL=postgresql://azureuser:PASSWORD@servername.postgres.database.azure.com:5432/careerflow?sslmode=require

# FREE Storage Account
USE_AZURE_STORAGE=True
AZURE_ACCOUNT_NAME=careerflowfree
AZURE_ACCOUNT_KEY=your-storage-key

# LOCAL OLLAMA (FREE - Run on your computer!)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral

# App settings
ALLOWED_HOSTS=careerflow-free-app.azurewebsites.net
```

---

## 📊 Free Tier Limits & Monitoring

### Always Monitor These Limits:

```powershell
# Check storage usage
az storage account show-usage `
  --name careerflowfree `
  --resource-group careerflow-free

# Check database storage
az postgres server show `
  --name careerflow-free-db `
  --resource-group careerflow-free `
  --query storageProfile

# Set up billing alerts (free!)
az monitor metrics alert create `
  --name "Budget Alert" `
  --resource-group careerflow-free `
  --scopes "/subscriptions/{id}" `
  --condition "total > 150"  # Alert at $150 spent
```

### Free Tier Limits to Avoid:
| Limit | Allowed | Monitor |
|-------|---------|---------|
| App Service | B1 only (744 hrs) | Stop if over |
| PostgreSQL | 50 GB storage | Clean up old data |
| Storage | 5 GB (free) | Upload limit |
| Data Transfer | 100 GB/month out | Heavy downloads |

**Stay within limits = $0 cost!**

---

## 🎯 Step-by-Step FREE Deployment

### Phase 1: Setup (5 minutes)
```powershell
# 1. Create free Azure account
# https://azure.microsoft.com/free

# 2. Install prerequisites
az --version  # Already have if installed
docker --version  # Ensure Docker is running

# 3. Login
az login
```

### Phase 2: Deploy Infrastructure (10 minutes)
```powershell
# Run the free deployment script
.\deploy-azure-free.ps1

# Save all the outputs!
# Database URL
# Storage Key
# App URL
```

### Phase 3: Build & Deploy App (15 minutes)
```powershell
# 1. Update .env with outputs from Phase 2
# 2. Build Docker image
docker build -f Dockerfile.prod -t careerflow-free:latest .

# 3. Deploy to Azure
az webapp up `
  --name careerflow-free-app `
  --resource-group careerflow-free `
  --runtime "PYTHON:3.11"

# 4. Run migrations
# SSH into the app and run:
python manage.py migrate
python manage.py createsuperuser
```

### Phase 4: Verify (5 minutes)
```powershell
# Check it's working
curl https://careerflow-free-app.azurewebsites.net/admin/

# View logs
az webapp log tail --name careerflow-free-app --resource-group careerflow-free
```

---

## 💾 How to Stay FREE for 12+ Months

### Month 1-12: Use Free Tier ($200 credit = covers $70/month)
```
✓ B1 App Service
✓ PostgreSQL Single Server
✓ Storage Account (5GB free)
✓ Local Ollama (FREE)
```

### Month 13+: Switch to Always-Free Services (~$20/month)
```
✓ App Service Free Tier ($0)
✓ PostgreSQL Always-Free: 750 hours/month ($0)
✓ Storage Always-Free: 5GB free (then pay)
✓ Local Ollama (FREE)
```

**Cost after Month 13:**
- App Service Free: $0
- PostgreSQL: $0 (first 750 hours)
- Storage: $5 (after 5GB)
- **Total: $5/month** (after 5GB storage)

---

## 🚨 What NOT to Do (To Stay FREE)

❌ **DON'T** use GPU containers (costs $200+/month)
❌ **DON'T** use Premium App Service tiers
❌ **DON'T** use Azure's expensive AI services
❌ **DON'T** exceed storage limits (5GB free)
❌ **DON'T** generate massive data transfer
❌ **DON'T** use Azure ML or Azure Cognitive Services
❌ **DON'T** use Premium PostgreSQL (use Flexible Server)

✅ **DO** use:
- ✓ B1 App Service tier only
- ✓ PostgreSQL Single Server (free 1st month) or Flexible (always-free)
- ✓ Local Ollama (your computer)
- ✓ Standard Storage (5GB free tier)
- ✓ Container Instances (always-free limits)

---

## 🎓 Free Tier Services You Can Use

### Always-Free (Forever - No Credit Used)
| Service | Free Amount | When Active |
|---------|------------|-----------|
| Container Instances | 30 ACU-hrs/month | Container runs |
| Application Insights | 1 GB/month | Logs collected |
| Service Bus | 1M messages/mo | Queues/topics |
| Functions | 1M requests/mo | Serverless code |
| Cosmos DB | 5GB storage | Free tier account |

### Free for 12 Months with $200 Credit
| Service | Free Amount | After Year 1 |
|---------|------------|-------------|
| App Service | 744 hours/month (B1) | Pay or switch tier |
| PostgreSQL | 50 GB + 1 month | Pay or use always-free |
| Storage | 5 GB + more included | Pay or stay at 5GB |
| Bandwidth | 100 GB/month | $0.087/GB |

---

## 📞 Free Support Resources

- **Azure Free Account Support**: Limited
- **Stack Overflow**: Free community support ([azure] tag)
- **Microsoft Docs**: 100% free
- **GitHub Forums**: Free community help
- **Azure Community**: Free forums

---

## 🎉 Success = FREE Deployment in 30 Minutes!

After following this guide, you'll have:

✅ CareerFlow AI running on Azure
✅ PostgreSQL database configured
✅ Zero monthly cost (uses free credit)
✅ Ollama running locally (free)
✅ Interview flow working end-to-end
✅ 12 months of free operation
✅ Option to continue cheaply after ($5-20/month)

---

## 💡 Pro Tips for Maximum Free Value

1. **Monitor Dashboard Daily**
   ```
   Azure Portal → Cost Management + Billing
   Check daily usage against limits
   ```

2. **Set Billing Alerts**
   ```powershell
   az monitor metrics alert create --condition "total > 150"
   ```

3. **Cleanup Old Data**
   ```powershell
   # Delete old interview data monthly
   python manage.py shell
   >>> from interviews.models import InterviewSession
   >>> InterviewSession.objects.filter(created_at__lt=...).delete()
   ```

4. **Use Application Insights for Monitoring**
   ```
   Always-free: 1 GB/month ingestion
   Helps you find bottlenecks (saves cost!)
   ```

5. **Backup Before Trial Ends**
   ```powershell
   # Export database before month 12
   pg_dump connectionstring > backup.sql
   ```

---

## 📋 FREE Deployment Checklist

- [ ] Create Azure free account (https://azure.microsoft.com/free)
- [ ] Install Azure CLI
- [ ] Clone CareerFlow AI repo
- [ ] Run `deploy-azure-free.ps1` script
- [ ] Save all connection details
- [ ] Update `.env` with free tier settings
- [ ] Build production Docker image
- [ ] Deploy to Azure Web App
- [ ] Run database migrations
- [ ] Create admin user
- [ ] Test at `https://careerflow-free-app.azurewebsites.net`
- [ ] Setup local Ollama (or use container)
- [ ] Monitor usage in Azure Portal
- [ ] Set billing alerts
- [ ] Plan for month 13 (switch to always-free)

---

## 🚀 Start Your FREE Deployment NOW!

**Total Time: 30 minutes**
**Total Cost: $0** (uses Azure free credit)
**Result: CareerFlow AI live on Azure!**

Next Step: Follow the "Step-by-Step FREE Deployment" section above! ⬆️

---

**Questions about free tier?** Check Azure Free FAQ: https://azure.microsoft.com/free/free-account-faq/

