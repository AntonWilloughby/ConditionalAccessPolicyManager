# ✅ First-Time Setup Checklist

Use this checklist when setting up the CA Policy Manager for the first time.

---

## 📋 Pre-Setup

- [ ] **Python 3.11 or higher** installed

  - Windows: Download from https://python.org/downloads/
  - Linux/Ubuntu: `sudo apt install python3.11 python3.11-venv`
  - macOS: `brew install python@3.11`
  - Verify: `python --version` shows 3.11+

- [ ] **Git** installed (for cloning)

  - Verify: `git --version`

- [ ] **Azure AD access** to create App Registration
  - Role needed: Application Administrator (or Global Admin)
  - Or ask admin to create app registration for you

---

## 🚀 Automated Setup (Recommended)

### Windows Users

- [ ] **Option 1: Double-click method** (Easiest)

  - [ ] Double-click `SETUP.bat`
  - [ ] Wait for completion (2-3 minutes)
  - [ ] Edit `.env` file when prompted
  - [ ] Double-click `START_APP.bat` to launch

- [ ] **Option 2: PowerShell method**
  ```powershell
  .\setup-local.ps1
  notepad CA_Policy_Manager_Web\.env
  cd CA_Policy_Manager_Web
  python app.py
  ```

### Linux/macOS Users

- [ ] Make script executable

  ```bash
  chmod +x setup-local.sh
  ```

- [ ] Run setup

  ```bash
  ./setup-local.sh
  ```

- [ ] Edit configuration

  ```bash
  nano CA_Policy_Manager_Web/.env
  # or: vim CA_Policy_Manager_Web/.env
  ```

- [ ] Start app
  ```bash
  cd CA_Policy_Manager_Web
  python app.py
  ```

---

## 🔐 Azure App Registration Setup

Choose one method:

### Method A: Automated Script (Fastest)

- [ ] Run registration script

  ```powershell
  cd scripts
  .\Register-EntraApp-Delegated.ps1
  ```

- [ ] Script automatically updates your `.env` file
- [ ] Verify by opening `CA_Policy_Manager_Web\.env`

### Method B: Manual Setup (5 minutes)

- [ ] **Go to Azure Portal**

  - Navigate to https://portal.azure.com
  - Go to **Azure Active Directory** → **App registrations**

- [ ] **Create App Registration**

  - Click **New registration**
  - Name: `CA Policy Manager - Local Dev`
  - Supported account types: **Single tenant**
  - Redirect URI (Web): `http://localhost:5000/auth/callback`
  - Click **Register**

- [ ] **Copy Application (client) ID**

  - From **Overview** page
  - Paste into `MSAL_CLIENT_ID` in `.env`

- [ ] **Create Client Secret**

  - Go to **Certificates & secrets**
  - Click **New client secret**
  - Description: `Local Development Secret`
  - Expires: Choose duration (e.g., 6 months)
  - Click **Add**
  - **IMPORTANT**: Copy the secret **VALUE** immediately (shows only once!)
  - Paste into `MSAL_CLIENT_SECRET` in `.env`

- [ ] **Configure API Permissions**

  - Go to **API permissions**
  - Click **Add a permission**
  - Choose **Microsoft Graph**
  - Choose **Delegated permissions**
  - Search and add:
    - [ ] `Policy.Read.All`
    - [ ] `Policy.ReadWrite.ConditionalAccess`
    - [ ] `Directory.Read.All`
  - Click **Add permissions**
  - Click **Grant admin consent** (requires admin)

- [ ] **Verify Redirect URI**
  - Go to **Authentication**
  - Confirm: `http://localhost:5000/auth/callback` is listed
  - Platform type: **Web**

---

## ⚙️ Configuration

- [ ] **Edit .env file**

  ```bash
  # Location: CA_Policy_Manager_Web/.env

  # Required - From Azure App Registration
  MSAL_CLIENT_ID=<paste_client_id_here>
  MSAL_CLIENT_SECRET=<paste_secret_here>

  # Auto-generated (already set by setup script)
  SECRET_KEY=<already_set_by_script>

  # Optional - Development settings
  FLASK_ENV=development
  VERIFY_SSL=true
  ```

- [ ] **Verify configuration**

  ```powershell
  # Check .env has valid values
  Get-Content CA_Policy_Manager_Web\.env | Select-String "MSAL"

  # Should NOT see:
  # ❌ MSAL_CLIENT_ID=your_app_id_here

  # Should see:
  # ✅ MSAL_CLIENT_ID=12345678-abcd-1234-abcd-123456789abc
  ```

---

## 🧪 Verification

- [ ] **Run security validation**

  ```powershell
  .\validate-security-fixes.ps1
  ```

  Expected output:

  ```
  ✅ Test 1: No hardcoded credentials
  ✅ Test 2: Debug mode controlled
  ✅ Test 3: SSL verification defaults
  ✅ Test 4: Session manager exists
  ✅ Test 5: Error handling sanitized
  ✅ Test 6: CSRF protection enabled
  ✅ Test 7: Security headers configured

  Result: ✅ All 7/7 security fixes verified!
  ```

- [ ] **Start the application**

  ```powershell
  cd CA_Policy_Manager_Web
  python app.py
  ```

- [ ] **Verify app starts**

  - Should see: `Running on http://127.0.0.1:5000`
  - Should see: `⚠️ Running in DEVELOPMENT mode`
  - Should NOT see errors

