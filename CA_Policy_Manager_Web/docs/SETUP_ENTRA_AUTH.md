# Setting Up Entra ID Sign-In

To enable the "Sign In with Entra ID" feature, you need to register a separate app in Azure Portal for **delegated authentication**.

## Quick Setup (5 minutes)

### Step 1: Register New App in Azure Portal

1. Go to **Azure Portal** → **Microsoft Entra ID** → **App registrations**
2. Click **+ New registration**
3. Enter details:
   - **Name**: `CA Policy Manager - Web (Delegated)`
   - **Supported account types**: `Accounts in this organizational directory only`
   - **Redirect URI**: 
     - Platform: `Web`
     - URI: `http://localhost:5000/auth/callback`
4. Click **Register**

### Step 2: Note the Application (client) ID

After registration, you'll see:
- **Application (client) ID**: Copy this (e.g., `12345678-1234-1234-1234-123456789abc`)

### Step 3: Configure API Permissions

1. In your new app, click **API permissions**
2. Click **+ Add a permission**
3. Select **Microsoft Graph**
4. Select **Delegated permissions** (NOT Application!)
5. Add these permissions:
   - ✅ `Policy.Read.All`
   - ✅ `Policy.ReadWrite.ConditionalAccess`
   - ✅ `User.Read` (should be added by default)
6. Click **Add permissions**
7. Click **Grant admin consent for [Organization]** ⚠️

### Step 4: Configure Authentication Settings

1. Click **Authentication** in the left menu
2. Under **Platform configurations**, find the **Web** platform
3. Ensure redirect URI is: `http://localhost:5000/auth/callback`
4. Under **Implicit grant and hybrid flows**:
   - ✅ Check **ID tokens** (optional, for user info)
5. Click **Save**

### Step 5: Update app.py with Client ID

Edit `app.py` and replace this line:

```python
MSAL_CLIENT_ID = os.environ.get('MSAL_CLIENT_ID', 'YOUR_CLIENT_ID')
```

With your actual Client ID:

```python
MSAL_CLIENT_ID = os.environ.get('MSAL_CLIENT_ID', '12345678-1234-1234-1234-123456789abc')
```

Or set it as an environment variable (recommended):

**PowerShell:**
```powershell
$env:MSAL_CLIENT_ID = "12345678-1234-1234-1234-123456789abc"
```

**Windows CMD:**
```cmd
set MSAL_CLIENT_ID=12345678-1234-1234-1234-123456789abc
```

### Step 6: Restart the Web App

```powershell
# Stop the current app (Ctrl+C in terminal)
# Then restart:
cd "C:\MyProjects\AV Policy\CA_Policy_Manager_Web"
& "C:/MyProjects/AV Policy/.venv/Scripts/python.exe" app.py
```

### Step 7: Test Sign-In

1. Open http://localhost:5000
2. Click **Connect** button
3. Click the **Sign In with Entra ID** card
4. You'll be redirected to Microsoft login
5. Sign in with your Microsoft 365 account
6. Grant permissions when prompted
7. You'll be redirected back to the app with your policies loaded

## How It Works

### Two Authentication Methods

**Method 1: App Credentials (Client Credentials Flow)**
- Uses Client ID + Secret
- Service-to-service authentication
- Good for automation and background tasks
- Requires `Application` permissions in Azure

**Method 2: Sign In with Entra ID (Delegated Flow)** ⭐ NEW!
- User signs in with their Microsoft 365 account
- Acts on behalf of the signed-in user
- Uses `Delegated` permissions
- Better for interactive use
- Users see their own policies

### Security Benefits

**Delegated Authentication:**
- ✅ No sharing of client secrets
- ✅ Users authenticate with their own credentials
- ✅ MFA and Conditional Access policies apply
- ✅ Audit logs show actual user who made changes
- ✅ Respects user's existing permissions

## Production Deployment

### For Internet Access

If deploying to a server accessible over the internet:

1. **Update Redirect URI** in Azure Portal:
   ```
   https://yourdomain.com/auth/callback
   ```

2. **Update MSAL_REDIRECT_URI** in app.py:
   ```python
   MSAL_REDIRECT_URI = 'https://yourdomain.com/auth/callback'
   ```

3. **Enable HTTPS** (required for production):
   - Get SSL certificate
   - Configure reverse proxy (nginx/Apache)
   - Ensure all traffic uses HTTPS

### Multi-Tenant Support

To allow users from other organizations to sign in:

1. **During app registration**, select:
   - "Accounts in any organizational directory (Any Azure AD directory - Multitenant)"

2. **Update Authority** in app.py:
   ```python
   MSAL_AUTHORITY = 'https://login.microsoftonline.com/organizations'  # Already set!
   ```

## Troubleshooting

### Error: "AADSTS50011: The reply URL specified in the request does not match"

**Fix:** Update redirect URI in Azure Portal to match exactly:
- Development: `http://localhost:5000/auth/callback`
- Production: `https://yourdomain.com/auth/callback`

### Error: "Need admin approval"

**Fix:** Admin must grant consent in Azure Portal:
1. Go to App registrations → Your app → API permissions
2. Click "Grant admin consent for [Organization]"

### Error: "AADSTS65001: The user or administrator has not consented"

**Fix:** 
1. Ensure delegated permissions are added (not application)
2. Grant admin consent
3. User must accept consent prompt during first sign-in

### Sign-in works but can't retrieve policies

**Check:**
1. User has appropriate role in Entra ID (Security Administrator, Conditional Access Administrator, or Global Administrator)
2. Delegated permissions are granted (Policy.Read.All, Policy.ReadWrite.ConditionalAccess)
3. Admin consent was granted

## Permissions Comparison

### Application Permissions (Client Credentials)
- ✅ Works without user sign-in
- ✅ Good for automation
- ❌ Requires client secret management
- ❌ All-or-nothing access
- Uses: Background jobs, scheduled tasks

### Delegated Permissions (Sign In with Entra ID)
- ✅ User authenticates themselves
- ✅ Respects user's actual permissions
- ✅ Better audit trail
- ✅ MFA/CA policies apply
- ❌ Requires user interaction
- Uses: Interactive web applications, user-facing tools

## Security Best Practices

1. **Use Delegated Auth for Interactive Use**
   - Let users sign in with their accounts
   - Better security and audit trail

2. **Keep Client Secrets Secure**
   - For app credentials method
   - Use environment variables
   - Rotate regularly

3. **Enable MFA**
   - Require MFA for admin accounts
   - Applies automatically with delegated auth

4. **Review Permissions Regularly**
   - Least privilege principle
   - Remove unused permissions

5. **Monitor Sign-In Logs**
   - Azure Portal → Entra ID → Sign-in logs
   - Review who's accessing the app

## Support

**App Registration Issues:**
- Ensure you're registering in the correct directory
- Verify you have permissions to register apps
- Check that redirect URI matches exactly

**Permission Issues:**
- Admin consent must be granted
- User must have appropriate Azure role
- Wait 5 minutes after granting consent

**Still Not Working?**
Check the PowerShell terminal for detailed error messages from the Flask app.

---

**Enjoy secure, user-friendly Entra ID authentication!** 🎉
