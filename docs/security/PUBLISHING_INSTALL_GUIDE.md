# Conditional Access Policy Manager – Local Install Guide

Use this hand-off when you share the repo with a customer or teammate. It walks through everything they need from the moment they fork the repo to the first successful run, including AI setup.

---

## 1. Fork & Clone

1. Fork `AntonWilloughby/ConditionalAccessPolicyManager` into your own GitHub org or account.
2. On your workstation:
   ```powershell
   git clone https://github.com/<YOUR-ORG>/ConditionalAccessPolicyManager.git
   cd ConditionalAccessPolicyManager
   ```

## 2. Prerequisites

- **Python 3.11.x or 3.12.x** (3.13/3.14 are blocked). During installation, check “Add Python to PATH.”
- **PowerShell 7 (pwsh)** suggested on Windows; Bash works on macOS/Linux.
- Optional: Azure subscription if you want Azure OpenAI and Graph access.

## 3. Automated Setup

From the repo root run one of the setup scripts (they create `.venv`, install dependencies, and scaffold `.env`).

### Windows

```powershell
.\setup-local.ps1
```

### macOS / Linux

```bash
chmod +x setup-local.sh
./setup-local.sh
```

_Outputs_: `.venv/` virtual environment, updated `CA_Policy_Manager_Web\.env` with `SECRET_KEY` and `DEMO_MODE=true`.

## 4. Configure `.env`

Edit `CA_Policy_Manager_Web\.env` (this file is gitignored). Key settings:

```ini
# --- Required for production use ---
MSAL_CLIENT_ID=<app registration client id>
MSAL_CLIENT_SECRET=<client secret if using client creds>
MSAL_TENANT_ID=<tenant id>
MSAL_AUTHORITY=https://login.microsoftonline.com/<tenant id>
MSAL_REDIRECT_URI=http://localhost:5000/auth/callback
DEMO_MODE=false  # flip once IDs are populated

# --- Optional: AI provider ---
AI_ENABLED=true
AI_PROVIDER=azure        # azure | openai | local
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15
AZURE_OPENAI_API_KEY=<azure openai key>
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

# For OpenAI instead
# AI_PROVIDER=openai
# OPENAI_API_KEY=sk-...
# OPENAI_MODEL=gpt-4o-mini

# For local models (Ollama)
# AI_PROVIDER=local
# LOCAL_MODEL=phi3
```

## 5. Azure App Registration (MSAL)

1. In Azure Portal → **App registrations** → **New registration**.
2. Redirect URI: `http://localhost:5000/auth/callback`.
3. API permissions → Microsoft Graph → add `Policy.Read.All` + `Policy.ReadWrite.ConditionalAccess` (admin consent needed).
4. Certificates & Secrets → **New client secret**. Copy the value into `.env`.

Automated option: run `scripts/Register-EntraApp-Delegated.ps1` and follow prompts.

## 6. Azure/OpenAI Resource (AI Optional)

See `AI_SETUP_GUIDE.md`:

- Azure OpenAI: create resource, deploy `gpt-4o-mini`, copy endpoint/key/deployment into `.env`.
- OpenAI: grab API key from https://platform.openai.com/ and set `AI_PROVIDER=openai`.
- Local: install Ollama, pull a model, set `AI_PROVIDER=local`.

If `AI_ENABLED=false`, the UI will show guidance instead of calling any model.

## 7. Run the App

Every time you work:

```powershell
cd ConditionalAccessPolicyManager
cd CA_Policy_Manager_Web
python app.py
```

Open `http://localhost:5000`. Demo mode shows the UI without Microsoft Graph; once you flip `DEMO_MODE=false` and supply MSAL values, the sign-in button talks to your tenant.

> **Tip:** When you edit `.env`, stop all running `python` processes (`Stop-Process -Name python -Force` on Windows) before restarting `python app.py` so Flask rereads the environment.

## 8. Validation & Delivery

- Run `.\validate-security-fixes.ps1` in the repo root to prove the hardened baseline is still intact (no hardcoded credentials, SSL on, CSRF enabled, etc.).
- Share this guide along with any tenant-specific secrets out-of-band.
- Optional: teach users about helper scripts (`SETUP.bat`, `START_APP.bat`, `scripts/Register-EntraApp-Delegated.ps1`).

That’s it—these steps take a new fork from zero to a working local instance with AI support configured to the client’s own Azure/OpenAI tenant.
