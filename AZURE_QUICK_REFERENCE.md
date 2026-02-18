# Azure Deployment - Quick Reference & Cheat Sheet

## 🚀 Quick Start (5 minutes)

### 1. One-Command Setup (Using PowerShell Script)
```powershell
cd "C:\Users\user\OneDrive\Desktop\CareerFlow AI"
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser
.\deploy-azure.ps1
```

### 2. Manual Setup (Step-by-Step)
```powershell
# Login to Azure
az login

# Set variables
$rg = "careerflow-ai-rg"
$loc = "eastus"
$app = "careerflow-ai-app"

# Create resource group
az group create --name $rg --location $loc

# Create database
az postgres flexible-server create `
  --resource-group $rg `
  --name "$app-db" `
  --location $loc `
  --admin-user azureuser `
  --admin-password "YourSecurePassword123!" `
  --sku-name Standard_B1ms
```

---

## 📚 Essential Azure CLI Commands

### Authentication
```powershell
az login                              # Interactive login
az login --service-principal          # Service principal login
az account show                       # Current subscription
az account list                       # All subscriptions
az account set --subscription ID      # Switch subscription
```

### Resource Groups
```powershell
az group create --name rg-name --location eastus
az group list                         # List all groups
az group show --name rg-name          # Show group details
az group delete --name rg-name        # Delete group
```

### PostgreSQL Database
```powershell
# Create server
az postgres flexible-server create `
  --resource-group careerflow-ai-rg `
  --name careerflow-ai-db `
  --location eastus `
  --admin-user azureuser `
  --admin-password "P@ssw0rd123!" `
  --sku-name Standard_B1ms `
  --tier Burstable `
  --storage-size 32

# Create database
az postgres flexible-server db create `
  --resource-group careerflow-ai-rg `
  --server-name careerflow-ai-db `
  --database-name careerflow

# Get connection string
az postgres flexible-server show-connection-string `
  --server-name careerflow-ai-db

# List databases
az postgres flexible-server db list `
  --resource-group careerflow-ai-rg `
  --server-name careerflow-ai-db

# Delete server
az postgres flexible-server delete `
  --resource-group careerflow-ai-rg `
  --name careerflow-ai-db
```

### Container Registry
```powershell
# Create registry
az acr create --resource-group rg-name --name registry-name --sku Basic

# Login to registry
az acr login --name registry-name

# List repositories
az acr repository list --name registry-name

# Show images in repository
az acr repository show --name registry-name --repository image-name

# Delete image
az acr repository delete --name registry-name --repository image-name

# Get credentials
az acr credential show --name registry-name
```

### Web App / App Service
```powershell
# Create app service plan
az appservice plan create `
  --name plan-name `
  --resource-group rg-name `
  --is-linux `
  --sku B2

# Create web app
az webapp create `
  --resource-group rg-name `
  --plan plan-name `
  --name app-name

# Deploy from Docker image
az webapp config container set `
  --name app-name `
  --resource-group rg-name `
  --docker-custom-image-name registry.azurecr.io/image:latest `
  --docker-registry-server-url https://registry.azurecr.io `
  --docker-registry-server-user username `
  --docker-registry-server-password password

# Set environment variables
az webapp config appsettings set `
  --name app-name `
  --resource-group rg-name `
  --settings `
  DEBUG=False `
  SECRET_KEY="your-secret" `
  DATABASE_URL="postgresql://..." `
  OLLAMA_HOST="http://..."

# Get app properties
az webapp show --name app-name --resource-group rg-name

# Stream logs
az webapp log stream --name app-name --resource-group rg-name

# SSH into app
az webapp ssh --resource-group rg-name --name app-name --instance-id 0
```

### Storage Account
```powershell
# Create storage account
az storage account create `
  --name storage-name `
  --resource-group rg-name `
  --location eastus `
  --sku Standard_LRS

# Create container
az storage container create `
  --account-name storage-name `
  --name media

