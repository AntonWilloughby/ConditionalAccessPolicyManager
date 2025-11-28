# Conditional Access Policy Manager

**Modern Flask web application for managing Azure AD Conditional Access policies via Microsoft Graph API.**

## ☁️ Deploy to Azure (Recommended for Production)

### Option 1: Fully Automated (One Command) ⭐

Follow these steps from the repository root (the folder that contains `azuredeploy.json`, `DEPLOY_TO_AZURE.bat`, etc.).

```powershell
# 1) Open a new PowerShell window
# 2) Change directory into the cloned repo (adjust the path if yours is different)
cd C:\Github\CA Policy Manager Tool
```

```powershell
# Windows - Interactive wizard
.\scripts\DEPLOY_TO_AZURE.bat

# OR Windows PowerShell
.\scripts\deploy-to-azure.ps1 -ResourceGroupName "ca-policy-rg" -WebAppName "my-ca-manager" -OpenAIName "my-openai-helper"

# macOS / Linux (from repo root)
./scripts/deploy-to-azure.sh -g ca-policy-rg -w my-ca-manager -o my-openai-helper
```

**Fully automated deployment includes:**

- ✅ Creates Azure App Service + Azure OpenAI
- ✅ Configures all app settings automatically
- ✅ Generates secure secrets
- ✅ Creates Azure AD App Registration
- ✅ Deploys application code
- ✅ Enables diagnostic logging

**Time:** 10-12 minutes | **Cost:** $0-13/month

📖 **[Complete Automation Guide](docs/deployment/AUTOMATED_DEPLOYMENT.md)**

### Option 2: Deploy to Azure Button

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAntonWilloughby%2FConditionalAccessPolicyManager%2Fmain%2Fazuredeploy.json)

**⏱️ Time:** 10-15 minutes | **💰 Cost:** Free tier available (F1) or $13/month (B1)

**✨ Fully Automated Deployment:**

- ✅ Creates Azure App Service + OpenAI
- ✅ **Automatically deploys application code from GitHub**
- ✅ Auto-generates all secrets (SECRET_KEY, API keys)
- ✅ Configures all environment variables
- ✅ Root-level `requirements.txt` ensures Azure installs dependencies automatically
- ⏱️ Wait 5-10 minutes for build to complete after deployment

**📋 What You Need to Do:**

1. **Click button** → Fill parameters → Deploy (5-8 min)
2. **Wait for build** → Code deploys automatically (5-10 min)
3. **Create Azure AD App Registration** (5 min) - OR enable DEMO_MODE for testing
4. **Need to redeploy custom changes later?** Use the Zip Deploy workflow below so dependencies install correctly every time.

**Manual redeploy (Zip Deploy) when you customize code:**

```powershell
# Always run from the repo root so the top-level requirements.txt is included
cd "C:\Github\CA Policy Manager Tool"

# (Optional) confirm the shim points to the app folder
Get-Content .\requirements.txt  # should output: -r CA_Policy_Manager_Web/requirements.txt

# Build and deploy
Compress-Archive -Path * -DestinationPath deploy.zip -Force
az webapp deploy --name <your-app-name> --resource-group <your-rg> --src-path deploy.zip --type zip
Remove-Item deploy.zip
```

**👉 [Complete Deployment Guide](DEPLOY_BUTTON_COMPLETE_GUIDE.md)** - Follow this for step-by-step instructions

**✅ Validate deployment:** After clicking the button, run:

```powershell
.\validate-deployment.ps1 -WebAppName "your-app-name" -ResourceGroup "your-rg-name"
```

---

## 📁 Project Structure

```
CA Policy Manager Tool/
│
├── CA_Policy_Manager_Web/      # Main web application
│   ├── app.py                  # Flask application
│   ├── ca_policy_manager.py    # Core CA policy logic
│   ├── ca_policy_examples.py   # Policy templates
│   ├── config.py               # Configuration management
│   ├── requirements.txt        # Python dependencies
│   ├── templates/              # HTML templates
│   ├── static/                 # CSS/JS assets
│   ├── utils/                  # Helper modules (AI, report analyzer)
│   ├── docs/                   # App-specific documentation
│   └── data/                   # User data and backups
│
├── docs/                       # 📚 All documentation (organized)
│   ├── setup/                  # Setup and installation guides
│   ├── security/               # Security and publishing docs
│   └── archive/                # Archived/outdated docs
│
├── setup-local.ps1             # Automated setup (Windows)
├── setup-local.sh              # Automated setup (macOS/Linux)
├── SETUP.bat                   # Quick launcher (Windows)
├── START_APP.bat               # App launcher (Windows)
└── README.md                   # This file
```

## 🌟 Features

