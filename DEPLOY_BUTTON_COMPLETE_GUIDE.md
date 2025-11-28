# Deploy to Azure Button - Complete Setup Guide

**⏱️ Total Time: 15-20 minutes** | **💰 Cost: Free Tier Available (F1) or $13/month (B1)**

This guide walks you through deploying the CA Policy Manager to Azure using the "Deploy to Azure" button.

---

## 🚀 Quick Deploy

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAntonWilloughby%2FConditionalAccessPolicyManager%2Fmain%2Fazuredeploy.json)

---

## 📋 What Gets Deployed

The ARM template automatically creates and configures:

✅ **Azure App Service** (Linux, Python 3.12)

- Preconfigured with Gunicorn WSGI server
- HTTPS enforced
- Auto-generated SECRET_KEY
- Ready for code deployment

✅ **Azure OpenAI** (GPT-4o-mini)

- Deployment created and configured
- API key automatically linked to App Service
- 30K tokens/minute capacity (configurable)

✅ **Environment Variables**

- `AZURE_OPENAI_ENDPOINT` - Auto-configured
- `AZURE_OPENAI_DEPLOYMENT` - Set to "gpt-4o-mini"
- `AZURE_OPENAI_API_KEY` - Auto-retrieved from OpenAI resource
- `SECRET_KEY` - Auto-generated secure key
- `MSAL_CLIENT_ID` - Ready for your App Registration
- `MSAL_TENANT_ID` - Set to "organizations" (multi-tenant)
- `DEMO_MODE` - Set to "false" (requires auth)

---

## 📝 Step-by-Step Deployment

### Step 1: Click Deploy Button (2 minutes)

1. Click the **Deploy to Azure** button above
2. Sign in to your Azure account
3. Fill in the deployment parameters:

| Parameter                | Example                  | Description                         |
| ------------------------ | ------------------------ | ----------------------------------- |
| **Subscription**         | Visual Studio Enterprise | Your Azure subscription             |
| **Resource Group**       | `ca-policy-manager-rg`   | Create new or use existing          |
| **Region**               | `East US 2`              | Choose region (OpenAI availability) |
| **Web App Name**         | `my-ca-manager`          | Globally unique name                |
| **OpenAI Resource Name** | `my-openai-helper`       | Globally unique name                |
| **App Service Plan SKU** | `F1` or `B1`             | F1=Free, B1=$13/mo                  |
| **Model Capacity**       | `30`                     | Tokens/min (in thousands)           |

4. Click **Review + Create** → **Create**
5. Wait 5-8 minutes for deployment to complete

### Step 2: Deploy Application Code (5-7 minutes)

> **Skip this step if you deployed directly from the main repository.**
> The ARM template now clones the GitHub repo automatically and Oryx installs dependencies (thanks to the root `requirements.txt`). Only follow the options below if you forked the project or want to redeploy custom code.

**Option A: GitHub Integration (Recommended)**

1. **Fork the repository:**

   - Go to: https://github.com/AntonWilloughby/ConditionalAccessPolicyManager
   - Click **Fork** → Create your own copy

2. **Connect to Azure:**

   - Azure Portal → Your App Service → **Deployment Center**
   - Source: **GitHub**
   - Authorize GitHub connection
   - Select your forked repository
   - Branch: `main`
   - Build Provider: **App Service Build Service (Oryx)**
   - Click **Save**

3. **Wait for build:**
   - Monitor deployment logs (3-5 minutes)
   - Status: "Success (Active)" when complete

**Option B: Azure CLI (Manual Zip Deploy)**

> 🔁 Use this when you’ve customized the code and need to redeploy. **Always package from the repo root** so Azure sees the shim `requirements.txt` and installs dependencies.

```powershell
# Install Azure CLI if needed
# https://learn.microsoft.com/cli/azure/install-azure-cli

# Login to Azure
az login

# Navigate to the repository root (contains azuredeploy.json and requirements.txt)
cd "C:\Github\CA Policy Manager Tool"

# (Optional) Verify the shim points to the real dependency file
Get-Content .\requirements.txt   # Should output: -r CA_Policy_Manager_Web/requirements.txt

# Create deployment package from the root
Compress-Archive -Path * -DestinationPath deploy.zip -Force

# Deploy to Azure (replace with your names)
az webapp deploy `
   --name my-ca-manager `
   --resource-group ca-policy-manager-rg `
   --src-path deploy.zip `
   --type zip

# Watch deployment progress
Start-Sleep -Seconds 5
Start-Process "https://my-ca-manager.scm.azurewebsites.net/api/deployments"

# Cleanup
Remove-Item deploy.zip
```

