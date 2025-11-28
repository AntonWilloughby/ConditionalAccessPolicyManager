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
$ScriptRoot = $PSScriptRoot
$RepoRoot = (Resolve-Path (Join-Path $ScriptRoot '..')).Path
$AppFolderPath = Join-Path $RepoRoot 'CA_Policy_Manager_Web'
$RootRequirementsPath = Join-Path $RepoRoot 'requirements.txt'
$LocalEnvFile = Join-Path $AppFolderPath '.env'

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
    $azVersion = az version --query 'azure-cli' -o tsv 2>$null
    Write-Success "Azure CLI installed (version $azVersion)"
}
catch {
    Write-Error-Custom "Azure CLI not found. Install from: https://aka.ms/installazurecli"
    exit 1
}

# Check if logged in
try {
    $accountJson = az account show 2>&1
    if ($LASTEXITCODE -ne 0 -or $accountJson -match "Please run 'az login'") {
        throw "Not logged in"
    }
    $account = $accountJson | ConvertFrom-Json
    Write-Success "Logged in as: $($account.user.name)"
    Write-Info "Subscription: $($account.name) ($($account.id))"
}
catch {
    Write-Info "Not logged in to Azure. Launching browser..."
    az login | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Azure login failed. Please run 'az login' manually and try again."
        exit 1
    }
    $account = az account show | ConvertFrom-Json
    Write-Success "Logged in as: $($account.user.name)"
    Write-Info "Subscription: $($account.name) ($($account.id))"
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
# Step 1b: Validate Repository Structure
# ============================================================================
Write-Step "Validating repository structure..."

if (-not (Test-Path $AppFolderPath)) {
    Write-Error-Custom "CA_Policy_Manager_Web folder not found at: $AppFolderPath"
    Write-Info "Run this script from the repository root using .\\scripts\\deploy-to-azure.ps1"
    exit 1
}

if (-not (Test-Path $RootRequirementsPath)) {
    Write-Error-Custom "requirements.txt not found at repository root ($RepoRoot)."
    Write-Info "This file is required so Azure installs dependencies automatically."
    exit 1
}

if (Test-Path $LocalEnvFile) {
    Write-Info "Local .env detected in CA_Policy_Manager_Web (will be excluded from deployment package)."
}
else {
    Write-Info "No local .env file detected in CA_Policy_Manager_Web."
}

Write-Success "Repository detected at $RepoRoot"

# ============================================================================
# Step 2: Register Required Resource Providers
# ============================================================================
Write-Step "Registering required Azure Resource Providers..."

$requiredProviders = @(
    'Microsoft.Web',
    'Microsoft.CognitiveServices'
)

foreach ($provider in $requiredProviders) {
    $providerState = az provider show --namespace $provider --query "registrationState" -o tsv 2>$null
    
    if ($providerState -eq 'Registered') {
        Write-Success "$provider is registered"
    }
    elseif ($providerState -eq 'Registering') {
        Write-Info "$provider is currently registering..."
    }
    else {
        Write-Info "Registering $provider (this may take 1-2 minutes)..."
        az provider register --namespace $provider --wait --output none
        Write-Success "$provider registered"
    }
}

# ============================================================================
# Step 3: Create Resource Group
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
# Step 4: Generate Secrets
# ============================================================================
Write-Step "Generating secure secrets..."

$secretKey = python -c "import secrets; print(secrets.token_hex(32))"
Write-Success "Flask SECRET_KEY generated"

# ============================================================================
# Step 5: Deploy Azure OpenAI
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
    $createResult = az cognitiveservices account create `
        --name $OpenAIName `
        --resource-group $ResourceGroupName `
        --location $Location `
        --kind OpenAI `
        --sku S0 `
        --custom-domain $OpenAIName `
        --output none 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Failed to create Azure OpenAI resource."
        Write-Host $createResult -ForegroundColor Red
        exit 1
    }

    Write-Success "Azure OpenAI resource created"
}

# Get OpenAI endpoint and key
$openAIEndpoint = az cognitiveservices account show `
    --name $OpenAIName `
    --resource-group $ResourceGroupName `
    --query properties.endpoint -o tsv

if ($LASTEXITCODE -ne 0 -or -not $openAIEndpoint) {
    Write-Error-Custom "Unable to retrieve Azure OpenAI endpoint."
    exit 1
}

$openAIKey = az cognitiveservices account keys list `
    --name $OpenAIName `
    --resource-group $ResourceGroupName `
    --query key1 -o tsv

if ($LASTEXITCODE -ne 0 -or -not $openAIKey) {
    Write-Error-Custom "Unable to retrieve Azure OpenAI API key."
    exit 1
}

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
    $deployModelResult = az cognitiveservices account deployment create `
        --name $OpenAIName `
        --resource-group $ResourceGroupName `
        --deployment-name gpt-4o-mini `
        --model-name gpt-4o-mini `
        --model-version "2024-07-18" `
        --model-format OpenAI `
        --sku-capacity 30 `
        --sku-name "Standard" `
        --output none 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Failed to deploy GPT-4o-mini model."
        Write-Host $deployModelResult -ForegroundColor Red
        exit 1
    }

    Write-Success "GPT-4o-mini model deployed"
}

