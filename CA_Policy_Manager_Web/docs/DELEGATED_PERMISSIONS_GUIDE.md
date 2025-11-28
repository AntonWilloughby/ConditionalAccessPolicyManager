# Delegated Permissions Guide 🔐

**Why Delegated-Only?** The CA Policy Manager uses **delegated permissions only** for a simple, user-friendly setup. No admin consent configuration needed!

## 🎯 Quick Summary

- ✅ **Zero Configuration**: Register app, sign in, consent once, done!
- ✅ **User Context**: All operations run with your signed-in user's permissions
- ✅ **Automatic Consent**: Permissions requested during first sign-in
- ✅ **No Admin Hassle**: Most delegated permissions don't require admin consent

## 📋 Permissions Explained

The app requests these **6 delegated permissions** when you sign in:

| Permission | What It Does | Why Needed |
|------------|--------------|------------|
| **Policy.Read.All** | Read Conditional Access policies | View existing policies |
| **Policy.ReadWrite.ConditionalAccess** | Create/update CA policies | Deploy your policies |
| **Application.Read.All** | Read application registrations | Validate app exclusions in policies (e.g., exclude Intune apps) |
| **Directory.Read.All** | Read directory objects | Look up users, groups, and directory info |
| **Group.ReadWrite.All** | Create and manage groups | Create CA security groups |
| **User.Read** | Read your profile | Basic sign-in and profile info |

## 🚀 Setup Process

### Step 1: Register Your App

Run the simplified registration script:

```powershell
cd 'c:\MyProjects\AV Policy\CA_Policy_Manager_Web\scripts'
.\Register-EntraApp-Delegated.ps1
```

This script will:
- Create an Azure AD app registration
- Add all 6 delegated permissions
- Give you a Client ID
- (Optional) Automatically update app.py with the Client ID

### Step 2: Update app.py (if not done automatically)

Add your Client ID to `app.py`:

```python
MSAL_CLIENT_ID = os.environ.get('MSAL_CLIENT_ID', 'YOUR-CLIENT-ID-HERE')
```

### Step 3: Start the App

```powershell
cd 'c:\MyProjects\AV Policy\CA_Policy_Manager_Web'
python app.py
```

### Step 4: Sign In & Consent

1. Navigate to `http://localhost:5000`
2. Click **"Sign In with Entra ID"**
3. Sign in with your Azure AD account
4. **Consent screen appears** showing all 6 permissions
5. Click **"Accept"** to grant consent
6. ✅ You're in! Consent is saved for future sign-ins.

## 🔒 Consent Deep Dive

### What is Consent?

When you sign in, Azure AD shows you a **consent screen** listing all permissions the app wants. You review and approve (or deny) these permissions.

### User Consent vs Admin Consent

| Scenario | Consent Type | What It Means |
|----------|--------------|---------------|
| **Regular User** | User Consent | You can consent to permissions that affect only your data |
| **Admin-Level Permissions** | Admin Consent | Some permissions (like Group.ReadWrite.All) may require an admin to approve for the organization |

### Which Permissions Need Admin Consent?

In our app:
- ✅ **User can self-consent**: Policy.Read.All, Policy.ReadWrite.ConditionalAccess, User.Read
- ⚠️ **May need admin**: Application.Read.All, Directory.Read.All, Group.ReadWrite.All

**Good news**: If your Azure AD role is **Global Admin** or **Conditional Access Administrator**, you can self-consent to all these permissions!

### How to Grant Admin Consent (If Needed)

If you're not an admin but need these permissions:

**Option 1: Have an admin pre-approve**

1. Admin goes to Azure Portal → App Registrations → [Your App]
2. API Permissions → Click **"Grant admin consent for [Tenant]"**
3. All users in the tenant can now use the app without individual consent

**Option 2: Admin Consent URL**

Admin clicks this special URL (replace placeholders):
```
https://login.microsoftonline.com/{TENANT_ID}/admins/consent?client_id={CLIENT_ID}
```

## 🎭 User Roles Required

To use this app effectively, your Azure AD account needs one of these roles:

- **Global Administrator** ⭐ (can do everything, consent to all permissions)
- **Conditional Access Administrator** (recommended for CA policy management)
- **Security Administrator** (read-only CA policies, but can create groups)

**Note**: Even with delegated permissions, you can only do what your Azure AD role allows!

## ❓ Troubleshooting

### "Insufficient privileges" error when deploying policies

**Problem**: Your user account doesn't have the right Azure AD role.

**Solution**: Have a Global Admin or Conditional Access Admin:
1. Assign you the **Conditional Access Administrator** role
2. Azure Portal → Users → [Your User] → Assigned roles → Add assignments

### "Need admin approval" on consent screen

**Problem**: Some permissions require admin consent for your organization.

**Solution**: 
- If you're an admin: Click "Consent on behalf of your organization" checkbox
- If not: Share the admin consent URL with your IT admin (see above)

### "AADSTS65001: User or administrator has not consented"

**Problem**: Consent was skipped or permissions changed.

**Solution**: Sign out and sign in again to re-trigger the consent screen.

### App shows "Not authenticated" after sign-in

**Problem**: Token acquisition failed or permissions not granted.

**Solution**:
1. Check browser console for errors (F12)
2. Verify Client ID matches your Azure AD app
3. Ensure Redirect URI is configured: `http://localhost:5000/auth/callback`
4. Clear browser cache and cookies, try again

## 🆚 Delegated vs Application Permissions

### Why We Chose Delegated-Only

| Aspect | Delegated Permissions | Application Permissions |
|--------|----------------------|-------------------------|
| **Who performs actions** | Signed-in user | App itself (no user context) |
| **Consent** | User consents during sign-in | Admin must pre-approve in Azure Portal |
| **Setup complexity** | ✅ Simple - automatic | ❌ Complex - manual configuration |
| **Use case** | Interactive web apps | Background services, automation |
| **User must be signed in** | Yes | No |

**Our philosophy**: Since CA Policy Manager is a web app where someone is always signed in, delegated permissions provide a simpler, more secure experience.

## 🔐 Security Best Practices

1. **Principle of Least Privilege**: We only request permissions actually needed for app functionality.

2. **Review Consent Carefully**: Always read what you're consenting to before clicking "Accept".

3. **Regular Audits**: Periodically review app permissions in Azure Portal.

4. **Production Security**: 
   - Use HTTPS (not HTTP) for redirect URIs
   - Consider Azure AD Conditional Access for the app itself
   - Enable MFA for admin accounts

5. **Credential Safety**:
   - Keep Client ID non-secret (it's public in a web app)
   - Never hardcode secrets in code (we don't use client secrets with delegated flow)
   - Use environment variables for configuration

## 📚 Additional Resources

- [Microsoft Graph Permissions Reference](https://learn.microsoft.com/en-us/graph/permissions-reference)
- [Understanding Consent in Azure AD](https://learn.microsoft.com/en-us/azure/active-directory/develop/application-consent-experience)
- [Delegated vs Application Permissions](https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-permissions-and-consent)

---

**Questions?** Check our [Main Setup Guide](SETUP_ENTRA_AUTH.md) or review the consent screen carefully when you sign in!
