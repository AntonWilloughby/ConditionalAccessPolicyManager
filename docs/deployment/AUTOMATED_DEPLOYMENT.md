# 🚀 One-Command Azure Deployment

Deploy CA Policy Manager to Azure in **one command** with full automation.

## Quick Start

### Windows (PowerShell)

```powershell
.\deploy-to-azure.ps1 -ResourceGroupName "ca-policy-rg" -WebAppName "my-ca-manager" -OpenAIName "my-openai-helper"
```

### Windows (Wizard - Easiest)

```cmd
DEPLOY_TO_AZURE.bat
```

Follow the interactive prompts.

### macOS / Linux (Bash)

```bash
chmod +x deploy-to-azure.sh
./deploy-to-azure.sh -g ca-policy-rg -w my-ca-manager -o my-openai-helper
```

## What Gets Automated

✅ **Azure Resources Created:**

- App Service (Python 3.12 web app)
- App Service Plan
- Azure OpenAI Service (GPT-4o-mini)

✅ **Automatic Configuration:**

- All application settings (AI, auth, Flask)
- Secret key generation
- HTTPS enforcement
- Startup commands
- Diagnostic logging

✅ **Azure AD Setup:**

- App Registration creation
- Redirect URI configuration
- API permission assignment
- Client ID injection

✅ **Code Deployment:**

- Automatic package creation
- ZIP deployment to Azure
- Build during deployment

## Prerequisites

