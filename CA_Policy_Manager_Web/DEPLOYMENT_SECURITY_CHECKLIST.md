# Deployment Security Checklist

**Document Version**: 1.0
**Last Updated**: November 22, 2025
**Status**: Pre-Deployment Review Required

---

## Critical Security Fixes Implemented

This document confirms that the following 7 critical security issues have been implemented:

### ✅ 1. Debug Mode Removed

- **Status**: FIXED
- **Change**: `app.py` line 1274: Debug mode now controlled by `FLASK_ENV` environment variable
- **Verification**:
  ```bash
  FLASK_ENV=production python app.py  # Runs without debug
  FLASK_ENV=development python app.py # Runs with debug
  ```
- **Production**: Use gunicorn: `gunicorn --workers 4 --bind 0.0.0.0:8000 app:app`

### ✅ 2. Hardcoded Credentials Removed

- **Status**: FIXED
- **Changes**:
  - Removed default `MSAL_CLIENT_ID` from `config.py`
  - Added validation for required environment variables: `MSAL_CLIENT_ID`, `MSAL_CLIENT_SECRET`, `SECRET_KEY`
  - Application fails to start if required credentials not provided
- **Verification**:
  ```bash
  python app.py  # Will fail: "MSAL_CLIENT_ID environment variable is required"
  MSAL_CLIENT_ID=test MSAL_CLIENT_SECRET=test SECRET_KEY=test python app.py  # Works
  ```

### ✅ 3. SSL Verification Defaults Fixed

- **Status**: FIXED
- **Changes**:
  - Development config now defaults to `VERIFY_SSL=true`
  - SSL verification only disabled when explicitly set in environment
  - Added warnings when disabled
  - Guidance for corporate proxies documented
- **Verification**:
  ```bash
  VERIFY_SSL=false python app.py  # Shows warning about SSL disabled
  python app.py  # Uses VERIFY_SSL=true (secure)
  ```

### ✅ 4. Session Storage for Production

- **Status**: FIXED
- **Implementation**:
  - New `session_manager.py` with Redis support
  - Automatic fallback to in-memory for development
  - Session data properly stored per-user
- **Verification**:

  ```bash
  # Development (in-memory)
  python app.py  # Uses in-memory sessions

  # Production (Redis)
  REDIS_URL=redis://myredis:6379 python app.py  # Uses Redis
  ```

### ✅ 5. Error Responses Sanitized

- **Status**: FIXED
- **Changes**:
  - Added centralized error handling
  - API responses no longer expose sensitive error details
  - Full errors logged server-side for debugging
  - Safe error messages returned to client
- **Example**:
  ```python
  # Before: Error included response.text with sensitive data
  # After: Generic "Operation failed" with error_type for debugging
  ```

### ✅ 6. CSRF Protection Enabled

- **Status**: FIXED
- **Changes**:
  - Added `flask-wtf` dependency
  - `CSRFProtect` initialized in app
  - Production config has `WTF_CSRF_ENABLED=True`
  - Development config allows override for testing
- **Verification**: All forms now include CSRF tokens

### ✅ 7. Security Headers Added

- **Status**: FIXED
- **Implementation**:
  - `@app.after_request` middleware added
  - Headers configured:
    - `X-Content-Type-Options: nosniff`
    - `X-Frame-Options: SAMEORIGIN`
    - `Strict-Transport-Security: max-age=31536000`
    - `Content-Security-Policy` with strict directives
    - `Referrer-Policy: strict-origin-when-cross-origin`

---

## Pre-Deployment Verification Checklist

### Environment Configuration

