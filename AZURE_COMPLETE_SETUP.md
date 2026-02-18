# CareerFlow AI - Azure Deployment Complete Setup Guide

## 📊 Estimated Monthly Costs

### Minimal Setup (Development/Testing)
| Service | Tier | Cost/Month |
|---------|------|-----------|
| App Service | Standard_B1ms | ~$15 |
| PostgreSQL | Burstable B1ms | ~$40 |
| Container Registry | Basic | ~$5 |
| Storage Account | Standard LRS | ~$5 |
| Container Instances | On-demand | ~$10-20 |
| **Total** | | **~$75-85** |

### Production Setup (High Performance)
| Service | Tier | Cost/Month |
|---------|------|-----------|
| App Service | Premium P1V2 | ~$100 |
| PostgreSQL | General Purpose | ~$300 |
| Container Registry | Standard | ~$100 |
| Storage Account | Standard LRS | ~$10 |
| Container Instances | GPU | ~$200 |
| **Total** | | **~$710** |

**💡 Recommendation**: Start with minimal setup, scale up as needed.

---

## 🚀 Complete Deployment Workflow (30 minutes)

### Phase 1: Prerequisites (5 minutes)
```powershell
# 1. Check installations
az --version
docker --version
git --version

# 2. Login to Azure
az login

# 3. Verify subscription
az account show
```

### Phase 2: Automated Setup (10 minutes)
```powershell
# 1. Navigate to project folder
cd "C:\Users\user\OneDrive\Desktop\CareerFlow AI"

# 2. Run deployment script
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser
.\deploy-azure.ps1

# 3. Save all output information
# - Database URL
# - Storage Account Key
# - Registry Credentials
```

### Phase 3: Application Setup (10 minutes)
```powershell
# 1. Update .env with Azure credentials
Copy-Item ".env.azure" ".env"
# Edit .env with values from Phase 2

# 2. Build Docker image
docker build -f Dockerfile.prod -t careerflowacr.azurecr.io/careerflow-ai:latest .

# 3. Push to registry
az acr login --name careerflowacr
docker push careerflowacr.azurecr.io/careerflow-ai:latest

# 4. Create App Service components
az appservice plan create `
  --name careerflow-plan `
  --resource-group careerflow-ai-rg `
  --is-linux `
  --sku B2

az webapp create `
  --resource-group careerflow-ai-rg `
  --plan careerflow-plan `
  --name careerflow-ai-app `
  --deployment-container-image-name careerflowacr.azurecr.io/careerflow-ai:latest
```

### Phase 4: Configuration (5 minutes)
```powershell
# Apply environment settings to web app
az webapp config appsettings set `
  --resource-group careerflow-ai-rg `
  --name careerflow-ai-app `
  --settings @env-settings.json
```

### Phase 5: Verification
```powershell
# Test the deployment
curl https://careerflow-ai-app.azurewebsites.net

# Check logs
az webapp log tail --name careerflow-ai-app --resource-group careerflow-ai-rg
```

---

## 📋 Step-by-Step Setup with Ollama Integration

### Step 1: Create Azure Resources
```powershell
# Variables
$rg = "careerflow-ai-rg"
$loc = "eastus"
$app = "careerflow-ai-app"

# Create resource group
az group create --name $rg --location $loc

# Create PostgreSQL
az postgres flexible-server create `
  --resource-group $rg `
  --name "$app-db" `
  --location $loc `
  --admin-user azureuser `
  --admin-password "SecurePassword123!" `
  --sku-name Standard_B1ms

# Create database
az postgres flexible-server db create `
  --resource-group $rg `
  --server-name "$app-db" `
  --database-name careerflow

# Create storage
az storage account create `
  --name careerflowstorage `
  --resource-group $rg `
  --location $loc `
  --sku Standard_LRS

az storage container create `
  --account-name careerflowstorage `
  --name media

# Create registry
az acr create `
  --resource-group $rg `
  --name careerflowacr `
  --sku Basic
```

### Step 2: Deploy Ollama Service
```powershell
# Create container instance for Ollama
az container create `
  --resource-group careerflow-ai-rg `
  --name ollama-mistral `
  --image ollama/ollama:latest `
  --memory 8 `
  --cpu 2 `
  --dns-name-label ollama-careerflow `
  --ports 11434 `
  --environment-variables "OLLAMA_HOST=0.0.0.0:11434"

# Get FQDN
$ollamaFqdn = az container show `
  --resource-group careerflow-ai-rg `
  --name ollama-mistral `
  --query ipAddress.fqdn -o tsv

Write-Host "Ollama endpoint: http://$ollamaFqdn:11434"

# Pull Mistral model (inside container)
# Note: This happens automatically when created or use custom image
```

