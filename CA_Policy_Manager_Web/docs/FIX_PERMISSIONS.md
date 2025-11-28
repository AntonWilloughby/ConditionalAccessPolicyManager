# Fix: 401 Unauthorized Error

## Problem
After successfully authenticating, you see:
```
❌ Error listing policies: 401 Client Error: Unauthorized
```

## Cause
Your Azure App Registration is **missing required API permissions** to read/write Conditional Access policies.

## Solution: Add API Permissions

### Step 1: Open Azure Portal
1. Go to https://portal.azure.com
2. Navigate to **Azure Active Directory** (or **Microsoft Entra ID**)
3. Click **App registrations** in the left menu
4. Find and click your app (Client ID: `bcb41e64-e9a8-421c-9331-699dd9041d58`)

### Step 2: Add API Permissions
1. In your app, click **API permissions** in the left menu
2. Click **+ Add a permission**
3. Select **Microsoft Graph**
4. Select **Application permissions** (NOT Delegated)
5. Search for and add these permissions:
   - ✅ **Policy.Read.All**
   - ✅ **Policy.ReadWrite.ConditionalAccess**
   - ✅ **Application.Read.All** (optional, for better error messages)
6. Click **Add permissions**

### Step 3: Grant Admin Consent
⚠️ **Critical Step** - Permissions won't work without this!

1. Still in **API permissions**, click the **Grant admin consent for [Your Organization]** button
2. Click **Yes** to confirm
3. Wait for the green checkmarks to appear next to each permission

### Step 4: Verify Permissions
Your API permissions should show:
```
✅ Policy.Read.All                          Application  ✓ Granted
✅ Policy.ReadWrite.ConditionalAccess      Application  ✓ Granted
```

### Step 5: Wait and Retry
1. **Wait 2-5 minutes** for permissions to propagate
2. **Refresh** your web app (http://localhost:5000)
3. Click **Connect** again
4. Enter credentials and connect

## Alternative: Use Existing Working Credentials

If the desktop GUI app (`ca_policy_manager_gui.py`) works, you can use the same `config.json` credentials because they already have the correct permissions.

## Still Not Working?

### Check Permission Status
In Azure Portal → App registrations → Your app → API permissions:
- All permissions should show **"Granted for [Organization]"**
- Green checkmarks should be visible
- Status column should say **"Granted"**

### Clear Browser Cache
Your browser might be caching the old authentication token:
1. Press **Ctrl+Shift+Delete**
2. Clear cookies and cache
3. Refresh the page
4. Try connecting again

### Regenerate Client Secret
If the secret is old or compromised:
1. Azure Portal → App registrations → Your app
2. **Certificates & secrets** → Client secrets
3. Click **+ New client secret**
4. Copy the new secret value
5. Update your credentials in the web app

### Check Application Type
Your app registration must be:
- **Application (client) ID**: Shows your Client ID
- **Supported account types**: Should allow your organization
- **Authentication**: May need platform configurations

## What These Permissions Do

### Policy.Read.All
- Read all Conditional Access policies
- Required for: Listing policies, viewing policy details

### Policy.ReadWrite.ConditionalAccess  
- Create, update, and delete CA policies
- Required for: Deploying templates, creating policies, bulk delete

### Why Application Permissions?
The web app uses **Client Credentials Flow** (app-to-app authentication), not user delegation. This requires **Application permissions**, not Delegated permissions.

## Security Note

After adding these permissions, your app has **powerful capabilities**:
- ✅ Read all CA policies
- ✅ Create new policies
- ✅ Modify existing policies
- ✅ Delete policies

**Recommendations**:
1. Protect the Client Secret carefully
2. Don't share credentials publicly
3. Consider creating separate app registrations for different environments (dev/test/prod)
4. Review who has access to the app registration in Azure Portal
5. Rotate client secrets regularly (every 90 days)

## Quick Reference: Azure Portal Path

```
Azure Portal
  └─ Microsoft Entra ID (or Azure Active Directory)
      └─ App registrations
          └─ [Your App]
              └─ API permissions
                  └─ Add a permission
                      └─ Microsoft Graph
                          └─ Application permissions
                              └─ Policy.Read.All ✓
                              └─ Policy.ReadWrite.ConditionalAccess ✓
                          └─ Grant admin consent ⚠️ (REQUIRED!)
```

## Need Help?

1. Check Azure Portal for permission status
2. Verify you have admin rights to grant consent
3. Wait 5 minutes after granting consent
4. Check the PowerShell terminal for detailed error messages
5. Verify the Client ID and Tenant ID are correct

---

Once permissions are properly configured, the web app will work exactly like the desktop version! 🎉
