# Quick Start Guide - CA Policy Manager

## 🚀 Get Started in 5 Minutes

### Step 1: Install Prerequisites

**You need:**
- Python 3.11+ ([Download](https://www.python.org/downloads/))
- Azure AD access with Conditional Access permissions
- An Azure AD app registration (see below)

### Step 2: Register Azure AD App

1. Go to [Azure Portal](https://portal.azure.com) → Azure Active Directory → App Registrations
2. Click **New registration**
3. Name: `CA Policy Manager`
4. Redirect URI: Select "Web" and enter: `http://localhost:5000/auth/callback`
5. Click **Register**
6. Copy the **Application (client) ID** - you'll need this!
7. Go to **API Permissions** → Add a permission → Microsoft Graph → Delegated permissions
8. Add these permissions:
   - `Policy.Read.All`
   - `Policy.ReadWrite.ConditionalAccess`
   - `Application.Read.All`
   - `Directory.Read.All`
   - `Group.ReadWrite.All`
   - `User.Read`
9. Click **Grant admin consent** (requires Global Admin or CA Admin role)

### Step 3: Download and Setup

```bash
# Clone or download the code
cd CA_Policy_Manager_Web

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate    # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Copy example config
copy .env.example .env   # Windows
cp .env.example .env     # Mac/Linux
```

### Step 4: Configure

Edit `.env` file:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this
MSAL_CLIENT_ID=paste-your-client-id-here
```

**Generate a secret key:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 5: Run!

```bash
python app.py
```

Open your browser to: **http://localhost:5000**

---

## 🎯 What Can You Do?

### View Policies
1. Click **"Sign In with Entra ID"**
2. Sign in with your Azure AD account
3. Grant permissions when prompted
4. View all Conditional Access policies in your tenant

### Deploy Policy Templates
1. Go to **Templates** tab
2. Browse 17 pre-built policy templates
3. Select policies to deploy
4. Click **Deploy Selected**
5. Policies are created in **Report-Only** mode by default

### Manage Groups
1. Go to **Groups** tab
2. Create all 67 recommended CA security groups
3. Groups follow naming convention: `CA-Persona-*`

### Analyze Reports
1. Upload a Zero Trust Assessment report
2. Get policy recommendations
3. Deploy recommended policies directly

---

## ❓ Common Issues

**"Module not found" error?**
```bash
pip install -r requirements.txt
```

**Authentication fails?**
- Wait 5-10 minutes after granting admin consent
- Make sure redirect URI is exactly: `http://localhost:5000/auth/callback`
- Check you're using the correct Client ID

**SSL certificate error?**
- If behind a corporate proxy that intercepts HTTPS:
  ```env
  # Add to .env
  DISABLE_SSL_VERIFY=true
  ```
  ⚠️ Only use this in development!

**Port 5000 already in use?**
```bash
# Use a different port
$env:PORT=5001; python app.py  # PowerShell
PORT=5001 python app.py        # Bash
```

---

## 📚 Learn More

- **Full Documentation:** See `docs/` folder
- **Security:** Read `docs/SECURITY_CHECKLIST.md` before production
- **Azure Deployment:** See `docs/DEPLOYMENT.md`
- **Policy Framework:** See `docs/CA_POLICY_FRAMEWORK.md`

---

## 💡 Tips for New Users

1. **Start in Report-Only Mode**
   - All templates default to "Report-Only"
   - Test policies for 1-2 weeks before enabling
   - Review sign-in logs for impact

2. **Create Groups First**
   - Go to Groups tab → Create All
   - Add users to appropriate groups
   - Then deploy policies

3. **Test with Your Account**
   - Deploy a policy targeting a test group
   - Add yourself to the group
   - Verify the policy applies as expected

4. **Enable Policies Gradually**
   - Start with low-risk policies (Guest access)
   - Move to medium-risk (Legacy auth blocking)
   - Last, enable high-risk (Device compliance)

---

## 🆘 Need Help?

- **Documentation Issues:** Open an issue in the repository
- **Azure AD Questions:** Check [Microsoft Learn](https://learn.microsoft.com/azure/active-directory/)
- **Bugs:** Report in issues with steps to reproduce

---

## ⚠️ Important Notes

### Security
- This is a development version - see `SECURITY_CHECKLIST.md` before production
- Never commit `.env` file to Git
- Keep your Client ID confidential
- Rotate secrets regularly

### Limitations
- Designed for single tenant use
- Requires appropriate Azure AD roles
- Break-glass accounts should be excluded from all policies
- Always test in Report-Only mode first

### Best Practices
- Back up existing policies before making changes
- Document why you're deploying each policy
- Review Azure AD sign-in logs regularly
- Keep groups organized with consistent naming

---

**Ready to get started?** Follow the steps above and you'll be managing CA policies in minutes!

**Questions?** Check the full docs in the `docs/` folder or ask your team lead.
