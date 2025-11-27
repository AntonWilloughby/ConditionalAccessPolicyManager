# Deploy to Azure - Validation Checklist
# Run this after clicking "Deploy to Azure" button to verify everything is configured correctly

param(
    [Parameter(Mandatory = $true)]
    [string]$WebAppName,
    
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroup,
    
    [switch]$SkipCodeDeployment
)

Write-Host "`n🔍 Validating Azure Deployment for CA Policy Manager`n" -ForegroundColor Cyan

$issues = @()
$warnings = @()
$success = @()

# Check if logged in to Azure
Write-Host "Checking Azure CLI login..." -NoNewline
try {
    $account = az account show 2>$null | ConvertFrom-Json
    if ($account) {
        Write-Host " ✅" -ForegroundColor Green
        $success += "Azure CLI authenticated as $($account.user.name)"
    }
    else {
        throw "Not logged in"
    }
}
catch {
    Write-Host " ❌" -ForegroundColor Red
    $issues += "Not logged in to Azure CLI. Run: az login"
}

# Check if resource group exists
Write-Host "Checking resource group '$ResourceGroup'..." -NoNewline
try {
    $rg = az group show --name $ResourceGroup 2>$null | ConvertFrom-Json
    if ($rg) {
        Write-Host " ✅" -ForegroundColor Green
        $success += "Resource group exists in $($rg.location)"
    }
    else {
        throw "Not found"
    }
}
catch {
    Write-Host " ❌" -ForegroundColor Red
    $issues += "Resource group '$ResourceGroup' not found"
}

# Check if App Service exists
Write-Host "Checking App Service '$WebAppName'..." -NoNewline
try {
    $app = az webapp show --name $WebAppName --resource-group $ResourceGroup 2>$null | ConvertFrom-Json
    if ($app) {
        Write-Host " ✅" -ForegroundColor Green
        $success += "App Service exists: https://$($app.defaultHostName)"
        $appUrl = "https://$($app.defaultHostName)"
    }
    else {
        throw "Not found"
    }
}
catch {
    Write-Host " ❌" -ForegroundColor Red
    $issues += "App Service '$WebAppName' not found in resource group '$ResourceGroup'"
}

# Check App Service configuration
if ($app) {
    Write-Host "`nValidating App Service Configuration:" -ForegroundColor Yellow
    
    # Get all app settings
    $settings = az webapp config appsettings list --name $WebAppName --resource-group $ResourceGroup 2>$null | ConvertFrom-Json
    $settingsHash = @{}
    $settings | ForEach-Object { $settingsHash[$_.name] = $_.value }
    
    # Check required settings
    $requiredSettings = @(
        @{Name = "SECRET_KEY"; Description = "Flask secret key" },
        @{Name = "AZURE_OPENAI_ENDPOINT"; Description = "OpenAI endpoint URL" },
        @{Name = "AZURE_OPENAI_DEPLOYMENT"; Description = "OpenAI deployment name" },
        @{Name = "AZURE_OPENAI_API_KEY"; Description = "OpenAI API key" },
        @{Name = "SCM_DO_BUILD_DURING_DEPLOYMENT"; Description = "Enable Oryx build" },
        @{Name = "ENABLE_ORYX_BUILD"; Description = "Enable Oryx build" }
    )
    
    foreach ($setting in $requiredSettings) {
        Write-Host "  Checking $($setting.Name)..." -NoNewline
        if ($settingsHash.ContainsKey($setting.Name) -and $settingsHash[$setting.Name]) {
            Write-Host " ✅" -ForegroundColor Green
            $success += "$($setting.Name) is configured"
        }
        else {
            Write-Host " ❌" -ForegroundColor Red
            $issues += "$($setting.Name) is missing ($($setting.Description))"
        }
    }
    
    # Check optional settings (warnings)
    $optionalSettings = @(
        @{Name = "MSAL_CLIENT_ID"; Description = "Azure AD App Registration Client ID (required for auth)" },
        @{Name = "MSAL_TENANT_ID"; Description = "Azure AD Tenant ID" }
    )
    
    foreach ($setting in $optionalSettings) {
        Write-Host "  Checking $($setting.Name)..." -NoNewline
        if ($settingsHash.ContainsKey($setting.Name) -and $settingsHash[$setting.Name] -and $settingsHash[$setting.Name] -ne "") {
            Write-Host " ✅" -ForegroundColor Green
            $success += "$($setting.Name) is configured"
        }
        else {
            Write-Host " ⚠️" -ForegroundColor Yellow
            $warnings += "$($setting.Name) is not configured ($($setting.Description))"
        }
    }
    
    # Check DEMO_MODE
    Write-Host "  Checking DEMO_MODE..." -NoNewline
    if ($settingsHash.ContainsKey("DEMO_MODE")) {
        $demoMode = $settingsHash["DEMO_MODE"]
        if ($demoMode -eq "true") {
            Write-Host " ⚠️ (Enabled)" -ForegroundColor Yellow
            $warnings += "DEMO_MODE is enabled - app will work without authentication but won't manage real policies"
        }
        else {
            Write-Host " ✅ (Disabled)" -ForegroundColor Green
            $success += "DEMO_MODE is disabled (production mode)"
        }
    }
}

