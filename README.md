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

## 🚀 Quick Start

### 1. Install Dependencies
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
