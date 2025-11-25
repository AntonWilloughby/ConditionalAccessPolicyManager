# 🎯 Setup Flow Diagram - Visual Guide

## Quick Reference: Choose Your Path

```
┌─────────────────────────────────────────────────────────────────┐
│                    FORK REPOSITORY ON GITHUB                     │
│                   git clone <your_fork_url>                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  What OS are   │
                    │   you using?   │
                    └────────┬───────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
     ┌──────────┐     ┌──────────┐    ┌──────────┐
     │ Windows  │     │  Linux   │    │  macOS   │
     └────┬─────┘     └────┬─────┘    └────┬─────┘
          │                │                │
          │                │                │
┌─────────┴─────────┐      │                │
│ Skill Level?      │      │                │
│ 1. GUI User       │      │                │
│ 2. CLI User       │      │                │
└─────┬─────┬───────┘      │                │
      │     │               │                │
      │     │               │                │
      ▼     ▼               ▼                ▼
   ╔═══╗ ╔═══╗         ╔═══╗            ╔═══╗
   ║ 1 ║ ║ 2 ║         ║ 3 ║            ║ 4 ║
   ╚═╤═╝ ╚═╤═╝         ╚═╤═╝            ╚═╤═╝
     │     │             │                │
     │     │             │                │
     └─────┴─────────────┴────────────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │  AUTOMATED SETUP RUNS  │
            │  • Detects Python      │
            │  • Creates venv        │
            │  • Installs packages   │
            │  • Creates .env        │
            └───────────┬────────────┘
                        │
                        ▼
            ┌────────────────────────┐
            │  EDIT .env FILE        │
            │  Add Azure credentials │
            │  • MSAL_CLIENT_ID      │
            │  • MSAL_CLIENT_SECRET  │
            └───────────┬────────────┘
                        │
                        ▼
            ┌────────────────────────┐
            │   START APPLICATION    │
            │   python app.py        │
            └───────────┬────────────┘
                        │
                        ▼
            ┌────────────────────────┐
            │ OPEN BROWSER           │
            │ http://localhost:5000  │
            └───────────┬────────────┘
                        │
                        ▼
               ┌────────────────┐
               │   SUCCESS! 🎉  │
               └────────────────┘
```

---

## Detailed Path Breakdowns

### Path 1: Windows GUI User (Easiest)

```
START
  │
  ├─> Double-click "SETUP.bat"
  │      │
  │      ├─> [Automated] Check Python
  │      ├─> [Automated] Create venv
  │      ├─> [Automated] Install packages
  │      └─> [Automated] Create .env
  │
  ├─> Notepad opens with .env file
  │      │
  │      └─> Paste Azure credentials
  │          Save and close
  │
  ├─> Double-click "START_APP.bat"
  │      │
  │      └─> Browser opens to localhost:5000
  │
  └─> ✅ DONE (5-10 minutes total)
```

### Path 2: Windows CLI User

```
START
  │
  ├─> Open PowerShell
  │      │
  │      └─> cd "path\to\repo"
  │
  ├─> Run: .\setup-local.ps1
  │      │
  │      ├─> [Automated] Check Python
  │      ├─> [Automated] Create venv
  │      ├─> [Automated] Install packages
  │      └─> [Automated] Create .env
  │
  ├─> Run: notepad CA_Policy_Manager_Web\.env
  │      │
  │      └─> Add Azure credentials
  │
  ├─> Run: cd CA_Policy_Manager_Web
  │      Run: python app.py
  │
  └─> ✅ DONE (5-10 minutes total)
```

### Path 3: Linux User

```
START
  │
  ├─> Open Terminal
  │      │
  │      └─> cd ~/path/to/repo
  │
  ├─> Run: chmod +x setup-local.sh
  │      Run: ./setup-local.sh
  │      │
  │      ├─> [Automated] Check Python
  │      ├─> [Automated] Create venv
  │      ├─> [Automated] Install packages
  │      └─> [Automated] Create .env
  │
  ├─> Run: nano CA_Policy_Manager_Web/.env
  │      │
  │      └─> Add Azure credentials
  │          Ctrl+X, Y, Enter to save
  │
  ├─> Run: cd CA_Policy_Manager_Web
  │      Run: python app.py
  │
  └─> ✅ DONE (5-10 minutes total)
```

### Path 4: macOS User

```
START
  │
  ├─> Open Terminal
  │      │
  │      └─> cd ~/path/to/repo
  │
  ├─> Run: chmod +x setup-local.sh
  │      Run: ./setup-local.sh
  │      │
  │      ├─> [Automated] Check Python
  │      ├─> [Automated] Create venv
  │      ├─> [Automated] Install packages
  │      └─> [Automated] Create .env
  │
  ├─> Run: nano CA_Policy_Manager_Web/.env
  │      │  (or use your favorite editor)
  │      └─> Add Azure credentials
  │          Cmd+X, Y, Enter to save
  │
  ├─> Run: cd CA_Policy_Manager_Web
  │      Run: python app.py
  │
  └─> ✅ DONE (5-10 minutes total)
```

---

## Troubleshooting Flow

