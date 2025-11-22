# Conditional Access Policy Manager

**Modern Flask web application for managing Azure AD Conditional Access policies via Microsoft Graph API.**

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FYOUR_USERNAME%2FYOUR_REPO%2Fmain%2Fazure-deploy.json)

> **Note:** Replace `YOUR_USERNAME/YOUR_REPO` in the badge URL above with your actual GitHub username and repository name.

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
│   ├── CAPolicyWorkbook.json   # Azure workbook for monitoring
│   ├── templates/              # HTML templates
│   ├── static/                 # CSS/JS assets
│   ├── utils/                  # Helper modules (AI, report analyzer)
│   ├── docs/                   # Documentation
│   ├── scripts/                # Deployment scripts
│   └── data/                   # User data and backups
│
├── README.md                   # This file
└── README_NEW.md               # Detailed documentation
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

## 🚀 Quick Start - Automated Setup

### ⚡ 1-Command Setup (Recommended)

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

- **Detailed Guide**: See `README_NEW.md` for comprehensive documentation
- **Setup Guides**: Check `CA_Policy_Manager_Web/docs/` for setup and deployment
- **API Documentation**: See `CA_Policy_Manager_Web/docs/` for Graph API details
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
