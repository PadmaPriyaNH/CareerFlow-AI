# Azure Deployment Guide - CareerFlow AI

## Overview
This guide covers deploying CareerFlow AI to Microsoft Azure with:
- **Web App Service** for Django application
- **PostgreSQL Database** for data persistence
- **Container Registry** for Docker images
- **Ollama with Mistral** model on separate container
- **Storage Account** for media files (resumes)
- **CI/CD Pipeline** for automated deployment

---

## Prerequisites
- Azure subscription (Free tier works for testing)
- Azure CLI installed: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli
- Docker Desktop installed
- GitHub account (for repo and actions)
- Git CLI installed

### Install Azure CLI (Windows)
```powershell
# Using Microsoft Installer
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi
Start-Process .\AzureCLI.msi -Wait

# Or using winget
winget install Microsoft.AzureCLI

# Verify installation
az --version
```

---

## Step 1: Azure Setup & Authentication

### Login to Azure
```powershell
az login
# Opens browser to authenticate
# Verify your subscription
az account show
```

### Set Variables (Customize these)
```powershell
# Set your variables
$resourceGroup = "careerflow-ai-rg"
$location = "eastus"  # or your preferred region
$appName = "careerflow-ai-app"
$dbName = "careerflow-db"
$registryName = "careerflowacr"
$storageName = "careerflowstorage"

# Save these for later use
Write-Host "Resource Group: $resourceGroup"
Write-Host "App Name: $appName"
Write-Host "Location: $location"
```

---

## Step 2: Create Resource Group

```powershell
az group create `
  --name $resourceGroup `
  --location $location

# Verify
az group show --name $resourceGroup
```

---

## Step 3: Create PostgreSQL Database

### Create PostgreSQL Flexible Server
```powershell
$dbAdmin = "azureuser"
$dbPassword = "P@ssw0rd123!ChangeMe"  # Change this!

az postgres flexible-server create `
  --resource-group $resourceGroup `
  --name $dbName `
  --location $location `
  --admin-user $dbAdmin `
  --admin-password $dbPassword `
  --sku-name Standard_B1ms `
  --tier Burstable `
  --storage-size 32 `
  --version 14 `
  --high-availability Disabled

# Create database
az postgres flexible-server db create `
  --resource-group $resourceGroup `
  --server-name $dbName `
  --database-name careerflow

# Allow Azure services to access
az postgres flexible-server firewall-rule create `
  --resource-group $resourceGroup `
  --name $dbName `
  --rule-name AllowAzureServices `
  --start-ip-address 0.0.0.0 `
  --end-ip-address 0.0.0.0

# Get connection string (save this!)
$dbConnection = "postgresql://${dbAdmin}:${dbPassword}@${dbName}.postgres.database.azure.com:5432/careerflow?sslmode=require"
Write-Host "DATABASE_URL: $dbConnection"
```

---

## Step 4: Create Storage Account (for Media Files)

```powershell
az storage account create `
  --name $storageName `
  --resource-group $resourceGroup `
  --location $location `
  --sku Standard_LRS `
  --kind StorageV2

# Create blob container for media
az storage container create `
  --account-name $storageName `
  --name media

# Get storage keys
$storageKey = az storage account keys list `
  --account-name $storageName `
  --resource-group $resourceGroup `
  --query "[0].value" -o tsv

Write-Host "AZURE_ACCOUNT_NAME: $storageName"
Write-Host "AZURE_ACCOUNT_KEY: $storageKey"
```

---

## Step 5: Create Container Registry

```powershell
az acr create `
  --resource-group $resourceGroup `
  --name $registryName `
  --sku Basic

# Get login credentials
az acr credential show `
  --name $registryName
```

---

## Step 6: Prepare Docker Images

### Update Dockerfile for Production

Create `Dockerfile.prod` in project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --clear

# Expose port
EXPOSE 8000

# Run Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "config.wsgi:application"]
```

### Build and Push to Azure Container Registry

```powershell
# Login to ACR
az acr login --name $registryName

# Build image
docker build -f Dockerfile.prod -t "${registryName}.azurecr.io/careerflow-ai:latest" .

# Push to registry
docker push "${registryName}.azurecr.io/careerflow-ai:latest"

# Verify
az acr repository list --name $registryName
```

---

## Step 7: Create App Service Plan & Web App

```powershell
# Create App Service plan (Linux container support)
az appservice plan create `
  --name careerflow-plan `
  --resource-group $resourceGroup `
  --is-linux `
  --sku B2  # Change to B1 for cost savings

# Create Web App
az webapp create `
  --resource-group $resourceGroup `
  --plan careerflow-plan `
  --name $appName `
  --deployment-container-image-name "${registryName}.azurecr.io/careerflow-ai:latest"

# Configure container registry access
$registryPassword = az acr credential show `
  --name $registryName `
  --query "passwords[0].value" -o tsv

az webapp config container set `
  --name $appName `
  --resource-group $resourceGroup `
  --docker-custom-image-name "${registryName}.azurecr.io/careerflow-ai:latest" `
  --docker-registry-server-url "https://${registryName}.azurecr.io" `
  --docker-registry-server-user $registryName `
  --docker-registry-server-password $registryPassword
