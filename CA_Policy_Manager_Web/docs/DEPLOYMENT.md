# CA Policy Manager - Deployment Guide

## 📋 Table of Contents
- [Local Development Setup](#local-development-setup)
- [Azure App Service Deployment](#azure-app-service-deployment)
- [Configuration](#configuration)
- [Security Considerations](#security-considerations)

---

## 🏠 Local Development Setup

### Prerequisites
- Python 3.11 or higher
- Azure AD app registration (see [SETUP_ENTRA_AUTH.md](SETUP_ENTRA_AUTH.md))
- Access to an Azure AD tenant with Conditional Access

### Step 1: Clone and Install

```bash
cd CA_Policy_Manager_Web

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your values
notepad .env  # Windows
nano .env     # Mac/Linux
```

**Required settings in `.env`:**
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-this
MSAL_CLIENT_ID=your-azure-ad-client-id
```

### Step 3: Register Azure AD Redirect URI

Go to [Azure Portal](https://portal.azure.com) → App Registrations → Your App → Authentication:

Add redirect URI:
```
http://localhost:5000/auth/callback
```

### Step 4: Run Development Server

```bash
python app.py
```

Navigate to: **http://localhost:5000**

### Development Tips

**Enable CSRF Protection (Recommended for testing):**
```env
ENABLE_CSRF=true
```

**Disable SSL Verification (Corporate Proxy Only):**
```env
DISABLE_SSL_VERIFY=true
```
⚠️ Only use this behind corporate proxies that intercept HTTPS traffic.

---

## ☁️ Azure App Service Deployment

### Option 1: Deploy from VS Code

#### Prerequisites
- [Azure Tools Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)
- Azure subscription

#### Steps

1. **Open VS Code** in your project folder

2. **Install Azure App Service Extension**
   - Extensions → Search "Azure App Service" → Install

3. **Sign in to Azure**
   - Click Azure icon in sidebar → Sign in

4. **Create App Service**
   - Azure sidebar → App Services → + Create New Web App
   - Name: `ca-policy-manager-[yourorg]`
   - Runtime: Python 3.11
   - Region: Choose closest to you

5. **Configure Application Settings**
   - Right-click your app → Application Settings → Add New Setting
   - Add each setting from `.env.azure`:

```
FLASK_ENV=production
SECRET_KEY=<generate-new-secret>
MSAL_CLIENT_ID=<your-client-id>
MSAL_AUTHORITY=https://login.microsoftonline.com/<your-tenant-id>
```

6. **Deploy**
   - Right-click your app → Deploy to Web App
   - Select folder: `CA_Policy_Manager_Web`
   - Confirm deployment

### Option 2: Deploy with Azure CLI

```bash
# Login to Azure
az login

# Create resource group
az group create --name rg-ca-policy-manager --location eastus

# Create App Service Plan (Basic B1 or higher)
az appservice plan create \
  --name plan-ca-policy-manager \
  --resource-group rg-ca-policy-manager \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --resource-group rg-ca-policy-manager \
  --plan plan-ca-policy-manager \
  --name ca-policy-manager-yourorg \
  --runtime "PYTHON:3.11"

# Configure app settings
az webapp config appsettings set \
  --resource-group rg-ca-policy-manager \
  --name ca-policy-manager-yourorg \
  --settings \
    FLASK_ENV=production \
    SECRET_KEY="your-secret-key" \
    MSAL_CLIENT_ID="your-client-id"

# Deploy code
az webapp up \
  --resource-group rg-ca-policy-manager \
  --name ca-policy-manager-yourorg \
  --runtime "PYTHON:3.11"
```

### Option 3: GitHub Actions CI/CD

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Azure App Service

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd CA_Policy_Manager_Web
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Deploy to Azure
      uses: azure/webapps-deploy@v2
      with:
        app-name: 'ca-policy-manager-yourorg'
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
        package: ./CA_Policy_Manager_Web
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FLASK_ENV` | No | `development` | Environment mode (`development`, `production`) |
| `SECRET_KEY` | **Yes** | - | Session encryption key (generate unique per deployment) |
| `MSAL_CLIENT_ID` | **Yes** | - | Azure AD app registration client ID |
| `MSAL_AUTHORITY` | No | `https://login.../organizations` | Azure AD authority URL |
| `BASE_URL` | No | Auto-detected | Base URL for OAuth redirects |
| `UPLOAD_FOLDER` | No | `data/uploads` | Directory for uploaded files |
| `ENABLE_CSRF` | No | `false` (dev) / `true` (prod) | Enable CSRF protection |
| `DISABLE_SSL_VERIFY` | No | `false` | Disable SSL verification (dev only) |

### Generate Secure Secret Key

```python
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output to your `SECRET_KEY` environment variable.

### Azure App Service Configuration

Azure Portal → Your App Service → Configuration → Application Settings:

```
FLASK_ENV=production
SECRET_KEY=<your-generated-secret>
MSAL_CLIENT_ID=<your-client-id>
MSAL_AUTHORITY=https://login.microsoftonline.com/<tenant-id>
UPLOAD_FOLDER=/home/site/uploads
```

### Startup Command (Azure)

Azure Portal → Configuration → General Settings → Startup Command:

```bash
gunicorn --bind=0.0.0.0:8000 --workers=4 --timeout=600 app:app
```

---

## 🔐 Security Considerations

### Development vs Production

| Feature | Development | Production |
|---------|-------------|------------|
| **Debug Mode** | ✅ Enabled | ❌ Disabled |
| **HTTPS** | Optional | ✅ Required |
| **SSL Verification** | Optional | ✅ Enforced |
| **CSRF Protection** | Optional | ✅ Enforced |
| **Secure Cookies** | Disabled | ✅ Enabled |

### Post-Deployment Checklist

- [ ] **Update Azure AD Redirect URI**
  - Add: `https://your-app.azurewebsites.net/auth/callback`
  - Remove localhost URI (or keep for dev)

- [ ] **Enable HTTPS Only**
  - Azure Portal → TLS/SSL Settings → HTTPS Only: **On**

- [ ] **Configure Custom Domain (Optional)**
  - Azure Portal → Custom Domains → Add custom domain
  - Update redirect URI in Azure AD

- [ ] **Enable Application Insights**
  - Azure Portal → Application Insights → Enable
  - Monitor errors and performance

- [ ] **Set up Backup**
  - Azure Portal → Backups → Configure automatic backups

- [ ] **Review Security Settings**
  - See [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md)

### Azure AD App Registration Settings

**Redirect URIs:**
- Development: `http://localhost:5000/auth/callback`
- Production: `https://your-app.azurewebsites.net/auth/callback`

**Implicit grant and hybrid flows:**
- ✅ Access tokens (for implicit flow)
- Currently using implicit flow (see [SECURITY_REMEDIATION_PLAN.md](SECURITY_REMEDIATION_PLAN.md) for upgrade to PKCE)

---

## 🐛 Troubleshooting

### Common Issues

**Problem:** "Module not found" errors
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Problem:** "MSAL authentication failed"
```bash
# Solution: Check Azure AD configuration
1. Verify CLIENT_ID is correct
2. Verify redirect URI matches exactly
3. Check API permissions are granted
4. Wait 5-10 minutes after granting consent
```

**Problem:** SSL certificate verification fails in development
```bash
# Solution: Add to .env (development only)
DISABLE_SSL_VERIFY=true
```

**Problem:** Azure deployment fails
```bash
# Solution: Check logs
az webapp log tail --name your-app-name --resource-group your-rg

# Or in Azure Portal: App Service → Log stream
```

**Problem:** "Session expired" immediately after login
```bash
# Solution: Check SECRET_KEY is set and persistent
# Azure: Application Settings must have SECRET_KEY
# Local: .env must have SECRET_KEY
```

### Logs and Debugging

**Local Development:**
```bash
# Flask runs with debug=True automatically in development
python app.py
# Check terminal output for errors
```

**Azure App Service:**
```bash
# Stream logs
az webapp log tail --name your-app-name --resource-group your-rg

# Download logs
az webapp log download --name your-app-name --resource-group your-rg
```

**Azure Portal Logs:**
- App Service → Log stream
- Application Insights → Failures
- Monitoring → Metrics

---

## 📚 Additional Resources

- [Azure App Service Python Documentation](https://learn.microsoft.com/en-us/azure/app-service/quickstart-python)
- [Flask Deployment Options](https://flask.palletsprojects.com/en/stable/deploying/)
- [Microsoft Identity Platform](https://learn.microsoft.com/en-us/azure/active-directory/develop/)
- [Conditional Access API Reference](https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccesspolicy)

---

## 🆘 Support

**Issues:** Open an issue in the repository  
**Security:** Review [SECURITY_REMEDIATION_PLAN.md](SECURITY_REMEDIATION_PLAN.md)  
**Azure Support:** https://azure.microsoft.com/support/

---

**Last Updated:** November 21, 2025  
**Tested On:** Python 3.11, Azure App Service Linux
