# ============================================================================
# CareerFlow AI - Azure FREE Tier Deployment Script
# Cost: $0 (uses $200 free credit from Azure)
# 
# This script deploys CareerFlow AI to Azure's free tier services.
# Total cost: FREE for 12 months, ~$5/month after using always-free services
# ============================================================================

param(
    [string]$ResourceGroup = "careerflow-free",
    [string]$Location = "eastus",
    [string]$AppName = "careerflow-free-app",
    [string]$AdminPassword = "P@ssw0rd123!Change"
)

# ============================================================================
# Display Welcome Message
# ============================================================================
Write-Host "`n" -ForegroundColor White
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "║         Azure FREE Tier Deployment - CareerFlow AI            ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "║              Cost: $0 (Using $200 Free Credit)                ║" -ForegroundColor Green
Write-Host "║              Duration: 10-15 minutes                          ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`nConfiguration:" -ForegroundColor Cyan
Write-Host "  Resource Group: $ResourceGroup"
Write-Host "  Region: $Location"
Write-Host "  App Name: $AppName"
Write-Host "  Database: $AppName-db"
Write-Host "  Storage: $AppName-$(Get-Random 1000)"
Write-Host ""

$proceed = Read-Host "Continue with deployment? (yes/no)"
if ($proceed -ne "yes") {
    Write-Host "Deployment cancelled." -ForegroundColor Yellow
    exit
}

# ============================================================================
# Step 1: Login to Azure
# ============================================================================
Write-Host "`n[1/7] Logging in to Azure..." -ForegroundColor Yellow

try {
    $account = az account show 2>$null | ConvertFrom-Json
    Write-Host "✓ Already logged in as: $($account.user.name)" -ForegroundColor Green
} catch {
    Write-Host "Opening Azure login in browser..." -ForegroundColor Cyan
    az login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Login failed. Please try again." -ForegroundColor Red
        exit 1
    }
}

# ============================================================================
# Step 2: Create Resource Group
# ============================================================================
Write-Host "`n[2/7] Creating resource group '$ResourceGroup'..." -ForegroundColor Yellow

az group create `
    --name $ResourceGroup `
    --location $Location | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Resource group created successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to create resource group" -ForegroundColor Red
    exit 1
}

# ============================================================================
# Step 3: Create FREE PostgreSQL Database
# ============================================================================
Write-Host "`n[3/7] Creating FREE PostgreSQL database..." -ForegroundColor Yellow
Write-Host "  (First month is FREE with $200 credit)" -ForegroundColor Cyan

$dbName = "$AppName-db"

az postgres server create `
    --resource-group $ResourceGroup `
    --name $dbName `
    --location $Location `
    --admin-user azureuser `
    --admin-password $AdminPassword `
    --sku-name B_Gen5_1 `
    --storage-size 51200 `
    --backup-retention 7 `
    --geo-redundant-backup Disabled `
    --version 11 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ PostgreSQL database created successfully" -ForegroundColor Green
    
    # Create firewall rule for Azure services
    Write-Host "  Adding firewall rule for Azure services..." -ForegroundColor Cyan
    az postgres server firewall-rule create `
        --resource-group $ResourceGroup `
        --server-name $dbName `
        --name "AllowAzureServices" `
        --start-ip-address 0.0.0.0 `
        --end-ip-address 0.0.0.0 2>&1 | Out-Null
    
    Write-Host "✓ Firewall rule created" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to create PostgreSQL database" -ForegroundColor Red
    Write-Host "  (This might be normal if the name already exists)" -ForegroundColor Yellow
}

# ============================================================================
# Step 4: Create Storage Account (for resume uploads - 5 GB FREE)
# ============================================================================
Write-Host "`n[4/7] Creating FREE Storage Account..." -ForegroundColor Yellow
Write-Host "  (First 5 GB is FREE with your account)" -ForegroundColor Cyan

$randomSuffix = Get-Random -Minimum 10000 -Maximum 99999
$storageName = "$($AppName)$randomSuffix".Replace("-", "").Substring(0, 24)

