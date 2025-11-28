# 🧪 Local Testing Guide for CA Policy Manager

**Created**: November 22, 2025  
**Status**: Setup & Testing Instructions

---

## ⚠️ Current Environment Status

Your system appears to be missing Python in the PATH. Here's how to fix and test locally:

---

## 📋 Prerequisites

### 1. **Install Python 3.11+**

**Windows**:

```powershell
# Option A: Microsoft Store (Recommended)
# Go to: https://apps.microsoft.com/detail/9NRWMJP3717K
# Click "Get"

# Option B: Direct Download
# Go to: https://www.python.org/downloads/
# Download Python 3.11+ installer
# ✅ Check: "Add Python to PATH" during installation

# Verify Installation
python --version  # Should show Python 3.11+
pip --version     # Should show pip version
```

### 2. **Navigate to Project**

```powershell
cd c:\Github\CA Policy Manager Tool\CA_Policy_Manager_Web
```

---

## 🚀 Setup & Run Locally

### Step 1: Create Python Virtual Environment

```powershell
# Navigate to project root
cd c:\Github\CA Policy Manager Tool

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# You should see (.venv) in your prompt
```

### Step 2: Install Dependencies

```powershell
# Make sure you're in the project root with .venv activated
pip install --upgrade pip setuptools wheel

# Install all requirements
cd CA_Policy_Manager_Web
pip install -r requirements.txt

# Verify installations
pip list | Select-String "flask\|msal\|redis"
```

### Step 3: Create .env Configuration File

```powershell
# Copy template
Copy-Item .env.example .env

# Edit .env with your test credentials
# Use your favorite editor (VS Code, Notepad, etc.)
notepad .env

# Required values to add (get from Azure Portal):
# MSAL_CLIENT_ID=your_test_app_registration_id
# MSAL_CLIENT_SECRET=your_test_secret
# SECRET_KEY=your_secret_key_here

# Generate a SECRET_KEY:
python -c "import secrets; print(secrets.token_hex(32))"
# Copy the output to .env as SECRET_KEY value
```

### Step 4: Run the Flask App

```powershell
# Set development environment
$env:FLASK_ENV="development"
$env:VERIFY_SSL="true"

# Run the application
python app.py

# You should see:
# ⚠️  Running in DEVELOPMENT mode - do not use in production!
# * Running on http://127.0.0.1:5000
# * Press CTRL+C to quit
```

### Step 5: Test in Browser

```
http://localhost:5000

# You should see:
✅ Conditional Access Policy Manager dashboard
✅ "Not Connected" status badge
✅ No errors in console
```

---

## ✅ What to Verify During Testing

### 1. **Startup Verification**

- [ ] App starts without errors
- [ ] Shows message: "Running in DEVELOPMENT mode"
- [ ] Shows: "Running on http://127.0.0.1:5000"
- [ ] No error about missing environment variables

### 2. **Configuration Verification**

```python
# In Python console (while app is running, open another terminal)
# With .venv activated, run:

python -c "from config import get_config; c = get_config(); print(f'Config: {c.__name__}')"
# Should output: Config: DevelopmentConfig

python -c "from app import app; print(f'Debug: {app.debug}')"
# Should output: Debug: True (in development)
```

### 3. **Security Features Verification**

**Check Security Headers**:

```powershell
# While app is running, in new terminal:
Invoke-WebRequest http://localhost:5000 -Method HEAD | Select-Object -ExpandProperty Headers

# Look for:
✓ X-Content-Type-Options: nosniff
✓ X-Frame-Options: SAMEORIGIN
✓ Strict-Transport-Security: max-age=31536000
✓ Content-Security-Policy: default-src 'self';
```

**Check CSRF Protection**:

```python
# In browser console, check:
# 1. View page source
# 2. Search for "csrf_token"
# 3. Should be present in any forms
```

**Check Error Handling**:

```python
# Test endpoint that doesn't exist:
# http://localhost:5000/api/fake-endpoint

# Should return:
# {"success": false, "error": "Operation failed...", "error_type": "..."}
# Should NOT show stack trace
```

### 4. **Session Storage Verification**

```python
# With app running, open Python shell:
python

# Try:
from session_manager import SessionManager
sm = SessionManager()
print(f"Using Redis: {sm.use_redis}")
print(f"Using in-memory: {not sm.use_redis}")

# In development: Should show "Using in-memory: True"
# (unless REDIS_URL is set)
```

### 5. **Logging Verification**

```
# While app is running, check terminal output:
# Should show logs like:
2025-11-22 14:30:45,123 - flask.app - INFO - * Running on http://127.0.0.1:5000
```

---

## 🧪 Testing Scenarios

### Scenario 1: Missing Environment Variables

```powershell
# Delete .env file temporarily
Remove-Item .env

# Try to run app
python app.py

# Expected: ❌ Error message about missing MSAL_CLIENT_ID
# ✅ App fails gracefully with clear error
```

### Scenario 2: Debug Mode Control