# Check if code is deployed
if (-not $SkipCodeDeployment) {
    Write-Host "`nChecking code deployment..." -NoNewline
    try {
        $response = Invoke-WebRequest -Uri $appUrl -Method Get -TimeoutSec 10 -UseBasicParsing 2>$null
        if ($response.Content -match "CA Policy Manager" -or $response.Content -match "Connect") {
            Write-Host " ✅" -ForegroundColor Green
            $success += "Application code is deployed and responding"
        }
        elseif ($response.Content -match "Your App Service app is up and running") {
            Write-Host " ⚠️" -ForegroundColor Yellow
            $warnings += "Default Azure page detected - application code not deployed yet"
        }
        else {
            Write-Host " ⚠️" -ForegroundColor Yellow
            $warnings += "App is responding but content is unexpected"
        }
    }
    catch {
        Write-Host " ❌" -ForegroundColor Red
        $issues += "Unable to connect to $appUrl - Error: $($_.Exception.Message)"
    }
}

# Check OpenAI resource
Write-Host "`nChecking Azure OpenAI resource..." -NoNewline
if ($settingsHash -and $settingsHash.ContainsKey("AZURE_OPENAI_ENDPOINT")) {
    $openAIEndpoint = $settingsHash["AZURE_OPENAI_ENDPOINT"]
    # Extract resource name from endpoint URL
    if ($openAIEndpoint -match "https://([^.]+)\.openai\.azure\.com") {
        $openAIName = $matches[1]
        try {
            $openAI = az cognitiveservices account show --name $openAIName --resource-group $ResourceGroup 2>$null | ConvertFrom-Json
            if ($openAI) {
                Write-Host " ✅" -ForegroundColor Green
                $success += "Azure OpenAI resource '$openAIName' exists"
                
                # Check deployment
                Write-Host "  Checking GPT-4o-mini deployment..." -NoNewline
                $deployments = az cognitiveservices account deployment list --name $openAIName --resource-group $ResourceGroup 2>$null | ConvertFrom-Json
                if ($deployments | Where-Object { $_.properties.model.name -eq "gpt-4o-mini" }) {
                    Write-Host " ✅" -ForegroundColor Green
                    $success += "GPT-4o-mini deployment exists"
                }
                else {
                    Write-Host " ❌" -ForegroundColor Red
                    $issues += "GPT-4o-mini deployment not found in OpenAI resource"
                }
            }
        }
        catch {
            Write-Host " ❌" -ForegroundColor Red
            $issues += "Azure OpenAI resource '$openAIName' not found"
        }
    }
}
else {
    Write-Host " ⚠️ (Skipped - endpoint not configured)" -ForegroundColor Yellow
}

