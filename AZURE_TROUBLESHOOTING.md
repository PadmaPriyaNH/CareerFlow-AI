# Azure Deployment Troubleshooting Guide

## 🔴 Common Issues & Solutions

### Issue 1: "Connection refused" when connecting to database

**Symptoms:**
- `psycopg2.OperationalError: could not connect to server: Connection refused`
- Django migration fails
- Web app returns 500 error

**Solutions:**

```powershell
# Check if PostgreSQL server is running
az postgres flexible-server show `
  --name careerflow-ai-db `
  --resource-group careerflow-ai-rg `
  --query state

# Verify firewall rules allow Azure services
az postgres flexible-server firewall-rule list `
  --name careerflow-ai-db `
  --resource-group careerflow-ai-rg

# Add firewall rule if missing
az postgres flexible-server firewall-rule create `
  --resource-group careerflow-ai-rg `
  --name careerflow-ai-db `
  --rule-name "AllowAzureServices" `
  --start-ip-address 0.0.0.0 `
  --end-ip-address 0.0.0.0

# Test connection from local machine
psql -h careerflow-ai-db.postgres.database.azure.com `
     -U azureuser `
     -d careerflow `
     -c "SELECT version();"

# Check DATABASE_URL format is correct
# Should be: postgresql://user:password@host:port/dbname?sslmode=require
```

---

### Issue 2: "Container image not found" in web app

**Symptoms:**
- Web app shows 404 or blank page
- Error: `AzureWebJobsStorage connection string is not defined`
- Container won't start

**Solutions:**

```powershell
# Verify image exists in registry
az acr repository show `
  --name careerflowacr `
  --repository careerflow-ai

# Verify image tag
az acr repository show-tags `
  --name careerflowacr `
  --repository careerflow-ai

# If missing, rebuild and push
docker build -f Dockerfile.prod -t careerflowacr.azurecr.io/careerflow-ai:latest .
docker push careerflowacr.azurecr.io/careerflow-ai:latest

# Verify web app is using correct image
az webapp config container show `
  --name careerflow-ai-app `
  --resource-group careerflow-ai-rg

# If incorrect, update it
az webapp config container set `
  --name careerflow-ai-app `
  --resource-group careerflow-ai-rg `
  --docker-custom-image-name careerflowacr.azurecr.io/careerflow-ai:latest `
  --docker-registry-server-url "https://careerflowacr.azurecr.io" `
  --docker-registry-server-user careerflowacr `
  --docker-registry-server-password $registryPassword
```

---

### Issue 3: "Ollama connection timeout"

**Symptoms:**
- `requests.exceptions.ConnectTimeout: HTTPConnectionPool(host='...', port=11434)`
- Interview setup hangs or times out
- "AI service unavailable" message appears

**Solutions:**

```powershell
# Check if Ollama container is running
az container show `
  --name ollama-mistral `
  --resource-group careerflow-ai-rg `
  --query "containers[0].instanceView.currentState.state"

# View container logs
az container logs `
  --name ollama-mistral `
  --resource-group careerflow-ai-rg `
  --tail 50

# If not running, restart it
az container restart `
  --name ollama-mistral `
  --resource-group careerflow-ai-rg

# Increase container resources (if timeout is due to slow response)
az container delete --name ollama-mistral --resource-group careerflow-ai-rg --yes

az container create `
  --resource-group careerflow-ai-rg `
  --name ollama-mistral `
  --image ollama/ollama:latest `
  --memory 8 `
  --cpu 4 `
  --dns-name-label ollama-careerflow `
  --ports 11434 `
  --environment-variables "OLLAMA_HOST=0.0.0.0:11434"

# Test Ollama endpoint
$ollamaUrl = az container show `
  --name ollama-mistral `
  --resource-group careerflow-ai-rg `
  --query ipAddress.fqdn -o tsv

Invoke-WebRequest -Uri "http://$ollamaUrl:11434/api/models"
```

---

### Issue 4: "Static files not loading" (CSS/JS missing)

**Symptoms:**
- Website looks broken (no styling)
- Console errors about missing CSS/JS
- 404 errors for `/static/...` files

**Solutions:**

```powershell
# SSH into web app
az webapp ssh --name careerflow-ai-app --resource-group careerflow-ai-rg

# Inside container:
python manage.py collectstatic --noinput --clear

# Check static files location
ls -la /app/staticfiles/

# Verify STATIC_URL and STATIC_ROOT in settings
# STATIC_URL = '/static/'
# STATIC_ROOT = BASE_DIR / 'staticfiles'

# Check if WhiteNoise is configured
grep -i "whitenoise" /app/config/settings.py

# Restart web app to apply changes
exit  # Exit SSH
az webapp restart --name careerflow-ai-app --resource-group careerflow-ai-rg
```

