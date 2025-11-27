# 🚀 Azure Deployment Quick Start

## Prerequisites (5 minutes)

1. **Azure Subscription** - You need an active Azure subscription
2. **Azure AD App Registration** - Your MSAL app (`bcb41e64-e9a8-421c-9331-699dd9041d58`)
3. **Azure OpenAI Resource** - Already have: `ca-policy-manager-helper.openai.azure.com`

---

## 🎯 Deployment Steps (15-20 minutes)

### Step 1: Create Azure App Service (5 min)

**Using Azure Portal:**

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **"Create a resource"** → **"Web App"**
3. Fill in:

   - **Subscription**: Your subscription
   - **Resource Group**: Create new → `rg-ca-policy-manager`
   - **Name**: `ca-policy-manager` (or your preferred name - must be globally unique)
   - **Publish**: `Code`
   - **Runtime stack**: `Python 3.12`
   - **Operating System**: `Linux`
   - **Region**: Choose closest to you (e.g., `East US 2`)
   - **Pricing Plan**: `B1` (Basic) or higher

4. Click **"Review + Create"** → **"Create"**
5. Wait for deployment to complete (~2 minutes)

---

### Step 2: Configure App Settings (5 min)

Once deployed, go to your App Service:

1. **Configuration** → **Application settings** → **New application setting**

Add these settings (one by one):

```
SECRET_KEY = <generate new random string>
MSAL_CLIENT_ID = bcb41e64-e9a8-421c-9331-699dd9041d58
MSAL_AUTHORITY = https://login.microsoftonline.com/organizations
DEMO_MODE = false
AI_ENABLED = true
AI_PROVIDER = azure
AZURE_OPENAI_ENDPOINT = https://ca-policy-manager-helper.openai.azure.com/
AZURE_OPENAI_API_KEY = <your Azure OpenAI key>
AZURE_OPENAI_DEPLOYMENT = gpt-4o-mini
AZURE_OPENAI_API_VERSION = 2024-02-15-preview
FLASK_ENV = production
DISABLE_SSL_VERIFY = false
```

**Generate SECRET_KEY:**

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

2. Click **"Save"** at the top
3. Click **"Continue"** to restart the app

---

### Step 3: Update Azure AD Redirect URI (2 min)