> ✅ A successful deployment log will show Oryx running `pip install -r requirements.txt` and listing packages like `msal`, `flask`, etc. If you don’t see that, the root `requirements.txt` wasn’t included.

### Step 3: Create Azure AD App Registration (5 minutes)

**This step is optional if you want to use DEMO_MODE, but required for production authentication.**

1. **Create App Registration:**

   - Azure Portal → **Azure Active Directory** → **App registrations**
   - Click **New registration**
   - Name: `CA Policy Manager`
   - Supported account types: **Accounts in any organizational directory (Multi-tenant)**
   - Redirect URI:
     - Platform: **Web**
     - URL: `https://<your-app-name>.azurewebsites.net/auth/callback`
   - Click **Register**

2. **Note the Client ID:**

   - Copy the **Application (client) ID** from Overview page

3. **Configure API Permissions:**

   - Go to **API permissions**
   - Click **Add a permission** → **Microsoft Graph** → **Delegated permissions**
   - Add these permissions:
     - `User.Read` (Read user profile)
     - `Policy.Read.All` (Read CA policies)
     - `Policy.ReadWrite.ConditionalAccess` (Manage CA policies)
     - `Directory.Read.All` (Read directory data)
   - Click **Add permissions**
   - Click **Grant admin consent** (if you're admin)

4. **Enable Implicit Flow (Required):**
   - Go to **Authentication**
   - Scroll to **Implicit grant and hybrid flows**
   - ✅ Check **ID tokens**
   - ✅ Check **Access tokens**
   - Click **Save**

### Step 4: Update App Service Configuration (2 minutes)

1. **Add App Registration details:**

   - Azure Portal → Your App Service → **Configuration**
   - Click **New application setting** (repeat for each):

   | Name             | Value                               |
   | ---------------- | ----------------------------------- |
   | `MSAL_CLIENT_ID` | `<your-app-client-id>`              |
   | `MSAL_TENANT_ID` | `organizations` (or your tenant ID) |

2. **Click Save** → **Continue**

3. **Restart the App:**
   - Overview → Click **Restart**

---

## ✅ Verify Deployment

### Test Basic Functionality (2 minutes)

1. **Open your app:**

   - `https://<your-app-name>.azurewebsites.net`

2. **Check the landing page:**

   - Should see "CA Policy Manager" title
   - "Connect" button should be visible
   - No errors in browser console (F12)

3. **Test Authentication:**

   - Click **Connect**
   - Sign in with your Azure AD account
   - Should redirect back to app
   - User info card should appear in navbar
   - Connection badge should show "Connected"

4. **Test AI Features:**

   - Should see AI assistant available
   - Try asking: "What are conditional access policies?"
   - Should get AI-generated response

5. **Test Policy Management:**
   - View existing policies (if any)
   - Try creating a test policy
   - Verify policy appears in Azure AD portal

---

## 🔧 Troubleshooting

### Issue: App shows "Your App Service is up and running"

**Problem:** Code not deployed yet

**Solution:**

- Complete Step 2 (Deploy Application Code)
- If using GitHub: Check Deployment Center → Logs
- If using CLI: Check build logs at `https://<app>.scm.azurewebsites.net/api/deployments`

### Issue: "SECRET_KEY environment variable is required"

**Problem:** ARM template didn't set SECRET_KEY (old version)

**Solution:**

```powershell
# Generate a secure key
$secretKey = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})

# Add to App Service
az webapp config appsettings set `
  --name <your-app-name> `
  --resource-group <your-rg> `
  --settings SECRET_KEY=$secretKey
```

### Issue: "ModuleNotFoundError: No module named 'msal'"

**Problem:** Dependencies not installed

**Solution:**

- App Service → Deployment Center → Sync (re-deploy)
- Or check build logs for errors: `https://<app>.scm.azurewebsites.net/api/logs/docker`
- Should see "Build successful" in logs
- Confirm the root `requirements.txt` file exists at the repository root (it now references `CA_Policy_Manager_Web/requirements.txt` so Oryx can install dependencies automatically)

### Issue: "AI features not working"

**Problem:** OpenAI API key not configured

**Solution:**

1. Azure Portal → Your OpenAI resource → **Keys and Endpoint**
2. Copy **KEY 1**
3. App Service → Configuration → New application setting:
   - Name: `AZURE_OPENAI_API_KEY`
   - Value: `<your-key>`
4. Save and restart

### Issue: "MSAL_CLIENT_ID is required"

**Problem:** App Registration not configured

**Options:**

- **Option A:** Complete Step 3 (Create App Registration)
- **Option B:** Enable demo mode (no auth required):
  - App Service → Configuration
  - Set `DEMO_MODE=true`
  - Save and restart

### Issue: "401 Unauthorized" when loading policies

**Problem:** Missing API permissions or not granted consent

**Solution:**

1. App Registration → API permissions
2. Verify all 4 permissions are added
3. Click **Grant admin consent for <tenant>**
4. Sign out and sign in again to app

### Issue: Login redirect fails

**Problem:** Redirect URI mismatch

**Solution:**

1. App Registration → Authentication
2. Ensure redirect URI exactly matches:
   - `https://<your-app-name>.azurewebsites.net/auth/callback`
   - ⚠️ Must be HTTPS
   - ⚠️ No trailing slash
   - ⚠️ Must match exactly

---

## 🎯 Optional: Enable Demo Mode

If you want to test the app without Azure AD authentication:

1. App Service → **Configuration**
2. Find `DEMO_MODE` setting
3. Change value to `true`
4. **Save** → **Restart**

**What this enables:**

- ✅ App loads without authentication
- ✅ Sample policies shown
- ✅ UI fully functional
- ❌ Cannot connect to real Azure AD
- ❌ Cannot manage real policies

---

## 📊 Cost Breakdown

### Free Tier (F1)

- **App Service:** Free
- **Azure OpenAI:** Pay-as-you-go (~$0.15 per 1M tokens)
- **Estimated Monthly Cost:** $0-5 (depending on AI usage)

### Basic Tier (B1) - Recommended

- **App Service:** ~$13/month
- **Azure OpenAI:** Pay-as-you-go (~$0.15 per 1M tokens)
- **Estimated Monthly Cost:** $13-18/month

### Features Comparison

| Feature          | F1 (Free) | B1 (Basic) |
| ---------------- | --------- | ---------- |
| Always On        | ❌ No     | ✅ Yes     |
| Cold Start       | 🐌 Slow   | ⚡ Fast    |
| Custom Domain    | ❌ No     | ✅ Yes     |
| SSL Certificates | ❌ No     | ✅ Yes     |
| Deployment Slots | ❌ No     | ❌ No      |

---

## 🔐 Security Checklist

After deployment, ensure:

- ✅ HTTPS enforced (automatic)
- ✅ SECRET_KEY is unique and not shared
- ✅ API permissions granted with admin consent
- ✅ Redirect URIs configured correctly
- ✅ DEMO_MODE disabled for production
- ✅ Diagnostic logs enabled (optional)
- ✅ Break-glass admin accounts excluded from test policies

---

## 📚 Additional Resources

- **Full Documentation:** [README.md](README.md)
- **Automated Deployment:** [AUTOMATED_DEPLOYMENT.md](AUTOMATED_DEPLOYMENT.md)
- **Troubleshooting:** [CA_Policy_Manager_Web/docs/QUICK_START.md](CA_Policy_Manager_Web/docs/QUICK_START.md)
- **Security Best Practices:** [SECURITY.md](SECURITY.md)

---

## 💡 Next Steps

Once deployed and working:

1. **Test in Report-Only Mode:**

   - Create test policies with "Report-only" state
   - Monitor sign-in logs for impact
   - Adjust as needed before enforcement

2. **Set Up Monitoring:**

   - Azure Portal → App Service → Monitoring
   - Enable Application Insights (optional)
   - Review diagnostic logs

3. **Create Backups:**

   - Use the Export feature to backup existing policies
   - Store backup files securely
   - Test restore process

4. **Review Templates:**
   - Browse 20+ policy templates
   - Customize for your environment
   - Deploy incrementally

---

## ❓ Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#-troubleshooting) section above
2. Review deployment logs: `https://<app>.scm.azurewebsites.net/api/logs/docker`
3. Check App Service logs: Azure Portal → Diagnose and solve problems
4. Open an issue: [GitHub Issues](https://github.com/AntonWilloughby/ConditionalAccessPolicyManager/issues)

---

**🎉 Congratulations!** Your CA Policy Manager is now deployed to Azure!