---

### Issue 5: "Media files not uploading" (Azure Storage error)

**Symptoms:**
- Resume upload fails
- `ClientAuthenticationError: Incorrect account name or key`
- Files not appearing in blob storage

**Solutions:**

```powershell
# Verify storage account exists
az storage account show `
  --name careerflowstorage `
  --resource-group careerflow-ai-rg

# Verify container exists
az storage container exists `
  --account-name careerflowstorage `
  --name media

# If container missing, create it
az storage container create `
  --account-name careerflowstorage `
  --name media

# Verify storage key is correct
az storage account keys list `
  --account-name careerflowstorage `
  --resource-group careerflow-ai-rg

# Update web app settings with correct key
$newKey = az storage account keys list `
  --account-name careerflowstorage `
  --resource-group careerflow-ai-rg `
  --query "[0].value" -o tsv

az webapp config appsettings set `
  --name careerflow-ai-app `
  --resource-group careerflow-ai-rg `
  --settings AZURE_ACCOUNT_KEY=$newKey

# Test upload
# Try uploading a file through web interface

# Check uploaded files
az storage blob list `
  --account-name careerflowstorage `
  --container-name media
```

---

### Issue 6: "502 Bad Gateway" after deployment

**Symptoms:**
- Web app returns 502 Bad Gateway
- Recently deployed and everything was working
- Container not responding

**Solutions:**

```powershell
# Check web app logs
az webapp log tail --name careerflow-ai-app --resource-group careerflow-ai-rg --timeout 30

# Check container logs
docker logs <container-id>

# Verify app can start locally
docker run --rm -e DEBUG=False -e SECRET_KEY=test -p 8000:8000 `
  careerflowacr.azurecr.io/careerflow-ai:latest

# Common causes and fixes:
# 1. Database not accessible - check CONNECTION_STRING
# 2. Missing environment variable - verify all settings are set
# 3. Worker process crashed - check logs for Python exceptions
# 4. Port not exposed - ensure Dockerfile exposes port 8000

# Restart web app
az webapp restart --name careerflow-ai-app --resource-group careerflow-ai-rg

# Increase container timeout
az webapp config appsettings set `
  --name careerflow-ai-app `
  --resource-group careerflow-ai-rg `
  --settings WEBSITES_CONTAINER_START_TIME_LIMIT=600
```

---

### Issue 7: "Database migration fails"

**Symptoms:**
- `django.db.utils.OperationalError: table "..._....." does not exist`
- `django.core.exceptions.ImproperlyConfigured: Error loading psycopg2 module`
- Migrations not applied

**Solutions:**

```powershell
# SSH into web app
az webapp ssh --name careerflow-ai-app --resource-group careerflow-ai-rg

# Check migration status
python manage.py migrate --plan

# Show pending migrations
python manage.py migrate --noop

# Try migration with verbose output
python manage.py migrate -v 3

# If migration is stuck, force apply specific migration
python manage.py migrate interviews 0001_initial

# Roll back if needed
python manage.py migrate interviews zero

# Then apply fresh
python manage.py migrate

# Verify migrations applied
python manage.py migrate --check
```

---

### Issue 8: "Out of storage" or "Quota exceeded"

**Symptoms:**
- `OperationalError: database disk image is malformed`
- Storage account full
- Cannot upload files

**Solutions:**

```powershell
# Check database size
az postgres flexible-server show `
  --name careerflow-ai-db `
  --resource-group careerflow-ai-rg `
  --query "storage.storageSizeGB"

# Resize database if needed
az postgres flexible-server update `
  --name careerflow-ai-db `
  --resource-group careerflow-ai-rg `
  --storage-size 64  # Increase from 32 to 64 GB

# Check storage account usage
az storage account show-usage `
  --name careerflowstorage `
  --resource-group careerflow-ai-rg

# Delete old resume files to free space
az storage blob delete-batch `
  --account-name careerflowstorage `
  --source media `
  --daysago 30  # Delete files older than 30 days

# Check web app disk usage
az webapp exec --name careerflow-ai-app --resource-group careerflow-ai-rg --command "df -h"
```

---

### Issue 9: "Performance is slow"

**Symptoms:**
- Website loads slowly
- Interview setup takes >10 seconds
- Database queries are slow

**Solutions:**

```powershell
# Upgrade web app tier for better CPU
az appservice plan update `
  --name careerflow-plan `
  --resource-group careerflow-ai-rg `
  --sku P1V2

# Upgrade database tier
az postgres flexible-server update `
  --name careerflow-ai-db `
  --resource-group careerflow-ai-rg `
  --sku-name Standard_D2s_v3

