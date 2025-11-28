# Deploy to Azure Button - Quick Guide

## What Gets Deployed Automatically

Clicking the "Deploy to Azure" button automatically provisions and configures:

### Resources Created

1. **Azure App Service** (Web App)

   - Python 3.12 runtime
   - Linux-based hosting
   - HTTPS enabled by default
   - Configurable pricing tier (F1/B1/S1/P1v2)
   - **Application code deployed from GitHub**

2. **App Service Plan**

   - Dedicated compute resources for your web app
   - Auto-scaling support (on higher tiers)

3. **Azure OpenAI Service**
   - GPT-4o-mini model deployment
   - Configurable token capacity (30K TPM default)
   - S0 tier (pay-per-use)

### Configuration Automated

- ✅ `SECRET_KEY` - Auto-generated secure key
- ✅ `AZURE_OPENAI_API_KEY` - Auto-retrieved from OpenAI resource
- ✅ `AZURE_OPENAI_ENDPOINT` - Auto-configured
- ✅ All Python dependencies installed via Oryx build
- ✅ Gunicorn WSGI server configured
- ✅ Source code deployed from GitHub repository

**What you still need to do:** Create Azure AD App Registration (5 minutes) or enable DEMO_MODE for testing.

## Deployment Steps

### Step 1: Click the Deploy Button

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAntonWilloughby%2FConditionalAccessPolicyManager%2Fmain%2Fazuredeploy.json)

### Step 2: Fill in Parameters

| Parameter                | Description                   | Example                | Required         |
| ------------------------ | ----------------------------- | ---------------------- | ---------------- |
| **Subscription**         | Your Azure subscription       | "My Subscription"      | ✅ Yes           |
| **Resource Group**       | Create new or use existing    | "ca-policy-manager-rg" | ✅ Yes           |
| **Region**               | Azure region for deployment   | "East US 2"            | ✅ Yes           |
| **Web App Name**         | Unique name for your app      | "my-ca-policy-manager" | ✅ Yes           |
| **OpenAI Resource Name** | Unique name for OpenAI        | "my-openai-helper"     | ✅ Yes           |
| **App Service Plan SKU** | Pricing tier                  | "B1" (recommended)     | ✅ Yes           |
| **Model Capacity**       | Tokens per minute (thousands) | 30                     | No (default: 30) |
| **MSAL Client ID**       | Azure AD App Client ID        | Leave empty for now    | No               |
| **MSAL Tenant ID**       | Azure AD Tenant ID            | "organizations"        | No               |

#### Naming Guidelines

- **Web App Name**: 2-60 chars, alphanumeric + hyphens, globally unique
  - This becomes: `https://<web-app-name>.azurewebsites.net`
- **OpenAI Resource Name**: 2-64 chars, alphanumeric + hyphens, globally unique

#### Pricing Tier Recommendations

- **F1 (Free)**: Testing only, no "Always On", 60 min/day limit
- **B1 (Basic)**: ~$13/month, good for small teams, 1.75GB RAM
- **S1 (Standard)**: ~$70/month, auto-scaling, backup support
- **P1v2 (Premium)**: ~$85/month, better performance, staging slots

### Step 3: Review + Create

1. Click **Review + Create**
2. Azure validates the template (takes ~30 seconds)
3. Review the estimated costs
4. Click **Create** to start deployment

**Deployment time:** 5-10 minutes

### Step 4: Monitor Deployment

- Watch the deployment progress in Azure Portal
- Click **Go to resource group** when complete
- You'll see 3 resources created:
  - App Service Plan
  - App Service (Web App)
  - Cognitive Services (Azure OpenAI)

## Post-Deployment Configuration

After deployment completes, the ARM template automatically:

- ✅ Creates all Azure resources
- ✅ Configures environment variables
- ✅ Auto-generates SECRET_KEY
- ✅ Auto-retrieves AZURE_OPENAI_API_KEY
- ✅ **Deploys application code from GitHub** (takes 5-10 minutes)

