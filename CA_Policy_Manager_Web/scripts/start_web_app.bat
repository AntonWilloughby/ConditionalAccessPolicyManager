@echo off
echo ================================================================================
echo  CA Policy Manager - Web Application
echo ================================================================================
echo.
echo Starting web server...
echo.
echo Access the application at:
echo   - On this machine: http://localhost:5000
echo   - On your network:  http://192.168.1.242:5000 (or your IP address)
echo.
echo Share the network URL with colleagues so they can access via browser!
echo.
echo Press Ctrl+C to stop the server
echo ================================================================================
echo.

cd /d "%~dp0"
"C:\MyProjects\AV Policy\.venv\Scripts\python.exe" app.py

pause