- [ ] All credentials in environment variables (no hardcoded values)
- [ ] `.env` file created locally from `.env.example`
- [ ] `.env` is in `.gitignore` (verified)
- [ ] `SECRET_KEY` generated: `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] `MSAL_CLIENT_ID` obtained from Azure App Registrations
- [ ] `MSAL_CLIENT_SECRET` stored securely (NOT in version control)
- [ ] `.gitignore` blocks: `.env`, `*.secret`, `*.key`

### Code Security Verification

- [ ] No `debug=True` in production code (use env var instead)
- [ ] No print statements with sensitive data
- [ ] All API endpoints return safe error messages
- [ ] File uploads validated (size, type, MIME)
- [ ] Session data stored with Redis or validated fallback
- [ ] SSL verification defaults to `True`
- [ ] CSRF protection enabled in production

### Dependencies

- [ ] `requirements.txt` updated with all security packages:
  - `flask-wtf==1.2.1` (CSRF protection)
  - `redis==5.0.0` (Session storage)
  - `flask-session==0.5.0` (Session management)
  - `flask-limiter==3.5.0` (Rate limiting)
  - `gunicorn==21.2.0` (Production WSGI)
- [ ] All dependencies pinned to specific versions
- [ ] Run: `pip install -r requirements.txt`

### Authentication & OAuth

- [ ] OAuth uses authorization code flow (not implicit grant)
- [ ] Tokens have expiration handling
- [ ] HTTPS enforced in production
- [ ] Redirect URI matches Azure App Registration configuration
- [ ] State parameter validates CSRF

### Database & Storage

- [ ] Session data configured for Redis in production
- [ ] File uploads stored in `data/uploads/` with proper permissions
- [ ] Uploaded files scanned for malware (optional)
- [ ] No sensitive data stored in session cookies

### Monitoring & Logging

- [ ] Logging configured to file or monitoring system
- [ ] Error tracking enabled (Application Insights, Sentry, etc.)
- [ ] Audit logs recorded for policy changes
- [ ] No sensitive data logged (tokens, secrets, credentials)
- [ ] Log retention policy defined

### Azure App Service Configuration

- [ ] Application Settings configured:
  ```
  FLASK_ENV=production
  SECRET_KEY=<generated-64-char-hex>
  MSAL_CLIENT_ID=<from-azure-portal>
  MSAL_CLIENT_SECRET=<from-azure-portal-application-secrets>
  REDIS_URL=redis://<your-redis>.redis.cache.windows.net:6380?ssl=True
  ```
- [ ] HTTPS enforced (HTTPS Only = ON)
- [ ] Startup command set: `gunicorn --workers 4 --bind 0.0.0.0:8000 app:app`
- [ ] Always On = ON (for continuous availability)
- [ ] App Service Plan >= B2 (for production)

### Testing Before Deployment

- [ ] Local testing with `.env` file works
- [ ] Run test suite: `pytest tests/` (if available)
- [ ] Manual testing of:
  - [ ] Authentication flow
  - [ ] Policy CRUD operations
  - [ ] File upload with validation
  - [ ] Error handling (no stack traces exposed)
  - [ ] Session timeout and refresh
  - [ ] HTTPS redirect works
  - [ ] Security headers present (check with browser dev tools)

### Post-Deployment Verification

- [ ] Application starts without errors
- [ ] Health check endpoint responds: `/api/health`
- [ ] Authentication redirects to login properly
- [ ] Can create/read/update/delete policies
- [ ] HTTPS certificate is valid and not expired
- [ ] Security headers present in responses (use online checker)
- [ ] No console errors in browser developer tools
- [ ] Logs show normal operation (no ERROR level messages)
- [ ] Session persists across page reloads (if Redis configured)

### Security Scanning

- [ ] Run dependency check: `safety check` (or pip-audit)
- [ ] Static code analysis: `pylint app.py` or `flake8`
- [ ] No hardcoded secrets detected: `git log -p | grep -i "secret\|password\|key"`
- [ ] Verify `.gitignore` is working: `git status`

---

## Security Headers Verification

Use online tool or browser developer tools to verify headers:
https://securityheaders.com

Expected headers:

```
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; ...
Referrer-Policy: strict-origin-when-cross-origin
```

---

## Incident Response

### If credentials leak:

1. Rotate `SECRET_KEY` immediately
2. Delete and regenerate `MSAL_CLIENT_SECRET` in Azure Portal
3. Update all environment variables
4. Redeploy application
5. Review audit logs for unauthorized access

### If SSL certificate expires:

1. Azure App Service auto-renews managed certificates
2. For custom domains: Update certificate 30 days before expiration

### If error messages expose sensitive data:

1. Check logs for what was exposed
2. Notify users if necessary
3. Update error handling to be more generic
4. Review other endpoints for similar issues

---

## Next Steps for High Priority Issues

The following High Priority issues should be scheduled for the next sprint:

1. **Add Rate Limiting** - Prevent DOS attacks on API endpoints
2. **Migrate to Authorization Code + PKCE** - Enhanced OAuth security
3. **Add Token Refresh Logic** - Handle token expiration
4. **Add Audit Logging** - Compliance and forensics
5. **Add Request Validation** - Prevent injection attacks

See `SECURITY_REMEDIATION_DETAILED.md` for implementation details.

---

## Sign-Off

- [ ] Security review completed by: ********\_********
- [ ] All critical issues verified: Date: ********\_********
- [ ] Approved for deployment: ********\_********
- [ ] Date: ********\_********

---

## Contacts & Resources

- **Security Issues**: Report to [security@yourorg.com]
- **Azure AD Support**: https://docs.microsoft.com/en-us/azure/active-directory/
- **Flask Security**: https://flask.palletsprojects.com/security/
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