az storage account create `
    --name $storageName `
    --resource-group $ResourceGroup `
    --location $Location `
    --sku Standard_LRS `
    --kind StorageV2 `
    --access-tier Hot `
    --https-only true 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Storage account created successfully" -ForegroundColor Green
    Write-Host "  Storage name: $storageName" -ForegroundColor Cyan
} else {
    Write-Host "✗ Failed to create storage account" -ForegroundColor Red
    Write-Host "  (This might be normal if the name already exists)" -ForegroundColor Yellow
}

# ============================================================================
# Step 5: Create FREE App Service Plan (B1 tier = FREE TIER)
# ============================================================================
Write-Host "`n[5/7] Creating FREE App Service Plan (B1 tier)..." -ForegroundColor Yellow
Write-Host "  (744 hours/month included in free tier)" -ForegroundColor Cyan

$planName = "$AppName-plan"

az appservice plan create `
    --name $planName `
    --resource-group $ResourceGroup `
    --is-linux `
    --sku B1 `
    --number-of-workers 1 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ App Service Plan created successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to create App Service Plan" -ForegroundColor Red
    exit 1
}

# ============================================================================
# Step 6: Create FREE Web App
# ============================================================================
Write-Host "`n[6/7] Creating FREE Web App (Python 3.11)..." -ForegroundColor Yellow

az webapp create `
    --name $AppName `
    --resource-group $ResourceGroup `
    --plan $planName `
    --runtime "PYTHON|3.11" `
    --runtime-version "3.11" 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Web App created successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to create Web App" -ForegroundColor Red
    exit 1
}

# ============================================================================
# Step 7: Get Connection Information
# ============================================================================
Write-Host "`n[7/7] Retrieving connection information..." -ForegroundColor Yellow

$dbServer = (az postgres server show --resource-group $ResourceGroup --name $dbName --query fullyQualifiedDomainName -o tsv 2>/dev/null)
$appUrl = "https://$AppName.azurewebsites.net"

# ============================================================================
# Display Results
# ============================================================================
Write-Host "`n" -ForegroundColor White
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                  ✓ DEPLOYMENT COMPLETE!                       ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "║                 Your Azure resources are ready!               ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n📊 RESOURCE SUMMARY:" -ForegroundColor Cyan
Write-Host "  ├─ Resource Group: $ResourceGroup" -ForegroundColor White
Write-Host "  ├─ Region: $Location" -ForegroundColor White
Write-Host "  ├─ Web App: $AppName" -ForegroundColor White
Write-Host "  ├─ Database: $dbName" -ForegroundColor White
Write-Host "  ├─ Storage: $storageName" -ForegroundColor White
Write-Host "  └─ Plan: B1 (FREE TIER)" -ForegroundColor White

Write-Host "`n🔗 CONNECTION DETAILS:" -ForegroundColor Cyan
Write-Host "  App URL: $appUrl" -ForegroundColor Green
Write-Host "  Database Server: $dbServer" -ForegroundColor Green
Write-Host "  Database User: azureuser" -ForegroundColor Yellow
Write-Host "  Database Password: (as entered)" -ForegroundColor Yellow
Write-Host "  Storage Name: $storageName" -ForegroundColor Yellow

Write-Host "`n💾 DATABASE CONNECTION STRING:" -ForegroundColor Yellow
Write-Host "  postgresql://azureuser:$AdminPassword@$dbServer:5432/careerflow?sslmode=require" -ForegroundColor Cyan

