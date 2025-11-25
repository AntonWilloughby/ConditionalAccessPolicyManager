# GitHub Publication Checklist

## ✅ Pre-Publication Tasks

### 1. Clean Up Repository Structure
- [x] Remove old/unused files
- [ ] Remove sensitive data
- [ ] Update .gitignore
- [ ] Organize documentation

### 2. Files to DELETE Before Publishing

#### Root Directory
```
ca_policies_backup.json          # Contains sensitive tenant data
Microsoft_Defender_Policies.xlsx # Generated file
web_data/                        # Generated/cached data
__pycache__/                     # Python cache
```

#### CA_Policy_Manager_Web/
```
.env                            # CRITICAL: Contains API keys and secrets!
.env.azure                      # Contains credentials
data/uploads/                   # User uploaded files
data/backups/                   # May contain tenant data
__pycache__/                    # Python cache
organize_folder.ps1             # Internal utility
SETUP_COMPLETE.md              # Personal setup notes
```

#### CA_Policy_Manager/
```
config.json                     # CRITICAL: Contains tenant ID and credentials!
ca_policy_examples_OLD.py.bak  # Backup file
temp_script.js                 # Temporary file
extract_js_data.py             # One-off utility
debug_report.py                # Debug utility
test_report_analyzer.py        # Test file
__pycache__/                   # Python cache
```

### 3. Update .gitignore (Root Level)
Ensure these patterns are included:
```gitignore
# Environment files
.env
.env.*
!.env.example

# Credentials
config.json
*.secret
*.key

# User data
data/uploads/*
data/backups/*
ca_policies_backup*.json

# Generated files
web_data/
*.xlsx
!*Reference*.xlsx  # Keep template files if any

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.venv/
venv/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
desktop.ini

# Logs
*.log
```

### 4. Verify Example Files Are Safe
Check these files for sensitive data:
- [ ] `.env.example` - No real credentials
- [ ] `config.json.template` - No real tenant IDs
- [ ] All README files - No personal info

### 5. Create/Update Documentation

#### Required Files:
- [x] `README.md` (main project overview)
- [ ] `LICENSE` (choose license: MIT recommended)
- [ ] `CONTRIBUTING.md` (contribution guidelines)
- [ ] `SECURITY.md` (security policy)
- [ ] `CODE_OF_CONDUCT.md` (optional but recommended)

#### Per-Tool Documentation:
- [x] `CA_Policy_Manager_Web/README.md`
- [x] `CA_Policy_Manager_Web/QUICKSTART.md`
- [x] `CA_Policy_Manager_Web/AI_SETUP_GUIDE.md`
- [x] `CA_Policy_Manager/README.md`
- [x] `CA_Policy_Manager/CA_SETUP_GUIDE.md`

### 6. Clean Up Code

#### Remove Debug/Test Code:
- [ ] Review all `print()` statements
- [ ] Remove commented-out code blocks
- [ ] Remove `# TODO` comments or document them in Issues
- [ ] Verify no hardcoded credentials

#### Code Quality:
- [ ] Add docstrings to all functions
- [ ] Ensure consistent formatting
- [ ] Remove unused imports

### 7. Security Scan

Run these commands to find potential issues:
```powershell
# Search for potential secrets
Select-String -Path "*.py" -Pattern "password|secret|key|token" -CaseSensitive

# Search for hardcoded IPs/URLs
Select-String -Path "*.py" -Pattern "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"

# Check for tenant IDs
Select-String -Path "*.py","*.json" -Pattern "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
```

### 8. Repository Metadata

#### Create LICENSE file (MIT License recommended):
```
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy...
```

#### Create SECURITY.md:
```markdown
# Security Policy

## Reporting Security Issues

Please report security vulnerabilities to [your email]

## Credential Management

This tool requires Azure AD credentials. Never commit:
- .env files
- config.json files
- Access tokens or API keys
```

### 9. Final Checks Before Push

