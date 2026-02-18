# CareerFlow AI - Azure Deployment Automation Script
# This script automates the complete deployment to Microsoft Azure

param(
    [Parameter(Mandatory=$false)]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroup = "careerflow-ai-rg",
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "eastus",
    
    [Parameter(Mandatory=$false)]
    [string]$AppName = "careerflow-ai-app",
    
    [Parameter(Mandatory=$false)]
    [string]$RegistryName = "careerflowacr"
)

# Color output
function Write-Success { Write-Host $args -ForegroundColor Green -BackgroundColor Black }
function Write-Error { Write-Host $args -ForegroundColor Red -BackgroundColor Black }
function Write-Info { Write-Host $args -ForegroundColor Cyan -BackgroundColor Black }
function Write-Warning { Write-Host $args -ForegroundColor Yellow -BackgroundColor Black }

Write-Info "╔════════════════════════════════════════════════════════════════╗"
Write-Info "║         CareerFlow AI - Azure Deployment Script               ║"
Write-Info "║                    Automated Setup & Deploy                   ║"
Write-Info "╚════════════════════════════════════════════════════════════════╝"

# Verification Functions
function Check-AzureCLI {
    Write-Info "`n[1/8] Checking Azure CLI installation..."
    try {
        $version = az --version
        Write-Success "✓ Azure CLI is installed"
        return $true
    }
    catch {
        Write-Error "✗ Azure CLI not found. Please install from: https://learn.microsoft.com/cli/azure"
        return $false
    }
}

function Check-Docker {
    Write-Info "[2/8] Checking Docker installation..."
    try {
        docker --version | Out-Null
        Write-Success "✓ Docker is installed"
        return $true
    }
    catch {
        Write-Error "✗ Docker not found. Please install Docker Desktop"
        return $false
    }
}

function Check-GitBash {
    Write-Info "[3/8] Checking Git installation..."
    try {
        git --version | Out-Null
        Write-Success "✓ Git is installed"
        return $true
    }
    catch {
        Write-Warning "⚠ Git not found. Some features may be limited"
        return $false
    }
}

# Azure Setup
function Setup-AzureLogin {
    Write-Info "`n[4/8] Azure Authentication..."
    Write-Info "Checking Azure login status..."
    
    try {
        $account = az account show 2>$null
        if ($account) {
            Write-Success "✓ Already logged in to Azure"
            $currentSub = az account show --query id -o tsv
            Write-Info "Current Subscription: $currentSub"
            return $true
        }
    }
    catch {
        Write-Info "Opening browser for Azure login..."
        az login
        return $true
    }
}

function Create-ResourceGroup {
    Write-Info "`n[5/8] Creating Resource Group..."
    
    $exists = az group exists --name $ResourceGroup
    
    if ($exists -eq "true") {
        Write-Warning "⚠ Resource Group '$ResourceGroup' already exists"
    }
    else {
        Write-Info "Creating resource group: $ResourceGroup in $Location..."
        az group create `
            --name $ResourceGroup `
            --location $Location | Out-Null
        Write-Success "✓ Resource Group created"
    }
}

function Create-Database {
    Write-Info "`n[6/8] Setting up PostgreSQL Database..."
    
    $dbName = "$AppName-db"
    $dbAdmin = "azureuser"
    $dbPassword = Read-Host "Enter database password (min 8 chars with uppercase, lowercase, number, special)" -AsSecureString
    $dbPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($dbPassword))
    
    Write-Info "Creating PostgreSQL server: $dbName..."
    
    try {
        az postgres flexible-server create `
            --resource-group $ResourceGroup `
            --name $dbName `
            --location $Location `
            --admin-user $dbAdmin `
            --admin-password $dbPasswordPlain `
            --sku-name Standard_B1ms `
            --tier Burstable `
            --storage-size 32 `
            --version 14 `
            --high-availability Disabled | Out-Null
        
        Write-Info "Creating database 'careerflow'..."
        az postgres flexible-server db create `
            --resource-group $ResourceGroup `
            --server-name $dbName `
            --database-name careerflow | Out-Null
        
        Write-Info "Setting firewall rules..."
        az postgres flexible-server firewall-rule create `
            --resource-group $ResourceGroup `
            --name $dbName `
            --rule-name AllowAzureServices `
            --start-ip-address 0.0.0.0 `
            --end-ip-address 0.0.0.0 | Out-Null
        
        Write-Success "✓ PostgreSQL database created"
        
        $dbConnection = "postgresql://${dbAdmin}:${dbPasswordPlain}@${dbName}.postgres.database.azure.com:5432/careerflow?sslmode=require"
        Write-Info "Database connection string (save this!):"
        Write-Info "  $dbConnection"
        
        return @{
            DbName = $dbName
            Admin = $dbAdmin
            Password = $dbPasswordPlain
            ConnectionString = $dbConnection
        }
    }
    catch {
        Write-Error "✗ Failed to create database: $_"
        return $null
    }
}