You only need to configure authentication:

### Wait for Code Deployment (5-10 minutes)

The application code is **automatically deployed from GitHub**. Monitor progress:

**Option A: Deployment Logs**

```bash
Azure Portal → Resource Groups → [your-rg] → [web-app-name]
→ Deployment Center → Logs
```

**Option B: Kudu Deployments API**

```
https://<your-web-app-name>.scm.azurewebsites.net/api/deployments
```

Wait for status: **"Success"** before proceeding.

### Configure Authentication

Choose one of these options:

#### Option 1: Enable Demo Mode (Quick Testing)

Test the app without Azure AD authentication:

1. Azure Portal → Your Web App → Configuration
2. Find `DEMO_MODE` setting
3. Change value from `false` to `true`
4. Click **Save** → **Continue**
5. Click **Restart** (Overview page)

**What this does:** Loads sample policies, no sign-in required. Perfect for testing the UI.

#### Option 2: Production Authentication (Recommended)

Create Azure AD App Registration for real authentication:

**Step 1: Create App Registration**

```bash
Azure Portal → Azure Active Directory → App registrations
→ New registration
```

Fill in:

- **Name**: `CA Policy Manager`
- **Supported account types**: Accounts in any organizational directory (Multi-tenant)
- **Redirect URI**:
  - Platform: Web
  - URL: `https://<your-web-app-name>.azurewebsites.net/auth/callback`
- Click **Register**

**Step 2: Enable Implicit Flow**

```bash
Authentication → Implicit grant and hybrid flows
→ ✅ Check "ID tokens"
→ ✅ Check "Access tokens"
→ Save
```

**Step 3: Add API Permissions**

```bash
API permissions → Add a permission → Microsoft Graph → Delegated permissions
```

Add these permissions:

- `User.Read` (Read user profile)
- `Policy.Read.All` (Read CA policies)
- `Policy.ReadWrite.ConditionalAccess` (Manage CA policies)
- `Directory.Read.All` (Read directory data)

Click **Add permissions** → **Grant admin consent for [tenant]**

**Step 4: Update App Settings**

1. Copy the **Application (client) ID** from app registration
2. Azure Portal → Your Web App → Configuration
3. Find `MSAL_CLIENT_ID` setting
4. Update value with your Client ID
5. Change `DEMO_MODE` from `true` to `false` (if you enabled it)
6. Click **Save** → **Continue**
7. Click **Restart**

### Verify Deployment

1. Navigate to: `https://<your-web-app-name>.azurewebsites.net`
2. You should see the CA Policy Manager homepage
3. Click **Sign In** to test authentication
4. Try the AI explanation feature

## Template Outputs

After deployment, check the **Outputs** tab:

```json
{
  "webAppUrl": "https://my-ca-policy-manager.azurewebsites.net",
  "webAppName": "my-ca-policy-manager",
  "openAIEndpoint": "https://my-openai-helper.openai.azure.com/",
  "openAIResourceName": "my-openai-helper",
  "deploymentName": "gpt-4o-mini",
  "nextSteps": "1. Get OpenAI API Key... 2. Add secrets... 3. Update redirect URI... 4. Deploy code..."
}
```

Copy these values for configuration.

## Cost Breakdown

### Monthly Costs (Estimated)

| Component            | Tier              | Cost          |
| -------------------- | ----------------- | ------------- |
| **App Service Plan** | B1 (Basic)        | ~$13/month    |
| **App Service**      | (included)        | $0            |
| **Azure OpenAI**     | S0 base           | $0/month      |
| **Azure OpenAI**     | GPT-4o-mini usage | Pay-per-token |
|                      |                   |               |
| **Total Base**       |                   | ~$13/month    |
| **Total with Usage** |                   | ~$18-33/month |

### OpenAI Usage Pricing

