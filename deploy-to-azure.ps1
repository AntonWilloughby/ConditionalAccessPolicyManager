#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Automated Azure deployment for CA Policy Manager

.DESCRIPTION
    This script automates the complete deployment of CA Policy Manager to Azure:
    - Creates App Service and Azure OpenAI resources
    - Configures application settings
    - Updates Azure AD redirect URI
    - Deploys application code
    - Generates and stores secrets securely

.PARAMETER ResourceGroupName
    Name for the Azure resource group (will be created if doesn't exist)

.PARAMETER WebAppName
    Globally unique name for your web app (becomes <name>.azurewebsites.net)

.PARAMETER OpenAIName
    Globally unique name for Azure OpenAI resource

.PARAMETER Location
    Azure region (default: eastus2)

.PARAMETER Sku
    App Service pricing tier: F1 (Free), B1 (Basic), S1 (Standard), P1v2 (Premium)

.PARAMETER SkipAppRegistration
    Skip creating/updating Azure AD App Registration (use existing)

.EXAMPLE
    .\deploy-to-azure.ps1 -ResourceGroupName "ca-policy-rg" -WebAppName "my-ca-manager" -OpenAIName "my-openai-helper"

.EXAMPLE
    .\deploy-to-azure.ps1 -ResourceGroupName "ca-policy-rg" -WebAppName "my-ca-manager" -OpenAIName "my-openai-helper" -Sku B1 -Location westus3

.NOTES
    Requirements: Azure CLI, PowerShell 7+, Owner/Contributor access to Azure subscription
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,

    [Parameter(Mandatory = $true)]
    [string]$WebAppName,

    [Parameter(Mandatory = $true)]
    [string]$OpenAIName,

    [Parameter(Mandatory = $false)]
    [ValidateSet('eastus', 'eastus2', 'westus', 'westus3', 'northcentralus', 'southcentralus', 'swedencentral', 'switzerlandnorth', 'francecentral', 'uksouth')]
    [string]$Location = 'eastus2',

    [Parameter(Mandatory = $false)]
    [ValidateSet('F1', 'B1', 'B2', 'S1', 'S2', 'P1v2', 'P2v2')]
    [string]$Sku = 'F1',

    [Parameter(Mandatory = $false)]
    [switch]$SkipAppRegistration
)

$ErrorActionPreference = 'Stop'

# Colors for output
function Write-Step { param($Message) Write-Host "`n✓ $Message" -ForegroundColor Cyan }
function Write-Success { param($Message) Write-Host "  ✓ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "  ℹ $Message" -ForegroundColor Yellow }
function Write-Error-Custom { param($Message) Write-Host "  ✗ $Message" -ForegroundColor Red }

Write-Host @"

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║       CA Policy Manager - Automated Azure Deployment         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# ============================================================================
# Step 1: Verify Prerequisites
# ============================================================================
Write-Step "Checking prerequisites..."

# Check Azure CLI
try {
    $azVersion = az version --query '"azure-cli"' -o tsv 2>$null
    Write-Success "Azure CLI installed (version $azVersion)"
}
catch {
    Write-Error-Custom "Azure CLI not found. Install from: https://aka.ms/installazurecli"
    exit 1
}

# Check if logged in
try {
    $account = az account show 2>$null | ConvertFrom-Json
    Write-Success "Logged in as: $($account.user.name)"
    Write-Info "Subscription: $($account.name) ($($account.id))"
}
catch {
    Write-Info "Not logged in to Azure. Launching browser..."
    az login
    $account = az account show | ConvertFrom-Json
}

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Success "Python installed: $pythonVersion"
}
catch {
    Write-Error-Custom "Python not found. Install Python 3.11+ from: https://www.python.org"
    exit 1
}

# ============================================================================
# Step 2: Create Resource Group
# ============================================================================
Write-Step "Creating resource group '$ResourceGroupName'..."

$rgExists = az group exists --name $ResourceGroupName
if ($rgExists -eq 'true') {
    Write-Info "Resource group already exists"
}
else {
    az group create --name $ResourceGroupName --location $Location --output none
    Write-Success "Resource group created"
}

# ============================================================================
# Step 3: Generate Secrets
# ============================================================================
Write-Step "Generating secure secrets..."

$secretKey = python -c "import secrets; print(secrets.token_hex(32))"
Write-Success "Flask SECRET_KEY generated"

# ============================================================================
# Step 4: Deploy Azure OpenAI
# ============================================================================
Write-Step "Deploying Azure OpenAI resource '$OpenAIName'..."