### Step 3: Build & Push Docker Image
```powershell
# Login to registry
az acr login --name careerflowacr

# Build production image
docker build -f Dockerfile.prod `
  -t careerflowacr.azurecr.io/careerflow-ai:latest `
  -t careerflowacr.azurecr.io/careerflow-ai:v1.0 `
  .

# Push to registry
docker push careerflowacr.azurecr.io/careerflow-ai:latest
docker push careerflowacr.azurecr.io/careerflow-ai:v1.0
```

### Step 4: Create Web App
```powershell
# Create App Service Plan
az appservice plan create `
  --name careerflow-plan `
  --resource-group careerflow-ai-rg `
  --is-linux `
  --sku B2

# Create Web App
az webapp create `
  --resource-group careerflow-ai-rg `
  --plan careerflow-plan `
  --name careerflow-ai-app

# Configure container
$registryPassword = az acr credential show `
  --name careerflowacr `
  --query "passwords[0].value" -o tsv

az webapp config container set `
  --name careerflow-ai-app `
  --resource-group careerflow-ai-rg `
  --docker-custom-image-name careerflowacr.azurecr.io/careerflow-ai:latest `
  --docker-registry-server-url "https://careerflowacr.azurecr.io" `
  --docker-registry-server-user careerflowacr `
  --docker-registry-server-password $registryPassword
```

### Step 5: Configure Application Settings
```powershell
# Get database connection string
$dbConnection = "postgresql://azureuser:SecurePassword123!@careerflow-ai-db.postgres.database.azure.com:5432/careerflow?sslmode=require"

# Get storage key
$storageKey = az storage account keys list `
  --account-name careerflowstorage `
  --resource-group careerflow-ai-rg `
  --query "[0].value" -o tsv

# Set all app settings
az webapp config appsettings set `
  --resource-group careerflow-ai-rg `
  --name careerflow-ai-app `
  --settings `
  DEBUG=False `
  SECRET_KEY="django-insecure-your-secure-key-here" `
  ALLOWED_HOSTS="careerflow-ai-app.azurewebsites.net,yourdomain.com" `
  DATABASE_URL="$dbConnection" `
  OLLAMA_HOST="http://ollama-careerflow.eastus.azurecontainers.io:11434" `
  OLLAMA_MODEL="mistral" `
  USE_AZURE_STORAGE=True `
  AZURE_ACCOUNT_NAME="careerflowstorage" `
  AZURE_ACCOUNT_KEY="$storageKey" `
  AZURE_CONTAINER="media" `
  AZURE_CUSTOM_DOMAIN="careerflowstorage.blob.core.windows.net"
```

### Step 6: Run Database Migrations
```powershell
# SSH into web app
az webapp ssh --name careerflow-ai-app --resource-group careerflow-ai-rg

# Inside the container:
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput --clear

# Test Ollama connection
python manage.py shell
```

### Step 7: Verify Deployment
```powershell
# Check app status
az webapp show `
  --name careerflow-ai-app `
  --resource-group careerflow-ai-rg `
  --query state

# View logs
az webapp log tail --name careerflow-ai-app --resource-group careerflow-ai-rg

# Test HTTP endpoint
curl https://careerflow-ai-app.azurewebsites.net

# Test admin login
# Visit: https://careerflow-ai-app.azurewebsites.net/admin/
```

---

## 🧹 Cleanup & Cost Control

### Stop but Keep Resources
```powershell
# Stop web app without deleting
az webapp stop --name careerflow-ai-app --resource-group careerflow-ai-rg

# Stop Ollama container
az container stop --name ollama-mistral --resource-group careerflow-ai-rg

# This saves costs when not using but keeps resources ready
```

### Resume Resources
```powershell
az webapp start --name careerflow-ai-app --resource-group careerflow-ai-rg
az container start --name ollama-mistral --resource-group careerflow-ai-rg
```

### Complete Cleanup (Delete Everything)
```powershell
# Delete entire resource group (all resources deleted)
az group delete --name careerflow-ai-rg --yes

# This removes:
# - Web app
# - App Service plan
# - PostgreSQL server
# - Container registry
# - Storage account
# - Container instances
# - All associated resources
```

### Selective Cleanup
```powershell
# Delete only web app
az webapp delete --name careerflow-ai-app --resource-group careerflow-ai-rg

# Delete only Ollama container
az container delete --name ollama-mistral --resource-group careerflow-ai-rg

# Delete storage account
az storage account delete --name careerflowstorage --resource-group careerflow-ai-rg --yes
```

---

## 🔄 CI/CD - Automated Deployments

### Setup GitHub Actions

