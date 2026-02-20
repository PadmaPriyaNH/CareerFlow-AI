# CareerFlow AI - Pre-Deployment Checklist

**Complete this checklist before deploying to GitHub and Azure**

---

## ✅ Code Quality & Testing

- [ ] **Run all tests locally**
  ```powershell
  python manage.py test
  pytest tests/ -v
  python tests/test_ai_service.py
  ```

- [ ] **Run Django security checks**
  ```powershell
  python manage.py check --deploy
  ```

- [ ] **Verify no hardcoded secrets in code**
  - Search for API keys, passwords
  - Use `.env` for all secrets
  - Never commit `.env` file

- [ ] **Check code for commented-out debug code**
  - Remove `print()` statements
  - Remove test code
  - Clean up temporary fixes

---

## 🔐 Security Configuration

- [ ] **Generate strong SECRET_KEY**
  ```powershell
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

- [ ] **Set DEBUG=False in production**
  - Only True in development
  - False in `.env` for Azure

- [ ] **Configure ALLOWED_HOSTS**
  - Add your domain(s)
  - Include azurewebsites.net domain
  - Example: `careerflow-ai.azurewebsites.net,yourdomain.com`

- [ ] **Set GROQ_API_KEY**
  - Get from console.groq.com
  - Secure and never expose

- [ ] **Enable HTTPS**
  - Azure handles this automatically
  - All traffic redirects to HTTPS
  - HSTS configured in settings.py

- [ ] **Review CSRF settings**
  - CSRF_TRUSTED_ORIGINS set
  - CSRF_COOKIE_SECURE=True (when DEBUG=False)
  - SESSION_COOKIE_SECURE=True (when DEBUG=False)

---

## 📦 Dependencies & Versions

- [ ] **Review requirements.txt**
  - All packages pinned to specific versions
  - Run: `pip list --outdated`
  - Update critical packages
  
- [ ] **Test with frozen requirements**
  ```powershell
  pip install -r requirements.txt
  python manage.py test
  ```

- [ ] **Compatible Python version**
  - Project uses Python 3.11+
  - Tested with 3.11, 3.12, 3.13
  - Azure App Service: Select Python 3.11

---

## 🗄️ Database

- [ ] **Migrations up to date**
  ```powershell
  python manage.py migrate
  python manage.py makemigrations
  git status  # Should be clean
  ```

- [ ] **SQLite for dev, PostgreSQL for production**
  - Local: SQLite (db.sqlite3)
  - Azure: Set DATABASE_URL to PostgreSQL

- [ ] **Database backups configured**
  - Set up Azure Database backups
  - Retention period: 7+ days

---

## 📁 File Organization

- [ ] **No sensitive files in root**
  - `.env` not committed ✓
  - Database files not committed ✓
  - Private keys not committed ✓

- [ ] **Static files collected**
  ```powershell
  python manage.py collectstatic --noinput
  ```

- [ ] **Media folder permissions**
  - Non-web-accessible by default
  - Azure Storage preferred for production

- [ ] **Log directory exists**
  - Create: `mkdir logs/`
  - Avoid committing logs

---

## 🔄 Git & GitHub

- [ ] **GitHub repository created**
  - Repository name: `careerflow-ai`
  - Public (recommended) or Private

- [ ] **All code committed**
  ```powershell
  git add .
  git commit -m "Pre-deployment commit"
  ```

- [ ] **Verify .gitignore**
  - `.env` ignored ✓
  - `.venv/` ignored ✓
  - `__pycache__/` ignored ✓
  - Database files ignored ✓
  - `.pyc` files ignored ✓

- [ ] **First push successful**
  ```powershell
  git push -u origin main
  ```

- [ ] **GitHub Actions workflows visible**
  - Go to: GitHub.com → Your Repo → Actions
  - Should show CI workflow triggers

---

## 🌐 Azure Setup

- [ ] **Azure Account created**
  - Logged in locally: `az login`
  - Verified subscription: `az account show`

- [ ] **Resource Group created**
  ```powershell
  az group create --name careerflow-rg --location eastus
  ```

- [ ] **App Service created**
  - Name: `careerflow-ai`
  - Plan: F1 (Free) or Standard
  - Runtime: Python 3.11
  - Linux OS

- [ ] **PostgreSQL Database (optional but recommended)**
  - Server name: `careerflow-db`
  - Username: `adminuser`
  - Password: Strong and secure
  - Create database: `careerflow`
  - Get connection string for DATABASE_URL

- [ ] **App Settings configured**
  ```
  SECRET_KEY=your_generated_key
  DEBUG=False
  ALLOWED_HOSTS=careerflow-ai.azurewebsites.net
  AI_PROVIDER=groq
  GROQ_API_KEY=gsk_...
  GROQ_MODEL=llama-3.3-70b-versatile
  DATABASE_URL=postgresql://...  (if using PostgreSQL)
  ```

---

## 🚀 CI/CD & Deployment

- [ ] **GitHub Secrets configured** (for automatic deployment)
  - Go to: GitHub → Settings → Secrets & variables
  - Add:
    - `AZURE_WEBAPP_NAME` = `careerflow-ai`
    - `AZURE_WEBAPP_PUBLISH_PROFILE` = (your Azure publish profile)

- [ ] **CI/CD workflow files present**
  - `.github/workflows/ci.yml` ✓
  - `.github/workflows/azure-deploy.yml` ✓

- [ ] **Test GitHub Actions locally (optional)**
  - Using `act` tool for local testing
  - Or just push and monitor in Actions tab

- [ ] **First deployment test**
  - Make small change to code
  - Push to GitHub
  - Monitor: GitHub → Actions tab
  - Website should update within 5-10 minutes

---

## 🧪 Post-Deployment Tests

- [ ] **Website accessible**
  - Visit: https://careerflow-ai.azurewebsites.net
  - No 500 errors

- [ ] **Admin portal works**
  - Visit: https://careerflow-ai.azurewebsites.net/admin
  - Login page displays
  - Create superuser if needed

- [ ] **Test interview flow**
  - Create account / login
  - Upload resume (PDF or DOCX)
  - Enter job description
  - Get AI-generated questions
  - Answer a question
  - Verify AI feedback appears (<3 seconds)

- [ ] **Resume parsing works**
  - Upload sample resume
  - Verify extracted skills display

- [ ] **AI integration verified**
  - Check logs for any Groq errors
  - Verify response times are <3 seconds

- [ ] **Database accessible**
  - Datacan be saved
  - Can retrieve user data

- [ ] **Static files load**
  - CSS styling present
  - Images display correctly
  - No 404 errors in console

---

## 📊 Monitoring & Alerts

- [ ] **Azure monitoring enabled**
  - Application Insights connected
  - Data flows from app to insights

- [ ] **Log aggregation set up**
  - View logs via Azure Portal
  - Or: `az webapp log tail --resource-group careerflow-rg --name careerflow-ai`

- [ ] **Alerts configured**
  - CPU usage >80%
  - Failed requests >5/minute
  - Unhandled exceptions

- [ ] **Daily backup scheduled**
  - Azure Database backup settings
  - Retention: 7+ days

---

## 📚 Documentation

- [ ] **README.md updated**
  - Deployment instructions
  - How to run locally
  - How to contribute

- [ ] **Deployment guide completed**
  - DEPLOYMENT_GUIDE.md exists
  - Contains step-by-step instructions

- [ ] **Environment variables documented**
  - `.env.example` contains all variables
  - Comments explain each variable

- [ ] **GitHub wiki (optional)**
  - Deploy scripts documented
  - Troubleshooting guide
  - Architecture diagram

---

## 🔧 Maintenance Scripts

- [ ] **Backup script created**
  - Automated daily backups
  - Retention policy set

- [ ] **Scaling plan defined**
  - Expected user growth
  - Upgrade path for App Service
  - Database scaling plan

- [ ] **Update strategy**
  - Monthly security patches
  - Quarterly dependency updates
  - Annual framework upgrades

---

## ⚠️ Critical Before Going Public

- [ ] **All secrets removed from code**
  - No commented API keys
  - No hardcoded passwords
  - No dev tokens

- [ ] **Privacy policy in place**
  - Data collection disclosed
  - GDPR compliant if applicable
  - Link in footer

- [ ] **Terms of service**
  - Usage restrictions
  - Liability limitations
  - Dispute resolution

- [ ] **Error handling proper**
  - No stack traces to users (DEBUG=False)
  - Friendly error messages
  - Support contact info

- [ ] **Rate limiting (optional but recommended)**
  ```python
  # Add to settings.py for production
  REST_FRAMEWORK = {
      'DEFAULT_THROTTLE_CLASSES': [
          'rest_framework.throttling.AnonRateThrottle',
      ],
      'DEFAULT_THROTTLE_RATES': {
          'anon': '100/hour',
      }
  }
  ```

---

## 🎉 Final Check

- [ ] **All tests passing**
  ```powershell
  python manage.py test
  pytest tests/
  ```

- [ ] **No warnings or errors**
  - `python manage.py check` is clean
  - Build logs show no errors

- [ ] **Performance acceptable**
  - Page load: <2 seconds
  - AI responses: <5 seconds

- [ ] **Security review completed**
  - OWASP Top 10 addressed
  - Dependencies scanned for vulnerabilities
  - Code review completed

- [ ] **Ready for production**
  - Backup plan in place
  - Rollback strategy defined
  - Support process established

---

## 📝 Sign-Off

**Deployment Manager:** _______________  
**Date:** _______________  
**Notes:** _______________

---

## 🚀 You're Ready!

Once all checks are complete, your CareerFlow AI is ready for:
- ✅ GitHub public repository
- ✅ Microsoft Azure deployment
- ✅ Production traffic

**Next:** Follow [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for step-by-step deployment instructions.

---

*Last updated: February 2026*