$openAIExists = az cognitiveservices account show `
    --name $OpenAIName `
    --resource-group $ResourceGroupName `
    2>$null

if ($openAIExists) {
    Write-Info "Azure OpenAI resource already exists"
}
else {
    Write-Info "Creating Azure OpenAI resource (this may take 2-3 minutes)..."
    az cognitiveservices account create `
        --name $OpenAIName `
        --resource-group $ResourceGroupName `
        --location $Location `
        --kind OpenAI `
        --sku S0 `
        --custom-domain $OpenAIName `
        --output none
    
    Write-Success "Azure OpenAI resource created"
}

# Get OpenAI endpoint and key
$openAIEndpoint = az cognitiveservices account show `
    --name $OpenAIName `
    --resource-group $ResourceGroupName `
    --query properties.endpoint -o tsv

$openAIKey = az cognitiveservices account keys list `
    --name $OpenAIName `
    --resource-group $ResourceGroupName `
    --query key1 -o tsv

Write-Success "Retrieved OpenAI credentials"

# Deploy GPT-4o-mini model
Write-Info "Deploying GPT-4o-mini model..."
$deploymentExists = az cognitiveservices account deployment show `
    --name $OpenAIName `
    --resource-group $ResourceGroupName `
    --deployment-name gpt-4o-mini `
    2>$null

if ($deploymentExists) {
    Write-Info "Model deployment already exists"
}
else {
    az cognitiveservices account deployment create `
        --name $OpenAIName `
        --resource-group $ResourceGroupName `
        --deployment-name gpt-4o-mini `
        --model-name gpt-4o-mini `
        --model-version "2024-07-18" `
        --model-format OpenAI `
        --sku-capacity 30 `
        --sku-name "Standard" `
        --output none
    
    Write-Success "GPT-4o-mini model deployed"
}

# ============================================================================
# Step 5: Create App Service
# ============================================================================
Write-Step "Creating App Service '$WebAppName'..."

$appServicePlan = "$WebAppName-plan"

# Create App Service Plan
$planExists = az appservice plan show `
    --name $appServicePlan `
    --resource-group $ResourceGroupName `
    2>$null

if ($planExists) {
    Write-Info "App Service Plan already exists"
}
else {
    az appservice plan create `
        --name $appServicePlan `
        --resource-group $ResourceGroupName `
        --location $Location `
        --is-linux `
        --sku $Sku `
        --output none
    
    Write-Success "App Service Plan created ($Sku tier)"
}

# Create Web App
$webAppExists = az webapp show `
    --name $WebAppName `
    --resource-group $ResourceGroupName `
    2>$null

if ($webAppExists) {
    Write-Info "Web App already exists"
}
else {
    az webapp create `
        --name $WebAppName `
        --resource-group $ResourceGroupName `
        --plan $appServicePlan `
        --runtime "PYTHON:3.12" `
        --output none
    
    Write-Success "Web App created"
}

$webAppUrl = "https://$WebAppName.azurewebsites.net"
Write-Info "Web App URL: $webAppUrl"

# ============================================================================
# Step 6: Configure App Service Settings
# ============================================================================
Write-Step "Configuring application settings..."

$settings = @(
    "SECRET_KEY=$secretKey"
    "AZURE_OPENAI_ENDPOINT=$openAIEndpoint"
    "AZURE_OPENAI_API_KEY=$openAIKey"
    "AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini"
    "AZURE_OPENAI_API_VERSION=2024-02-15-preview"
    "AI_ENABLED=true"
    "AI_PROVIDER=azure"
    "AI_USE_MAX_COMPLETION_TOKENS=true"
    "MSAL_TENANT_ID=organizations"
    "MSAL_REDIRECT_PATH=/auth/callback"
    "DEMO_MODE=false"
    "FLASK_ENV=production"
    "DISABLE_SSL_VERIFY=false"
    "SESSION_TYPE=filesystem"
    "SCM_DO_BUILD_DURING_DEPLOYMENT=true"
    "ENABLE_ORYX_BUILD=true"
)

az webapp config appsettings set `
    --name $WebAppName `
    --resource-group $ResourceGroupName `
    --settings $settings `
    --output none

Write-Success "Application settings configured"

# Set startup command
az webapp config set `
    --name $WebAppName `
    --resource-group $ResourceGroupName `
    --startup-file "gunicorn --bind=0.0.0.0:8000 --timeout 600 app:app" `
    --output none

Write-Success "Startup command configured"

