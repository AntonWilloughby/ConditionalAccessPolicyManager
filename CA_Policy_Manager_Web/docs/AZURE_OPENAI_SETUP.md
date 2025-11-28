# Azure OpenAI Setup Guide

This guide will help you deploy Azure OpenAI resources to enable AI-powered policy explanations in the CA Policy Manager.

## Prerequisites

- Azure subscription with access to create resources
- Azure CLI installed ([Download here](https://docs.microsoft.com/cli/azure/install-azure-cli))
- Permissions to create Azure OpenAI resources in your subscription
- PowerShell (for Windows) or Bash (for Linux/Mac)

## Option 1: Automated Deployment (Recommended)

### Windows (PowerShell)

```powershell
cd scripts
.\deploy-azure-openai.ps1
```

### Linux/Mac (Bash)

```bash
cd scripts
chmod +x deploy-azure-openai.sh
./deploy-azure-openai.sh
```

The script will:

1. Prompt you to login to Azure
2. Let you select a subscription
3. Create a resource group (or use existing)
4. Deploy Azure OpenAI resource
5. Deploy a GPT-4o-mini model
6. Output the configuration values for your `.env` file

## Option 2: Manual Deployment via Azure Portal

### Step 1: Create Azure OpenAI Resource

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **"Create a resource"**
3. Search for **"Azure OpenAI"**
4. Click **"Create"**
5. Fill in the details:
   - **Subscription**: Choose your subscription
   - **Resource Group**: Create new or select existing (e.g., `rg-capolicy-dev`)
   - **Region**: Choose a region that supports GPT-4o-mini (e.g., `East US 2`, `Sweden Central`)
   - **Name**: Choose a unique name (e.g., `openai-capolicy-yourname`)
   - **Pricing tier**: Standard S0
6. Click **"Review + Create"**, then **"Create"**

### Step 2: Deploy GPT-4o-mini Model

1. Once the resource is created, go to the resource
2. Click on **"Model deployments"** in the left menu
3. Click **"+ Create new deployment"**
4. Fill in:
   - **Select a model**: `gpt-4o-mini`
   - **Model version**: Auto-update to default
   - **Deployment name**: `gpt-4o-mini` (use this exact name for compatibility)
   - **Deployment type**: Standard
   - **Tokens per Minute Rate Limit**: 30K (adjust based on your needs)
5. Click **"Create"**

### Step 3: Get Your Credentials

1. In your Azure OpenAI resource, click **"Keys and Endpoint"** in the left menu
2. Copy the following:
   - **Endpoint**: (e.g., `https://openai-capolicy-yourname.openai.azure.com/`)
   - **Key 1** or **Key 2**: (either one works)

### Step 4: Configure the Application

1. Open the `.env` file in the `CA_Policy_Manager_Web` folder
2. Update these values:

```env
# AI Configuration
AI_ENABLED=true
AI_PROVIDER=azure

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```

3. Restart the application

## Option 3: Manual Deployment via Azure CLI

```bash
# Login to Azure
az login

# Set your subscription (replace with your subscription ID)
az account set --subscription "YOUR_SUBSCRIPTION_ID"

# Create resource group
az group create --name rg-capolicy-dev --location eastus2

# Create Azure OpenAI resource
az cognitiveservices account create \
  --name openai-capolicy-dev \
  --resource-group rg-capolicy-dev \
  --kind OpenAI \
  --sku S0 \
  --location eastus2

# Deploy GPT-4o-mini model
az cognitiveservices account deployment create \
  --resource-group rg-capolicy-dev \
  --name openai-capolicy-dev \
  --deployment-name gpt-4o-mini \
  --model-name gpt-4o-mini \
  --model-version "2024-07-18" \
  --model-format OpenAI \
  --sku-capacity 30 \
  --sku-name Standard

# Get endpoint
az cognitiveservices account show \
  --resource-group rg-capolicy-dev \
  --name openai-capolicy-dev \
  --query "properties.endpoint" -o tsv

# Get API key
az cognitiveservices account keys list \
  --resource-group rg-capolicy-dev \
  --name openai-capolicy-dev \
  --query "key1" -o tsv
```

## Supported Regions for Azure OpenAI

Azure OpenAI with GPT-4o-mini is available in these regions:

- East US
- East US 2
- North Central US
- South Central US
- West US
- West US 3
- Sweden Central
- Switzerland North
- France Central
- UK South

Choose a region close to your users for best performance.

## Pricing Information

**Azure OpenAI GPT-4o-mini (as of November 2024)**:

- Input: $0.150 per 1M tokens (~750K words)
- Output: $0.600 per 1M tokens (~750K words)

**Estimated costs for typical usage**:

- 10 policy explanations/day: ~$0.03/day or ~$0.90/month
- 100 policy explanations/day: ~$0.30/day or ~$9/month
- 1000 policy explanations/day: ~$3.00/day or ~$90/month

Each policy explanation uses approximately:

- 800-1500 input tokens (policy JSON + system prompt)
- 300-800 output tokens (explanation text)

## Troubleshooting

### "Resource quota exceeded"

- Azure OpenAI has quota limits per subscription
- Request quota increase: [Azure Portal → Quotas](https://portal.azure.com/#view/Microsoft_Azure_Capacity/QuotaMenuBlade/~/overview)
- Or use a different region

### "Model not available in region"

- Check [Azure OpenAI Model Availability](https://learn.microsoft.com/azure/ai-services/openai/concepts/models#model-summary-table-and-region-availability)
- Try deploying in East US 2 or Sweden Central

### "Invalid API key"

- Make sure you copied the full key (no spaces)
- Try regenerating the key in Azure Portal
- Verify the endpoint URL ends with `/` (trailing slash)

### "Rate limit exceeded"

- Increase TPM (Tokens Per Minute) in your deployment settings
- Or wait a moment and try again
- Consider upgrading to Provisioned Throughput for high volume

## Security Best Practices

1. **Never commit `.env` file** to version control (already in `.gitignore`)
2. **Use different resources for dev/prod** environments
3. **Rotate API keys regularly** (every 90 days recommended)
4. **Use Azure Key Vault** for production deployments
5. **Enable diagnostic logging** to monitor usage
6. **Set up cost alerts** in Azure to monitor spending

## Alternative: OpenAI API (Non-Azure)

If you prefer to use OpenAI directly instead of Azure:

1. Create an account at [platform.openai.com](https://platform.openai.com)
2. Create an API key
3. Update `.env`:

```env
AI_ENABLED=true
AI_PROVIDER=openai

OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

**Note**: OpenAI API pricing is slightly different from Azure OpenAI.

## Next Steps

After setting up Azure OpenAI:

1. Test the AI features by clicking "Explain with AI" on any policy
2. Monitor your Azure OpenAI usage in the Azure Portal
3. Set up cost alerts to avoid unexpected charges
4. Share the `.env.example` template with your team

## Support

For issues with:

- **Azure OpenAI deployment**: Check [Azure OpenAI Documentation](https://learn.microsoft.com/azure/ai-services/openai/)
- **Application configuration**: See the root `README.md` and `QUICK_SETUP.md`
- **API errors**: Enable debug mode and check application logs
