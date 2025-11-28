# Test Plan: Deploy to Azure Button with Automatic Code Deployment

**Date:** November 28, 2025
**Tester:** ******\_******
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Completed

---

## 🎯 Test Objective

Verify that the "Deploy to Azure" button now automatically deploys application code from GitHub without requiring manual code deployment steps.

---

## ✅ Pre-Test Checklist

- [ ] Azure subscription available with credit/free tier
- [ ] Logged into Azure Portal
- [ ] Azure CLI installed (for validation script)
- [ ] PowerShell 5.1+ or PowerShell Core 7+

---

## 📝 Test Steps

### Test 1: Basic Deployment (Free Tier)

**Expected Duration:** 15-20 minutes

#### Step 1.1: Click Deploy Button

- [ ] Open: https://github.com/AntonWilloughby/ConditionalAccessPolicyManager
- [ ] Locate "Deploy to Azure" button in README
- [ ] Click the button
- [ ] Azure Portal opens with custom deployment template

**Expected Result:** ✅ Template loads with parameter form

#### Step 1.2: Fill Parameters

- [ ] **Subscription:** Select your Azure subscription
- [ ] **Resource Group:** Create new: `ca-test-deployment-001`
- [ ] **Region:** Select `East US 2`
- [ ] **Web App Name:** `ca-test-app-001` (must be globally unique)
- [ ] **OpenAI Resource Name:** `ca-test-openai-001` (must be globally unique)
- [ ] **App Service Plan SKU:** `F1` (Free tier)
- [ ] **Model Capacity:** `30` (default)
- [ ] **MSAL Client ID:** Leave empty (default)
- [ ] **MSAL Tenant ID:** `organizations` (default)

**Expected Result:** ✅ All parameters filled, validation passes

#### Step 1.3: Deploy Resources

- [ ] Click **Review + Create**
- [ ] Review deployment details
- [ ] Click **Create**
- [ ] Wait for deployment to complete

**Expected Duration:** 5-8 minutes

**Expected Result:** ✅ Deployment succeeds, shows outputs

#### Step 1.4: Review Deployment Outputs

- [ ] Deployment completes successfully
- [ ] Click **Outputs** tab
- [ ] Note the values:
  - `webAppUrl`: `https://ca-test-app-001.azurewebsites.net`
  - `webAppName`: `ca-test-app-001`
  - `openAIEndpoint`: `https://ca-test-openai-001.openai.azure.com/`
  - `deploymentName`: `gpt-4o-mini`
  - `nextSteps`: (long text with instructions)

**Expected Result:** ✅ All outputs present and correct

#### Step 1.5: Monitor Code Deployment

- [ ] Open: `https://ca-test-app-001.scm.azurewebsites.net/api/deployments`
- [ ] Should see deployment in progress or completed
- [ ] Wait for deployment status: "Success"

**Expected Duration:** 5-10 minutes

**Expected Result:** ✅ Code deployment completes successfully

**Screenshot:** 📸 Deployment status page

#### Step 1.6: Verify App is Deployed

- [ ] Open: `https://ca-test-app-001.azurewebsites.net`
- [ ] Page loads (may take 30-60 seconds first time)
- [ ] **Should NOT see:** "Your App Service app is up and running" (default page)
- [ ] **Should see:** CA Policy Manager login page or interface

**Expected Result:** ✅ Application code is deployed and running

**Screenshot:** 📸 Landing page

#### Step 1.7: Check Environment Variables

- [ ] Azure Portal → ca-test-app-001 → Configuration → Application settings
- [ ] Verify these settings exist:
  - [ ] `SECRET_KEY` (value present, non-empty)
  - [ ] `AZURE_OPENAI_ENDPOINT` (matches openAIEndpoint output)
  - [ ] `AZURE_OPENAI_API_KEY` (value present, non-empty)
  - [ ] `AZURE_OPENAI_DEPLOYMENT` = `gpt-4o-mini`
  - [ ] `MSAL_CLIENT_ID` (empty or has value)
  - [ ] `DEMO_MODE` = `false`
  - [ ] `SCM_DO_BUILD_DURING_DEPLOYMENT` = `true`
  - [ ] `ENABLE_ORYX_BUILD` = `true`

**Expected Result:** ✅ All required settings configured automatically

#### Step 1.8: Enable Demo Mode

```powershell
az webapp config appsettings set `
  --name ca-test-app-001 `
  --resource-group ca-test-deployment-001 `
  --settings DEMO_MODE=true

az webapp restart `
  --name ca-test-app-001 `
  --resource-group ca-test-deployment-001
```

- [ ] Commands execute successfully
- [ ] Wait 30 seconds for restart

**Expected Result:** ✅ App restarted with DEMO_MODE enabled

#### Step 1.9: Test Demo Mode

- [ ] Open: `https://ca-test-app-001.azurewebsites.net`
- [ ] Page loads showing sample data
- [ ] Navigation works
- [ ] No authentication required

**Expected Result:** ✅ App works in demo mode

**Screenshot:** 📸 Demo mode working

#### Step 1.10: Run Validation Script

```powershell
cd "C:\Github\CA Policy Manager Tool"
.\validate-deployment.ps1 `
  -WebAppName "ca-test-app-001" `
  -ResourceGroup "ca-test-deployment-001"
```