- [ ] Delete all real .env files
- [ ] Delete all config.json files with real credentials
- [ ] Delete data/uploads and data/backups folders
- [ ] Run: `git status` to verify no sensitive files staged
- [ ] Test installation from scratch on clean machine
- [ ] Verify .env.example and config.json.template work
- [ ] All links in README files work
- [ ] Screenshots (if any) don't contain sensitive data

### 10. GitHub Repository Setup

#### Repository Settings:
- Name: `conditional-access-policy-manager` or similar
- Description: "Web-based tool for managing Azure AD Conditional Access policies with AI-powered policy explanations"
- Topics: `azure`, `conditional-access`, `azure-ad`, `microsoft-graph`, `flask`, `security`, `openai`
- License: MIT
- Include README: Yes

#### Create Repository Sections:
- README badges for Python version, license, etc.
- Add screenshots to docs/ folder (sanitized!)
- Create GitHub Issues for known todos
- Set up GitHub Actions (optional - for linting/tests)

### 11. Post-Publication

- [ ] Add installation video/GIF
- [ ] Create example screenshots (no real tenant data!)
- [ ] Write blog post or tutorial
- [ ] Share on Reddit/LinkedIn/Twitter
- [ ] Monitor GitHub Issues

## 📋 Quick Cleanup Commands

### PowerShell Commands to Run:

```powershell
# Navigate to project root
cd "c:\MyProjects\AV Policy"

# Remove sensitive files
Remove-Item -Recurse -Force .venv, __pycache__, web_data -ErrorAction SilentlyContinue
Remove-Item -Force ca_policies_backup.json, Microsoft_Defender_Policies.xlsx -ErrorAction SilentlyContinue

# Clean CA_Policy_Manager_Web
cd CA_Policy_Manager_Web
Remove-Item -Force .env, .env.azure, organize_folder.ps1, SETUP_COMPLETE.md -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force __pycache__, data/uploads/*, data/backups/* -ErrorAction SilentlyContinue

# Clean CA_Policy_Manager
cd ../CA_Policy_Manager
Remove-Item -Force config.json, ca_policy_examples_OLD.py.bak, temp_script.js -ErrorAction SilentlyContinue
Remove-Item -Force extract_js_data.py, debug_report.py, test_report_analyzer.py -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force __pycache__ -ErrorAction SilentlyContinue

cd ..
```

## 🎯 Recommended Repository Structure (After Cleanup)

```
conditional-access-policy-manager/
├── .github/
│   └── workflows/          # GitHub Actions (optional)
├── CA_Policy_Manager_Web/  # Main web application
│   ├── static/
│   ├── templates/
│   ├── utils/
│   ├── data/
│   │   ├── .gitkeep
│   │   └── uploads/.gitkeep
│   ├── docs/              # Screenshots, guides
│   ├── scripts/           # Helper scripts
│   ├── app.py
│   ├── config.py
│   ├── ca_policy_examples.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── .gitignore
│   ├── README.md
│   ├── QUICKSTART.md
│   └── AI_SETUP_GUIDE.md
├── CA_Policy_Manager/      # CLI/GUI tool (legacy?)
│   ├── *.py
│   ├── config.json.template
│   ├── requirements.txt
│   └── README.md
├── .gitignore
├── LICENSE
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
└── CODE_OF_CONDUCT.md
```

## ⚠️ CRITICAL: Before `git push`

1. **Triple-check these files are NOT committed:**
   - `.env`
   - `config.json`
   - Any file with real credentials
   - Any file with tenant-specific data

2. **Run this check:**
   ```powershell
   git status
   git diff --staged
   ```

3. **If you accidentally commit secrets:**
   - DO NOT just delete and recommit
   - The secret is still in git history
   - Use: `git filter-branch` or BFG Repo-Cleaner
   - Or start a fresh repository

## 📝 Sample Commit Message (First Commit)

```
Initial commit: Conditional Access Policy Manager

- Web-based Flask application for managing Azure AD CA policies
- 20 enterprise policy templates
- AI-powered policy explanations (Azure OpenAI integration)
- Named Locations management
- Azure Portal quick links
- Real-time policy deployment and monitoring
- Comprehensive documentation and setup guides
```