# Enable query caching in Django
# Add to settings.py:
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
    }
}

# Add database index for frequently queried fields
# Create in Django ORM:
class Interview(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]

# Run database analytics
az postgres flexible-server server-logs list-action `
  --resource-group careerflow-ai-rg `
  --server-name careerflow-ai-db

# Enable Application Insights to identify bottlenecks
az monitor app-insights create `
  --resource-group careerflow-ai-rg `
  --app careerflow-insights
```

---

## 🔍 Diagnostic Commands

### Check Everything at Once
```powershell
# Create diagnostic report
$report = @"
=== DEPLOYMENT DIAGNOSTIC REPORT ===
Generated: $(Get-Date)

Resource Group: $(az group show -n careerflow-ai-rg --query name -o tsv)
Location: $(az group show -n careerflow-ai-rg --query location -o tsv)

Web App Status: $(az webapp show -n careerflow-ai-app -g careerflow-ai-rg --query state -o tsv)
Web App URL: https://$(az webapp show -n careerflow-ai-app -g careerflow-ai-rg --query defaultHostName -o tsv)

Database Status: $(az postgres flexible-server show -n careerflow-ai-db -g careerflow-ai-rg --query state -o tsv)
Storage Account: $(az storage account show -n careerflowstorage -g careerflow-ai-rg --query name -o tsv)

Container Registry: $(az acr show -n careerflowacr -g careerflow-ai-rg --query name -o tsv)
Ollama Container: $(az container show -n ollama-mistral -g careerflow-ai-rg --query "containers[0].instanceView.currentState.state" -o tsv 2>/dev/null || echo "Not found")

=== END REPORT ===
"@

$report | Tee-Object -FilePath diagnostic-report.txt
```

### View Real-Time Logs
```powershell
# Web app logs
az webapp log tail --name careerflow-ai-app --resource-group careerflow-ai-rg

# Ollama logs
az container logs --name ollama-mistral --resource-group careerflow-ai-rg --tail 100

# All logs in JSON
az monitor activity-log list `
  --resource-group careerflow-ai-rg `
  --status Failed `
  --max-events 10
```

---

## 📞 Getting Help

### Before Contacting Support
1. Check logs: `az webapp log tail ...`
2. Verify environment variables: `az webapp config appsettings list ...`
3. Test individual components (database, storage, container)
4. Reproduce issue locally if possible
5. Gather error messages and timestamps

### Support Options
- **Azure Support**: Azure Portal → Help + support
- **Stack Overflow**: Tag: [[azure-app-service]], [[postgresql]], [[docker]]
- **GitHub Issues**: Report to CareerFlow AI repository
- **Microsoft Docs**: https://learn.microsoft.com/azure/

### Information to provide when asking for help
1. Error message (exact text)
2. When it started happening
3. What action triggers the error
4. Output of diagnostic commands
5. Recent changes made
6. Relevant log entries

---

## 🆘 Emergency Procedures

### Emergency Rollback
```powershell
# If current version is broken, rollback to previous

# Get previous image version
az acr repository show-tags --name careerflowacr --repository careerflow-ai

# Deploy previous version
az webapp config container set `
  --name careerflow-ai-app `
  --resource-group careerflow-ai-rg `
  --docker-custom-image-name careerflowacr.azurecr.io/careerflow-ai:v1.0

# Start web app
az webapp start --name careerflow-ai-app --resource-group careerflow-ai-rg
```

### Emergency Database Backup
```powershell
# Create backup immediately
az postgres flexible-server backup create `
  --resource-group careerflow-ai-rg `
  --server-name careerflow-ai-db `
  --backup-name emergency-backup-$(Get-Date -Format 'yyyy-MM-dd-HHmmss')

# List backups
az postgres flexible-server backup list `
  --resource-group careerflow-ai-rg `
  --server-name careerflow-ai-db
```

### Rebuild Everything from Scratch
```powershell
# Full cleanup (WARNING: deletes all data)
az group delete --name careerflow-ai-rg --yes

# Then re-run deployment script
.\deploy-azure.ps1
```

---

## ✅ After You Fix an Issue

1. Verify the fix works (test in browser)
2. Check logs for new errors
3. Document what the issue was and how you fixed it
4. Update runbooks/documentation
5. Consider if this could happen again
6. Set up alerts to catch similar issues early
7. Update team about the incident

---

**Need more help?** Check [Microsoft Azure Documentation](https://learn.microsoft.com/azure/) or open an issue on [GitHub](https://github.com/your-org/careerflow-ai/issues)

