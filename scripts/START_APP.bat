@echo off
REM CA Policy Manager - Start Application (Double-click to run)

echo.
echo ================================================
echo   CA Policy Manager - Starting Application
echo ================================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please run SETUP.bat first to set up the application.
    echo.
    pause
    exit /b 1
)

REM Check if .env exists
if not exist "CA_Policy_Manager_Web\.env" (
    echo WARNING: .env file not found!
    echo.
    echo Running setup script to create it...
    call SETUP.bat
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo Setup failed. Please run SETUP.bat manually.
        pause
        exit /b 1
    )
    echo.
    echo Setup complete! Starting app in DEMO MODE...
    echo.
)

echo Starting Flask application...
echo.
echo The app will open in your default browser.
echo Press CTRL+C in this window to stop the server.
echo.
echo ================================================
echo.

REM Start the application
cd CA_Policy_Manager_Web
"%~dp0.venv\Scripts\python.exe" app.py

pause