# Upload file
az storage blob upload `
  --account-name storage-name `
  --container-name media `
  --file local-file-path `
  --name blob-name

# List blobs
az storage blob list `
  --account-name storage-name `
  --container-name media

# Get storage keys
az storage account keys list `
  --account-name storage-name `
  --resource-group rg-name
```

### Container Instances (for Ollama)
```powershell
# Create container instance
az container create `
  --resource-group rg-name `
  --name ollama-container `
  --image ollama/ollama:latest `
  --memory 8 `
  --cpu 2 `
  --dns-name-label ollama-careerflow `
  --ports 11434 `
  --environment-variables OLLAMA_HOST=0.0.0.0:11434

# View logs
az container logs `
  --resource-group rg-name `
  --name ollama-container

# Execute command in container
az container exec `
  --resource-group rg-name `
  --name ollama-container `
  --exec-command "/bin/bash"

# Delete container
az container delete `
  --resource-group rg-name `
  --name ollama-container
```

---

## 🔧 Docker Commands for Azure

### Build and Push Image
```powershell
# Login to Azure Container Registry
az acr login --name careerflowacr

# Build image
docker build -f Dockerfile.prod -t careerflowacr.azurecr.io/careerflow-ai:latest .

# Tag image
docker tag careerflow-ai:latest careerflowacr.azurecr.io/careerflow-ai:latest

# Push to registry
docker push careerflowacr.azurecr.io/careerflow-ai:latest

# List local images
docker images

# Remove image
docker rmi image-name:tag
```

---

## 📋 Deployment Workflow

### Step 1: Prepare Code
```bash
git add .
git commit -m "Deploy to Azure"
git push origin main
```

### Step 2: Build Docker Image
```powershell
docker build -f Dockerfile.prod -t careerflowacr.azurecr.io/careerflow-ai:latest .
```

### Step 3: Push to Registry
```powershell
az acr login --name careerflowacr
docker push careerflowacr.azurecr.io/careerflow-ai:latest
```

### Step 4: Deploy to Web App
```powershell
az webapp config container set `
  --name careerflow-ai-app `
  --resource-group careerflow-ai-rg `
  --docker-custom-image-name careerflowacr.azurecr.io/careerflow-ai:latest
```

### Step 5: Run Migrations
```powershell
# SSH into app
az webapp ssh --name careerflow-ai-app --resource-group careerflow-ai-rg

# Inside the container
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser  # If first time
```

### Step 6: Verify Deployment
```powershell
# Check app status
az webapp show --name careerflow-ai-app --resource-group careerflow-ai-rg

# View logs
az webapp log tail --name careerflow-ai-app --resource-group careerflow-ai-rg

# Test endpoint
curl https://careerflow-ai-app.azurewebsites.net
```

---

## 🐛 Troubleshooting

### Check Container Logs
```powershell
az container logs --name ollama-container --resource-group careerflow-ai-rg
```

### View Web App Logs in Real-Time
```powershell
az webapp log tail --name careerflow-ai-app --resource-group careerflow-ai-rg --provider AzureStorageLog
```

### SSH into Web App
```powershell
az webapp ssh --name careerflow-ai-app --resource-group careerflow-ai-rg
```

### Test Database Connection
```powershell
# From local machine
psql -h careerflow-ai-db.postgres.database.azure.com -U azureuser -d careerflow

