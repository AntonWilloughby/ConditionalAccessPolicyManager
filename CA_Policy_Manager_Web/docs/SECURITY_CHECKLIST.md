# Security Checklist for Production Deployment

## ⚠️ CRITICAL - Must Complete Before Production

### Authentication & Authorization
- [ ] OAuth flow uses Authorization Code + PKCE (not implicit grant)
- [ ] State parameter generated and validated on callback
- [ ] Nonce parameter included for replay protection
- [ ] Token acquisition happens server-side only
- [ ] Access tokens never sent to client browser
- [ ] Session tokens stored server-side (Redis/encrypted)
- [ ] Session timeout set to 30 minutes maximum
- [ ] Automatic session renewal implemented

### CSRF Protection
- [ ] Flask-WTF or Flask-SeaSurf installed and configured
- [ ] CSRF tokens on all POST/PUT/PATCH/DELETE endpoints
- [ ] JavaScript updated to include CSRF tokens in AJAX calls
- [ ] Cookie SameSite=Strict configured
- [ ] Double-submit cookie pattern implemented (alternative)

### TLS/SSL Security
- [ ] All `verify=False` removed from code
- [ ] TLS verification enabled for all Graph API calls
- [ ] HTTPS enforced (HTTP redirects to HTTPS)
- [ ] HSTS header configured (Strict-Transport-Security)
- [ ] Valid SSL certificate installed
- [ ] Certificate expiration monitoring enabled

### Server Configuration
- [ ] Flask debug mode disabled (`debug=False`)
- [ ] Werkzeug debugger not accessible
- [ ] Production WSGI server configured (Gunicorn/Waitress)
- [ ] Multiple worker processes configured
- [ ] Request timeout limits set
- [ ] Reverse proxy configured (Nginx/Apache)
- [ ] Rate limiting enabled on auth endpoints

### Session Security
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `SESSION_COOKIE_HTTPONLY = True`
- [ ] `SESSION_COOKIE_SAMESITE = 'Strict'`
- [ ] Secret key loaded from environment (not hardcoded)
- [ ] Secret key rotated regularly
- [ ] Session encryption key separate from signing key

### File Upload Security
- [ ] File extension whitelist enforced (.html, .xlsx only)
- [ ] MIME type validation implemented
- [ ] File size limits enforced (10MB max)
- [ ] Upload directory outside web root
- [ ] Uploaded files scanned for malware
- [ ] Auto-cleanup job configured (24 hour retention)
- [ ] Random filenames generated to prevent overwrites
- [ ] Per-user upload rate limiting

### API Security
- [ ] Rate limiting on all API endpoints
- [ ] Input validation on all parameters
- [ ] SQL injection protection (parameterized queries)
- [ ] XSS protection (output encoding)
- [ ] JSON response Content-Type headers correct
- [ ] API versioning strategy defined
- [ ] Error messages don't leak sensitive info

### Security Headers
- [ ] Content-Security-Policy configured
- [ ] X-Frame-Options: DENY
- [ ] X-Content-Type-Options: nosniff
- [ ] Referrer-Policy: strict-origin-when-cross-origin
- [ ] Permissions-Policy configured
- [ ] CORS properly configured (if needed)

### Secrets Management
- [ ] All secrets in environment variables (not code)
- [ ] .env file not in Git repository
- [ ] Azure Key Vault integration (for production)
- [ ] Secrets rotation policy defined
- [ ] No secrets in logs or error messages
- [ ] Database credentials encrypted at rest

### Logging & Monitoring
- [ ] Audit logging for all CA policy changes
- [ ] Authentication events logged
- [ ] Failed login attempts monitored
- [ ] Suspicious activity alerts configured
- [ ] Log retention policy defined
- [ ] Logs secured (no token leakage)
- [ ] Azure AD sign-in logs reviewed regularly

### Network Security
- [ ] Firewall rules configured
- [ ] Only required ports open (443, maybe 22)
- [ ] Internal network segmentation
- [ ] VPN or private link for Azure services
- [ ] DDoS protection enabled
- [ ] IP allowlisting for admin functions

