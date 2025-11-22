# Register Azure App for Entra ID Sign-In
# This script creates the app registration needed for delegated authentication

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CA Policy Manager - App Registration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Az module is installed
if (-not (Get-Module -ListAvailable -Name Az.Resources)) {
    Write-Host "Installing Azure PowerShell module..." -ForegroundColor Yellow
    Install-Module -Name Az.Resources -Scope CurrentUser -Force -AllowClobber
}

# Import module
Import-Module Az.Resources

# Connect to Azure
Write-Host "Connecting to Azure..." -ForegroundColor Yellow
Connect-AzAccount

# Get tenant info
$context = Get-AzContext
$tenantId = $context.Tenant.Id

Write-Host ""
Write-Host "Connected to Tenant: $tenantId" -ForegroundColor Green
Write-Host ""

# Create app registration
$appName = "CA Policy Manager - Web (Delegated)"
$redirectUri = "http://localhost:5000/auth/callback"

Write-Host "Creating app registration: $appName" -ForegroundColor Yellow

# Create the app
$app = New-AzADApplication -DisplayName $appName `
    -Web `
    -ReplyUrl $redirectUri

$appId = $app.AppId

Write-Host ""
Write-Host "✅ App created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Application (client) ID: $appId" -ForegroundColor Cyan
Write-Host ""

# Add Microsoft Graph API permissions
Write-Host "Adding Microsoft Graph permissions..." -ForegroundColor Yellow

# Get Microsoft Graph service principal
$graphSP = Get-AzADServicePrincipal -ApplicationId "00000003-0000-0000-c000-000000000000"

# Permission IDs for Microsoft Graph (Delegated permissions only)
$permissions = @(
    @{
        Id = "37f7f235-527c-4136-accd-4a02d197296e"  # Policy.Read.All (Delegated)
        Type = "Scope"
    },
    @{
        Id = "ad902697-1014-4ef5-81ef-2b4301988e8c"  # Policy.ReadWrite.ConditionalAccess (Delegated)
        Type = "Scope"
    },
    @{
        Id = "c79f8feb-a9db-4090-85f9-90d820caa0eb"  # Application.Read.All (Delegated)
        Type = "Scope"
    },
    @{
        Id = "06da0dbc-49e2-44d2-8312-53f166ab848a"  # Directory.Read.All (Delegated)
        Type = "Scope"
    },
    @{
        Id = "4e46008b-f24c-477d-8fff-7bb4ec7aafe0"  # Group.ReadWrite.All (Delegated)
        Type = "Scope"
    },
    @{
        Id = "e1fe6dd8-ba31-4d61-89e7-88639da4683d"  # User.Read (Delegated)
        Type = "Scope"
    }
)

# Add permissions
foreach ($permission in $permissions) {
    Add-AzADAppPermission -ObjectId $app.Id -ApiId $graphSP.AppId -PermissionId $permission.Id -Type $permission.Type
}

Write-Host "✅ Permissions added!" -ForegroundColor Green
Write-Host ""

# Grant admin consent
Write-Host "⚠️  IMPORTANT: Admin consent required!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Please complete these manual steps:" -ForegroundColor Yellow
Write-Host "1. Go to: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade" -ForegroundColor White
Write-Host "2. Find app: $appName" -ForegroundColor White
Write-Host "3. Click 'API permissions'" -ForegroundColor White
Write-Host "4. Click 'Grant admin consent for [Organization]'" -ForegroundColor White
Write-Host "5. Click 'Yes'" -ForegroundColor White
Write-Host ""

# Update app.py
Write-Host "Updating app.py with Client ID..." -ForegroundColor Yellow

$appPyPath = "C:\MyProjects\AV Policy\CA_Policy_Manager_Web\app.py"

if (Test-Path $appPyPath) {
    $content = Get-Content $appPyPath -Raw
    $content = $content -replace "MSAL_CLIENT_ID = os.environ.get\('MSAL_CLIENT_ID', 'YOUR_CLIENT_ID'\)", "MSAL_CLIENT_ID = os.environ.get('MSAL_CLIENT_ID', '$appId')"
    Set-Content -Path $appPyPath -Value $content
    
    Write-Host "✅ app.py updated!" -ForegroundColor Green
} else {
    Write-Host "❌ Could not find app.py at: $appPyPath" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Grant admin consent in Azure Portal (see link above)" -ForegroundColor White
Write-Host "2. Restart the web app" -ForegroundColor White
Write-Host "3. Click 'Sign In with Entra ID'" -ForegroundColor White
Write-Host ""
Write-Host "Your Client ID: $appId" -ForegroundColor Cyan
Write-Host ""