- **Azure CLI** installed ([Download](https://aka.ms/installazurecli))
- **Python 3.11+** installed
- **Azure subscription** with Owner or Contributor access
- **Logged in** to Azure CLI (`az login`)

## Script Parameters

### PowerShell Script

| Parameter              | Required | Default   | Description                     |
| ---------------------- | -------- | --------- | ------------------------------- |
| `-ResourceGroupName`   | ✅ Yes   | -         | Azure resource group name       |
| `-WebAppName`          | ✅ Yes   | -         | Unique web app name             |
| `-OpenAIName`          | ✅ Yes   | -         | Unique OpenAI resource name     |
| `-Location`            | No       | `eastus2` | Azure region                    |
| `-Sku`                 | No       | `F1`      | Pricing tier (F1, B1, S1, P1v2) |
| `-SkipAppRegistration` | No       | `false`   | Skip creating App Registration  |

### Bash Script

| Parameter | Required | Default   | Description          |
| --------- | -------- | --------- | -------------------- |
| `-g`      | ✅ Yes   | -         | Resource group name  |
| `-w`      | ✅ Yes   | -         | Web app name         |
| `-o`      | ✅ Yes   | -         | OpenAI resource name |
| `-l`      | No       | `eastus2` | Azure region         |
| `-s`      | No       | `F1`      | App Service SKU      |

## Examples

### Basic Deployment (Free Tier)

```powershell
.\deploy-to-azure.ps1 `
  -ResourceGroupName "ca-policy-rg" `
  -WebAppName "my-ca-manager" `
  -OpenAIName "my-openai-helper"
```

### Production Deployment (B1 Tier + Custom Region)

```powershell
.\deploy-to-azure.ps1 `
  -ResourceGroupName "ca-policy-prod-rg" `
  -WebAppName "company-ca-manager" `
  -OpenAIName "company-openai" `
  -Location "westus3" `
  -Sku "B1"
```

### Using Existing App Registration

```powershell
.\deploy-to-azure.ps1 `
  -ResourceGroupName "ca-policy-rg" `
  -WebAppName "my-ca-manager" `
  -OpenAIName "my-openai-helper" `
  -SkipAppRegistration

# Then manually add MSAL_CLIENT_ID to App Service settings
```

### Bash (macOS/Linux)

```bash
./deploy-to-azure.sh \
  -g ca-policy-rg \
  -w my-ca-manager \
  -o my-openai-helper \
  -l westus3 \
  -s B1
```

## Supported Azure Regions

| Region            | Code               | Notes                               |
| ----------------- | ------------------ | ----------------------------------- |
| East US           | `eastus`           | General availability                |
| East US 2         | `eastus2`          | **Recommended** - good availability |
| West US           | `westus`           | General availability                |
| West US 3         | `westus3`          | Newer region, good performance      |
| North Central US  | `northcentralus`   | Central US                          |
| South Central US  | `southcentralus`   | Central US                          |
| Sweden Central    | `swedencentral`    | Europe (GDPR)                       |
| Switzerland North | `switzerlandnorth` | Europe (GDPR)                       |
| France Central    | `francecentral`    | Europe (GDPR)                       |
| UK South          | `uksouth`          | Europe (GDPR)                       |

## Pricing Tiers

| SKU      | Monthly Cost | RAM    | Features                  | Best For     |
| -------- | ------------ | ------ | ------------------------- | ------------ |
| **F1**   | $0           | 1GB    | 60 min/day, no Always On  | Testing      |
| **B1**   | ~$13         | 1.75GB | Always On, custom domains | Small teams  |
| **B2**   | ~$26         | 3.5GB  | More CPU/RAM              | Medium teams |
| **S1**   | ~$70         | 1.75GB | Auto-scaling, backups     | Production   |
| **P1v2** | ~$85         | 3.5GB  | Better performance, slots | Enterprise   |

> **Recommendation:** Start with **F1** for testing, upgrade to **B1** for production.

## Deployment Timeline

| Phase               | Duration     | Description                     |
| ------------------- | ------------ | ------------------------------- |
| Prerequisites check | 10 sec       | Verify Azure CLI, Python, login |
| Resource creation   | 3-5 min      | Create App Service, OpenAI      |
| Configuration       | 1 min        | Set app settings, secrets       |
| App Registration    | 30 sec       | Create/update Azure AD app      |
| Code deployment     | 2-3 min      | Upload and build application    |
| Logging setup       | 10 sec       | Enable diagnostics              |
| **Total**           | **8-12 min** | End-to-end deployment           |

## Post-Deployment Steps

The script outputs a complete summary with next steps. You'll need to:

### 1. Grant Admin Consent for App Registration (Required)

The automated script creates an Azure AD App Registration called **"CA Policy Manager - <your-app-name>"**. You need to grant admin consent for the API permissions:

**Steps:**

1. Open **Azure Portal** → **Azure Active Directory** → **App registrations**
2. Click **All applications** tab (important - it's a new app)
3. Find and click **CA Policy Manager - <your-app-name>**
4. Click **API permissions** in the left menu
5. Click **"Grant admin consent for [your tenant name]"** button
6. Click **Yes** to confirm

**What this does:** Grants your tenant-wide approval for the app to access Microsoft Graph API (User.Read, Policy.Read.All, Policy.ReadWrite.ConditionalAccess, Directory.Read.All).

### 2. Wait for Build Completion (~2 minutes)

Monitor deployment:

```
Azure Portal → Your Web App → Deployment Center → Logs
```

### 3. Test Your Application

Navigate to: `https://<your-webapp-name>.azurewebsites.net`

## Deployment Output

The script creates a `deployment-info.json` file with all details:

```json
{
  "deploymentDate": "2025-11-27 10:30:00",
  "webAppUrl": "https://my-ca-manager.azurewebsites.net",
  "webAppName": "my-ca-manager",
  "resourceGroup": "ca-policy-rg",
  "location": "eastus2",
  "sku": "F1",
  "openAIEndpoint": "https://my-openai-helper.openai.azure.com/",
  "openAIResourceName": "my-openai-helper",
  "clientId": "12345678-1234-1234-1234-123456789abc"
}
```

## Useful Post-Deployment Commands

### View Real-Time Logs

```powershell
az webapp log tail --name <webapp-name> --resource-group <rg-name>
```

### Restart Web App

```powershell
az webapp restart --name <webapp-name> --resource-group <rg-name>
```

### Update App Settings

```powershell
az webapp config appsettings set `
  --name <webapp-name> `
  --resource-group <rg-name> `
  --settings DEMO_MODE=false
```

### Scale Up to B1

```powershell
az appservice plan update `
  --name <webapp-name>-plan `
  --resource-group <rg-name> `
  --sku B1
```

### Add Custom Domain

```powershell
az webapp config hostname add `
  --webapp-name <webapp-name> `
  --resource-group <rg-name> `
  --hostname <your-domain.com>
```

## Troubleshooting

### "Resource name already exists"

**Cause:** Web App or OpenAI names must be globally unique.

**Solution:** Use different names:

```powershell
-WebAppName "my-ca-manager-prod-2025"
-OpenAIName "my-openai-helper-prod-2025"
```

### "Quota exceeded for SKU"

**Cause:** Your subscription doesn't have quota for Basic/Standard VMs.

**Solution:**

1. Use F1 tier (no quota needed)
2. OR request quota increase: Azure Portal → Subscriptions → Usage + quotas

### "Azure CLI not found"

**Cause:** Azure CLI not installed.

**Solution:** Install from https://aka.ms/installazurecli

### "Python not found"

**Cause:** Python not in PATH.

**Solution:**

- Windows: Install from https://www.python.org
- macOS: `brew install python3`
- Linux: `sudo apt install python3`

### "Not logged in to Azure"

**Cause:** Not authenticated with Azure CLI.

**Solution:**

```bash
az login
```

### Deployment succeeds but app shows error

**Cause:** Build may still be in progress.

**Solution:**

1. Wait 2-3 minutes
2. Check logs: Azure Portal → Web App → Log stream
3. Restart: `az webapp restart --name <name> --resource-group <rg>`

### AI features don't work

**Cause:** OpenAI deployment still provisioning or wrong endpoint.

**Solution:**

1. Check OpenAI deployment: Azure Portal → OpenAI Resource → Model deployments
2. Verify endpoint ends with `/`
3. Check API key is correct

## Security Notes

✅ **Secrets are auto-generated** and never exposed in scripts
✅ **HTTPS-only** enforced by default
✅ **API keys** stored in Azure App Service settings (encrypted)
✅ **No credentials** committed to git
✅ **Deployment info** saved locally only (not tracked)

## Clean Up Resources

To delete everything:

```powershell
# Delete resource group (removes all resources)
az group delete --name ca-policy-rg --yes --no-wait

# OR delete individual resources
az webapp delete --name <webapp-name> --resource-group <rg-name>
az cognitiveservices account delete --name <openai-name> --resource-group <rg-name>
```

## Advanced Usage

### Deploy to Multiple Environments

```powershell
# Development
.\deploy-to-azure.ps1 -ResourceGroupName "ca-dev-rg" -WebAppName "ca-dev" -OpenAIName "openai-dev" -Sku F1

# Staging
.\deploy-to-azure.ps1 -ResourceGroupName "ca-staging-rg" -WebAppName "ca-staging" -OpenAIName "openai-staging" -Sku B1

# Production
.\deploy-to-azure.ps1 -ResourceGroupName "ca-prod-rg" -WebAppName "ca-prod" -OpenAIName "openai-prod" -Sku S1
```

### Use Existing Resources

If you already have Azure OpenAI or App Service Plan:

1. Deploy with different names
2. Manually update app settings to point to existing resources
3. Delete auto-created resources if not needed

### CI/CD Integration

Use the script in Azure DevOps or GitHub Actions:

```yaml
# .github/workflows/deploy.yml
- name: Deploy to Azure
  run: |
    ./deploy-to-azure.sh \
      -g ${{ secrets.RESOURCE_GROUP }} \
      -w ${{ secrets.WEBAPP_NAME }} \
      -o ${{ secrets.OPENAI_NAME }} \
      -s B1
```

## Support

- **Script Issues**: Open a GitHub issue
- **Azure Errors**: Check Azure Portal → Activity Log
- **Deployment Logs**: Azure Portal → Web App → Deployment Center → Logs
- **Application Logs**: Azure Portal → Web App → Log stream

## Comparison with Manual Deployment

| Task               | Manual     | Automated Script | Time Saved       |
| ------------------ | ---------- | ---------------- | ---------------- |
| Create resources   | 5 min      | Automated        | 5 min            |
| Generate secrets   | 2 min      | Automated        | 2 min            |
| Configure settings | 10 min     | Automated        | 10 min           |
| Create App Reg     | 5 min      | Automated        | 5 min            |
| Deploy code        | 5 min      | Automated        | 5 min            |
| Enable logging     | 2 min      | Automated        | 2 min            |
| **Total**          | **29 min** | **10 min**       | **19 min saved** |

Plus: No manual errors, consistent configuration, repeatable deployments! 🎉
