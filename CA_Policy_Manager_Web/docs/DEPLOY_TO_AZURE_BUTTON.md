# Deploy to Azure Button Setup

This guide explains how to add and configure the "Deploy to Azure" button for your GitHub repository.

## What the Button Does

The "Deploy to Azure" button allows users to deploy Azure OpenAI resources directly from your GitHub repository with one click. It uses an Azure Resource Manager (ARM) template to automate the deployment.

## Files Included

1. **`azure-deploy.json`** - ARM template that deploys:
   - Azure OpenAI Cognitive Services account
   - GPT-4o-mini model deployment with configurable capacity
   - Outputs endpoint and deployment information

## Setup Steps

### 1. Update README.md

Replace the placeholder in the README.md badge URL:

```markdown
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FYOUR_USERNAME%2FYOUR_REPO%2Fmain%2Fazure-deploy.json)
```

Change `YOUR_USERNAME/YOUR_REPO` to your actual GitHub path. For example:
- If your repo is `https://github.com/johndoe/ca-policy-manager`
- Change to: `johndoe%2Fca-policy-manager`

**Important:** The URL must be URL-encoded:
- `/` becomes `%2F`
- `:` becomes `%3A`

### 2. Commit and Push to GitHub

```bash
git add azure-deploy.json README.md
git commit -m "Add Deploy to Azure button with ARM template"
git push origin main
```

### 3. Verify the Template is Accessible

The ARM template must be accessible via raw GitHub URL. After pushing, verify:

```
https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/azure-deploy.json
```

### 4. Test the Button

1. View your README on GitHub
2. Click the "Deploy to Azure" button
3. You should be redirected to Azure Portal's custom deployment page
4. The form should show parameters from the template

## How Users Deploy

When someone clicks the button:

1. **Azure Login** - User is prompted to log in to Azure Portal
2. **Select Subscription** - Choose which Azure subscription to deploy to
3. **Configure Parameters**:
   - **Resource Group**: Create new or select existing
   - **Region**: Choose from supported regions (defaults to East US 2)
   - **OpenAI Resource Name**: Unique name for the OpenAI resource
   - **Deployment Name**: Name for the model deployment (default: gpt-4o-mini)
   - **Model Capacity**: Tokens per minute (default: 30K)
4. **Review + Create** - Azure validates the template and deploys resources
5. **Get Credentials** - After deployment, user navigates to the resource to get API keys

## ARM Template Parameters

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `openAIResourceName` | Unique name for Azure OpenAI resource | - | Yes |
| `location` | Azure region | `eastus2` | Yes |
| `deploymentName` | Model deployment name | `gpt-4o-mini` | No |
| `modelCapacity` | TPM capacity (thousands) | `30` | No |

## Supported Regions

The template restricts deployment to regions that support GPT-4o-mini:
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

## Template Outputs

After successful deployment, the template outputs:

```json
{
  "openAIEndpoint": "https://your-resource.openai.azure.com/",
  "openAIResourceName": "your-resource-name",
  "deploymentName": "gpt-4o-mini",
  "instructions": "Copy the endpoint above and retrieve your API key..."
}
```

Users can find these in the **Outputs** tab of the deployment in Azure Portal.

## Post-Deployment Steps for Users

After clicking "Deploy to Azure" and completing deployment:

1. **Get API Key**:
   ```
   Azure Portal → Your OpenAI Resource → Keys and Endpoint → Copy Key 1
   ```

2. **Configure .env file**:
   ```env
   AI_ENABLED=true
   AI_PROVIDER=azure
   AZURE_OPENAI_ENDPOINT=<from deployment outputs>
   AZURE_OPENAI_API_KEY=<from Keys and Endpoint>
   AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
   ```

3. **Restart the application**

## Alternative Deployment Methods

Users can also deploy using:

1. **PowerShell Script**: `scripts/deploy-azure-openai.ps1`
2. **Bash Script**: `scripts/deploy-azure-openai.sh`
3. **Azure CLI**: Commands in `docs/AZURE_OPENAI_SETUP.md`
4. **Manual**: Step-by-step in Azure Portal

## Troubleshooting

### Button Shows 404 Error
- Verify the ARM template is pushed to `main` branch
- Check the URL in the badge is correctly URL-encoded
- Ensure repository is public or user has access

### Template Validation Fails
- Region may not support Azure OpenAI
- Quota limit reached in subscription
- Resource name already taken (must be globally unique)

### Deployment Succeeds but No Endpoint
- Wait 1-2 minutes for resource provisioning
- Check deployment outputs tab in Azure Portal
- Verify model deployment completed successfully

## Customization

To modify the template:

1. Edit `azure-deploy.json`
2. Change parameters, resources, or outputs
3. Test with Azure CLI:
   ```bash
   az deployment group validate \
     --resource-group test-rg \
     --template-file azure-deploy.json \
     --parameters openAIResourceName=test-openai
   ```
4. Commit and push changes

## Security Considerations

- ✅ Template only creates resources, doesn't expose secrets
- ✅ API keys never appear in template or GitHub
- ✅ Users retrieve keys from their own Azure Portal
- ⚠️ Users should follow `.env` security practices (never commit)
- ⚠️ Recommend setting up Azure Key Vault for production

## Cost Estimation

Deploying via button creates:
- 1x Azure OpenAI resource (S0 tier): ~$0/month base
- 1x GPT-4o-mini deployment: Pay-per-token usage
  - Input: $0.150 per 1M tokens
  - Output: $0.600 per 1M tokens

Typical usage: $0.03-$3.00/day depending on volume.

## Additional Resources

- [Azure ARM Template Documentation](https://docs.microsoft.com/azure/azure-resource-manager/templates/)
- [Azure OpenAI Service](https://azure.microsoft.com/services/cognitive-services/openai-service/)
- [Deploy to Azure Button Documentation](https://docs.microsoft.com/azure/azure-resource-manager/templates/deploy-to-azure-button)