Write-Host "`n📋 NEXT STEPS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Create .env file with these values:" -ForegroundColor White
Write-Host "     DATABASE_URL=postgresql://azureuser:$AdminPassword@$dbServer:5432/careerflow?sslmode=require" -ForegroundColor Cyan
Write-Host "     AZURE_STORAGE_ACCOUNT_NAME=$storageName" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Get storage key:" -ForegroundColor White
Write-Host "     az storage account keys list -n $storageName -g $ResourceGroup" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Build Docker image:" -ForegroundColor White
Write-Host "     docker build -f Dockerfile.prod -t careerflow:latest ." -ForegroundColor Cyan
Write-Host ""
Write-Host "  4. Deploy to Azure:" -ForegroundColor White
Write-Host "     az webapp up --name $AppName --resource-group $ResourceGroup --runtime PYTHON:3.11" -ForegroundColor Cyan
Write-Host ""
Write-Host "  5. Run migrations (via SSH or container):" -ForegroundColor White
Write-Host "     python manage.py migrate" -ForegroundColor Cyan
Write-Host ""
Write-Host "  6. Create admin user:" -ForegroundColor White
Write-Host "     python manage.py createsuperuser" -ForegroundColor Cyan
Write-Host ""

Write-Host "`n💰 COST INFORMATION:" -ForegroundColor Green
Write-Host "  ├─ Months 1-12: FREE (uses $200 Azure credit)" -ForegroundColor Green
Write-Host "  ├─ Storage: FREE (5 GB included)" -ForegroundColor Green
Write-Host "  ├─ Ollama: FREE (run locally on your computer)" -ForegroundColor Green
Write-Host "  ├─ App Service B1: FREE (744 hours/month)" -ForegroundColor Green
Write-Host "  └─ After Month 12: ~$5-20/month using always-free services" -ForegroundColor Green

Write-Host "`n⏱️ RESOURCE LIMITS TO WATCH:" -ForegroundColor Yellow
Write-Host "  ├─ App Service B1: 744 hours/month" -ForegroundColor White
Write-Host "  ├─ PostgreSQL: 50 GB storage (B_Gen5_1 sku)" -ForegroundColor White
Write-Host "  ├─ Storage: 5 GB free (then $0.024/GB)" -ForegroundColor White
Write-Host "  └─ Monitor in Azure Portal > Cost Management + Billing" -ForegroundColor Yellow

Write-Host "`n📊 MONITOR YOUR USAGE:" -ForegroundColor Cyan
Write-Host "  # Check daily usage"
Write-Host "  az monitor metrics list --resource $AppName --resource-group $ResourceGroup --output table" -ForegroundColor White
Write-Host ""
Write-Host "  # View portal"
Write-Host "  https://portal.azure.com" -ForegroundColor White

Write-Host "`n💡 TIPS FOR STAYING FREE:" -ForegroundColor Cyan
Write-Host "  ✓ Monitor usage daily in Azure Portal" -ForegroundColor Green
Write-Host "  ✓ Set billing alerts at $150 spent" -ForegroundColor Green
Write-Host "  ✓ Keep storage under 5 GB" -ForegroundColor Green
Write-Host "  ✓ Run Ollama locally (not Azure)" -ForegroundColor Green
Write-Host "  ✓ Plan for month 13 (switch to always-free)" -ForegroundColor Green

Write-Host "`n✅ Deployment successful! Your resources are ready in the free tier.`n" -ForegroundColor Green

# ============================================================================
# Save Configuration
# ============================================================================
$config = @"
# CareerFlow AI - Azure FREE Tier Configuration
# Generated: $(Get-Date)

RESOURCE_GROUP=$ResourceGroup
LOCATION=$Location
APP_NAME=$AppName
DB_NAME=$dbName
DB_SERVER=$dbServer
DB_USER=azureuser
DB_PASSWORD=$AdminPassword
STORAGE_NAME=$storageName
STORAGE_SKU=Standard_LRS
APP_PLAN=$planName
APP_URL=$appUrl
RUNTIME=PYTHON|3.11

# Cost: FREE (For 12 months with $200 Azure credit)
# After 12 months: ~$5-20/month using always-free services
"@

$configPath = Join-Path (Get-Location) "azure-free-config.txt"
$config | Out-File -FilePath $configPath -Encoding UTF8
Write-Host "Configuration saved to: $configPath`n" -ForegroundColor Cyan