```

---

## Step 8: Configure Environment Variables

```powershell
# Generate a secure SECRET_KEY
$secretKey = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((New-Guid).ToString() + (New-Guid).ToString())) 

# Set application settings
az webapp config appsettings set `
  --resource-group $resourceGroup `
  --name $appName `
  --settings `
  DEBUG=False `
  SECRET_KEY=$secretKey `
  ALLOWED_HOSTS=$appName.azurewebsites.net `
  DATABASE_URL="postgresql://${dbAdmin}:${dbPassword}@${dbName}.postgres.database.azure.com:5432/careerflow?sslmode=require" `
  OLLAMA_HOST="http://ollama-container:11434" `
  OLLAMA_MODEL="mistral" `
  USE_AZURE_STORAGE=True `
  AZURE_ACCOUNT_NAME=$storageName `
  AZURE_ACCOUNT_KEY=$storageKey `
  AZURE_CONTAINER="media" `
  AZURE_CUSTOM_DOMAIN="${storageName}.blob.core.windows.net"
```

---

## Step 9: Deploy Ollama Container (Optional - For Production)

### Option A: Separate Container Instance for Ollama

```powershell
# Create container instance for Ollama
az container create `
  --resource-group $resourceGroup `
  --name ollama-container `
  --image ollama/ollama:latest `
  --memory 8 `
  --cpu 2 `
  --dns-name-label ollama-careerflow `
  --ports 11434 `
  --environment-variables OLLAMA_HOST=0.0.0.0:11434

# Get the FQDN
az container show `
  --resource-group $resourceGroup `
  --name ollama-container `
  --query ipAddress.fqdn -o tsv

# Pull mistral model (run inside container)
az container exec `
  --resource-group $resourceGroup `
  --name ollama-container `
  --exec-command "/bin/sh" `
  --exec-cmd "ollama pull mistral"
```

### Option B: Use Azure GPU Container (Recommended for AI)

```powershell
# Create container group with GPU
az container create `
  --resource-group $resourceGroup `
  --name ollama-gpu-container `
  --image ollama/ollama:latest `
  --memory 16 `
  --cpu 4 `
  --gpu 1 `
  --image-type private `
  --registry-login-server "${registryName}.azurecr.io" `
  --registry-username $registryName `
  --registry-password $registryPassword `
  --ports 11434 `
  --dns-name-label ollama-gpu-careerflow `
  --environment-variables OLLAMA_HOST=0.0.0.0:11434
```

---

## Step 10: Update Django Settings

Update your `.env` for Azure deployment:

```env
# Azure Production Settings
DEBUG=False
SECRET_KEY=your-secure-secret-key-here
ALLOWED_HOSTS=careerflow-ai-app.azurewebsites.net,yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@servername.postgres.database.azure.com:5432/careerflow?sslmode=require

# Ollama Configuration
OLLAMA_HOST=http://ollama-container.azurewebsites.net:11434
OLLAMA_MODEL=mistral
AI_PROVIDER=ollama

# Azure Storage
USE_AZURE_STORAGE=True
AZURE_ACCOUNT_NAME=careerflowstorage
AZURE_ACCOUNT_KEY=your-storage-account-key
AZURE_CONTAINER=media
AZURE_CUSTOM_DOMAIN=careerflowstorage.blob.core.windows.net
```

---

## Step 11: Database Migrations & Setup

```powershell
# SSH into App Service to run migrations
az webapp remote-build-enabled set `
  --name $appName `
  --resource-group $resourceGroup `
  --enable true

# Run migrations via Azure CLI
az webapp up `
  --name $appName `
  --resource-group $resourceGroup `
  --plan careerflow-plan
```

Or manually run migrations:

```powershell
# Using deployment slot for safe migrations
az webapp deployment slot create `
  --name $appName `
  --resource-group $resourceGroup `
  --slot staging

# Deploy to staging first and test
# Then swap with production
az webapp deployment slot swap `
  --name $appName `
  --resource-group $resourceGroup `
  --slot staging
