# Conditional Access Policy Manager

[![Python 3.11–3.12](https://img.shields.io/badge/python-3.11--3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![Microsoft Graph](https://img.shields.io/badge/Microsoft-Graph%20API-blue.svg)](https://docs.microsoft.com/en-us/graph/)

A modern web-based tool for managing Azure AD Conditional Access policies with AI-powered policy explanations and comprehensive policy templates.

![Conditional Access Policy Manager](docs/screenshot-placeholder.png)

## 🌟 Features

### Core Functionality

- 🎯 **Deploy from 20+ Enterprise Templates** - Production-ready policy templates for common scenarios
- 🔄 **Real-time Policy Management** - Create, read, update, and delete CA policies via Microsoft Graph API
- 🤖 **AI-Powered Explanations** - Get plain-English explanations of complex policies using Azure OpenAI
- 🌍 **Named Locations Management** - View and manage IP-based and geographic location configurations
- 📊 **Bulk Operations** - Deploy multiple policies at once with progress tracking
- 🔗 **Azure Portal Integration** - Quick links to related Azure Portal pages

### Authentication & Security

- 🔐 **Dual Authentication Modes** - Support for both delegated (user) and service principal (app) auth
- 🛡️ **Secure Session Management** - Session-based tokens, no persistent credential storage
- ✅ **Duplicate Detection** - Prevents accidentally deploying policies with duplicate names
- 🔍 **Permission Validation** - Clear error messages for missing Graph API permissions

### User Experience

- 💅 **Modern UI** - Clean, responsive interface with Bootstrap 5
- 📱 **Mobile-Friendly** - Works on tablets and mobile devices
- 🎨 **Beautiful Gradient Theme** - Professional purple gradient design
- ⚡ **Real-time Updates** - Live policy status and deployment progress
- 💰 **AI Cost Tracking** - Monitor AI usage and estimated costs

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Features in Detail](#-features-in-detail)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage Guide](#-usage-guide)
- [Policy Templates](#-policy-templates)
- [AI Features](#-ai-features)
- [API Reference](#-api-reference)
- [Contributing](#-contributing)
- [Security](#-security)
- [License](#-license)

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or 3.12
- Azure AD tenant with admin privileges
- Azure AD App Registration with appropriate permissions

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/conditional-access-policy-manager.git
   cd conditional-access-policy-manager/CA_Policy_Manager_Web
   ```

2. **Run the automated setup** (supports Python 3.11 and 3.12)

   ```powershell
   # Windows (PowerShell)
   ./setup-local.ps1
   ```

   ```bash
   # macOS/Linux
   ./setup-local.sh
   ```

   The script creates `.venv`, installs all dependencies, and generates `.env` with `DEMO_MODE=true` so you can tour the UI before wiring up Azure.

3. **Add your Azure credentials when ready**

   ```bash
   # Edit CA_Policy_Manager_Web/.env
   MSAL_CLIENT_ID=<your app id>
   # Optional unless you use client-credential flows
   MSAL_CLIENT_SECRET=<client secret>
   DEMO_MODE=false
   ```

   > ℹ️ After saving `.env`, fully stop any running dev server (`Stop-Process -Name python -Force` on Windows or `pkill -f "python app.py"` on macOS/Linux) so Flask reloads the updated environment variables.

4. **Run the application**

   ```bash
   cd CA_Policy_Manager_Web
   python app.py
   ```

5. **Open browser**
   Navigate to `http://localhost:5000`

For detailed setup instructions, see [QUICKSTART.md](CA_Policy_Manager_Web/QUICKSTART.md)

## ✨ Features in Detail

### Policy Templates

20 pre-configured enterprise-ready templates across 4 categories:

#### 🏢 **Baseline & Admins** (4 policies)

- Block legacy authentication
- Require MFA for admins
- Require MFA for Azure management
- Block access from unknown locations (admins)

#### 👥 **Internals** (9 policies)

- Require MFA for all users
- Block legacy authentication for all users
- Require device compliance
- Require approved client apps
- Block high-risk sign-ins
- Identity Protection policies (3x)
- App protection requirements

#### 🌐 **Guests & External** (4 policies)

- Require MFA for guests
- Block guest access from untrusted locations
- Require compliant devices for guests
- Block high-risk guests

#### 📊 **Attack Surface Reduction** (3 policies)

- Block persistence attempts (risky sign-ins)
- Require MFA for Box cloud storage
- Block high-risk administrative actions

### AI-Powered Policy Explanations

When enabled, the AI assistant provides:

- **Plain-English Summaries** - Understand what policies do without technical jargon
- **Impact Analysis** - Know how policies affect your users
- **Smart Recommendations** - Get suggestions for policy improvements
- **Cost Tracking** - Monitor AI usage and costs in real-time

### Named Locations

View and manage Conditional Access named locations:

- **IP Range Locations** - CIDR notation with trust status
- **Country/Region Locations** - Geographic restrictions
- **Trust Indicators** - Visual badges for trusted vs untrusted locations
- **Detailed Views** - Full JSON inspection for troubleshooting

### Azure Portal Quick Links

One-click access to:

- Conditional Access Insights & Reporting
- Policy management blade
- Sign-in logs
- What If tool
- Identity Protection
- Authentication methods

## 💻 Installation

### System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux
- **Python**: 3.11 or 3.12 (later 3.x releases are currently unsupported)
- **Memory**: 2GB RAM minimum
- **Network**: Internet connection for Graph API access

### Detailed Installation Steps

See [QUICKSTART.md](CA_Policy_Manager_Web/QUICKSTART.md) for:

- Azure AD app registration steps
- Required Graph API permissions
- Environment variable configuration
- Troubleshooting common issues

## ⚙️ Configuration

### Required Environment Variables

```bash
# Azure AD OAuth
MSAL_CLIENT_ID=your-client-id
MSAL_AUTHORITY=https://login.microsoftonline.com/organizations

# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Optional: AI Features
AI_ENABLED=true
AI_PROVIDER=azure
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```

### Graph API Permissions Required

**Delegated Permissions** (for user login):

- `Policy.Read.All` - Read Conditional Access policies
- `Policy.ReadWrite.ConditionalAccess` - Manage CA policies
- `Directory.Read.All` - Read directory data (for group resolution)

**Application Permissions** (for service principal):

- `Policy.Read.All`
- `Policy.ReadWrite.ConditionalAccess`
- `Application.Read.All`
- `Group.Read.All`

## 📖 Usage Guide

### Basic Workflow

1. **Connect to Azure AD**

   - Click "Connect" button
   - Choose authentication method
   - Sign in with admin credentials

2. **View Existing Policies**

   - Policies tab shows all current CA policies
   - Sort by name, state, or conditions
   - Click eye icon to view policy JSON
   - Use AI button for plain-English explanation

3. **Deploy Templates**

   - Navigate to "Deploy Templates" tab
   - Browse available templates by category
   - Click "Preview" to see policy JSON
   - Click "Deploy" to create policy
   - Or use "Deploy All Templates" for bulk deployment

4. **Manage Named Locations**

   - Go to "Named Locations" tab
   - Click "Refresh" to load locations
   - View IP ranges, countries, and trust status
   - Click eye icon for detailed information

5. **Access Azure Portal**
   - Use "Azure Portal Links" tab
   - Quick access to Insights & Reporting
   - Direct links to What If tool and other resources

### Advanced Features

#### Bulk Policy Deletion

- Select multiple policies using checkboxes
- Click "Bulk Delete Selected"
- Confirm deletion
- Track progress in real-time

#### Policy Import/Export

- Export policies as JSON for backup
- Import policies from other tenants
- Version control your policy configurations

#### AI Cost Monitoring

- View real-time AI usage statistics
- Track tokens consumed and estimated costs
- Monitor average response times
- Session and 7-day cost breakdown

## 📦 Policy Templates

### Template Structure

Each template includes:

- **Display Name** - Descriptive policy name
- **State** - enabledForReportingButNotEnforced (safe default)
- **Conditions** - Who, what, when, where
- **Grant Controls** - MFA, compliant device, approved app, etc.
- **Session Controls** - Sign-in frequency, persistent browser, etc.

### Customization

Templates use placeholder groups like:

- `CA-Internals` - Internal employees
- `CA-Admins-Conditional-Access` - CA administrators
- `CA-Guests` - External users
- `CA-BreakGlass` - Emergency access accounts

Create these groups in Azure AD before deploying, or modify templates to use your existing groups.

### Modifying Templates

Edit `ca_policy_examples.py` to:

- Add new templates
- Modify existing templates
- Adjust default states
- Change exclusion groups

## 🤖 AI Features

### Setup

See [AI_SETUP_GUIDE.md](CA_Policy_Manager_Web/AI_SETUP_GUIDE.md) for:

- Azure OpenAI resource creation
- API key configuration
- Model deployment
- Cost estimation

### Supported Providers

- **Azure OpenAI** (Recommended) - Enterprise-grade, compliant
- **OpenAI** - Direct API access
- **Local Models** - Ollama for air-gapped environments

### Cost Optimization

- Uses `gpt-4o-mini` by default (cost-effective)
- Smart token management
- Real-time cost tracking
- Configurable rate limits

## 📚 API Reference

### Endpoints

#### Policies

- `GET /api/policies` - List all policies
- `POST /api/policies` - Create policy
- `GET /api/policies/<id>` - Get policy details
- `PUT /api/policies/<id>` - Update policy
- `DELETE /api/policies/<id>` - Delete policy
- `POST /api/policies/bulk-delete` - Delete multiple policies

#### Templates

- `GET /api/templates` - List available templates
- `POST /api/templates/deploy` - Deploy single template
- `POST /api/templates/deploy-all` - Deploy all templates

#### Named Locations

- `GET /api/named-locations` - List named locations

#### AI Features

- `GET /api/policies/<id>/explain` - Get AI explanation
- `GET /api/ai/stats` - Get usage statistics

### Authentication

All API endpoints require authentication:

- **Delegated**: Session-based after user login
- **Client Credentials**: Set in environment variables

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Code of conduct
- Development setup
- Coding standards
- Pull request process
- Testing guidelines

### Development Roadmap

- [ ] Policy effectiveness analytics
- [ ] Sign-in log integration
- [ ] Policy conflict detection
- [ ] Multi-tenant support
- [ ] Policy versioning and rollback
- [ ] Automated testing framework

## 🔒 Security

### Reporting Vulnerabilities

See [SECURITY.md](SECURITY.md) for:

- How to report security issues
- Secure usage guidelines
- Credential management best practices
- Deployment security checklist

### Security Features

- ✅ Session-based authentication (no persistent tokens)
- ✅ HTTPS recommended for production
- ✅ Input validation and sanitization
- ✅ CSRF protection (configurable)
- ✅ No sensitive data logging
- ✅ Environment variable isolation

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Powered by [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/)
- UI components from [Bootstrap 5](https://getbootstrap.com/)
- Icons by [Bootstrap Icons](https://icons.getbootstrap.com/)
- AI integration via [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service)

## 📞 Support

- **Documentation**: See [docs/](docs/) folder
- **Issues**: [GitHub Issues](https://github.com/yourusername/conditional-access-policy-manager/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/conditional-access-policy-manager/discussions)

## 🗺️ Project Structure

```
conditional-access-policy-manager/
├── CA_Policy_Manager_Web/        # Main web application
│   ├── static/                   # CSS, JS, images
│   ├── templates/                # HTML templates
│   ├── utils/                    # Utility modules
│   ├── data/                     # Upload/backup storage
│   ├── docs/                     # Documentation
│   ├── scripts/                  # Helper scripts
│   ├── app.py                    # Flask application
│   ├── config.py                 # Configuration management
│   ├── ca_policy_examples.py     # Policy templates
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Environment template
│   └── README.md                 # Detailed docs
├── .gitignore                    # Git ignore patterns
├── LICENSE                       # MIT license
├── CONTRIBUTING.md               # Contribution guidelines
├── SECURITY.md                   # Security policy
└── README.md                     # This file
```

---

**Made with ❤️ for Azure AD administrators**

_Simplify Conditional Access management and secure your organization with confidence._
