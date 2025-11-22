# AI Policy Explainer - Setup Guide

## ✨ Feature Overview

The AI Policy Explainer adds an **"AI" button** next to each Conditional Access policy that provides:
- Plain-English explanation of what the policy does
- Who it affects (users/groups)
- When it applies (conditions)
- What happens (grant controls)
- User impact assessment
- Recommendations for improvements

## 🚀 Quick Setup (5 minutes)

### Step 1: Get Azure OpenAI Credentials

You have two options:

#### Option A: Azure OpenAI (Recommended - Enterprise Security)

1. Go to [Azure Portal](https://portal.azure.com)
2. Search for "Azure OpenAI" and create a resource
3. Once created, go to the resource
4. Click **"Keys and Endpoint"** in the left menu
5. Copy:
   - **Endpoint** (e.g., `https://your-resource.openai.azure.com/`)
   - **Key 1** (your API key)
6. Go to **"Model deployments"** → **"Manage Deployments"**
7. Click **"Create new deployment"**
   - Model: `gpt-4o-mini` (cost-effective, fast)
   - Deployment name: `gpt-4o-mini` (or your choice)
8. Copy the **deployment name**

#### Option B: OpenAI (Simpler - No Azure Account Needed)

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create account
3. Click **"Create new secret key"**
4. Copy the API key (starts with `sk-`)

### Step 2: Update .env File

Open `c:\MyProjects\AV Policy\CA_Policy_Manager_Web\.env` and update:

**For Azure OpenAI:**
```bash
# AI Configuration
AI_ENABLED=true
AI_PROVIDER=azure

# Your Azure OpenAI credentials
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=1234567890abcdef1234567890abcdef
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```

**For OpenAI:**
```bash
# AI Configuration
AI_ENABLED=true
AI_PROVIDER=openai

# Your OpenAI API key
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

### Step 3: Restart the Application

```powershell
# Stop the running app (Ctrl+C in terminal)
# Then restart:
cd 'c:\MyProjects\AV Policy\CA_Policy_Manager_Web'
python app.py
```

You should see:
```
✨ AI Assistant initialized (Azure OpenAI - gpt-4o-mini)
```

### Step 4: Test It Out!

1. Go to http://localhost:5000
2. Sign in with your account
3. Click the **Policies** tab
4. Find any policy and click the **"AI" button** (lightbulb icon)
5. Wait 2-5 seconds for the explanation

## 💡 Usage

### The AI Button

Every policy now has three buttons:
- 👁️ **Eye icon** - View raw JSON
- 💡 **Lightbulb icon** - Get AI explanation (NEW!)
- 🗑️ **Trash icon** - Delete policy

### What You'll See

When you click the AI button, you'll get:

**📝 Explanation Card (Blue)**
- Summary of what the policy does
- Who it affects
- When it applies
- What happens

**👥 User Impact Card (Yellow)**
- How users experience this policy
- Daily workflow effects

**💡 Recommendations Card (Green)**
- Security improvements
- Best practices
- Potential issues

## 💰 Cost Estimation

### Azure OpenAI (gpt-4o-mini)
- **Input:** $0.15 per 1M tokens
- **Output:** $0.60 per 1M tokens
- **Per explanation:** ~$0.0005 (less than a penny!)
- **1,000 explanations:** ~$0.50

### OpenAI (gpt-4o-mini)
- Same pricing as Azure OpenAI
- No Azure account needed
- Slightly higher latency

### Example Monthly Costs
- 10 policies/day: **~$1.50/month**
- 50 policies/day: **~$7.50/month**
- 100 policies/day: **~$15/month**

## 🔧 Troubleshooting

### "AI features are not enabled"
**Problem:** AI button shows setup message

**Solutions:**
1. Check `.env` file has `AI_ENABLED=true`
2. Verify API credentials are correct
3. Restart Flask app (`Ctrl+C` then `python app.py`)
4. Check console output for error messages

### "Failed to explain policy"
**Problem:** Error when clicking AI button

**Solutions:**
1. Check Azure OpenAI resource is deployed
2. Verify deployment name matches `.env`
3. Check API key is valid (not expired)
4. Ensure you have quota remaining in Azure

### Slow Responses (10+ seconds)
**Problem:** AI takes too long

**Solutions:**
- First request is always slower (model initialization)
- Check your internet connection
- Azure OpenAI: Verify region is close to you
- Consider using `gpt-3.5-turbo` for faster responses

### Import Error: "No module named 'openai'"
**Problem:** Python can't find openai package

**Solution:**
```powershell
pip install openai==1.12.0
```

## 🔒 Security Notes

### Azure OpenAI vs OpenAI
- **Azure OpenAI:** Data stays in your Azure tenant, GDPR compliant, no training on your data
- **OpenAI:** Data sent to OpenAI servers, covered by OpenAI's data policy

### Data Privacy
- Policy JSON is sent to AI service for analysis
- No data is stored by AI service (single request/response)
- API keys are stored in `.env` (never committed to Git)

### For Air-Gapped Environments
Use local model option (see Advanced Setup below)

## 📊 Advanced Setup

### Local Models (Air-Gapped/Offline)

For environments without internet access:

1. **Install Ollama:**
   ```powershell
   winget install Ollama.Ollama
   ```

2. **Download Model:**
   ```powershell
   ollama pull phi3
   ```

3. **Update .env:**
   ```bash
   AI_ENABLED=true
   AI_PROVIDER=local
   LOCAL_MODEL=phi3
   ```

4. **Install Python client:**
   ```powershell
   pip install ollama
   ```

**Pros:** Free, runs locally, no API costs
**Cons:** Slower (5-10s), requires 4GB+ RAM, less accurate than GPT-4

## 🎯 What's Next?

Future AI features you can expect:
- 🔍 **Policy Conflict Detector** - Find overlapping/contradicting policies
- 📝 **Natural Language Policy Creator** - "Block guests from SharePoint" → Creates policy
- 📊 **Smart Report Analysis** - AI-enhanced Zero Trust recommendations
- 🔧 **Policy Optimizer** - Suggest ways to consolidate policies
- 🚨 **Security Risk Scanner** - Identify vulnerabilities in policy setup

## 📞 Support

If you encounter issues:

1. Check Flask console output for error messages
2. Verify API credentials in Azure Portal
3. Test API key with:
   ```powershell
   curl https://your-resource.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-02-15 `
     -H "api-key: YOUR_API_KEY" `
     -H "Content-Type: application/json" `
     -d '{"messages":[{"role":"user","content":"test"}],"max_tokens":10}'
   ```

## ✅ Ready to Use!

You're all set! The AI Policy Explainer is now active. 

**Current Status:**
- ✅ Code deployed
- ✅ Package installed (openai)
- ⏳ **Waiting for your Azure OpenAI credentials**
- ⏳ Restart app after updating .env

Once you add your credentials and restart, you'll see:
```
✨ AI Assistant initialized (Azure OpenAI - gpt-4o-mini)
```

Then click any policy's AI button and enjoy instant explanations! 🎉