# Check Python runtime
Write-Host "`nChecking Python runtime..." -NoNewline
try {
    $config = az webapp config show --name $WebAppName --resource-group $ResourceGroup 2>$null | ConvertFrom-Json
    if ($config.linuxFxVersion -match "PYTHON\|3\.12") {
        Write-Host " ✅" -ForegroundColor Green
        $success += "Python 3.12 runtime configured"
    }
    else {
        Write-Host " ⚠️ ($($config.linuxFxVersion))" -ForegroundColor Yellow
        $warnings += "Unexpected Python version: $($config.linuxFxVersion)"
    }
}
catch {
    Write-Host " ❌" -ForegroundColor Red
    $issues += "Unable to check Python runtime configuration"
}

# Summary
Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "VALIDATION SUMMARY" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan

if ($success.Count -gt 0) {
    Write-Host "`n✅ SUCCESS ($($success.Count)):" -ForegroundColor Green
    $success | ForEach-Object { Write-Host "  • $_" -ForegroundColor Green }
}

if ($warnings.Count -gt 0) {
    Write-Host "`n⚠️  WARNINGS ($($warnings.Count)):" -ForegroundColor Yellow
    $warnings | ForEach-Object { Write-Host "  • $_" -ForegroundColor Yellow }
}

if ($issues.Count -gt 0) {
    Write-Host "`n❌ ISSUES ($($issues.Count)):" -ForegroundColor Red
    $issues | ForEach-Object { Write-Host "  • $_" -ForegroundColor Red }
}

# Next steps
Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "NEXT STEPS" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan

if ($warnings -match "Default Azure page detected") {
    Write-Host "`n📦 DEPLOY APPLICATION CODE:" -ForegroundColor Yellow
    Write-Host "  Method 1 - GitHub (Recommended):" -ForegroundColor White
    Write-Host "    1. Fork: https://github.com/AntonWilloughby/ConditionalAccessPolicyManager"
    Write-Host "    2. Azure Portal → $WebAppName → Deployment Center"
    Write-Host "    3. Connect your forked repo → Save"
    Write-Host "`n  Method 2 - Azure CLI:" -ForegroundColor White
    Write-Host "    cd CA_Policy_Manager_Web"
    Write-Host "    Compress-Archive -Path * -DestinationPath deploy.zip -Force"
    Write-Host "    az webapp deploy --name $WebAppName --resource-group $ResourceGroup --src-path deploy.zip --type zip --async true"
}

if ($warnings -match "MSAL_CLIENT_ID") {
    Write-Host "`n🔐 CONFIGURE AUTHENTICATION:" -ForegroundColor Yellow
    Write-Host "  Option 1 - Enable Demo Mode (Quick Test):" -ForegroundColor White
    Write-Host "    az webapp config appsettings set --name $WebAppName --resource-group $ResourceGroup --settings DEMO_MODE=true"
    Write-Host "`n  Option 2 - Create App Registration (Production):" -ForegroundColor White
    Write-Host "    See: DEPLOY_BUTTON_COMPLETE_GUIDE.md - Step 3"
    Write-Host "    1. Create App Registration in Azure AD"
    Write-Host "    2. Add API permissions (User.Read, Policy.Read.All, etc.)"
    Write-Host "    3. Update app settings with MSAL_CLIENT_ID"
    Write-Host "    4. Configure redirect URI: $appUrl/auth/callback"
}

Write-Host "`n🌐 APP URL: $appUrl" -ForegroundColor Cyan

if ($issues.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "`n🎉 Deployment looks great! Your app should be fully functional." -ForegroundColor Green
    Write-Host "   Open: $appUrl" -ForegroundColor Green
}
elseif ($issues.Count -eq 0) {
    Write-Host "`n✅ No critical issues found. Review warnings above." -ForegroundColor Yellow
}
else {
    Write-Host "`n⚠️  Please resolve the issues above before using the app." -ForegroundColor Red
}

Write-Host ""
