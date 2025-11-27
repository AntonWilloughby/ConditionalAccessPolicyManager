# 🚀 Quick Guide: Making Your Repo Public

## ⚠️ CURRENT STATUS: NOT SAFE TO PUBLISH

Your repository is **mostly secure**, but you have **3 critical items** to fix first.

---

## 🔥 DO THIS NOW (15 minutes)

### Step 1: Rotate Your Azure OpenAI API Key (5 min)

**Why:** Your current key is in your local `.env` file. While it's not in git, rotating it ensures safety.

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to: **Azure OpenAI** → **ca-policy-manager-helper** → **Keys and Endpoint**
3. Click **Regenerate Key 1**
4. Copy the new key
5. Update `CA_Policy_Manager_Web/.env`:
   ```env
   AZURE_OPENAI_API_KEY=<paste-new-key-here>
   ```

**Old key will stop working** - this is intentional!

---

### Step 2: Run the Cleanup Script (5 min)

This removes your real Client ID and resource names from documentation:

```powershell
.\prepare-for-public.ps1
```

This will:

- Replace `bcb41e64-e9a8-421c-9331-699dd9041d58` with `<your-client-id-here>`
- Replace `ca-policy-manager-helper` with `<your-resource-name>`
- Create backups in case you need to undo

---

### Step 3: Verify Nothing Sensitive is Tracked (2 min)

Run these commands:

```powershell
# Should only show .env.example
git ls-files | Select-String ".env"

# Should show nothing (or only files you just cleaned)
git status
```

---

### Step 4: Commit Your Changes (3 min)

```powershell
git add .
git commit -m "Security: Remove sensitive data for public release"
git push origin main
```

---

## ✅ NOW YOU CAN MAKE IT PUBLIC

### In GitHub:

1. Go to: **Settings** → **General**
2. Scroll to **Danger Zone**
3. Click **Change visibility** → **Make public**
4. Type your repository name to confirm

---

## 🛡️ Post-Publication Security

### Enable GitHub Secret Scanning:

1. **Settings** → **Security** → **Code security and analysis**
2. Enable **Secret scanning**
3. Enable **Push protection**

This prevents accidental credential commits in the future.

---

## 📋 Verification Checklist

Before clicking "Make Public":

- [ ] Azure OpenAI API key rotated
- [ ] Old key updated in your local `.env`
- [ ] Ran `prepare-for-public.ps1` successfully
- [ ] Reviewed `git diff` (should see placeholder replacements)
- [ ] Committed changes
- [ ] Verified: `git ls-files | Select-String ".env"` shows only `.env.example`
- [ ] Read `PRE_PUBLICATION_SECURITY_REPORT.md`

---

## 🆘 If Something Goes Wrong

### "I accidentally committed my .env file!"

**DON'T PANIC**, but act quickly:

```powershell
# Remove from staging
git reset HEAD CA_Policy_Manager_Web/.env

# Remove from git tracking (keeps local file)
git rm --cached CA_Policy_Manager_Web/.env

# Commit the removal
git commit -m "Remove .env from git tracking"

# Rotate ALL credentials in your .env immediately
```

### "I already pushed real credentials to GitHub!"

1. **IMMEDIATELY rotate all credentials** in Azure Portal
2. Make repo private again if already public
3. Use BFG Repo-Cleaner or `git filter-branch` to remove from history
4. Force push: `git push --force origin main`
5. Rotate credentials AGAIN (assume they were compromised)

---

## 📞 Still Unsure?

**Better safe than sorry!**

- Read the full report: `PRE_PUBLICATION_SECURITY_REPORT.md`
- Test the cleanup first
- Ask for a security review
- Take your time - credentials in public repos = permanent compromise

---

## ⏱️ Time Estimate

- **Total time:** ~15 minutes
- **Difficulty:** Easy (mostly clicking in Azure Portal)
- **Risk if done wrong:** HIGH (exposed credentials)
- **Risk if done right:** NONE (completely safe)

**Take the 15 minutes. It's worth it!** 🔒
