# 🚀 Quick Start - Run Flask App Locally

**Status**: ✅ All security fixes verified and ready to test

---

## 🎯 3-Minute Quick Start

### Step 1: Run Setup Script (1 min)

```powershell
cd c:\Github\CA Policy Manager Tool
.\setup-local.ps1
```

**What it does**:

- ✅ Checks Python installation
- ✅ Creates virtual environment
- ✅ Installs dependencies
- ✅ Creates .env file (if missing)

### Step 2: Configure .env (1 min)

```powershell
# Edit the .env file
notepad CA_Policy_Manager_Web\.env

# Required fields to update:
MSAL_CLIENT_ID=your_test_app_id
MSAL_CLIENT_SECRET=your_test_secret
SECRET_KEY=<generate_new>
```

**Generate SECRET_KEY**:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
# Copy output to .env
```

### Step 3: Start App (1 min)

```powershell
cd CA_Policy_Manager_Web
python app.py
```

**Expected output**:

```
⚠️  Running in DEVELOPMENT mode - do not use in production!
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

---

## 🌐 Access the App

Open browser to: **http://localhost:5000**

You should see the Conditional Access Policy Manager dashboard with:

- ✅ "Not Connected" status
- ✅ Connect button
- ✅ No errors

---

## ✅ Verification Checklist

While app is running, verify these security fixes are working:

### 1. ✅ Credentials Required

```powershell
# Try to run without .env
Remove-Item CA_Policy_Manager_Web\.env
cd CA_Policy_Manager_Web
python app.py

# Expected: ❌ Clear error about missing credentials
# ✅ App fails gracefully
```

### 2. ✅ Debug Mode Controlled

```powershell
# Development mode (debug enabled)
$env:FLASK_ENV="development"
python app.py
# Shows: ⚠️  Running in DEVELOPMENT mode

# Production mode (debug disabled)
$env:FLASK_ENV="production"
python app.py
# No debug warning
```

### 3. ✅ SSL Verification

```powershell
# Check SSL is enabled by default
$env:VERIFY_SSL=$null
python app.py
# Uses VERIFY_SSL=true (secure by default)

# Can disable for corporate proxy (dev only)
$env:VERIFY_SSL="false"
python app.py
# Shows: ⚠️ WARNING: SSL verification disabled
```

### 4. ✅ Session Storage

```powershell
# While app running, in new terminal:
cd CA_Policy_Manager_Web
python -c "from session_manager import SessionManager; sm = SessionManager(); print(f'Redis: {sm.use_redis}, In-Memory: {not sm.use_redis}')"

# Output: Redis: False, In-Memory: True (development)
# (Unless REDIS_URL is set)
```

### 5. ✅ Error Handling Safe

```powershell
# Test non-existent endpoint
Invoke-WebRequest http://localhost:5000/api/fake -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Content

# Should return JSON, not HTML stack trace:
# {"success": false, "error": "Operation failed..."}
```

### 6. ✅ CSRF Protection Active

```powershell
# Check CSRF tokens in forms
Invoke-WebRequest http://localhost:5000 | Select-String "csrf_token"

# Should find csrf_token in response
```

### 7. ✅ Security Headers Present

```powershell
# Check security headers
Invoke-WebRequest http://localhost:5000 -Method HEAD | Select-Object -ExpandProperty Headers

# Should have:
# X-Content-Type-Options: nosniff
# X-Frame-Options: SAMEORIGIN
# Strict-Transport-Security: max-age=31536000
```

---

## 🧪 Test All 7 Fixes

Run the validation script:

```powershell
.\validate-security-fixes.ps1

# Expected output:
# ✅ All 7/7 security fixes verified!
```

---

## 🎓 What You're Testing

