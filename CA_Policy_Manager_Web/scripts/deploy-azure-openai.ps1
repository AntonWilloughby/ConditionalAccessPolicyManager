#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Deploy Azure OpenAI resources for CA Policy Manager

.DESCRIPTION
    This script automates the deployment of Azure OpenAI resources including:
    - Azure OpenAI cognitive service
    - GPT-4o-mini model deployment
    - Configuration output for .env file

.PARAMETER ResourceGroupName
    Name of the resource group (default: rg-capolicy-dev)

.PARAMETER Location
    Azure region for deployment (default: eastus2)

.PARAMETER OpenAIResourceName
    Name for the Azure OpenAI resource (default: auto-generated)

.EXAMPLE
    .\deploy-azure-openai.ps1
    
.EXAMPLE
    .\deploy-azure-openai.ps1 -ResourceGroupName "rg-capolicy-prod" -Location "swedencentral"
#>

param(
    [string]$ResourceGroupName = "",
    [string]$Location = "",
    [string]$OpenAIResourceName = ""
)

Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Azure OpenAI Deployment for CA Policy Manager          ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Check if Azure CLI is installed
try {
    $azVersion = az version --output json 2>$null | ConvertFrom-Json
    Write-Host "✓ Azure CLI found (version $($azVersion.'azure-cli'))" -ForegroundColor Green
}
catch {
    Write-Host "✗ Azure CLI not found" -ForegroundColor Red
    Write-Host "`nPlease install Azure CLI from: https://docs.microsoft.com/cli/azure/install-azure-cli" -ForegroundColor Yellow
    exit 1
}

# Login to Azure
Write-Host "`n📋 Step 1: Azure Login" -ForegroundColor Cyan
Write-Host "─────────────────────────" -ForegroundColor DarkGray

$account = az account show 2>$null | ConvertFrom-Json
if (-not $account) {
    Write-Host "Not logged in. Opening browser for authentication..." -ForegroundColor Yellow
    az login
    $account = az account show | ConvertFrom-Json
}

Write-Host "✓ Logged in as: $($account.user.name)" -ForegroundColor Green
Write-Host "✓ Subscription: $($account.name) ($($account.id))" -ForegroundColor Green

# Confirm subscription or let user choose
Write-Host "`nDo you want to use this subscription? (Y/n): " -ForegroundColor Yellow -NoNewline
$response = Read-Host
if ($response -eq 'n' -or $response -eq 'N') {
    Write-Host "`nAvailable subscriptions:"
    az account list --output table
    Write-Host "`nEnter subscription ID: " -NoNewline
    $subId = Read-Host
    az account set --subscription $subId
    $account = az account show | ConvertFrom-Json
    Write-Host "✓ Switched to: $($account.name)" -ForegroundColor Green
}

# Get or prompt for resource group name
if (-not $ResourceGroupName) {
    Write-Host "`n📦 Step 2: Resource Group" -ForegroundColor Cyan
    Write-Host "─────────────────────────" -ForegroundColor DarkGray
    Write-Host "Enter resource group name (press Enter for 'rg-capolicy-dev'): " -ForegroundColor Yellow -NoNewline
    $input = Read-Host
    $ResourceGroupName = if ($input) { $input } else { "rg-capolicy-dev" }
}

# Check if resource group exists
$rgExists = az group exists --name $ResourceGroupName
if ($rgExists -eq "true") {
    Write-Host "✓ Resource group '$ResourceGroupName' already exists" -ForegroundColor Green
}
else {
    # Get or prompt for location
    if (-not $Location) {
        Write-Host "`nRecommended regions for Azure OpenAI:" -ForegroundColor Cyan
        Write-Host "  1. eastus2       (East US 2)"
        Write-Host "  2. swedencentral (Sweden Central)"
        Write-Host "  3. uksouth       (UK South)"
        Write-Host "  4. westus3       (West US 3)"
        Write-Host "`nEnter region (press Enter for 'eastus2'): " -ForegroundColor Yellow -NoNewline
        $input = Read-Host
        $Location = if ($input) { $input } else { "eastus2" }
    }
    
    Write-Host "Creating resource group..." -ForegroundColor Yellow
    az group create --name $ResourceGroupName --location $Location --output none
    Write-Host "✓ Created resource group '$ResourceGroupName' in $Location" -ForegroundColor Green
}

# Get or generate OpenAI resource name
if (-not $OpenAIResourceName) {
    Write-Host "`n🤖 Step 3: Azure OpenAI Resource" -ForegroundColor Cyan
    Write-Host "─────────────────────────────────" -ForegroundColor DarkGray
    
    # Generate default name with random suffix for uniqueness
    $randomSuffix = -join ((97..122) | Get-Random -Count 4 | ForEach-Object { [char]$_ })
    $defaultName = "openai-capolicy-$randomSuffix"
    
    Write-Host "Enter Azure OpenAI resource name (press Enter for '$defaultName'): " -ForegroundColor Yellow -NoNewline
    $input = Read-Host
    $OpenAIResourceName = if ($input) { $input } else { $defaultName }
}

