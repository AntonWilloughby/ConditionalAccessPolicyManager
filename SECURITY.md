# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in this project, please report it privately. **Do not open a public GitHub issue.**

### How to Report

- **Email**: Open a GitHub Security Advisory on this repository
- **Response Time**: We aim to respond within 48 hours
- **Disclosure**: We will coordinate disclosure timing with you

## Secure Usage Guidelines

### ⚠️ Critical Security Practices

1. **Never commit credentials**
   - Never commit `.env` files with real credentials
   - Never commit `config.json` files with real tenant IDs
   - Always use `.env.example` and `config.json.template` as templates

2. **Protect your access tokens**
   - Access tokens are stored in session memory only
   - Tokens are never logged or written to disk
   - Clear browser cache if you suspect token exposure

3. **Azure AD Permissions**
   - Use least-privilege principle
   - Review required permissions in setup guides
   - Consider using a dedicated service account

4. **API Keys (AI Features)**
   - Store Azure OpenAI keys in `.env` file only
   - Never log or display API keys
   - Rotate keys if exposed
   - Monitor usage for anomalies

### 🔒 What We Do to Protect You

- Session-based authentication (no persistent storage)
- HTTPS required for production deployments
- Input validation and sanitization
- CSRF protection (configurable)
- No sensitive data logging
- Environment variable isolation

### 🛡️ Best Practices for Deployment

#### Development
```bash
# Use .env file for local development
cp .env.example .env
# Edit .env with your credentials
# NEVER commit .env to git
```

#### Production
```bash
# Use environment variables directly
export MSAL_CLIENT_ID="your-client-id"
export AZURE_OPENAI_API_KEY="your-api-key"
# Or use Azure Key Vault integration
```

### 📋 Security Checklist for Contributors

Before submitting a PR:
- [ ] No hardcoded credentials in code
- [ ] No sensitive data in example files
- [ ] No real tenant IDs or user data in tests
- [ ] Updated `.gitignore` if adding new file types
- [ ] Secrets use environment variables
- [ ] No debugging code that logs sensitive data

### 🚨 What to Do If You Committed Secrets

If you accidentally committed credentials to git:

1. **Immediately rotate the exposed credentials**
   - Change passwords
   - Regenerate API keys
   - Revoke access tokens

2. **Remove from git history**
   ```bash
   # Use BFG Repo-Cleaner or git filter-branch
   # DO NOT just delete and recommit
   ```

3. **Report the incident**
   - Document what was exposed
   - Update security procedures
   - Notify affected parties if needed

### 🔍 Dependency Security

- Dependencies are listed in `requirements.txt`
- Run `pip-audit` regularly to check for vulnerabilities
- Keep dependencies updated
- Review dependency security advisories

```bash
# Check for known vulnerabilities
pip install pip-audit
pip-audit
```

### 📞 Contact

For security concerns, contact: [Open a Security Advisory]

---

**Last Updated**: November 2025
