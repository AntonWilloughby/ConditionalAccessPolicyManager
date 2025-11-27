# Deploy to Azure Button - Quick Guide

## What Gets Deployed

Clicking the "Deploy to Azure" button automatically provisions:

### Resources Created

1. **Azure App Service** (Web App)

   - Python 3.12 runtime
   - Linux-based hosting
   - HTTPS enabled by default
   - Configurable pricing tier (F1/B1/S1/P1v2)

2. **App Service Plan**

   - Dedicated compute resources for your web app
   - Auto-scaling support (on higher tiers)

3. **Azure OpenAI Service**
   - GPT-4o-mini model deployment
   - Configurable token capacity (30K TPM default)
   - S0 tier (pay-per-use)

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

After deployment completes, you need to add secrets and deploy code:

### 1. Get Azure OpenAI API Key

```bash
# Navigate to your OpenAI resource in Azure Portal
Azure Portal → Resource Groups → [your-rg] → [openai-resource-name]
→ Keys and Endpoint → Copy "Key 1"
```

### 2. Generate Secret Key

Run this locally to generate a secure secret:

```powershell
# PowerShell
python -c "import secrets; print(secrets.token_hex(32))"
```

```bash
# Bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Add Configuration Settings

```bash
# Navigate to your Web App in Azure Portal
Azure Portal → Resource Groups → [your-rg] → [web-app-name]
→ Configuration → Application settings → New application setting
```

Add these settings:

| Name                   | Value                   | Notes                      |
| ---------------------- | ----------------------- | -------------------------- |
| `AZURE_OPENAI_API_KEY` | `<key from step 1>`     | From OpenAI resource       |
| `SECRET_KEY`           | `<generated in step 2>` | For Flask session security |

Click **Save** and wait for restart.

### 4. Create Azure AD App Registration

If you didn't provide MSAL Client ID during deployment:

```powershell
# Run the registration script
cd CA_Policy_Manager_Web/scripts
./Register-EntraApp-Delegated.ps1 -AppName "CA Policy Manager" -RedirectUri "https://<your-app-name>.azurewebsites.net/auth/callback"
```

This creates the app registration and outputs the Client ID.

**Add the Client ID to App Settings:**

1. Azure Portal → Your Web App → Configuration
2. Find `MSAL_CLIENT_ID` setting
3. Update value with your Client ID
4. Click **Save**

### 5. Deploy Application Code

Choose one of these methods:

#### Option A: VS Code (Easiest)

```bash
# Install Azure App Service extension
1. Open VS Code
2. Install "Azure App Service" extension
3. Sign in to Azure (bottom-left account icon)
4. Right-click CA_Policy_Manager_Web folder
5. Select "Deploy to Web App..."
6. Choose your web app
7. Confirm deployment
```

#### Option B: Azure CLI

```bash
# From CA_Policy_Manager_Web directory
cd "CA_Policy_Manager_Web"

# Create deployment zip
powershell Compress-Archive -Path * -DestinationPath deploy.zip -Force

# Deploy to Azure
az webapp deployment source config-zip `
  --resource-group ca-policy-manager-rg `
  --name <your-web-app-name> `
  --src deploy.zip
```

#### Option C: GitHub Actions (CI/CD)

```bash
# Download publish profile
Azure Portal → Your Web App → Get publish profile

# Add to GitHub Secrets
GitHub Repo → Settings → Secrets → New repository secret
Name: AZURE_WEBAPP_PUBLISH_PROFILE
Value: <paste publish profile XML>

# Create workflow file at .github/workflows/azure-deploy.yml
# See AZURE_DEPLOYMENT_QUICKSTART.md for workflow template
```

### 6. Verify Deployment

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