- **Input**: $0.150 per 1M tokens (~$0.0000015 per 1K tokens)
- **Output**: $0.600 per 1M tokens (~$0.0000060 per 1K tokens)

**Example usage costs:**

- 100 policy explanations/day: ~$0.30/day = ~$9/month
- 500 policy explanations/day: ~$1.50/day = ~$45/month

### Free Tier Option

If you select **F1 (Free)** tier:

- App Service: $0/month (limited to 60 min/day, no Always On)
- OpenAI usage: Still pay-per-token
- **Total**: ~$5-20/month (depending on usage)

## Troubleshooting

### Deployment Fails: "Resource name already exists"

**Issue**: Web App or OpenAI resource name is taken (must be globally unique)

**Solution**: Use a different name

- Try: `<yourname>-ca-policy-manager-<random-number>`
- Example: `jsmith-ca-policy-manager-7342`

### Deployment Fails: "Region doesn't support Azure OpenAI"

**Issue**: Selected region doesn't have GPT-4o-mini availability

**Solution**: Choose one of these regions:

- East US 2 (recommended)
- Sweden Central
- West US 3

### Web App Shows "Service Unavailable"

**Issue**: Code not deployed yet

**Solution**: Complete Step 5 (Deploy Application Code)

### Authentication Redirect Error

**Issue**: Redirect URI not configured in Azure AD

**Solution**:

1. Azure Portal → Azure Active Directory → App Registrations
2. Find your app → Authentication
3. Add redirect URI: `https://<your-app>.azurewebsites.net/auth/callback`
4. Save

### AI Explanations Don't Work

**Issue**: Missing AZURE_OPENAI_API_KEY

**Solution**:

1. Get key: Azure Portal → OpenAI Resource → Keys and Endpoint
2. Add to Web App: Configuration → Application settings
3. Save and restart

## Update Deployment

To update resources after initial deployment:

### Update App Code

```bash
# Redeploy via VS Code or Azure CLI (see Step 5)
```

### Update Configuration

```bash
# Azure Portal → Web App → Configuration
# Edit application settings → Save
```

### Scale App Service

```bash
# Azure Portal → App Service Plan → Scale up (pricing tier)
# Choose new tier → Apply
```

### Increase OpenAI Capacity

```bash
# Azure Portal → OpenAI Resource → Model deployments
# Click gpt-4o-mini → Edit → Adjust TPM capacity → Save
```

## Clean Up Resources

To delete everything:

```bash
# Azure Portal → Resource Groups → [your-rg]
# Click "Delete resource group"
# Type the resource group name to confirm
# Click Delete
```

Or via Azure CLI:

```bash
az group delete --name ca-policy-manager-rg --yes --no-wait
```

## Security Checklist

After deployment:

- [ ] Rotate OpenAI API key if shared during setup
- [ ] Enable Application Insights for monitoring
- [ ] Configure custom domain with SSL (optional)
- [ ] Set up Azure Key Vault for secrets (production)
- [ ] Enable diagnostic logging
- [ ] Configure network restrictions (if needed)
- [ ] Review RBAC permissions on resources
- [ ] Set up backup policy for App Service

## Additional Resources

- **Full Deployment Guide**: [AZURE_DEPLOYMENT_QUICKSTART.md](AZURE_DEPLOYMENT_QUICKSTART.md)
- **Azure OpenAI Setup**: [docs/AZURE_OPENAI_SETUP.md](CA_Policy_Manager_Web/docs/AZURE_OPENAI_SETUP.md)
- **Security Guide**: [docs/security/SECURITY_CHECKLIST.md](docs/security/SECURITY_CHECKLIST.md)
- **ARM Template**: [azuredeploy.json](azuredeploy.json)

## Support

- **Issues**: Open a GitHub issue
- **Azure Support**: [Azure Portal Support](https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade)
- **ARM Template Docs**: [Azure Resource Manager](https://docs.microsoft.com/azure/azure-resource-manager/templates/)
