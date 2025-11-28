@echo off
REM Quick Azure Deployment Launcher for CA Policy Manager
REM ======================================================
REM This batch file launches the PowerShell deployment script with user-friendly prompts

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║       CA Policy Manager - Quick Azure Setup                  ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

echo This wizard will deploy CA Policy Manager to Azure App Service.
echo.
echo You will need:
echo   - Azure subscription (with Owner/Contributor access)
echo   - 3 unique names for resources
echo.

pause

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo   STEP 1: Resource Configuration
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

set /p RG_NAME="Enter Resource Group name (e.g., ca-policy-rg): "
set /p WEBAPP_NAME="Enter Web App name (e.g., my-ca-manager): "
set /p OPENAI_NAME="Enter OpenAI resource name (e.g., my-openai-helper): "

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo   STEP 2: Optional Configuration
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Azure Region options:
echo   1) East US 2 (recommended)
echo   2) West US 3
echo   3) Sweden Central
echo   4) UK South
echo.
set /p REGION_CHOICE="Select region [1-4] (default: 1): "

if "%REGION_CHOICE%"=="2" (
    set LOCATION=westus3
) else if "%REGION_CHOICE%"=="3" (
    set LOCATION=swedencentral
) else if "%REGION_CHOICE%"=="4" (
    set LOCATION=uksouth
) else (
    set LOCATION=eastus2
)

echo.
echo Pricing Tier options:
echo   1) F1 - Free (60 min/day, good for testing)
echo   2) B1 - Basic $13/mo (recommended for production)
echo   3) S1 - Standard $70/mo (auto-scaling)
echo.
set /p SKU_CHOICE="Select pricing tier [1-3] (default: 1): "

if "%SKU_CHOICE%"=="2" (
    set SKU=B1
) else if "%SKU_CHOICE%"=="3" (
    set SKU=S1
) else (
    set SKU=F1
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo   DEPLOYMENT SUMMARY
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo   Resource Group:    %RG_NAME%
echo   Web App Name:      %WEBAPP_NAME%
echo   OpenAI Resource:   %OPENAI_NAME%
echo   Azure Region:      %LOCATION%
echo   Pricing Tier:      %SKU%
echo.
echo   Your app will be: https://%WEBAPP_NAME%.azurewebsites.net
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

set /p CONFIRM="Ready to deploy? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo Deployment cancelled.
    pause
    exit /b
)

echo.
echo Starting deployment...
echo This will take approximately 10-15 minutes.
echo.

REM Run PowerShell deployment script
powershell.exe -ExecutionPolicy Bypass -File "%~dp0deploy-to-azure.ps1" ^
    -ResourceGroupName "%RG_NAME%" ^
    -WebAppName "%WEBAPP_NAME%" ^
    -OpenAIName "%OPENAI_NAME%" ^
    -Location "%LOCATION%" ^
    -Sku "%SKU%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ✗ Deployment failed. Check errors above.
    pause
    exit /b 1
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo   DEPLOYMENT COMPLETE!
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Your app is deploying to: https://%WEBAPP_NAME%.azurewebsites.net
echo.
echo Next steps saved in: deployment-info.json
echo.
pause