```

---

## Step 12: Setup CI/CD Pipeline (GitHub Actions)

Create `.github/workflows/azure-deploy.yml`:

```yaml
name: Deploy to Azure

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY_NAME: careerflowacr
  DOCKER_PATH: ./
  IMAGE_NAME: careerflow-ai
  AZURE_WEBAPP_NAME: careerflow-ai-app

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Build and push image to registry
      uses: azure/docker-login@v1
      with:
        login-server: ${{ env.REGISTRY_NAME }}.azurecr.io
        username: ${{ secrets.REGISTRY_USERNAME }}
        password: ${{ secrets.REGISTRY_PASSWORD }}
    
    - name: Build Docker image
      run: |
        docker build . -t ${{ env.REGISTRY_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}:${{ github.sha }}
        docker build . -t ${{ env.REGISTRY_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}:latest
    
    - name: Push image to registry
      run: |
        docker push ${{ env.REGISTRY_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}:${{ github.sha }}
        docker push ${{ env.REGISTRY_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}:latest
    
    - name: Deploy to Azure Web App
      uses: azure/webapps-deploy@v2
      with:
        app-name: ${{ env.AZURE_WEBAPP_NAME }}
        images: ${{ env.REGISTRY_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}:${{ github.sha }}
    
    - name: Run migrations
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.AZURE_APP_HOST }}
        username: ${{ secrets.AZURE_APP_USER }}
        key: ${{ secrets.AZURE_SSH_KEY }}
        script: |
          cd /app
          python manage.py migrate
          python manage.py collectstatic --noinput
```

---

## Step 13: Setup GitHub Secrets for CI/CD

Go to GitHub repo → Settings → Secrets and add:

```
AZURE_CREDENTIALS          # From: az ad sp create-for-rbac ...
REGISTRY_USERNAME          # From: az acr credential show ...
REGISTRY_PASSWORD          # From: az acr credential show ...
AZURE_APP_HOST             # Your app service hostname
AZURE_APP_USER             # SSH user
AZURE_SSH_KEY              # SSH private key
```

### Generate Azure Credentials:

```powershell
# Create service principal
az ad sp create-for-rbac `
  --name careerflow-ai-deployer `
  --role owner `
  --scopes /subscriptions/{subscription-id} `
  --json-auth

# Copy the output and add as AZURE_CREDENTIALS secret
```

---

## Step 14: Configure Custom Domain (Optional)

```powershell
# Add custom domain
az webapp config hostname add `
  --resource-group $resourceGroup `
  --webapp-name $appName `
  --hostname yourdomain.com

# Setup SSL certificate
az webapp config ssl create `
  --resource-group $resourceGroup `
  --name $appName `
  --certificate-name careerflow-cert

# Bind certificate
az webapp config ssl bind `
  --resource-group $resourceGroup `
  --name $appName `
  --certificate-thumbprint {thumbprint} `
  --ssl-type SNI
```

---

## Step 15: Monitoring & Logging

```powershell
# Enable Application Insights
az monitor app-insights create `
  --resource-group $resourceGroup `
  --application-type web `
  --kind web `
  --name careerflow-insights

# Stream logs
az webapp log tail `
  --name $appName `
  --resource-group $resourceGroup

# View real-time metrics
az monitor metrics list-definitions `
  --resource-group $resourceGroup `
  --resource-type "Microsoft.Web/sites" `
  --resource $appName
```

---

## Step 16: Test Deployment

```powershell
# Get app URL
$appUrl = az webapp show `
  --name $appName `
  --resource-group $resourceGroup `
  --query defaultHostName -o tsv

Write-Host "App URL: https://$appUrl"

# Test health endpoint
Invoke-WebRequest -Uri "https://$appUrl" -UseBasicParsing
```

---

## Troubleshooting

### Check App Logs
```powershell
az webapp log stream --name $appName --resource-group $resourceGroup
```

### Check Container Logs
```powershell
az container logs --name ollama-container --resource-group $resourceGroup
```

### Verify Database Connection
```powershell
az postgres flexible-server db show `
  --name careerflow `
  --server-name $dbName `
  --resource-group $resourceGroup
```

### Common Issues

| Issue | Solution |
|-------|----------|
| "Connection refused" | Check firewall rules: `az postgres flexible-server firewall-rule list` |
| Container won't start | Check logs: `az container logs` |
| Static files missing | Run: `python manage.py collectstatic --noinput` |
| Database migration failed | SSH into app and run: `python manage.py migrate --noop` |
| Ollama timeout | Increase timeout in `ollama_engine.py` or use larger container |

---

## Cost Optimization

### Reduce Costs:
1. **Use Standard_B1ms** instead of higher tiers
2. **Set auto-scaling** for web app
3. **Use Burstable tier** for PostgreSQL
4. **Compress images** in blob storage
5. **Enable CDN** for static files

```powershell
# Enable auto-scaling
az monitor autoscale create `
  --resource-group $resourceGroup `
  --resource-name $appName `
  --min-count 1 `
  --max-count 3 `
  --count 1
```

---

## Security Best Practices

1. **Never commit secrets** - use Azure Key Vault
2. **Enable HTTPS** - set redirect
3. **Use managed identities** for Azure services
4. **Enable WAF** (Web Application Firewall)
5. **Regular backups** - enable for PostgreSQL

```powershell
# Enable HTTPS redirect
az webapp config set `
  --resource-group $resourceGroup `
  --name $appName `
  --https-only true
```

---

## Next Steps

1. ✅ Deploy app to Azure Web App
2. ✅ Setup Ollama container with Mistral
3. ✅ Configure PostgreSQL database
4. ✅ Setup CI/CD pipeline
5. ✅ Add custom domain
6. ✅ Enable monitoring
7. ✅ Setup backups

**Your CareerFlow AI will be live at:** `https://careerflow-ai-app.azurewebsites.net`

---

## Support & Resources

- Azure CLI Docs: https://learn.microsoft.com/cli/azure
- Azure App Service: https://learn.microsoft.com/azure/app-service
- PostgreSQL on Azure: https://learn.microsoft.com/azure/postgresql
- Docker on Azure: https://learn.microsoft.com/azure/container-instances
- GitHub Actions: https://github.com/features/actions
