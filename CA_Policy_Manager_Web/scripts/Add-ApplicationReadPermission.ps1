# Fix Azure AD App Permissions - Add Application.Read.All
# This script adds the missing Application.Read.All permission to your Azure AD app

Write-Host "🔐 Adding Application.Read.All permission to Azure AD app..." -ForegroundColor Cyan
Write-Host ""

# Check if user is logged in to Azure
$azContext = Get-AzContext -ErrorAction SilentlyContinue
if (-not $azContext) {
    Write-Host "⚠️  Not logged in to Azure. Logging in..." -ForegroundColor Yellow
    Connect-AzAccount
}

Write-Host "📋 Current Azure subscription: $($azContext.Subscription.Name)" -ForegroundColor Green
Write-Host ""

# Get app registration details
$appDisplayName = Read-Host "Enter your Azure AD app display name (e.g., 'CA Policy Manager')"

$app = Get-AzADApplication -DisplayName $appDisplayName

if (-not $app) {
    Write-Host "❌ App not found: $appDisplayName" -ForegroundColor Red
    Write-Host "💡 Run this to list your apps:" -ForegroundColor Yellow
    Write-Host "   Get-AzADApplication | Select-Object DisplayName, AppId" -ForegroundColor Gray
    exit 1
}

Write-Host "✅ Found app: $($app.DisplayName)" -ForegroundColor Green
Write-Host "   App ID: $($app.AppId)" -ForegroundColor Gray
Write-Host ""

# Microsoft Graph API Application ID
$graphAppId = "00000003-0000-0000-c000-000000000000"

# Get Microsoft Graph service principal
$graphSP = Get-AzADServicePrincipal -ApplicationId $graphAppId

# Permission IDs we need
$requiredPermissions = @{
    "Policy.Read.All" = "246dd0d5-5bd0-4def-940b-0421030a5b68"
    "Policy.ReadWrite.ConditionalAccess" = "01c0a623-fc9b-48e9-b794-0756f8e8f067"
    "Application.Read.All" = "9a5d68dd-52b0-4cc2-bd40-abcf44ac3a30"  # NEW - Required for app conditions
    "Directory.Read.All" = "7ab1d382-f21e-4acd-a863-ba3e13f7da61"
    "Group.Read.All" = "5b567255-7703-4780-807c-7be8301ae99b"
}

Write-Host "📋 Checking current permissions..." -ForegroundColor Cyan

# Get current permissions
$currentPerms = $app.RequiredResourceAccess | Where-Object { $_.ResourceAppId -eq $graphAppId }

if ($currentPerms) {
    Write-Host "Current Microsoft Graph permissions:" -ForegroundColor Yellow
    foreach ($perm in $currentPerms.ResourceAccess) {
        $permName = $requiredPermissions.Keys | Where-Object { $requiredPermissions[$_] -eq $perm.Id }
        if ($permName) {
            Write-Host "  ✓ $permName" -ForegroundColor Green
        } else {
            Write-Host "  ? $($perm.Id)" -ForegroundColor Gray
        }
    }
}

Write-Host ""
Write-Host "🔧 Adding missing permissions..." -ForegroundColor Cyan

# Build the required resource access
$resourceAccess = @()
foreach ($permName in $requiredPermissions.Keys) {
    $resourceAccess += @{
        Id = $requiredPermissions[$permName]
        Type = "Role"  # Application permissions
    }
}

$graphResource = @{
    ResourceAppId = $graphAppId
    ResourceAccess = $resourceAccess
}

# Update the app registration
try {
    Update-AzADApplication -ObjectId $app.Id -RequiredResourceAccess @($graphResource)
    Write-Host "✅ Permissions updated successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Admin consent is required!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🔗 Grant admin consent using one of these methods:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "METHOD 1 - Azure Portal:" -ForegroundColor White
    Write-Host "  1. Go to: https://portal.azure.com/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/RegisteredApps" -ForegroundColor Gray
    Write-Host "  2. Find your app: $($app.DisplayName)" -ForegroundColor Gray
    Write-Host "  3. Go to 'API permissions'" -ForegroundColor Gray
    Write-Host "  4. Click 'Grant admin consent for [Your Tenant]'" -ForegroundColor Gray
    Write-Host "  5. Click 'Yes' to confirm" -ForegroundColor Gray
    Write-Host ""
    Write-Host "METHOD 2 - Direct URL:" -ForegroundColor White
    Write-Host "  https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/CallAnAPI/appId/$($app.AppId)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "After granting consent, your policies should deploy successfully!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Failed to update permissions: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Try manually adding the permission:" -ForegroundColor Yellow
    Write-Host "  1. Go to Azure Portal > App Registrations > $($app.DisplayName)" -ForegroundColor Gray
    Write-Host "  2. Click 'API permissions' > 'Add a permission'" -ForegroundColor Gray
    Write-Host "  3. Select 'Microsoft Graph' > 'Application permissions'" -ForegroundColor Gray
    Write-Host "  4. Search for and add: 'Application.Read.All'" -ForegroundColor Gray
    Write-Host "  5. Click 'Grant admin consent'" -ForegroundColor Gray
}

Write-Host ""
Write-Host "📝 Required permissions:" -ForegroundColor Cyan
foreach ($permName in $requiredPermissions.Keys) {
    Write-Host "  • $permName" -ForegroundColor White
}