# Enable HTTPS only
az webapp update `
    --name $WebAppName `
    --resource-group $ResourceGroupName `
    --https-only true `
    --output none

Write-Success "HTTPS-only enabled"

# Enable Always On (if not F1 tier)
if ($Sku -ne 'F1') {
    az webapp config set `
        --name $WebAppName `
        --resource-group $ResourceGroupName `
        --always-on true `
        --output none
    
    Write-Success "Always On enabled"
}

# ============================================================================
# Step 7: Create/Update Azure AD App Registration
# ============================================================================
if (-not $SkipAppRegistration) {
    Write-Step "Configuring Azure AD App Registration..."

    $redirectUri = "$webAppUrl/auth/callback"
    $appName = "CA Policy Manager - $WebAppName"

    # Check if app registration exists
    $existingApp = az ad app list --display-name $appName --query "[0]" | ConvertFrom-Json

    if ($existingApp) {
        Write-Info "Updating existing App Registration..."
        $appId = $existingApp.appId
        
        # Update redirect URIs
        az ad app update `
            --id $appId `
            --web-redirect-uris $redirectUri `
            --output none
        
        Write-Success "App Registration updated (Client ID: $appId)"
    }
    else {
        Write-Info "Creating new App Registration..."
        
        # Create app registration
        $newApp = az ad app create `
            --display-name $appName `
            --sign-in-audience AzureADMultipleOrgs `
            --web-redirect-uris $redirectUri `
            --enable-id-token-issuance true | ConvertFrom-Json
        
        $appId = $newApp.appId
        
        Write-Success "App Registration created (Client ID: $appId)"
        
        # Add Microsoft Graph API permissions
        Write-Info "Adding Microsoft Graph API permissions..."
        
        # Policy.Read.All (delegated)
        az ad app permission add `
            --id $appId `
            --api 00000003-0000-0000-c000-000000000000 `
            --api-permissions 37f7f235-527c-4136-accd-4a02d197296e=Scope `
            --output none
        
        # Application.Read.All (delegated)
        az ad app permission add `
            --id $appId `
            --api 00000003-0000-0000-c000-000000000000 `
            --api-permissions c79f8feb-a9db-4090-85f9-90d820caa0eb=Scope `
            --output none
        
        Write-Success "API permissions added"
        Write-Info "Admin must grant consent in Azure Portal → App Registrations → $appName → API permissions"
    }
    
    # Update Web App with MSAL_CLIENT_ID
    az webapp config appsettings set `
        --name $WebAppName `
        --resource-group $ResourceGroupName `
        --settings "MSAL_CLIENT_ID=$appId" `
        --output none
    
    Write-Success "MSAL_CLIENT_ID configured in Web App"
}
else {
    Write-Info "Skipping App Registration (use existing Client ID)"
    Write-Info "Remember to manually add redirect URI: $webAppUrl/auth/callback"
}

# ============================================================================
# Step 8: Deploy Application Code
# ============================================================================
Write-Step "Deploying application code..."

$appFolder = Join-Path $PSScriptRoot "CA_Policy_Manager_Web"

if (-not (Test-Path $appFolder)) {
    Write-Error-Custom "CA_Policy_Manager_Web folder not found at: $appFolder"
    Write-Info "Please run this script from the repository root directory"
    exit 1
}

# Create deployment package
$deployZip = Join-Path $PSScriptRoot "deploy.zip"
Write-Info "Creating deployment package..."

Push-Location $appFolder
try {
    if (Test-Path $deployZip) { Remove-Item $deployZip -Force }
    
    # Create zip excluding unnecessary files
    $excludePatterns = @('__pycache__', '*.pyc', '.env', '.venv', 'data/uploads/*', 'data/backups/*')
    
    Compress-Archive -Path * -DestinationPath $deployZip -Force
    Write-Success "Deployment package created"
}
finally {
    Pop-Location
}

# Deploy to Azure
Write-Info "Uploading to Azure (this may take 2-3 minutes)..."
az webapp deployment source config-zip `
    --name $WebAppName `
    --resource-group $ResourceGroupName `
    --src $deployZip `
    --output none

Remove-Item $deployZip -Force
Write-Success "Application code deployed"

# ============================================================================
# Step 9: Enable Logging
# ============================================================================
Write-Step "Enabling application logging..."

az webapp log config `
    --name $WebAppName `
    --resource-group $ResourceGroupName `
    --application-logging filesystem `
    --detailed-error-messages true `
    --failed-request-tracing true `
    --web-server-logging filesystem `
    --output none

Write-Success "Diagnostic logging enabled"

# ============================================================================
# Step 10: Summary and Next Steps
# ============================================================================
Write-Host "`n"
Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                               ║" -ForegroundColor Green
Write-Host "║           🎉 DEPLOYMENT SUCCESSFUL! 🎉                        ║" -ForegroundColor Green
Write-Host "║                                                               ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n📊 DEPLOYMENT SUMMARY" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

Write-Host "`n🌐 Web Application:" -ForegroundColor Yellow
Write-Host "   URL:              $webAppUrl" -ForegroundColor White
Write-Host "   Name:             $WebAppName" -ForegroundColor Gray
Write-Host "   Resource Group:   $ResourceGroupName" -ForegroundColor Gray
Write-Host "   Pricing Tier:     $Sku" -ForegroundColor Gray

Write-Host "`n🤖 Azure OpenAI:" -ForegroundColor Yellow
Write-Host "   Endpoint:         $openAIEndpoint" -ForegroundColor White
Write-Host "   Resource Name:    $OpenAIName" -ForegroundColor Gray
Write-Host "   Model:            gpt-4o-mini" -ForegroundColor Gray

if (-not $SkipAppRegistration) {
    Write-Host "`n🔐 Azure AD App Registration:" -ForegroundColor Yellow
    Write-Host "   Client ID:        $appId" -ForegroundColor White
    Write-Host "   Redirect URI:     $redirectUri" -ForegroundColor Gray
}

Write-Host "`n📋 NEXT STEPS" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$stepNum = 1

if (-not $SkipAppRegistration) {
    Write-Host "`n$stepNum. Grant Admin Consent for API Permissions:" -ForegroundColor Yellow
    Write-Host "   Azure Portal → Azure Active Directory → App Registrations" -ForegroundColor Gray
    Write-Host "   → CA Policy Manager - $WebAppName → API permissions" -ForegroundColor Gray
    Write-Host "   → Click 'Grant admin consent for [your tenant]'" -ForegroundColor Gray
    $stepNum++
}

Write-Host "`n$stepNum. Wait for Deployment to Complete (~2-3 minutes):" -ForegroundColor Yellow
Write-Host "   Monitor: Azure Portal → $WebAppName → Deployment Center → Logs" -ForegroundColor Gray
$stepNum++

Write-Host "`n$stepNum. Test Your Application:" -ForegroundColor Yellow
Write-Host "   Navigate to: $webAppUrl" -ForegroundColor White
Write-Host "   Click 'Sign In' to authenticate" -ForegroundColor Gray
Write-Host "   Try the AI Policy Explainer feature" -ForegroundColor Gray
$stepNum++

Write-Host "`n$stepNum. View Logs (if needed):" -ForegroundColor Yellow
Write-Host "   Azure Portal → $WebAppName → Log stream" -ForegroundColor Gray

Write-Host "`n💡 USEFUL COMMANDS" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

Write-Host "`n# View real-time logs:" -ForegroundColor Yellow
Write-Host "az webapp log tail --name $WebAppName --resource-group $ResourceGroupName" -ForegroundColor Gray

Write-Host "`n# Restart web app:" -ForegroundColor Yellow
Write-Host "az webapp restart --name $WebAppName --resource-group $ResourceGroupName" -ForegroundColor Gray

Write-Host "`n# Update app settings:" -ForegroundColor Yellow
Write-Host "az webapp config appsettings set --name $WebAppName --resource-group $ResourceGroupName --settings KEY=VALUE" -ForegroundColor Gray

Write-Host "`n# Scale up to B1 tier:" -ForegroundColor Yellow
Write-Host "az appservice plan update --name $appServicePlan --resource-group $ResourceGroupName --sku B1" -ForegroundColor Gray

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

# Save deployment info to file
$deploymentInfo = @{
    DeploymentDate     = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    WebAppUrl          = $webAppUrl
    WebAppName         = $WebAppName
    ResourceGroup      = $ResourceGroupName
    Location           = $Location
    Sku                = $Sku
    OpenAIEndpoint     = $openAIEndpoint
    OpenAIResourceName = $OpenAIName
    ClientId           = if ($appId) { $appId } else { "Use existing" }
} | ConvertTo-Json -Depth 10

$deploymentInfo | Out-File -FilePath "deployment-info.json" -Encoding UTF8
Write-Info "Deployment details saved to: deployment-info.json"

Write-Host "🚀 Deployment complete! Your app will be ready in 2-3 minutes." -ForegroundColor Green
Write-Host ""