- [ ] Script runs successfully
- [ ] Review output:
  - [ ] ✅ Success count > 5
  - [ ] ⚠️ Warnings count (expected: MSAL_CLIENT_ID not set)
  - [ ] ❌ Issues count = 0

**Expected Result:** ✅ No critical issues, only expected warnings

**Screenshot:** 📸 Validation output

---

### Test 2: Paid Tier Deployment (B1)

**Expected Duration:** 15-20 minutes

Repeat Test 1 with these changes:

- [ ] **Resource Group:** Create new: `ca-test-deployment-002`
- [ ] **Web App Name:** `ca-test-app-002`
- [ ] **OpenAI Resource Name:** `ca-test-openai-002`
- [ ] **App Service Plan SKU:** `B1` (Basic tier - $13/month)

**Additional Checks:**

- [ ] Verify `alwaysOn` setting = `true` in Configuration
- [ ] App starts faster (no cold start delay)
- [ ] Performance is better than F1 tier

---

### Test 3: With Azure AD Authentication

**Expected Duration:** 20-25 minutes

Starting from Test 1 deployment (ca-test-app-001):

#### Step 3.1: Create App Registration

- [ ] Azure Portal → Azure Active Directory → App registrations
- [ ] Click **New registration**
- [ ] **Name:** `CA Policy Manager Test`
- [ ] **Supported account types:** Accounts in any organizational directory (Multitenant)
- [ ] **Redirect URI:**
  - Platform: Web
  - URL: `https://ca-test-app-001.azurewebsites.net/auth/callback`
- [ ] Click **Register**

**Expected Result:** ✅ App registration created

#### Step 3.2: Enable Implicit Flow

- [ ] App registration → Authentication
- [ ] Scroll to "Implicit grant and hybrid flows"
- [ ] ✅ Check **ID tokens**
- [ ] ✅ Check **Access tokens**
- [ ] Click **Save**

**Expected Result:** ✅ Implicit flow enabled

#### Step 3.3: Add API Permissions

- [ ] App registration → API permissions
- [ ] Click **Add a permission**
- [ ] **Microsoft Graph** → **Delegated permissions**
- [ ] Add:
  - [ ] `User.Read`
  - [ ] `Policy.Read.All`
  - [ ] `Policy.ReadWrite.ConditionalAccess`
  - [ ] `Directory.Read.All`
- [ ] Click **Add permissions**
- [ ] Click **Grant admin consent for [tenant]**

**Expected Result:** ✅ Permissions granted

#### Step 3.4: Configure App Service

- [ ] Copy **Application (client) ID** from app registration
- [ ] Azure Portal → ca-test-app-001 → Configuration
- [ ] Update settings:
  - `MSAL_CLIENT_ID` = `<your-client-id>`
  - `DEMO_MODE` = `false`
- [ ] Click **Save** → **Continue**
- [ ] Click **Restart** (Overview page)

**Expected Result:** ✅ Settings updated, app restarted

#### Step 3.5: Test Authentication

- [ ] Open: `https://ca-test-app-001.azurewebsites.net`
- [ ] Click **Connect** button
- [ ] Redirected to Microsoft login
- [ ] Sign in with Azure AD account
- [ ] Consent to permissions (if prompted)
- [ ] Redirected back to app

**Expected Result:** ✅ Successfully authenticated, user info displayed

**Screenshot:** 📸 Authenticated view with user info card

#### Step 3.6: Test Policy Management

- [ ] View existing policies (if any)
- [ ] Try creating a test policy
- [ ] Verify policy appears in list

**Expected Result:** ✅ Policy management works

---

## 🧹 Cleanup

After testing completes:

```powershell
# Delete test resource groups
az group delete --name ca-test-deployment-001 --yes --no-wait
az group delete --name ca-test-deployment-002 --yes --no-wait

# Delete test app registration
# Azure Portal → Azure AD → App registrations → Delete "CA Policy Manager Test"
```

- [ ] Resource group 001 deleted
- [ ] Resource group 002 deleted
- [ ] App registration deleted

---

## 📊 Test Results Summary

| Test                    | Status            | Duration   | Issues Found |
| ----------------------- | ----------------- | ---------- | ------------ |
| Test 1: Free Tier (F1)  | ⬜ Pass / ⬜ Fail | \_\_\_ min |              |
| Test 2: Basic Tier (B1) | ⬜ Pass / ⬜ Fail | \_\_\_ min |              |
| Test 3: With Auth       | ⬜ Pass / ⬜ Fail | \_\_\_ min |              |

---

## 🐛 Issues Found

### Issue #1

- **Description:**
- **Severity:** ⬜ Critical / ⬜ High / ⬜ Medium / ⬜ Low
- **Steps to Reproduce:**
- **Expected:**
- **Actual:**
- **Screenshot:**

### Issue #2

- **Description:**
- **Severity:** ⬜ Critical / ⬜ High / ⬜ Medium / ⬜ Low
- **Steps to Reproduce:**
- **Expected:**
- **Actual:**
- **Screenshot:**

---

## ✅ Final Approval

- [ ] All tests passed
- [ ] No critical issues found
- [ ] Documentation accurate
- [ ] Ready for production use

**Tester Signature:** ******\_******
**Date:** ******\_******

---

## 📝 Notes

_Add any additional observations or comments here_