### Azure AD Configuration
- [ ] App registration permissions minimal (least privilege)
- [ ] Admin consent granted by Global Admin
- [ ] Redirect URIs explicitly configured
- [ ] App secret expiration monitored
- [ ] Conditional Access policies applied to app
- [ ] MFA required for admin users
- [ ] Privileged Identity Management enabled

### Backup & Recovery
- [ ] Policy backup mechanism tested
- [ ] Disaster recovery plan documented
- [ ] Backup encryption configured
- [ ] Recovery time objective (RTO) defined
- [ ] Recovery point objective (RPO) defined
- [ ] Backup restoration tested

### Compliance & Documentation
- [ ] Security documentation complete
- [ ] Deployment runbook created
- [ ] Incident response plan documented
- [ ] Change management process defined
- [ ] Security review conducted
- [ ] Penetration testing completed
- [ ] Vulnerability scan performed

## 🧪 Security Testing

### Manual Tests to Perform

#### 1. CSRF Attack Test
```bash
# Create malicious HTML page
<form action="https://yourapp.com/api/policies" method="POST">
  <input name="displayName" value="Malicious Policy">
</form>
<script>document.forms[0].submit();</script>

# Expected: Request blocked with 403 CSRF token missing
```

#### 2. Token Exposure Test
```javascript
// Open browser dev tools → Application → Cookies
// Expected: No access_token visible in cookies
// Expected: Only opaque session ID present
```

#### 3. Debug Console Access Test
```bash
# Try to access debug console
curl https://yourapp.com/console

# Expected: 404 Not Found (debug disabled)
```

#### 4. File Upload Attack Test
```bash
# Try uploading executable
curl -X POST https://yourapp.com/api/report/upload \
  -F "file=@malware.exe" \
  -H "Cookie: session=..."

# Expected: 400 Bad Request (file type not allowed)
```

#### 5. MITM Test
```bash
# Use mitmproxy to intercept traffic
mitmproxy -p 8080

# Configure proxy and test
# Expected: TLS verification fails, no traffic captured
```

#### 6. OAuth State Bypass Test
```bash
# Modify state parameter in callback URL
https://yourapp.com/auth/callback?code=...&state=WRONG_STATE

# Expected: 400 Bad Request (state validation failed)
```

### Automated Security Scans

```bash
# Run OWASP ZAP scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://yourapp.com

# Run Bandit (Python security linter)
bandit -r . -ll

# Run Safety (dependency vulnerability check)
safety check --json

# Run Trivy (container scan if Dockerized)
trivy image yourapp:latest
```

## 📊 Security Metrics to Track

### Pre-Production
- [ ] Zero HIGH/CRITICAL vulnerabilities in dependencies
- [ ] Zero TLS verification bypasses in code
- [ ] 100% of endpoints have CSRF protection
- [ ] All security tests passing
- [ ] Penetration test report reviewed

### Production Monitoring
- [ ] Failed authentication rate < 5%
- [ ] Session hijacking attempts = 0
- [ ] Suspicious file uploads = 0
- [ ] Rate limit violations logged
- [ ] Certificate expires in > 30 days

## 🚨 Go/No-Go Decision

### STOP Deployment If:
- ❌ Any CRITICAL vulnerability unresolved
- ❌ TLS verification disabled anywhere
- ❌ Debug mode still enabled
- ❌ CSRF protection not implemented
- ❌ OAuth flow not secured (PKCE + state)
- ❌ Tokens stored client-side
- ❌ Security testing not completed

### Proceed with Deployment If:
- ✅ All CRITICAL items checked above
- ✅ Security team sign-off received
- ✅ Penetration testing completed
- ✅ Incident response plan ready
- ✅ Rollback procedure tested
- ✅ Monitoring alerts configured

---

**Last Updated:** November 21, 2025  
**Approved By:** [Security Team Lead]  
**Next Review:** [Date after Phase 1]

**Status:** 🔴 NOT READY FOR PRODUCTION
