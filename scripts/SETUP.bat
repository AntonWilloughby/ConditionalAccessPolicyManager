@echo off
REM CA Policy Manager - Windows Setup (Double-click to run)
REM This batch file runs the PowerShell setup script

echo.
echo ================================================
echo   CA Policy Manager - Automated Setup
echo ================================================
echo.
echo This will set up the application for local use.
echo.
echo What will happen:
echo   1. Check Python installation
echo   2. Create virtual environment
echo   3. Install dependencies
echo   4. Create .env configuration
echo.
pause

echo.
echo Running PowerShell setup script...
echo.

powershell.exe -ExecutionPolicy Bypass -File "%~dp0setup-local.ps1"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================
    echo   Setup Complete!
    echo ================================================
    echo.
    echo Next steps:
    echo   1. Edit CA_Policy_Manager_Web\.env with Azure credentials
    echo   2. Run START_APP.bat to launch the application
    echo.
) else (
    echo.
    echo ================================================
    echo   Setup Failed
    echo ================================================
    echo.
    echo Please check the error messages above.
    echo You may need to:
    echo   1. Install Python 3.11+ from python.org
    echo   2. Run as Administrator
    echo   3. Check internet connection for pip packages
    echo.
)

pause