- [ ] **Test in browser**

  - [ ] Open: http://localhost:5000
  - [ ] Page loads successfully
  - [ ] Click "Connect to Microsoft Graph"
  - [ ] Redirects to Microsoft login
  - [ ] After login, returns to dashboard
  - [ ] Can see tenant information

- [ ] **Test basic functionality**
  - [ ] Click "View Policies" - Should load existing policies
  - [ ] Click "Create Policy" - Should show policy templates
  - [ ] Check console - No errors

---

## 📁 Verify File Structure

After setup, you should have:

```
ConditionalAccessPolicyManager/
├── .venv/                           ✅ Virtual environment
│   ├── Scripts/                     ✅ Windows
│   └── bin/                         ✅ Linux/macOS
├── CA_Policy_Manager_Web/
│   ├── .env                         ✅ YOUR credentials
│   ├── .env.example                 ✅ Template
│   ├── app.py                       ✅ Main app
│   ├── requirements.txt             ✅ Dependencies
│   └── ...
├── setup-local.ps1                  ✅ Windows setup script
├── setup-local.sh                   ✅ Linux/macOS setup script
├── SETUP.bat                        ✅ Windows double-click setup
├── START_APP.bat                    ✅ Windows double-click start
└── validate-security-fixes.ps1      ✅ Security validation
```

---

## 🐛 Common Issues & Solutions

### Issue: Python not found

- [ ] **Solution**: Install from https://python.org/downloads/
- [ ] Check "Add Python to PATH" during installation
- [ ] Restart terminal/PowerShell
- [ ] Verify: `python --version`

### Issue: pip install fails

- [ ] **Solution**: Upgrade pip first
  ```powershell
  python -m pip install --upgrade pip
  cd CA_Policy_Manager_Web
  pip install -r requirements.txt
  ```

### Issue: Virtual environment activation fails

- [ ] **Windows**: May need to enable scripts
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- [ ] **Linux/macOS**: Use `source .venv/bin/activate`

### Issue: Port 5000 already in use

- [ ] **Solution**: Use different port
  ```powershell
  $env:PORT="5001"
  python app.py
  ```

### Issue: Authentication fails in browser

- [ ] Check redirect URI is exactly: `http://localhost:5000/auth/callback`
- [ ] Check Client ID and Secret are correct in `.env`
- [ ] Check API permissions granted in Azure Portal
- [ ] Try incognito/private browser window

### Issue: "No module named 'flask'"

- [ ] Virtual environment not activated
- [ ] **Solution**: Re-run setup script or manually activate:

  ```powershell
  # Windows
  .\.venv\Scripts\Activate.ps1

  # Linux/macOS
  source .venv/bin/activate
  ```

---

## ✅ Success Criteria

You're ready to use the app when ALL these are true:

- [ ] ✅ Setup script completed without errors
- [ ] ✅ `.env` file exists with real Azure credentials
- [ ] ✅ Security validation shows 7/7 tests passing
- [ ] ✅ App starts and shows development mode warning
- [ ] ✅ Browser shows dashboard at localhost:5000
- [ ] ✅ Can log in with Microsoft account
- [ ] ✅ Can view existing Conditional Access policies
- [ ] ✅ No errors in terminal or browser console

---

## 📚 Next Steps

Once setup is complete:

1. **Read the docs**

   - [ ] [LOCAL_TESTING_GUIDE.md](LOCAL_TESTING_GUIDE.md) - Testing guide
   - [ ] [CA_POLICY_FRAMEWORK.md](docs/CA_POLICY_FRAMEWORK.md) - Policy creation guide
   - [ ] [SECURITY_FIXES_COMPLETE.md](SECURITY_FIXES_COMPLETE.md) - Security overview

2. **Explore features**

   - [ ] View existing policies
   - [ ] Create policy from template
   - [ ] Export policies to JSON
   - [ ] Try AI policy explanation (if Azure OpenAI configured)

3. **Customize**

   - [ ] Edit policy templates in `ca_policy_examples.py`
   - [ ] Adjust UI in `templates/` and `static/`
   - [ ] Configure additional settings in `config.py`

4. **Deploy to Azure** (optional)
   - [ ] See [DEPLOY_TO_AZURE_BUTTON.md](docs/DEPLOY_TO_AZURE_BUTTON.md)
   - [ ] Or use [DEPLOYMENT.md](docs/DEPLOYMENT.md) for manual deployment

---

## 🆘 Getting Help

If you're stuck:

1. **Check troubleshooting docs**

   - [LOCAL_TESTING_GUIDE.md](LOCAL_TESTING_GUIDE.md) has detailed solutions

2. **Run diagnostics**

   ```powershell
   # Check Python
   python --version

   # Check virtual environment
   Get-Command python | Select-Object Source

   # Check packages
   pip list

   # Check environment variables
   Get-Content CA_Policy_Manager_Web\.env
   ```

3. **Review logs**

   - Terminal output from `python app.py`
   - Browser console (F12 → Console tab)

4. **Clean reinstall**

   ```powershell
   # Remove virtual environment
   Remove-Item .venv -Recurse -Force

   # Remove config
   Remove-Item CA_Policy_Manager_Web\.env

   # Re-run setup
   .\setup-local.ps1
   ```

5. **Open GitHub issue**
   - Include Python version
   - Include error messages
   - Include steps to reproduce

---

## 🎉 Ready to Go!

If all checkboxes are ticked, you're ready to manage Conditional Access policies! 🚀

**Daily usage**: Just run `START_APP.bat` (Windows) or `python app.py` (all platforms)

---

**Made with ❤️ for IT Admins managing Conditional Access**