- 🎯 **Deploy from 20+ enterprise policy templates** - Production-ready configurations
- 🔄 **Real-time policy management** - Create, read, update, and delete CA policies
- 🤖 **AI-powered policy explanations** - Understand complex policies in plain English
- 🌍 **Named locations management** - Configure IP-based and geographic locations
- 📊 **Bulk policy deployment** - Deploy multiple policies with progress tracking
- 🔐 **Dual authentication modes** - Support for delegated and service principal auth
- 💅 **Modern, responsive UI** - Clean interface built with Bootstrap 5
- 📁 **Policy backups** - Export and import policy configurations

## 🚀 Quick Start - Local Development

### ⚡ 1-Command Setup (Windows/macOS/Linux)

> **Supported Python versions:** 3.11 and 3.12. The checker now fails fast if only Python 3.13/3.14+ is installed (those builds break several dependencies).

**Windows (PowerShell)**

```powershell
./setup-local.ps1
```

**Linux/macOS**

```bash
chmod +x setup-local.sh
./setup-local.sh
```

**The setup script now:**

- ✅ Locates a real Python 3.11/3.12 installation (shows unsupported versions it finds)
- ✅ Creates a fresh `.venv` virtual environment
- ✅ Installs all 13 Python dependencies with upgraded `pip`
- ✅ Generates a secure `SECRET_KEY`
- ✅ Creates `.env` with `DEMO_MODE=true` so you can load the UI without Azure creds
- ✅ Highlights any missing `MSAL_CLIENT_ID` and explains that the client secret is optional for delegated sign-in
- ✅ Reminds you to fully stop Python (`Stop-Process -Name python -Force`) when you change `.env`

**Time**: about 2–3 minutes on a broadband connection

### 📝 Finish Configuration

1. Open `CA_Policy_Manager_Web/.env`
2. Replace the placeholders when you're ready to leave demo mode:

```bash
MSAL_CLIENT_ID=<your Azure app id>
# Optional unless you use client-credential auth
MSAL_CLIENT_SECRET=<client secret>
DEMO_MODE=false
```

3. **Hard-restart the dev server after saving `.env`** – Flask caches environment variables. On Windows use `Stop-Process -Name python -Force`; on macOS/Linux run `pkill -f "python app.py"` before launching again.

**Need Azure credentials?** Follow [docs/QUICK_SETUP.md](docs/QUICK_SETUP.md) (≈5 minutes).

### 🚀 Launch the Application

```powershell
cd CA_Policy_Manager_Web
python app.py
```

Open a browser at **http://localhost:5000**. If you left `DEMO_MODE=true`, the UI loads with sample data and the sign-in button will remind you to add real credentials.

### ✅ Verify Setup

```powershell
./validate-security-fixes.ps1
# Expected: ✅ All 7/7 security fixes verified!
```

---

## 📚 Setup Documentation

- **[SETUP_FOR_FORKS.md](SETUP_FOR_FORKS.md)** - Complete setup guide for forked repos (5 min)
- **[QUICK_START.md](QUICK_START.md)** - Detailed quick start with troubleshooting
- **[LOCAL_TESTING_GUIDE.md](LOCAL_TESTING_GUIDE.md)** - Comprehensive testing guide

### Alternative: Manual Setup

### 1. Install Dependencies Manually

```powershell
cd CA_Policy_Manager_Web
pip install -r requirements.txt
```

### 2. Launch the Application

```powershell
python app.py
```

### 3. Access the Web Interface

Open your browser to `http://localhost:5000`

## 🔧 Installation

### Environment Setup

```powershell
# Create virtual environment (recommended)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
cd CA_Policy_Manager_Web
pip install -r requirements.txt
```

---

## 📖 Documentation

- **Detailed Guide**: See `docs/README.md` for the full documentation index
- **Setup Guides**: Check `CA_Policy_Manager_Web/docs/` for setup and deployment
- **API Documentation**: See `CA_Policy_Manager_Web/docs/` for Graph API details

## 📚 Documentation

- **Quick Start**: See `docs/setup/QUICK_START.md`
- **First Time Setup**: See `docs/setup/START_HERE.md`
- **All Documentation**: Browse `docs/README.md` for complete index
- **Contributing**: See `CONTRIBUTING.md`
- **Security**: See `SECURITY.md`

---

## 🔒 Security Best Practices

- Store credentials securely (never commit `.env` or `config.json`)
- Use separate Azure AD app registrations for read vs. write operations
- Always test policies in report-only mode first
- Maintain break-glass accounts excluded from policies
- Review audit logs regularly

---

## 📝 License

MIT License - See `LICENSE` file for details

---

## 🤝 Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for guidelines.

---

## ⚠️ Disclaimer

This tool modifies production security policies. Always test in non-production environments first and maintain proper backups.