# ============================================================================
# Step 6: Create App Service
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
    Write-Info "Creating App Service Plan ($Sku tier)..."
    $planResult = az appservice plan create `
        --name $appServicePlan `
        --resource-group $ResourceGroupName `
        --location $Location `
        --is-linux `
        --sku $Sku `
        2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Failed to create App Service Plan"
        Write-Host "`n$planResult" -ForegroundColor Red
        
        if ($planResult -match "quota") {
            Write-Host "`n⚠️  QUOTA ISSUE DETECTED" -ForegroundColor Yellow
            Write-Host "Your subscription has no quota for $Sku tier App Services." -ForegroundColor Yellow
            Write-Host "`nOptions:" -ForegroundColor Cyan
            Write-Host "  1. Request quota increase:" -ForegroundColor White
            Write-Host "     Azure Portal → Subscriptions → Usage + quotas → Search 'App Service' → Request increase" -ForegroundColor Gray
            Write-Host "`n  2. Try a different SKU (run script again with -Sku parameter):" -ForegroundColor White
            Write-Host "     -Sku B1  (Basic - usually has quota)" -ForegroundColor Gray
            Write-Host "     -Sku S1  (Standard - may have quota)" -ForegroundColor Gray
            Write-Host "`n  3. Use a different Azure region (run script again with -Location parameter):" -ForegroundColor White
            Write-Host "     -Location westus3" -ForegroundColor Gray
            Write-Host "     -Location eastus" -ForegroundColor Gray
        }
        exit 1
    }
    
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
    Write-Info "Creating Web App..."
    $webAppResult = az webapp create `
        --name $WebAppName `
        --resource-group $ResourceGroupName `
        --plan $appServicePlan `
        --runtime "PYTHON:3.12" `
        2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Failed to create Web App"
        Write-Host "`n$webAppResult" -ForegroundColor Red
        exit 1
    }
    
    Write-Success "Web App created"
}

$webAppUrl = "https://$WebAppName.azurewebsites.net"
Write-Info "Web App URL: $webAppUrl"

# ============================================================================
# Step 7: Configure App Service Settings
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
    --startup-file "gunicorn --chdir CA_Policy_Manager_Web --bind=0.0.0.0:8000 --timeout 600 app:app" `
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
# Step 8: Create/Update Azure AD App Registration
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
            --enable-id-token-issuance true `
            --enable-access-token-issuance true | ConvertFrom-Json
        
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
# Step 9: Deploy Application Code
# ============================================================================
Write-Step "Deploying application code..."

# Create deployment package from repo root so requirements.txt is included
$deployZip = Join-Path $RepoRoot "deploy.zip"
$envBackupPath = $null
$envTemporarilyMoved = $false
if (Test-Path $LocalEnvFile) {
    $envBackupPath = Join-Path $RepoRoot (".env.backup." + [Guid]::NewGuid().ToString('N'))
    Write-Info "Temporarily removing CA_Policy_Manager_Web\\.env from deployment (secrets will remain configured via App Service settings)."
    Move-Item -Path $LocalEnvFile -Destination $envBackupPath -Force
    $envTemporarilyMoved = $true
}
Write-Info "Creating deployment package..."

Push-Location $RepoRoot
try {
    if (Test-Path $deployZip) { Remove-Item $deployZip -Force }
    
    Compress-Archive -Path 'requirements.txt', 'CA_Policy_Manager_Web' -DestinationPath $deployZip -Force
    Write-Success "Deployment package created"
}
finally {
    Pop-Location
    if ($envTemporarilyMoved -and (Test-Path $envBackupPath)) {
        Move-Item -Path $envBackupPath -Destination $LocalEnvFile -Force
        Write-Info "Restored local CA_Policy_Manager_Web\\.env file."
    }
}

# Deploy to Azure
Write-Info "Uploading to Azure (this may take 2-3 minutes)..."
Write-Info "Using ZIP deploy method..."

$deployResult = az webapp deploy `
    --name $WebAppName `
    --resource-group $ResourceGroupName `
    --src-path $deployZip `
    --type zip `
    --async true `
    2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Deployment upload failed"
    Write-Host "$deployResult" -ForegroundColor Red
    Remove-Item $deployZip -Force
    exit 1
}

Write-Success "Deployment package uploaded"
Write-Info "Azure is building and deploying your app (this continues in background)"
Write-Info "You can monitor progress: Azure Portal → $WebAppName → Deployment Center → Logs"

Remove-Item $deployZip -Force

# Wait a moment for initial deployment to register
Write-Info "Waiting for deployment to initialize..."
Start-Sleep -Seconds 10

# Restart the web app to ensure clean start
Write-Info "Restarting web app to apply deployment..."
az webapp restart --name $WebAppName --resource-group $ResourceGroupName --output none
Write-Success "Application deployed and restarted"

# ============================================================================
# Step 10: Enable Logging
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
# Step 11: Summary and Next Steps
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
    Write-Host "`n$stepNum. Grant Admin Consent for API Permissions (REQUIRED):" -ForegroundColor Yellow
    Write-Host "   The script created an App Registration called 'CA Policy Manager - $WebAppName'" -ForegroundColor Cyan
    Write-Host "   You need to grant admin consent for it to access Microsoft Graph API." -ForegroundColor Cyan
    Write-Host "" 
    Write-Host "   Steps:" -ForegroundColor Gray
    Write-Host "   1. Azure Portal → Azure Active Directory → App Registrations" -ForegroundColor Gray
    Write-Host "   2. Click 'All applications' tab" -ForegroundColor Gray
    Write-Host "   3. Find and click: CA Policy Manager - $WebAppName" -ForegroundColor Gray
    Write-Host "   4. Click 'API permissions' in left menu" -ForegroundColor Gray
    Write-Host "   5. Click 'Grant admin consent for [your tenant]' button" -ForegroundColor Gray
    Write-Host "   6. Click 'Yes' to confirm" -ForegroundColor Gray
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
