# Quick Setup - Sign In with Entra ID

## Current Status
✅ Your Client ID is already in app.py: `bcb41e64-e9a8-421c-9331-699dd9041d58`

## What You Need To Do

### Step 1: Open Azure Portal
Click this link: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade

### Step 2: Find Your App
Look for an app with Client ID: **bcb41e64-e9a8-421c-9331-699dd9041d58**

**If the app EXISTS:**
- Open it
- Go to "API permissions"
- Check if you have:
  - ✅ Microsoft Graph > Policy.Read.All (Delegated)
  - ✅ Microsoft Graph > Policy.ReadWrite.ConditionalAccess (Delegated)
- If permissions are there but not consented:
  - Click "Grant admin consent for [Your Organization]"
  - Click "Yes"
- Skip to Step 4

**If the app DOES NOT exist:**
- Continue to Step 3

### Step 3: Create New App Registration
1. Click **"+ New registration"**
2. Fill in:
   - **Name:** `CA Policy Manager Web`
   - **Supported account types:** Select "Accounts in this organizational directory only (Single tenant)"
   - **Redirect URI:** 
     - Platform: **Web**
     - URI: `http://localhost:5000/auth/callback`
3. Click **"Register"**
4. On the Overview page, copy the **Application (client) ID**
5. Go back to app.py and replace the CLIENT_ID on line 33 with your new one

### Step 4: Add API Permissions
1. Click **"API permissions"** in the left menu
2. Click **"+ Add a permission"**
3. Click **"Microsoft Graph"**
4. Click **"Delegated permissions"** (NOT Application permissions!)
5. Search and check:
   - ☑️ `Policy.Read.All`
   - ☑️ `Policy.ReadWrite.ConditionalAccess`
6. Click **"Add permissions"**
7. Click **"Grant admin consent for [Your Organization]"**
8. Click **"Yes"**
9. Wait for green checkmarks ✅ to appear

### Step 5: Verify Redirect URI
1. Click **"Authentication"** in the left menu
2. Under "Web" section, verify you have:
   - `http://localhost:5000/auth/callback`
3. If missing, click **"+ Add URI"** and add it

### Step 6: Test It!
1. Restart your Flask app (Ctrl+C, then run it again)
2. Open http://localhost:5000
3. Click **"Connect"**
4. Click **"Sign In with Entra ID"**
5. You should be redirected to Microsoft login
6. Sign in with your work account
7. Accept the consent prompt (first time only)
8. You should be redirected back to the app with your policies!

## Troubleshooting

**Error: "AADSTS700016: Application not found"**
- The CLIENT_ID in app.py doesn't match any app registration
- Follow Step 3 to create a new app and update app.py

**Error: "AADSTS65001: User consent not granted"**
- Admin consent not granted
- Follow Step 4, item 7-9

**Error: "Insufficient privileges"**
- Wrong permission type (Application instead of Delegated)
- Delete the permissions and re-add as **Delegated**

**Nothing happens after clicking "Sign In with Entra ID"**
- Check browser console (F12) for errors
- Check Flask terminal for error messages
- Make sure app.py is running

## Need Help?
Check SETUP_ENTRA_AUTH.md for detailed step-by-step guide with screenshots.