1. **Generate Azure Credentials**:
```powershell
az ad sp create-for-rbac `
  --name careerflow-deployer `
  --role owner `
  --scopes /subscriptions/{your-subscription-id}/resourceGroups/careerflow-ai-rg `
  --json-auth
```

2. **Add GitHub Secrets**:
   - Go to GitHub repo → Settings → Secrets and Variables → Actions
   - Add `AZURE_CREDENTIALS` (from step 1)
   - Add `REGISTRY_USERNAME` and `REGISTRY_PASSWORD`
   - Add `AZURE_WEBAPP_NAME`

3. **Workflow File** (`.github/workflows/deploy.yml`):
```yaml
name: Deploy to Azure

on:
  push:
    branches: [ main ]

env:
  REGISTRY: careerflowacr.azurecr.io
  IMAGE: careerflow-ai

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Build and Push Image
      run: |
        az acr login --name careerflowacr
        docker build -f Dockerfile.prod -t ${{ env.REGISTRY }}/${{ env.IMAGE }}:${{ github.sha }} .
        docker push ${{ env.REGISTRY }}/${{ env.IMAGE }}:${{ github.sha }}
    
    - name: Deploy to Web App
      uses: azure/webapps-deploy@v2
      with:
        app-name: careerflow-ai-app
        images: ${{ env.REGISTRY }}/${{ env.IMAGE }}:${{ github.sha }}
```

---

## 📊 Monitoring Setup

### Enable Application Insights
```powershell
# Create Application Insights
az monitor app-insights create `
  --resource-group careerflow-ai-rg `
  --app careerflow-insights `
  --kind web

# Get instrumentation key
$instrumentationKey = az monitor app-insights show `
  --name careerflow-insights `
  --resource-group careerflow-ai-rg `
  --query instrumentationKey -o tsv

# Add to web app
az webapp config appsettings set `
  --name careerflow-ai-app `
  --resource-group careerflow-ai-rg `
  --settings APPINSIGHTS_INSTRUMENTATION_KEY=$instrumentationKey
```

### Setup Alerts
```powershell
# Alert on high error rate (>10 errors/minute)
az monitor metrics alert create `
  --name "High Error Rate Alert" `
  --resource-group careerflow-ai-rg `
  --scopes "/subscriptions/{id}/resourceGroups/careerflow-ai-rg/providers/Microsoft.Web/sites/careerflow-ai-app" `
  --condition "avg http5xx > 10" `
  --window-size 1m `
  --evaluation-frequency 1m
```

---

## 📱 Access Your Application

### After Deployment
```
Web App: https://careerflow-ai-app.azurewebsites.net
Admin Panel: https://careerflow-ai-app.azurewebsites.net/admin/
Login: https://careerflow-ai-app.azurewebsites.net/account/login/
```

### Default Credentials
- Username: (from `createsuperuser` command)
- Password: (from `createsuperuser` command)

---

## 🆘 Getting Help

### Azure Support Resources
- [Azure Documentation](https://learn.microsoft.com/azure/)
- [Azure CLI Reference](https://learn.microsoft.com/cli/azure/)
- [Azure Pricing](https://azure.microsoft.com/pricing/)
- [Azure Support Plans](https://azure.microsoft.com/support/plans/)

### Common Azure Forums
- Stack Overflow (`[[azure]]` tag)
- Azure Community Forums
- GitHub Issues

---

## ✅ Pre-Launch Checklist

- [ ] Azure account created and subscribed
- [ ] Resource group created
- [ ] PostgreSQL database configured
- [ ] Container registry setup
- [ ] Docker image built and pushed
- [ ] Web app created and configured
- [ ] Ollama container running with Mistral
- [ ] Environment variables set
- [ ] Database migrations completed
- [ ] Admin user created
- [ ] Static files collected
- [ ] Email configuration setup (optional)
- [ ] Custom domain added (optional)
- [ ] SSL certificate installed (optional)
- [ ] Monitoring enabled (optional)
- [ ] Backups configured (optional)
- [ ] CI/CD pipeline setup (optional)

---

## 🎉 Success Indicators

After deployment, verify:
1. ✅ App loads at `https://careerflow-ai-app.azurewebsites.net`
2. ✅ Admin panel accessible with login
3. ✅ Database connected (no "Connection refused" errors)
4. ✅ Ollama service responding (check logs)
5. ✅ Static files loading (CSS/JS visible)
6. ✅ Can create interview session without hanging
7. ✅ Resume upload working
8. ✅ Questions generating (with AI or defaults)
9. ✅ Interview flow completes successfully
10. ✅ Logs show no critical errors

---

**🚀 Your CareerFlow AI application is now live on Azure!**

For ongoing updates: `git push` → GitHub Actions → Automatic deployment to Azure