| #   | Fix                              | How to Test                                 |
| --- | -------------------------------- | ------------------------------------------- |
| 1   | No hardcoded credentials         | App requires .env with MSAL_CLIENT_ID       |
| 2   | Debug mode removed               | FLASK_ENV controls debug, default false     |
| 3   | SSL defaults secure              | VERIFY_SSL=true by default                  |
| 4   | Session storage production-ready | session_manager.py uses Redis or in-memory  |
| 5   | Error responses safe             | API returns generic errors, no stack traces |
| 6   | CSRF protection                  | csrf_token in forms, flask-wtf installed    |
| 7   | Security headers                 | Headers present in all responses            |

---

## 🆘 Troubleshooting

### Problem: "Python not found"

```powershell
# Install Python 3.11+
# Go to: https://www.python.org/downloads/
# Check "Add Python to PATH" during install
# Restart terminal

# Or download from Microsoft Store:
# https://apps.microsoft.com/detail/9NRWMJP3717K
```

### Problem: "pip: command not found"

```powershell
# Reinstall pip
python -m pip install --upgrade pip
```

### Problem: "MSAL_CLIENT_ID environment variable is required"

```powershell
# Make sure .env exists in CA_Policy_Manager_Web/
# And has values set:
# MSAL_CLIENT_ID=your_value
# MSAL_CLIENT_SECRET=your_value
# SECRET_KEY=your_generated_key
```

### Problem: "Port 5000 already in use"

```powershell
# Find and kill process
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or use different port
$env:PORT="5001"
python app.py
# Access at: http://localhost:5001
```

### Problem: "ModuleNotFoundError: No module named 'flask'"

```powershell
# Make sure virtual environment is activated
.\.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📊 Expected Test Results

After running all verifications:

```
✅ All 7 critical security fixes working
✅ App starts without errors
✅ Dashboard loads in browser
✅ .env required (not optional)
✅ Debug mode environment-controlled
✅ SSL verification enabled by default
✅ Session manager ready
✅ Error messages safe
✅ CSRF protection active
✅ Security headers present
```

---

## 📚 Next Steps After Testing

1. **Code Review**: Review changed files

   - See: `CRITICAL_SECURITY_FIXES_SUMMARY.md`

2. **Deploy to Staging**: Follow checklist

   - See: `DEPLOYMENT_SECURITY_CHECKLIST.md`

3. **High-Priority Fixes**: Schedule for next sprint

   - See: `SECURITY_REMEDIATION_DETAILED.md`
   - Rate limiting, OAuth PKCE, token refresh, audit logging

4. **External Security Audit**: Book penetration testing

---

## 💾 File Structure

```
C:\Github\CA Policy Manager Tool\
├── setup-local.ps1              ← Run first
├── validate-security-fixes.ps1  ← Verify fixes
├── LOCAL_TESTING_GUIDE.md       ← Detailed guide
├── CA_Policy_Manager_Web/
│   ├── .env                     ← Create/edit this
│   ├── app.py                   ✅ Hardened
│   ├── config.py                ✅ Hardened
│   ├── requirements.txt          ✅ Updated
│   ├── session_manager.py        ✨ New
│   └── .env.example             ✅ Updated
└── Documentation/
    ├── CRITICAL_SECURITY_FIXES_SUMMARY.md
    ├── DEPLOYMENT_SECURITY_CHECKLIST.md
    └── SECURITY_REMEDIATION_DETAILED.md
```

---

## 🎯 Success Criteria

You'll know it's working when:

- [x] Setup script runs without errors
- [x] App starts with no Python exceptions
- [x] Browser shows dashboard at http://localhost:5000
- [x] All 7 security fixes verified
- [x] Error handling returns safe messages
- [x] Security headers present in responses
- [x] Validation script shows 7/7 passing

---

## 📞 Need Help?

1. **Setup issues**: See `LOCAL_TESTING_GUIDE.md`
2. **Security questions**: See `SECURITY_FIXES_COMPLETE.md`
3. **Deployment help**: See `DEPLOYMENT_SECURITY_CHECKLIST.md`
4. **API questions**: See README.md in CA_Policy_Manager_Web/

---

**Ready to test?**

Run: `.\setup-local.ps1`

Then: `python app.py`

Then: Open http://localhost:5000

✅ **All systems go!**
