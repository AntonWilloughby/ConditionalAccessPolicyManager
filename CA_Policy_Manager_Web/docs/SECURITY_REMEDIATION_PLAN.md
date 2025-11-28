# Security Remediation Plan
**CA Policy Manager Web Application**  
**Date:** November 21, 2025  
**Priority:** CRITICAL - Address before production deployment

---

## 🚨 Critical Security Findings

### HIGH RISK Issues (Must Fix Before Production)

#### 1. TLS Verification Disabled (CRITICAL)
**Issue:** All Microsoft Graph API calls use `verify=False`, allowing MITM attacks.

**Impact:**
- Attackers can intercept bearer tokens
- CA policies can be modified without detection
- Complete tenant compromise possible

**Remediation:**
```python
# BEFORE (INSECURE):
response = requests.get(url, headers=headers, verify=False)

# AFTER (SECURE):
response = requests.get(url, headers=headers, verify=True)
```

**Implementation:**
- Remove all `verify=False` parameters
- Add `DISABLE_SSL_VERIFY` env var for dev only (with warnings)
- Default to `verify=True` in all production configs

**Files to Fix:**
- `app.py` (15+ occurrences)
- `ca_policy_manager.py` (10+ occurrences)

---

#### 2. OAuth Flow CSRF Vulnerability (CRITICAL)
**Issue:** Implicit grant flow without state parameter; token fixation possible.

**Impact:**
- Attacker can inject their token into victim's session
- Cross-site request forgery during authentication
- Session hijacking

**Current Flow (INSECURE):**
```
User → Microsoft Login (no state) → Callback → Client-side token → POST to /api/auth/token
```

**Secure Flow (Authorization Code + PKCE):**
```
1. Server generates state + code_verifier (store in session)
2. Redirect to Microsoft with state + code_challenge
3. Microsoft redirects back with code + state
4. Server validates state, exchanges code for token (server-side)
5. Token never exposed to browser
```

**Implementation:**
- Replace implicit flow with auth code + PKCE
- Generate and validate state parameter
- Server-side token acquisition only
- Add nonce for additional replay protection

**Files to Update:**
- `app.py` - `/auth/login` and `/auth/callback` routes
- `templates/auth_callback.html` - remove client-side token handling
- `static/js/main.js` - remove token extraction logic

---

#### 3. No CSRF Protection on API Endpoints (CRITICAL)
**Issue:** All state-changing endpoints lack CSRF tokens.

**Impact:**
- Any website can trigger policy creation/deletion
- Group creation from malicious sites
- File uploads from attacker-controlled pages

**Remediation:**
```python
# Install Flask-WTF
pip install Flask-WTF

# In app.py:
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# Configure cookies
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
```

**Endpoints Requiring Protection:**
- `/api/connect` (POST)
- `/api/policies` (POST)
- `/api/policies/<id>` (PUT, DELETE)
- `/api/templates/deploy` (POST)
- `/api/templates/deploy-all` (POST)
- `/api/groups/create-all` (POST)
- `/api/report/upload` (POST)
- `/api/auth/token` (POST)

---

#### 4. Flask Debug Server in Production (CRITICAL)
**Issue:** `app.run(debug=True)` enables Werkzeug debugger.

**Impact:**
- Remote code execution via debugger console
- Full server compromise
- Environment variable exposure

**Remediation:**
```python
# NEVER in production:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # ❌

# Production deployment:
# Use Gunicorn or Waitress
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Implementation:**
- Set `debug=False` by default
- Create separate `run_dev.py` for development
- Document production WSGI deployment
- Add environment-based config

---

### MEDIUM RISK Issues (Fix Before Public Deployment)

#### 5. Insecure File Upload Handling
**Issue:** No file type validation; arbitrary files stored in web root.

**Current Code:**
```python
filename = secure_filename(file.filename)
filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
file.save(filepath)
```

**Vulnerabilities:**
- Arbitrary file upload (malware persistence)
- No MIME type validation
- Files stored in web root (potential execution)
- No cleanup policy (disk exhaustion)

**Remediation:**
```python
ALLOWED_EXTENSIONS = {'.html', '.xlsx', '.csv'}
ALLOWED_MIMETYPES = {
    'text/html',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/csv'
}

