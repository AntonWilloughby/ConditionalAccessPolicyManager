# Conditional Access Policy Manager - Web Application

> ⚠️ **IMPORTANT:** This is a development version. See [QUICKSTART.md](QUICKSTART.md) to get started quickly!
> 
> **Before Production:** Read [SECURITY_REMEDIATION_PLAN.md](docs/SECURITY_REMEDIATION_PLAN.md) and complete [SECURITY_CHECKLIST.md](docs/SECURITY_CHECKLIST.md)

A Flask-based web application for managing Microsoft Entra Conditional Access policies through Microsoft Graph API.

## 🚀 Quick Links

- **[Get Started in 5 Minutes](QUICKSTART.md)** - For new users
- **[Deploy to Azure](docs/DEPLOYMENT.md)** - For production hosting
- **[Security Guide](docs/SECURITY_CHECKLIST.md)** - Before going live
- **[Policy Framework](docs/CA_POLICY_FRAMEWORK.md)** - Understanding policies

## 📁 Project Structure

```
CA_Policy_Manager_Web/
├── app.py                      # Main Flask application
├── ca_policy_manager.py        # Microsoft Graph API manager
├── ca_policy_examples.py       # Policy templates (17 policies)
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── organize_folder.ps1         # Folder organization script
│
├── templates/                  # HTML templates
│   └── index.html             # Main UI
│
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css          # Application styles
│   └── js/
│       └── main.js            # Client-side JavaScript
│
├── utils/                      # Utility modules
│   ├── __init__.py
│   └── report_analyzer.py     # Zero Trust report analyzer
│
├── docs/                       # Documentation
│   ├── README.md              # This file
│   ├── QUICK_SETUP.md         # Quick setup guide
│   ├── QUICK_START.md         # Quick start guide
│   ├── SETUP_ENTRA_AUTH.md    # Entra authentication setup
│   ├── SHARE_WITH_FRIEND.md   # Sharing guide
│   ├── FIX_PERMISSIONS.md     # Permission troubleshooting
│   ├── SUMMARY.md             # Project summary
│   ├── CA_POLICY_FRAMEWORK.md # Policy framework docs
│   └── CA_POLICY_TEMPLATES_README.md # Template docs
│
├── scripts/                    # Utility scripts
│   ├── Register-EntraApp.ps1  # Azure AD app registration
│   ├── create_ca_groups.ps1   # Create security groups
│   ├── start_web_app.bat      # Windows startup script
│   ├── startup.sh             # Linux startup script
│   ├── build_templates.py     # Build policy templates
│   ├── generate_policies.py   # Generate policies
│   └── test_templates.py      # Test templates
│
└── data/                       # Data files
    ├── uploads/               # Uploaded reports
    └── backups/               # Backup files
        ├── ca_policy_examples_backup.py
        ├── ca_policy_examples_new.py
        └── ca_policy_examples_TEMPLATE.txt
```

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Authentication**
   - See `docs/SETUP_ENTRA_AUTH.md` for detailed setup
   - Run `scripts/Register-EntraApp.ps1` to create Azure AD app

3. **Start the Application**
   ```bash
   python app.py
   ```
   Or use platform-specific scripts:
   - Windows: `scripts\start_web_app.bat`
   - Linux/Mac: `scripts/startup.sh`

4. **Access the Application**
   - Open browser to `http://localhost:5000`
   - Sign in with Entra ID or use client credentials

## 📚 Features

- **Policy Management**: View, create, update, and delete Conditional Access policies
- **Template Deployment**: Deploy pre-configured policy templates (17 policies across 8 personas)
- **Report Analysis**: Import and analyze Zero Trust Assessment reports
- **Bulk Operations**: Deploy multiple policies, create security groups
- **Dual Authentication**: Supports both delegated (user) and application (client credentials) authentication
- **Sorting & Filtering**: Sort policies by name, state, created, or modified date

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: Flask session secret key (auto-generated if not set)
- SSL verification is disabled by default for development (set `verify_ssl=False`)

### Upload Limits
- Max file size: 50MB
- Supported formats: HTML (Zero Trust reports)

## 📖 Documentation

Detailed documentation is available in the `docs/` folder:
- **Quick Setup**: `docs/QUICK_SETUP.md`
- **Authentication**: `docs/SETUP_ENTRA_AUTH.md`
- **Policy Framework**: `docs/CA_POLICY_FRAMEWORK.md`
- **Templates**: `docs/CA_POLICY_TEMPLATES_README.md`

## 🤝 Contributing

This is a personal project for managing Conditional Access policies. Feel free to fork and adapt for your needs.

## 📝 License

See LICENSE file for details.

## ⚠️ Security Notes

- SSL verification is disabled for development environments with corporate proxies
- For production deployment, enable SSL verification
- Store sensitive credentials securely (use Azure Key Vault in production)
- Review all policies before deploying to production tenants

## 🐛 Troubleshooting

- **Import errors**: Ensure you're running from the project root directory
- **SSL errors**: SSL verification is disabled by default in development
- **Permission errors**: See `docs/FIX_PERMISSIONS.md`
- **Report analysis not working**: Debug output is enabled in the console

## 📦 Dependencies

Major dependencies:
- Flask 3.0.0
- requests
- msal (Microsoft Authentication Library)
- beautifulsoup4 (for report parsing)
- pandas (for data export)

See `requirements.txt` for complete list.