# Check if OpenAI resource already exists
$existingResource = az cognitiveservices account show `
    --resource-group $ResourceGroupName `
    --name $OpenAIResourceName `
    2>$null | ConvertFrom-Json

if ($existingResource) {
    Write-Host "✓ Azure OpenAI resource '$OpenAIResourceName' already exists" -ForegroundColor Green
    $endpoint = $existingResource.properties.endpoint
}
else {
    # Get location if not set
    if (-not $Location) {
        $rg = az group show --name $ResourceGroupName | ConvertFrom-Json
        $Location = $rg.location
    }
    
    Write-Host "Creating Azure OpenAI resource..." -ForegroundColor Yellow
    Write-Host "  Name: $OpenAIResourceName" -ForegroundColor Gray
    Write-Host "  Location: $Location" -ForegroundColor Gray
    Write-Host "  SKU: S0 (Standard)" -ForegroundColor Gray
    Write-Host "`nThis may take 2-3 minutes..." -ForegroundColor Yellow
    
    $result = az cognitiveservices account create `
        --name $OpenAIResourceName `
        --resource-group $ResourceGroupName `
        --kind OpenAI `
        --sku S0 `
        --location $Location `
        --yes `
        2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to create Azure OpenAI resource" -ForegroundColor Red
        Write-Host "Error: $result" -ForegroundColor Red
        Write-Host "`nCommon issues:" -ForegroundColor Yellow
        Write-Host "  - Region doesn't support Azure OpenAI (try eastus2 or swedencentral)" -ForegroundColor Yellow
        Write-Host "  - Quota limit reached (request increase in Azure Portal)" -ForegroundColor Yellow
        Write-Host "  - Name already taken (try a different name)" -ForegroundColor Yellow
        exit 1
    }
    
    $resource = az cognitiveservices account show `
        --resource-group $ResourceGroupName `
        --name $OpenAIResourceName | ConvertFrom-Json
    
    $endpoint = $resource.properties.endpoint
    Write-Host "✓ Created Azure OpenAI resource" -ForegroundColor Green
}

# Deploy GPT-4o-mini model
Write-Host "`n🎯 Step 4: Deploy GPT-4o-mini Model" -ForegroundColor Cyan
Write-Host "────────────────────────────────────" -ForegroundColor DarkGray

$deploymentName = "gpt-4o-mini"

# Check if deployment already exists
$existingDeployment = az cognitiveservices account deployment show `
    --resource-group $ResourceGroupName `
    --name $OpenAIResourceName `
    --deployment-name $deploymentName `
    2>$null | ConvertFrom-Json

if ($existingDeployment) {
    Write-Host "✓ Model deployment '$deploymentName' already exists" -ForegroundColor Green
}
else {
    Write-Host "Deploying gpt-4o-mini model..." -ForegroundColor Yellow
    Write-Host "  Deployment name: $deploymentName" -ForegroundColor Gray
    Write-Host "  Capacity: 30K TPM (tokens per minute)" -ForegroundColor Gray
    Write-Host "`nThis may take 1-2 minutes..." -ForegroundColor Yellow
    
    $deployResult = az cognitiveservices account deployment create `
        --resource-group $ResourceGroupName `
        --name $OpenAIResourceName `
        --deployment-name $deploymentName `
        --model-name "gpt-4o-mini" `
        --model-version "2024-07-18" `
        --model-format OpenAI `
        --sku-capacity 30 `
        --sku-name "Standard" `
        2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to deploy model" -ForegroundColor Red
        Write-Host "Error: $deployResult" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✓ Deployed gpt-4o-mini model" -ForegroundColor Green
}

# Get API keys
Write-Host "`n🔑 Step 5: Retrieve Credentials" -ForegroundColor Cyan
Write-Host "───────────────────────────────" -ForegroundColor DarkGray

$keys = az cognitiveservices account keys list `
    --resource-group $ResourceGroupName `
    --name $OpenAIResourceName | ConvertFrom-Json

$apiKey = $keys.key1

# Output configuration
Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║               ✓ Deployment Successful!                   ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "📋 Configuration Values for .env file:" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor DarkGray

Write-Host "`nAI_ENABLED=true" -ForegroundColor White
Write-Host "AI_PROVIDER=azure" -ForegroundColor White
Write-Host "AZURE_OPENAI_ENDPOINT=$endpoint" -ForegroundColor White
Write-Host "AZURE_OPENAI_API_KEY=$apiKey" -ForegroundColor White
Write-Host "AZURE_OPENAI_DEPLOYMENT=$deploymentName" -ForegroundColor White

Write-Host "`n═══════════════════════════════════════════════════════════" -ForegroundColor DarkGray

Write-Host "`n📝 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Copy the values above to your .env file" -ForegroundColor White
Write-Host "  2. Restart the Flask application" -ForegroundColor White
Write-Host "  3. Test AI features by clicking 'Explain with AI' on any policy" -ForegroundColor White

Write-Host "`n💰 Cost Monitoring:" -ForegroundColor Cyan
Write-Host "  View usage: https://portal.azure.com/#@/resource/subscriptions/$($account.id)/resourceGroups/$ResourceGroupName/providers/Microsoft.CognitiveServices/accounts/$OpenAIResourceName/overview" -ForegroundColor White

Write-Host "`n✨ Deployment complete!`n" -ForegroundColor Green