```
┌───────────────────────┐
│  Setup Failed? 🐛     │
└──────────┬────────────┘
           │
           ▼
    ┌─────────────┐
    │  Run This:  │
    │ diagnose.ps1│
    └──────┬──────┘
           │
           ▼
    ┌──────────────────────────┐
    │  7 Automated Checks:     │
    │  1. Python installed?    │
    │  2. Venv exists?         │
    │  3. Packages installed?  │
    │  4. Config files OK?     │
    │  5. App files present?   │
    │  6. Network OK?          │
    │  7. Security fixes?      │
    └──────┬───────────────────┘
           │
           ▼
    ┌──────────────┐
    │  All Pass?   │
    └───┬──────┬───┘
        │      │
        NO    YES
        │      │
        ▼      ▼
    ┌────┐  ┌──────────┐
    │Fix │  │ You're   │
    │It! │  │ Ready! ✅│
    └────┘  └──────────┘
```

---

## Azure Credentials Flow

```
┌─────────────────────────────┐
│ Need Azure Credentials?     │
└──────────┬──────────────────┘
           │
           ▼
    ┌──────────────┐
    │ Choose Path: │
    └──────┬───────┘
           │
    ┌──────┴───────┐
    │              │
    ▼              ▼
┌───────┐    ┌──────────┐
│Manual │    │Automated │
│Setup  │    │Script    │
└───┬───┘    └────┬─────┘
    │             │
    │             ▼
    │        ┌─────────────────────────┐
    │        │ Run:                    │
    │        │ .\scripts\              │
    │        │ Register-EntraApp-      │
    │        │ Delegated.ps1           │
    │        └──────────┬──────────────┘
    │                   │
    │                   ├─> Creates App
    │                   ├─> Sets Permissions
    │                   ├─> Generates Secret
    │                   └─> Updates .env ✅
    │
    ▼
┌──────────────────────────┐
│ 1. Azure Portal          │
│ 2. App Registrations     │
│ 3. New registration      │
│ 4. Set redirect URI      │
│ 5. Add API permissions   │
│ 6. Create secret         │
│ 7. Copy to .env          │
└──────────┬───────────────┘
           │
           ▼
    ┌──────────────┐
    │ Credentials  │
    │  in .env ✅  │
    └──────────────┘
```

---

## Validation Flow

```
┌────────────────────────┐
│ App Running?           │
│ Verify it's secure!    │
└───────────┬────────────┘
            │
            ▼
    ┌───────────────────┐
    │ Run:              │
    │ .\validate-       │
    │ security-fixes.ps1│
    └────────┬──────────┘
             │
             ▼
    ┌────────────────────────┐
    │  7 Security Tests:     │
    │  ✅ No hardcoded creds │
    │  ✅ Debug controlled   │
    │  ✅ SSL secure         │
    │  ✅ Session manager    │
    │  ✅ Error sanitized    │
    │  ✅ CSRF enabled       │
    │  ✅ Security headers   │
    └────────┬───────────────┘
             │
             ▼
    ┌────────────────┐
    │  All 7/7 Pass? │
    └────┬─────┬─────┘
         │     │
        YES    NO
         │     │
         ▼     ▼
    ┌──────┐ ┌────────────┐
    │Ready │ │Check       │
    │For   │ │Documentation│
    │Use!✅│ │For Fixes   │
    └──────┘ └────────────┘
```

---

## Daily Workflow (After Initial Setup)

```
Day 1: Setup (one time)
  │
  ├─> Run setup script
  ├─> Configure .env
  └─> Validate security

Day 2+: Daily Development
  │
  ├─> Option A (Windows GUI)
  │      └─> Double-click START_APP.bat
  │
  ├─> Option B (CLI)
  │      ├─> cd CA_Policy_Manager_Web
  │      └─> python app.py
  │
  └─> App runs immediately (no setup needed!)
```

---

## File Decision Tree

```
Which file should I use?

New to this repo?
  └─> SETUP_FOR_FORKS.md

Want quick start?
  └─> QUICK_START.md

Need step-by-step?
  └─> FIRST_TIME_SETUP_CHECKLIST.md

Having problems?
  └─> Run: diagnose.ps1

Want to test thoroughly?
  └─> LOCAL_TESTING_GUIDE.md

Need Azure setup help?
  └─> docs/QUICK_SETUP.md

Want to deploy?
  └─> docs/DEPLOYMENT.md

Understand security?
  └─> SECURITY_FIXES_COMPLETE.md
```

---

## Time Breakdown

```
Total Time to Running App: 5-10 minutes

┌─────────────────────────────────────┐
│ Fork & Clone         │ 1 min        │
├─────────────────────────────────────┤
│ Run Setup Script     │ 2-3 min      │
│  • Python check      │              │
│  • Venv creation     │              │
│  • Package install   │              │
│  • .env creation     │              │
├─────────────────────────────────────┤
│ Azure Setup          │ 2-5 min      │
│  • Automated script  │ 2 min   OR   │
│  • Manual portal     │ 5 min        │
├─────────────────────────────────────┤
│ Edit .env            │ 30 sec       │
├─────────────────────────────────────┤
│ Start App            │ 10 sec       │
├─────────────────────────────────────┤
│ Verify Security      │ 30 sec       │
└─────────────────────────────────────┘

TOTAL: 5-10 minutes ✅
```

---

## Success Indicators

```
✅ Setup Successful When You See:

Terminal Output:
  ✅ Virtual environment created
  ✅ Dependencies installed
  ✅ .env file created
  ✅ Running on http://127.0.0.1:5000

Browser:
  ✅ Dashboard loads
  ✅ "Connect to Microsoft Graph" button
  ✅ No error messages

Validation Script:
  ✅ All 7/7 security fixes verified!

You're Ready! 🎉
```

---

**Visual guide complete!** Use this flowchart to quickly understand the setup process.