# Or use Django shell
python manage.py shell
>>> from django.db import connections
>>> connections['default'].ensure_connection()
>>> print("Database connected!")
```

### Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| "Connection refused" | Check firewall rules: `az postgres flexible-server firewall-rule list ...` |
| "Image not found" | Ensure image is pushed: `az acr repository show --name careerflowacr ...` |
| "Ollama timeout" | Increase container CPU/memory: `az container create ... --cpu 4 --memory 8` |
| "Static files missing" | Run: `python manage.py collectstatic --noinput --clear` |
| "Database migration failed" | SSH into app and run: `python manage.py migrate --noop` |

---

## 💰 Cost Optimization

### Reduce Monthly Costs
```powershell
# Use Standard_B1ms tier (cheaper) instead of higher tiers
az postgres flexible-server update `
  --name careerflow-ai-db `
  --resource-group careerflow-ai-rg `
  --sku-name Standard_B1ms

# Use Basic tier for container registry
az acr create --sku Basic

# Enable auto-scaling for web app
az monitor autoscale create `
  --resource-group careerflow-ai-rg `
  --resource-name careerflow-ai-app `
  --min-count 1 `
  --max-count 3 `
  --count 1

# Use Blob Storage lifecycle rules to delete old files
az storage account management-policy create `
  --account-name careerflowstorage `
  --policy-name default
```

---

## 🔐 Security Best Practices

### Enable HTTPS and Redirect
```powershell
az webapp config set `
  --name careerflow-ai-app `
  --resource-group careerflow-ai-rg `
  --https-only true
```

### Setup Managed Identity
```powershell
az webapp identity assign `
  --name careerflow-ai-app `
  --resource-group careerflow-ai-rg
```

### Use Network Security Group
```powershell
az network nsg create `
  --name careerflow-nsg `
  --resource-group careerflow-ai-rg

# Allow only HTTPS
az network nsg rule create `
  --name AllowHTTPS `
  --nsg-name careerflow-nsg `
  --resource-group careerflow-ai-rg `
  --priority 100 `
  --source-address-prefixes "*" `
  --source-port-ranges "*" `
  --destination-address-prefixes "*" `
  --destination-port-ranges 443 `
  --access Allow `
  --protocol Tcp
```

---

## 📊 Monitoring & Analytics

### Enable Application Insights
```powershell
az monitor app-insights create `
  --resource-group careerflow-ai-rg `
  --app careerflow-insights `
  --kind web

# Link to web app
az webapp config appsettings set `
  --name careerflow-ai-app `
  --resource-group careerflow-ai-rg `
  --settings APPINSIGHTS_INSTRUMENTATION_KEY=...
```

### View Metrics
```powershell
az monitor metrics list `
  --resource-id /subscriptions/{id}/resourceGroups/careerflow-ai-rg/providers/Microsoft.Web/sites/careerflow-ai-app `
  --metric "Http4xx" "Http5xx" "ResponseTime"
```

---

## 📝 Setup Checklist

- [ ] Azure subscription created
- [ ] Azure CLI installed and authenticated
- [ ] Docker Desktop installed
- [ ] Resource group created
- [ ] PostgreSQL database created
- [ ] Container registry created
- [ ] Docker image built and pushed
- [ ] Storage account created for media
- [ ] App Service plan created
- [ ] Web app created
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] Admin user created
- [ ] Domain configured (optional)
- [ ] SSL certificate installed (optional)
- [ ] Monitoring enabled
- [ ] Backups configured
- [ ] CI/CD pipeline setup (optional)

---

## 🔗 Useful Links

- [Azure CLI Documentation](https://learn.microsoft.com/cli/azure/)
- [Azure App Service](https://learn.microsoft.com/azure/app-service/)
- [Azure PostgreSQL](https://learn.microsoft.com/azure/postgresql/)
- [Azure Container Instances](https://learn.microsoft.com/azure/container-instances/)
- [Azure Storage](https://learn.microsoft.com/azure/storage/)
- [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/)

---

## 💡 Pro Tips

1. **Use deployment slots** for zero-downtime updates
2. **Enable CI/CD** with GitHub Actions for automated deployments
3. **Monitor costs** regularly in Azure Portal
4. **Backup databases** daily using Azure Backup
5. **Use Azure Key Vault** for managing secrets
6. **Enable WAF** (Web Application Firewall) for additional security
7. **Setup alerts** for critical metrics and errors

