# 🚀 1-Click Setup for Forked Repos

**New to this project?** Follow this guide to get running in 5 minutes.

---

## ⚡ Fastest Path (All Platforms)

### Step 1: Fork & Clone

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/ConditionalAccessPolicyManager.git
cd ConditionalAccessPolicyManager
```

### Step 2: Run Setup Script

**Windows (PowerShell)**:

```powershell
.\setup-local.ps1
```

**Linux/macOS (Bash)**:

```bash
chmod +x setup-local.sh
./setup-local.sh
```

**What it does** (automated):

- ✅ Detects Python 3.11+
- ✅ Creates virtual environment
- ✅ Installs all 15 dependencies
- ✅ Generates secure SECRET_KEY
- ✅ Creates .env configuration file

**Time**: 2-3 minutes

### Step 3: Add Azure Credentials

Edit the `.env` file created in `CA_Policy_Manager_Web/`:

```bash
# Required - Get from Azure App Registration
MSAL_CLIENT_ID=your_client_id_here
MSAL_CLIENT_SECRET=your_secret_here
```

**Don't have Azure credentials?** See: [Azure Setup Guide](#azure-setup) (5 minutes)

### Step 4: Start the App

```powershell
# Windows
cd CA_Policy_Manager_Web
python app.py

# Linux/macOS
cd CA_Policy_Manager_Web
python app.py
```

### Step 5: Open Browser

Navigate to: **http://localhost:5000**

---

## 🔐 Azure Setup

### Option A: Automated (Recommended)

```powershell
cd scripts
.\Register-EntraApp-Delegated.ps1
```

The script automatically:

- Creates App Registration
- Configures API permissions
- Generates client secret
- Updates your .env file

### Option B: Manual (5 minutes)

1. **Azure Portal** → App Registrations → New registration
2. **Name**: "CA Policy Manager (Local)"
3. **Redirect URI**: `http://localhost:5000/auth/callback`
4. **API Permissions** → Add:
   - `Policy.Read.All`
   - `Policy.ReadWrite.ConditionalAccess`
5. **Certificates & secrets** → New client secret
6. Copy **Client ID** and **Secret** to `.env`

**Detailed instructions**: [docs/QUICK_SETUP.md](docs/QUICK_SETUP.md)

---

## 📋 Dependencies (Auto-Installed)

The setup script installs:

- Flask 3.0.0 (web framework)
- MSAL 1.25.0 (Azure authentication)
- Redis 5.0.0 (session storage)
- flask-wtf 1.2.1 (CSRF protection)
- - 11 more packages

**No manual installation needed** - the script handles everything!

---

## ✅ Verify Setup

Run validation script:

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

---

## 🐛 Common Issues

### Python Not Found

**Windows**:

1. Download from https://www.python.org/downloads/
2. During install: ✅ Check "Add Python to PATH"
3. Restart terminal
4. Re-run `.\setup-local.ps1`

**Linux/Ubuntu**:

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv
```

**macOS**:

```bash
brew install python@3.11
```

### Setup Script Fails

```powershell
# Clean start
Remove-Item .venv -Recurse -Force    # Windows
rm -rf .venv                          # Linux/macOS

# Try again
.\setup-local.ps1                    # Windows
./setup-local.sh                     # Linux/macOS
```

### Port 5000 Already in Use

```powershell
# Use different port
$env:PORT="5001"
python app.py
```

### More Help

See comprehensive troubleshooting: [LOCAL_TESTING_GUIDE.md](LOCAL_TESTING_GUIDE.md)

---

## 📁 What Gets Created

After running setup:

```
ConditionalAccessPolicyManager/
├── .venv/                    ← Virtual environment (Python packages)
├── CA_Policy_Manager_Web/
│   ├── .env                  ← YOUR configuration (gitignored)
│   └── ...
└── ...
```

**Note**: `.env` is automatically added to `.gitignore` - your credentials stay private!

---

## 🚀 Next Steps

### Daily Development

```powershell
cd CA_Policy_Manager_Web
python app.py
# No need to run setup again!
```

### Deploy to Azure

```powershell
# See deployment guide
cat docs/DEPLOY_TO_AZURE_BUTTON.md
```

### Customize for Your Org

```powershell
# Edit CA policy templates
cat data/ca_policies_backup.json
```

---

## 📚 Documentation

| Guide                          | Purpose                     | Time   |
| ------------------------------ | --------------------------- | ------ |
| **SETUP_FOR_FORKS.md**         | This file - getting started | 5 min  |
| **QUICK_START.md**             | Detailed quick start        | 10 min |
| **LOCAL_TESTING_GUIDE.md**     | Testing & verification      | 20 min |
| **docs/QUICK_SETUP.md**        | Azure AD setup              | 15 min |
| **SECURITY_FIXES_COMPLETE.md** | Security overview           | 5 min  |

---

## ✨ Features

This tool helps you:

- ✅ Manage Conditional Access policies via GUI
- ✅ Generate policies from templates
- ✅ Analyze Zero Trust security posture
- ✅ Export/import policy configurations
- ✅ AI-assisted policy recommendations (optional)

**Security-first design**:

- ✅ No hardcoded credentials
- ✅ CSRF protection enabled
- ✅ Secure session management
- ✅ All 7 critical security fixes applied

---

## 🤝 Contributing

Before submitting PR:

```powershell
# Validate security
.\validate-security-fixes.ps1

# Should show: ✅ All 7/7 security fixes verified!
```

See: [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📞 Support

- **Security issues**: See [SECURITY.md](SECURITY.md)
- **Bug reports**: Open GitHub issue
- **Questions**: Check [discussions](https://github.com/AntonWilloughby/ConditionalAccessPolicyManager/discussions)

---

## ⚖️ License

See [LICENSE](LICENSE)

---

**Ready to start?** Run `.\setup-local.ps1` and you'll be up in 5 minutes! 🎉