1. Go to [Azure Portal](https://portal.azure.com) → **App Registrations**
2. Find your app registration
3. Go to **Authentication**
4. Under **Redirect URIs**, add:

   ```
   https://ca-policy-manager.azurewebsites.net/auth/callback
   ```

   _(Replace `ca-policy-manager` with your actual App Service name)_

5. Click **"Save"**

---

### Step 4: Deploy Code (5-10 min)

**Option A: Deploy from VS Code (Easiest)**

1. Install **Azure App Service** extension in VS Code
2. Sign in to Azure (Azure icon in sidebar)
3. Right-click on `CA_Policy_Manager_Web` folder
4. Select **"Deploy to Web App..."**
5. Choose your App Service
6. Confirm deployment

**Option B: Deploy via Azure CLI**

```powershell
# Install Azure CLI if not already installed
# https://learn.microsoft.com/en-us/cli/azure/install-azure-cli

# Login to Azure
az login

# Navigate to your app folder
cd "C:\Github\CA Policy Manager Tool\CA_Policy_Manager_Web"

# Create a zip of your app
Compress-Archive -Path * -DestinationPath ../deploy.zip -Force

# Deploy to Azure
az webapp deployment source config-zip `
  --resource-group rg-ca-policy-manager `
  --name ca-policy-manager `
  --src ../deploy.zip
```

**Option C: Deploy via Git**

```powershell
cd "C:\Github\CA Policy Manager Tool\CA_Policy_Manager_Web"

# Get deployment credentials from Azure Portal
# App Service → Deployment Center → Local Git/FTPS credentials

# Add Azure as a remote
git remote add azure https://<deployment-username>@ca-policy-manager.scm.azurewebsites.net/ca-policy-manager.git

# Push to Azure
git push azure main
```

---

### Step 5: Verify Deployment (2 min)

1. Go to your App Service URL: `https://ca-policy-manager.azurewebsites.net`
2. You should see the login page
3. Click **"Sign In"** to test authentication
4. Try the AI explanation feature

---

## 🔧 Post-Deployment Configuration

### Enable Always On (Recommended)

1. App Service → **Configuration** → **General settings**
2. Set **Always On**: `On`
3. Click **"Save"**

This keeps your app warm and responsive.

### Enable Diagnostic Logging

1. App Service → **Monitoring** → **App Service logs**
2. Enable:
   - **Application logging**: `File System` (Level: `Information`)
   - **Detailed error messages**: `On`
   - **Failed request tracing**: `On`
3. Click **"Save"**

### View Logs

1. App Service → **Monitoring** → **Log stream**
2. Or download logs: **Advanced Tools** → **Go** → **Debug console** → **CMD**

---

## 🔒 Security Checklist

Before going live:

- [ ] **Rotate Azure OpenAI API key** (the one in your local .env is now in Azure config)
- [ ] **Enable HTTPS only**: App Service → Configuration → General settings → HTTPS Only: `On`
- [ ] **Set minimum TLS version**: TLS 1.2
- [ ] **Enable Managed Identity**: App Service → Identity → System assigned: `On`
- [ ] **Review CORS settings**: API → CORS (if using API from other domains)
- [ ] **Set up custom domain** (optional): App Service → Custom domains
- [ ] **Enable Azure AD authentication** (optional extra layer): Authentication → Add identity provider

---

## 📊 Monitoring & Scaling

### View Metrics

App Service → **Monitoring** → **Metrics**

Key metrics to watch:

- **CPU Percentage**
- **Memory Percentage**
- **HTTP Server Errors**
- **Response Time**

### Scale Up (More Power)

App Service → **Scale up (App Service plan)**

- Choose a higher tier (S1, P1V2, etc.)

### Scale Out (More Instances)

App Service → **Scale out (App Service plan)**

- Increase instance count (2-10 instances)
- Or enable **Autoscale** based on CPU/memory

---

## 🆘 Troubleshooting

### App won't start

1. Check logs: **Log stream** or **Kudu console**
2. Verify all environment variables are set
3. Check Python version is 3.12
4. Verify `requirements.txt` installed correctly

### Authentication fails

1. Verify redirect URI matches exactly (including `/auth/callback`)
2. Check MSAL_CLIENT_ID is correct
3. Ensure MSAL_AUTHORITY is set to `/organizations`

### AI features don't work

1. Verify Azure OpenAI endpoint is correct
2. Check API key is valid
3. Ensure deployment name matches (gpt-4o-mini)
4. Check App Service can reach Azure OpenAI (networking/firewall)

### Check logs in real-time

```powershell
# Using Azure CLI
az webapp log tail --name ca-policy-manager --resource-group rg-ca-policy-manager
```

---

## 💰 Cost Estimates

**Monthly cost for Basic setup:**

- App Service B1: ~$13/month
- Azure OpenAI (pay-per-use): ~$5-20/month (depends on usage)
- **Total**: ~$18-33/month

**Production setup (recommended):**

- App Service P1V2: ~$73/month
- Azure OpenAI: ~$20-50/month
- **Total**: ~$93-123/month

---

## 🔄 CI/CD Pipeline (Optional - Advanced)

Set up automated deployments:

1. App Service → **Deployment Center**
2. Choose source: **GitHub** (if public) or **Azure Repos**
3. Authenticate and select your repository
4. Configure build provider: **GitHub Actions** or **Azure Pipelines**
5. Azure will create the pipeline automatically

Every push to `main` will trigger automatic deployment.

---

## 📝 Next Steps

After successful deployment:

1. ✅ Test all features thoroughly
2. ✅ Set up monitoring and alerts
3. ✅ Configure custom domain (optional)
4. ✅ Enable backup: App Service → Backups
5. ✅ Document your deployment for your team

---

## 🔗 Useful Links

- [Azure App Service Documentation](https://learn.microsoft.com/en-us/azure/app-service/)
- [Python on Azure App Service](https://learn.microsoft.com/en-us/azure/app-service/quickstart-python)
- [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Your existing deployment guide](CA_Policy_Manager_Web/docs/DEPLOYMENT.md)

---

**Need help?** Check the detailed deployment guide at `CA_Policy_Manager_Web/docs/DEPLOYMENT.md`