function Create-StorageAccount {
    Write-Info "`n[7/8] Creating Storage Account for Media Files..."
    
    $storageName = "$AppName".Replace("-", "").ToLower()
    
    Write-Info "Creating storage account: $storageName..."
    
    try {
        az storage account create `
            --name $storageName `
            --resource-group $ResourceGroup `
            --location $Location `
            --sku Standard_LRS `
            --kind StorageV2 | Out-Null
        
        Write-Info "Creating blob container 'media'..."
        az storage container create `
            --account-name $storageName `
            --name media 2>$null | Out-Null
        
        $storageKey = az storage account keys list `
            --account-name $storageName `
            --resource-group $ResourceGroup `
            --query "[0].value" -o tsv
        
        Write-Success "✓ Storage Account created"
        Write-Info "Storage Account: $storageName"
        Write-Info "Storage Key: $storageKey"
        
        return @{
            Name = $storageName
            Key = $storageKey
        }
    }
    catch {
        Write-Error "✗ Failed to create storage: $_"
        return $null
    }
}

function Create-ContainerRegistry {
    Write-Info "`n[8/8] Creating Container Registry..."
    
    Write-Info "Creating Azure Container Registry: $RegistryName..."
    
    try {
        $registryExists = az acr list --resource-group $ResourceGroup --query "[?name=='$RegistryName']" 2>$null | ConvertFrom-Json
        
        if ($registryExists.Count -gt 0) {
            Write-Warning "⚠ Registry '$RegistryName' already exists"
        }
        else {
            az acr create `
                --resource-group $ResourceGroup `
                --name $RegistryName `
                --sku Basic | Out-Null
        }
        
        $registryCredentials = az acr credential show `
            --name $RegistryName `
            --resource-group $ResourceGroup | ConvertFrom-Json
        
        Write-Success "✓ Container Registry ready"
        Write-Info "Registry: $RegistryName.azurecr.io"
        Write-Info "Username: $($registryCredentials.username)"
        Write-Info "Password: $($registryCredentials.passwords[0].value)"
        
        return @{
            Name = $RegistryName
            Username = $registryCredentials.username
            Password = $registryCredentials.passwords[0].value
        }
    }
    catch {
        Write-Error "✗ Failed to create registry: $_"
        return $null
    }
}

# Main Execution
try {
    # Pre-checks
    if (-not (Check-AzureCLI)) { exit 1 }
    if (-not (Check-Docker)) { exit 1 }
    Check-GitBash | Out-Null
    
    # Azure Setup
    if (-not (Setup-AzureLogin)) { exit 1 }
    
    # Create Resources
    Create-ResourceGroup
    $db = Create-Database
    $storage = Create-StorageAccount
    $registry = Create-ContainerRegistry
    
    # Summary
    Write-Success "`n╔════════════════════════════════════════════════════════════════╗"
    Write-Success "║                   ✓ Setup Complete!                           ║"
    Write-Success "╚════════════════════════════════════════════════════════════════╝"
    
    Write-Info "`nNext Steps:"
    Write-Info "1. Update your .env file with the above credentials"
    Write-Info "2. Build and push Docker image:"
    Write-Info "   az acr login --name $($registry.Name)"
    Write-Info "   docker build -f Dockerfile.prod -t `"$($registry.Name).azurecr.io/careerflow-ai:latest`" ."
    Write-Info "   docker push `"$($registry.Name).azurecr.io/careerflow-ai:latest`""
    Write-Info "3. Create App Service Plan:"
    Write-Info "   az appservice plan create --name careerflow-plan --resource-group $ResourceGroup --is-linux --sku B2"
    Write-Info "4. Create Web App:"
    Write-Info "   az webapp create --name $AppName --resource-group $ResourceGroup --plan careerflow-plan"
    Write-Info "5. Configure container and environment variables in Azure Portal"
    Write-Info "6. Run migrations:"
    Write-Info "   python manage.py migrate"
    Write-Info "7. Create superuser:"
    Write-Info "   python manage.py createsuperuser"
    
    Write-Warning "`n⚠ Save the connection strings and credentials securely!"
    
}
catch {
    Write-Error "`n✗ Deployment script error: $_"
    exit 1
}