```powershell
# Test production mode (no debug)
$env:FLASK_ENV="production"
python app.py
# Should show: ✅ Running on http://127.0.0.1:5000 (no debug warning)
# Press CTRL+C to stop

# Test development mode (debug enabled)
$env:FLASK_ENV="development"
python app.py
# Should show: ✅ Running in DEVELOPMENT mode - do not use in production!
```

### Scenario 3: SSL Verification

```powershell
# Default (secure)
python app.py
# Should use VERIFY_SSL=true

# Explicitly disable (development only)
$env:VERIFY_SSL="false"
python app.py
# Should show: ⚠️ WARNING: SSL verification disabled
```

### Scenario 4: API Error Handling

```powershell
# While app is running, test error response:
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -ErrorAction SilentlyContinue
$response.Content

# Should return JSON, not HTML error page
```

---

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'flask'"

```powershell
# Solution: Missing dependencies
pip install -r requirements.txt
```

### Problem: "The system cannot find the path specified"

```powershell
# Solution: Virtual environment issue
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r CA_Policy_Manager_Web\requirements.txt
```

### Problem: "MSAL_CLIENT_ID environment variable is required"

```powershell
# Solution: .env file missing or incomplete
# 1. Make sure .env exists
# 2. Add required values:
#    MSAL_CLIENT_ID=test_value
#    MSAL_CLIENT_SECRET=test_value
#    SECRET_KEY=test_value
```

### Problem: Port 5000 already in use

```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process (get PID from output above)
taskkill /PID <PID> /F

# Or use different port:
$env:PORT="5001"
python app.py
```

### Problem: SSL Certificate verification fails

```powershell
# Only in development:
$env:VERIFY_SSL="false"
python app.py

# In production: Always use VERIFY_SSL=true
```

---

## 📊 Testing Checklist

### Basic Functionality

- [ ] App starts successfully
- [ ] Home page loads at http://localhost:5000
- [ ] No Python errors in terminal
- [ ] No browser console errors

### Security Features

- [ ] Security headers present (checked with curl/browser)
- [ ] CSRF tokens in forms
- [ ] Error messages safe (no stack traces)
- [ ] Debug mode disabled by default

### Configuration

- [ ] .env file loads credentials correctly
- [ ] App fails gracefully if .env missing
- [ ] Environment variables override defaults
- [ ] Log output shows development mode

### Session Management

- [ ] Session manager initializes
- [ ] In-memory fallback works (no Redis needed)
- [ ] Session data persists across requests

---

## 🔄 Development Workflow

### Daily Development

```powershell
# Start of day
cd c:\Github\CA Policy Manager Tool
.\.venv\Scripts\Activate.ps1

cd CA_Policy_Manager_Web
python app.py

# Access at: http://localhost:5000
# Edit files in VS Code while running
# Flask auto-reloads on file changes
```

### Making Changes

```powershell
# 1. Edit file (e.g., app.py)
# 2. Save file
# 3. Flask automatically reloads
# 4. Refresh browser to see changes
# 5. Check terminal for any errors
```

### Stopping the App

```powershell
# Press CTRL+C in terminal where app is running

# Or in separate terminal:
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

---

## 📝 Create Test .env File

Save this as `.env` in `CA_Policy_Manager_Web/`:

```dotenv
# Flask
FLASK_ENV=development
SECRET_KEY=your_generated_secret_key_here_64_char_hex
PORT=5000

# Azure AD (use test app registration)
MSAL_CLIENT_ID=bcb41e64-e9a8-421c-9331-699dd9041d58
MSAL_CLIENT_SECRET=test_secret_for_local_testing
MSAL_AUTHORITY=https://login.microsoftonline.com/organizations

# File Upload
UPLOAD_FOLDER=data/uploads

# SSL (use true in development)
VERIFY_SSL=true

# AI (disabled for local testing)
AI_ENABLED=false
```

---

## 📚 Next Steps After Testing

1. **Verify all 7 security fixes are working**

   - [ ] Credentials required
   - [ ] Debug mode controlled
   - [ ] SSL defaults to true
   - [ ] Error messages safe
   - [ ] CSRF protection active
   - [ ] Security headers present

2. **Test error scenarios**

   - [ ] Missing credentials
   - [ ] Invalid requests
   - [ ] File uploads
   - [ ] Session timeouts

3. **Prepare for staging**
   - [ ] Document any issues found
   - [ ] Fix any bugs discovered
   - [ ] Update security checklist

---

## 💻 Getting Help

If you encounter issues:

1. **Check logs**: Terminal output shows detailed errors
2. **Review .env**: Make sure all required variables are set
3. **Check Python**: `python --version` should show 3.11+
4. **Verify dependencies**: `pip list` should show all packages
5. **Test connectivity**: `curl http://localhost:5000` from another terminal

---

**Status**: Ready to test locally  
**Next**: Follow setup steps above to run the app  
**Questions**: Check troubleshooting section or security documentation