def validate_upload(file):
    # Check extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type {ext} not allowed")
    
    # Check MIME type
    mime = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)
    if mime not in ALLOWED_MIMETYPES:
        raise ValueError(f"MIME type {mime} not allowed")
    
    # Check file size by type
    max_size = 10 * 1024 * 1024  # 10MB for reports
    if file.content_length > max_size:
        raise ValueError("File too large")
    
    return True
```

**Additional Hardening:**
- Store uploads outside web root (`/var/uploads` or `C:\ProgramData\uploads`)
- Add virus scanning integration (Windows Defender API)
- Auto-delete files after 24 hours
- Generate random filenames to prevent overwrites
- Add per-user upload limits

---

#### 6. Insecure Session Token Storage
**Issue:** Access tokens stored in client-side sessions (signed but not encrypted).

**Impact:**
- Token exposure via browser dev tools
- XSS can steal tokens
- Cookie leakage in logs/referrer headers

**Remediation:**

**Option 1: Server-Side Sessions (Recommended)**
```python
# Install Flask-Session + Redis
pip install Flask-Session redis

from flask_session import Session
import redis

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

Session(app)
```

**Option 2: Encrypted Sessions**
```python
# Use cryptography for token encryption
from cryptography.fernet import Fernet

# Generate key once, store in environment
ENCRYPTION_KEY = os.environ['SESSION_ENCRYPTION_KEY']
cipher = Fernet(ENCRYPTION_KEY)

# Encrypt before storing
encrypted_token = cipher.encrypt(access_token.encode())
session['encrypted_token'] = encrypted_token

# Decrypt when needed
access_token = cipher.decrypt(session['encrypted_token']).decode()
```

---

## 📋 Implementation Roadmap

### Phase 1: Critical Fixes (Week 1) ⚠️ URGENT
- [ ] **Day 1-2:** Enable TLS verification globally
  - Remove all `verify=False`
  - Add dev-only override with warnings
  - Test against production Graph API
  
- [ ] **Day 2-3:** Implement CSRF protection
  - Install Flask-WTF
  - Add CSRF tokens to all forms
  - Configure secure cookie settings
  - Update JavaScript to include CSRF tokens in AJAX calls

- [ ] **Day 3-4:** Fix OAuth flow
  - Implement Authorization Code + PKCE
  - Add state parameter generation/validation
  - Move token acquisition server-side
  - Remove client-side token handling

- [ ] **Day 4-5:** Disable debug mode
  - Set `debug=False`
  - Create production config
  - Test with Gunicorn/Waitress
  - Add security headers middleware

### Phase 2: Medium Fixes (Week 2)
- [ ] **Day 6-7:** Harden file uploads
  - Add extension whitelist
  - Implement MIME type validation
  - Move uploads outside web root
  - Add auto-cleanup cron job

- [ ] **Day 8-9:** Secure session storage
  - Implement server-side sessions (Redis)
  - Or add session encryption
  - Rotate session keys
  - Add token expiration handling

### Phase 3: Additional Hardening (Week 3)
- [ ] Add rate limiting (Flask-Limiter)
- [ ] Implement audit logging
- [ ] Add Content Security Policy headers
- [ ] Set up security monitoring
- [ ] Perform penetration testing

---

## 🔧 Configuration Changes

### New Environment Variables Required

```bash
# Production .env file
FLASK_ENV=production
SECRET_KEY=<generate-with-secrets.token_urlsafe(32)>
SESSION_ENCRYPTION_KEY=<generate-with-Fernet.generate_key()>

# Redis for sessions
REDIS_URL=redis://localhost:6379/0

# Azure AD OAuth
MSAL_CLIENT_ID=your-client-id
MSAL_TENANT_ID=your-tenant-id
MSAL_REDIRECT_URI=https://yourdomain.com/auth/callback

# Security flags
ENABLE_HTTPS=true
SESSION_COOKIE_SECURE=true
CSRF_ENABLED=true

# Dev only (NEVER in production)
# DISABLE_SSL_VERIFY=true  # Only for corp proxy testing
```

### New Dependencies
```txt
Flask-WTF>=1.2.0         # CSRF protection
Flask-Session>=0.5.0     # Server-side sessions
redis>=5.0.0             # Session storage
cryptography>=41.0.0     # Token encryption
gunicorn>=21.0.0         # Production WSGI
python-magic>=0.4.27     # MIME type detection
```

---

## 🧪 Testing Checklist

### Before Production Deployment

- [ ] TLS verification enabled (no bypass flags)
- [ ] CSRF tokens present on all forms
- [ ] OAuth flow uses auth code + PKCE
- [ ] State parameter validated on callback
- [ ] Tokens not visible in browser dev tools
- [ ] Debug mode disabled
- [ ] File uploads restricted to allowed types
- [ ] Upload directory outside web root
- [ ] Security headers present (HSTS, CSP, etc.)
- [ ] Rate limiting active on auth endpoints
- [ ] HTTPS enforced (HTTP redirects to HTTPS)
- [ ] Cookie flags set (Secure, HttpOnly, SameSite)
- [ ] Session timeout configured (30 minutes)
- [ ] Audit logging operational

### Penetration Testing Scenarios

1. **MITM Attack:** Intercept Graph API traffic
2. **CSRF Attack:** Trigger policy creation from external site
3. **Token Fixation:** Inject attacker token into victim session
4. **File Upload Attack:** Upload malicious executable
5. **Session Hijacking:** Steal and reuse session cookies
6. **XSS Attack:** Inject scripts to steal tokens
7. **Debug Console:** Attempt to access Werkzeug debugger

---

## 📚 Security Resources

### Microsoft Graph Security
- [OAuth 2.0 Authorization Code Flow](https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)
- [PKCE for Public Clients](https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow#request-an-authorization-code)
- [Conditional Access API Security](https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccesspolicy)

### Flask Security
- [Flask-WTF CSRF Documentation](https://flask-wtf.readthedocs.io/en/stable/csrf.html)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/stable/security/)
- [OWASP Top 10 for Web Applications](https://owasp.org/www-project-top-ten/)

### Deployment Security
- [Gunicorn Deployment](https://docs.gunicorn.org/en/stable/deploy.html)
- [HTTPS with Let's Encrypt](https://letsencrypt.org/getting-started/)
- [Security Headers Guide](https://securityheaders.com/)

---

## ⚠️ Security Warnings

### DO NOT Deploy Before:
1. ✅ TLS verification enabled
2. ✅ CSRF protection implemented
3. ✅ OAuth flow secured (PKCE + state)
4. ✅ Debug mode disabled
5. ✅ File uploads hardened
6. ✅ Sessions secured server-side

### Development Guidelines
- Never commit secrets to Git
- Use environment variables for all credentials
- Test security fixes in isolated environment
- Rotate keys after any suspected compromise
- Monitor Azure AD sign-in logs for anomalies

### Incident Response
If a security breach occurs:
1. Immediately revoke all Azure AD app permissions
2. Rotate all secrets (app secret, session keys)
3. Review Azure AD audit logs for unauthorized changes
4. Notify affected tenants
5. Restore policies from backup if modified

---

## 📞 Contact

**Security Questions:** Review with security team before deployment  
**Microsoft Graph Support:** https://developer.microsoft.com/graph/support  
**Azure Security Center:** https://portal.azure.com/#blade/Microsoft_Azure_Security

---

**Last Updated:** November 21, 2025  
**Next Review:** After Phase 1 completion  
**Status:** 🔴 NOT PRODUCTION READY - Critical fixes required
