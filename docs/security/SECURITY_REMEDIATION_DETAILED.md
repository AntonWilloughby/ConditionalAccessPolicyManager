# Security Remediation Plan - CA Policy Manager

**Status**: Draft for Review
**Date**: November 22, 2025
**Priority**: Critical - Required before public release

---

## 1. CRITICAL ISSUES (Blockers)

### 1.1 Remove Debug Mode from Production

**Issue**: `app.py` line 1272 runs Flask development server with `debug=True`

**Current Code**:

```python
if __name__ == '__main__':
    # Development server - DO NOT use in production!
    # For production, use gunicorn or waitress
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**Risk**:

- Exposes detailed stack traces with sensitive paths
- Allows Werkzeug debugger access (remote code execution)
- Performance degradation

**Fix**:

```python
if __name__ == '__main__':
    # DEVELOPMENT ONLY - Use gunicorn in production
    # Production: gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
    import os
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=debug_mode,
        use_reloader=debug_mode
    )
```

**Deployment Steps**:

1. Create `wsgi.py` with production entry point:

   ```python
   import os
   from app import app

   if __name__ == "__main__":
       app.run()
   ```

2. In Azure App Service, set startup command: `gunicorn --workers 4 --bind 0.0.0.0:8000 wsgi:app`
3. Set environment: `FLASK_ENV=production`

---

### 1.2 Remove Hardcoded Credentials from config.py

**Issue**: Default MSAL_CLIENT_ID hardcoded publicly in source

**Current Code** (`config.py` line 18):

```python
MSAL_CLIENT_ID = os.environ.get('MSAL_CLIENT_ID', 'bcb41e64-e9a8-421c-9331-699dd9041d58')
```

**Risk**:

- Anyone cloning repo gets valid Client ID
- Can be used to enumerate tenants, test credentials
- Compromises your Azure app registration

**Fix**:

```python
MSAL_CLIENT_ID = os.environ.get('MSAL_CLIENT_ID')
if not MSAL_CLIENT_ID:
    raise ValueError(
        "MSAL_CLIENT_ID environment variable is required. "
        "Set in .env or Azure App Service configuration."
    )
```

**Additional Fixes Needed**:

- Line 34: `AZURE_OPENAI_API_KEY` - Add validation:
  ```python
  AZURE_OPENAI_API_KEY = os.environ.get('AZURE_OPENAI_API_KEY', '')
  if not AZURE_OPENAI_API_KEY and os.environ.get('AI_ENABLED') == 'true':
      raise ValueError("AZURE_OPENAI_API_KEY required when AI_ENABLED=true")
  ```
- Line 41: `OPENAI_API_KEY` - Same validation
- Remove all other hardcoded defaults except for non-sensitive configs

**Deployment Steps**:

1. Create `.env.example` showing required variables (NO VALUES):
   ```
   MSAL_CLIENT_ID=your_app_registration_client_id_here
   MSAL_AUTHORITY=https://login.microsoftonline.com/your_tenant_id
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your_azure_openai_key_here
   SECRET_KEY=generate_with_python_secrets_module
   ```
2. In Azure App Service: Use "Configuration" → "Application Settings" to set all values
3. Document in README that local development requires `.env` file (which is in `.gitignore`)

---

### 1.3 Fix SSL Verification Defaults

**Issue**: Production config has `VERIFY_SSL = True` but DevelopmentConfig has `VERIFY_SSL = False`

**Current Code** (`config.py` lines 36-37):

```python
class DevelopmentConfig(Config):
    """Development configuration - for localhost testing"""
    DEBUG = True

    # Security (relaxed for development)
    SESSION_COOKIE_SECURE = False  # Allow HTTP for localhost
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'  # Lax for development

    # SSL Verification (can be disabled for corporate proxies)
    VERIFY_SSL = os.environ.get('DISABLE_SSL_VERIFY', 'false').lower() != 'true'
```

**Risk**:

- If production environment is misconfigured, inherits insecure defaults
- Disabling SSL allows MITM attacks on Graph API calls
- Corporate proxy workaround should be explicit, not implicit

**Fix - Option A: Environment-based** (Recommended):

```python
class DevelopmentConfig(Config):
    """Development configuration - for localhost testing"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Allow HTTP for localhost
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # SSL verification - only disable explicitly for development
    # For corporate proxies, use CA bundle instead: requests.certs
    VERIFY_SSL = os.environ.get('VERIFY_SSL', 'true').lower() == 'true'

class ProductionConfig(Config):
    """Production configuration - for Azure App Service"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    VERIFY_SSL = True  # Always verify in production

    # If corporate proxy needed, set CA_BUNDLE env var:
    # os.environ['REQUESTS_CA_BUNDLE'] = '/path/to/ca-bundle.crt'
```

**Deployment Steps**:

1. If corporate proxy is needed: Document how to set `REQUESTS_CA_BUNDLE` env var
2. For local development: Only disable SSL if absolutely necessary, with explicit env var: `VERIFY_SSL=false`
3. Add to startup script a warning if SSL is disabled

---

### 1.4 Fix Session Storage for Production

**Issue**: Manager instances stored in Python dict `managers = {}` (line 63)

**Current Code** (`app.py` lines 62-67):

```python
# Store manager instances per session (in production, use Redis or similar)
managers = {}

# AI usage tracking per session
ai_usage_stats = {}
```

**Risk**:

- Resets on app restart, losing all user connections
- Doesn't scale to multiple app instances
- Memory leak - never cleared on session expiration
- Not thread-safe

**Fix - Implement Redis-backed sessions**:

Step 1: Add to `requirements.txt`:

```
redis==5.0.0
flask-session==0.5.0
```

Step 2: Create `session_manager.py`:

```python
import os
import json
from typing import Optional, Dict, Any
import redis

class SessionManager:
    """Manages user sessions in Redis or in-memory fallback"""

    def __init__(self):
        redis_url = os.environ.get('REDIS_URL')
        self.use_redis = redis_url is not None

        if self.use_redis:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                self.redis_client.ping()
                print("✅ Connected to Redis for session management")
            except Exception as e:
                print(f"⚠️  Redis connection failed: {e}")
                print("   Falling back to in-memory session storage")
                self.use_redis = False
                self.sessions = {}
        else:
            print("ℹ️  Using in-memory session storage (development only)")
            self.sessions = {}

    def get_manager(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve manager for session"""
        if self.use_redis:
            data = self.redis_client.get(f"manager:{session_id}")
            return json.loads(data) if data else None
        else:
            return self.sessions.get(session_id)

    def set_manager(self, session_id: str, manager_data: Dict[str, Any], ttl: int = 3600):
        """Store manager for session with TTL"""
        if self.use_redis:
            self.redis_client.setex(
                f"manager:{session_id}",
                ttl,
                json.dumps(manager_data)
            )
        else:
            self.sessions[session_id] = manager_data

    def clear_session(self, session_id: str):
        """Clear session data"""
        if self.use_redis:
            self.redis_client.delete(f"manager:{session_id}")
        else:
            self.sessions.pop(session_id, None)
```

Step 3: Update `app.py` config:

```python
from session_manager import SessionManager

app.config['SESSION_TYPE'] = 'redis' if os.environ.get('REDIS_URL') else 'filesystem'
if os.environ.get('REDIS_URL'):
    app.config['SESSION_REDIS'] = redis.from_url(os.environ.get('REDIS_URL'))

session_manager = SessionManager()
```

**Deployment Steps**:

1. Local development: Leave as-is (in-memory)
2. Azure deployment: Provision Azure Cache for Redis
3. Set `REDIS_URL` environment variable in App Service
4. Test session persistence across app restarts

---

### 1.5 Sanitize Error Responses

**Issue**: Full error messages and API responses returned to client

**Example** (`app.py` line 1031):

```python
return jsonify({
    'success': False,
    'error': f'Failed to create policy: {response.status_code} - {response.text}'  # EXPOSED!
}), response.status_code
```

**Risk**:

- `response.text` from Graph API may contain OAuth tokens, header info
- Stack traces exposed to client
- Helps attackers understand system architecture

**Fix - Create error handler**:

Add to `app.py`:

```python
import logging
from flask import render_template

logger = logging.getLogger(__name__)

@app.errorhandler(Exception)
def handle_error(error):
    """Centralized error handling"""
    # Log full error server-side
    logger.error(f"Unhandled exception: {error}", exc_info=True)

    # Return safe error to client
    return jsonify({
        'success': False,
        'error': 'An error occurred processing your request. Please try again.',
        'error_code': 'INTERNAL_ERROR'
    }), 500

# Use in endpoints:
def safe_error_response(error: Exception, error_type: str = 'OPERATION_FAILED', status_code: int = 400):
    """Generate safe error response"""
    logger.error(f"{error_type}: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Operation failed. Check your credentials and permissions.',
        'error_type': error_type
    }), status_code
```

**Update Endpoints**:

```python
@app.route('/api/policies', methods=['POST'])
def create_policy():
    try:
        policy_data = request.json
        # ... code ...
    except Exception as e:
        logger.error(f"Failed to create policy: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create policy. Verify the policy format and your permissions.'
        }), 400
```

**Deployment Steps**:

1. Configure logging to file or CloudWatch
2. Set log level to ERROR in production
3. Test that stack traces don't appear in client responses
4. Monitor logs for actual error details

---

### 1.6 Enable CSRF Protection

**Issue**: CSRF disabled in production (`config.py` line 49)

**Current Code**:

```python
class ProductionConfig(Config):
    # CSRF (always enabled in production)
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SSL_STRICT = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
```

**Already Correct!** However, ensure implementation:

**Fix - Add CSRF tokens to forms**:

In `templates/index.html`:

```html
<form id="connectForm">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />
  <!-- form fields -->
</form>
```

In `static/js/main.js`:

```javascript
// Include CSRF token in all POST/PUT/DELETE requests
async function apiCall(method, url, data) {
  const csrfToken =
    document.querySelector("[name=csrf_token]")?.value ||
    getCookie("csrf_token");

  const options = {
    method: method,
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken, // Add CSRF token header
    },
  };

  if (data) options.body = JSON.stringify(data);

  return fetch(url, options);
}
```

**In app.py, enable CSRF**:

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# Or for API endpoints that don't need CSRF:
@app.route('/api/health', methods=['GET'])
@csrf.exempt
def health_check():
    return jsonify({'success': True})
```

**Deployment Steps**:

1. Install flask-wtf: `pip install flask-wtf`
2. Add `WTF_CSRF_ENABLED = True` verification in config
3. Update all AJAX calls to include CSRF token
4. Test form submissions work with CSRF enabled

---

## 2. HIGH PRIORITY ISSUES

### 2.1 Add Rate Limiting

**Fix**:

Step 1: Add to `requirements.txt`:

```
flask-limiter==3.5.0
```

Step 2: Add to `app.py`:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.environ.get('REDIS_URL', None)
)

# Apply to sensitive endpoints
@app.route('/api/connect', methods=['POST'])
@limiter.limit("5 per minute")  # Prevent brute force
def connect():
    # ... existing code ...

@app.route('/auth/login', methods=['GET'])
@limiter.limit("10 per minute")
def auth_login():
    # ... existing code ...
```

---

### 2.2 Validate File Uploads

**Fix** (`app.py` line 1099):

```python
from werkzeug.utils import secure_filename
import mimetypes

ALLOWED_EXTENSIONS = {'.html', '.xlsx', '.csv'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

@app.route('/api/report/upload', methods=['POST'])
def upload_report():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        # Validate file size
        if len(file.read()) > MAX_FILE_SIZE:
            return jsonify({'success': False, 'error': 'File too large (max 50MB)'}), 413
        file.seek(0)  # Reset file pointer

        # Validate file extension
        filename = secure_filename(file.filename)
        _, ext = os.path.splitext(filename)

        if ext.lower() not in ALLOWED_EXTENSIONS:
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400

        # Validate MIME type
        mime_type = file.content_type
        allowed_mimes = {'text/html', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv'}
        if mime_type not in allowed_mimes:
            return jsonify({
                'success': False,
                'error': 'Invalid file type'
            }), 400

        # Scan for malware (optional - use ClamAV)
        if os.environ.get('ENABLE_VIRUS_SCAN') == 'true':
            # Implement virus scanning here
            pass

        # Save file
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        session['report_path'] = filepath

        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'Report uploaded successfully'
        })

    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        return jsonify({'success': False, 'error': 'Upload failed'}), 500
```

---

### 2.3 Migrate from Implicit Grant to Authorization Code + PKCE

**Current Issue** (`app.py` line 129):

```python
@app.route('/auth/login', methods=['GET'])
def auth_login():
    # Implicit grant (deprecated)
    auth_url = (
        f"{app.config['MSAL_AUTHORITY']}/oauth2/v2.0/authorize?"
        f"client_id={app.config['MSAL_CLIENT_ID']}&"
        f"response_type=token&"  # IMPLICIT GRANT - DEPRECATED
        ...
    )
```

**Fix - Use Authorization Code + PKCE**:

```python
import secrets
import hashlib
import base64

@app.route('/auth/login', methods=['GET'])
def auth_login():
    """Initiate OAuth with authorization code + PKCE flow"""
    try:
        # Generate PKCE parameters
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
        code_verifier = code_verifier.rstrip('=')  # Remove padding

        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode('utf-8').rstrip('=')

        # Store in session for later validation
        session['code_verifier'] = code_verifier
        session.permanent = True

        # Build authorization URL with PKCE
        auth_url = (
            f"{app.config['MSAL_AUTHORITY']}/oauth2/v2.0/authorize?"
            f"client_id={app.config['MSAL_CLIENT_ID']}&"
            f"response_type=code&"  # Authorization code flow
            f"redirect_uri={app.config['MSAL_REDIRECT_URI']}&"
            f"scope={'%20'.join(app.config['MSAL_SCOPE'])}&"
            f"state={secrets.token_urlsafe(32)}&"  # CSRF protection
            f"code_challenge={code_challenge}&"  # PKCE
            f"code_challenge_method=S256"  # PKCE method
        )

        return jsonify({
            'success': True,
            'auth_url': auth_url
        })

    except Exception as e:
        logger.error(f"Auth login error: {e}")
        return jsonify({'success': False, 'error': 'Failed to initiate authentication'}), 500

@app.route('/auth/callback', methods=['GET'])
def auth_callback():
    """Handle OAuth callback with authorization code"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')

        if not code:
            return render_template('auth_callback.html', error='No authorization code received')

        # Validate state parameter (CSRF protection)
        # In production, compare with stored state in session

        # Exchange code for token using PKCE verifier
        code_verifier = session.get('code_verifier')

        token_url = f"{app.config['MSAL_AUTHORITY']}/oauth2/v2.0/token"

        response = requests.post(token_url, data={
            'client_id': app.config['MSAL_CLIENT_ID'],
            'client_secret': app.config['MSAL_CLIENT_SECRET'],  # Confidential client
            'code': code,
            'redirect_uri': app.config['MSAL_REDIRECT_URI'],
            'grant_type': 'authorization_code',
            'code_verifier': code_verifier  # PKCE verifier
        }, verify=get_verify_ssl())

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            refresh_token = token_data.get('refresh_token')
            expires_in = token_data.get('expires_in')

            # Store tokens securely in session (with expiration)
            session['access_token'] = access_token
            session['refresh_token'] = refresh_token
            session['token_expiry'] = datetime.utcnow() + timedelta(seconds=expires_in)

            return render_template('auth_callback.html', success=True, count='loading')
        else:
            logger.error(f"Token exchange failed: {response.status_code}")
            return render_template('auth_callback.html', error='Failed to exchange authorization code')

    except Exception as e:
        logger.error(f"Auth callback error: {e}")
        return render_template('auth_callback.html', error='Authentication error')
```

---

### 2.4 Add Token Refresh Logic

**Fix - Add to `app.py`**:

```python
from functools import wraps
from datetime import datetime, timedelta

def ensure_valid_token(f):
    """Decorator to ensure access token is valid, refresh if needed"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('auth_method') == 'delegated':
            token_expiry = session.get('token_expiry')

            if token_expiry and datetime.fromisoformat(token_expiry) < datetime.utcnow():
                # Token expired, refresh it
                if not refresh_access_token():
                    return jsonify({'success': False, 'error': 'Session expired. Please sign in again.'}), 401

        return f(*args, **kwargs)

    return decorated_function

def refresh_access_token() -> bool:
    """Refresh the access token using refresh token"""
    try:
        refresh_token = session.get('refresh_token')
        if not refresh_token:
            return False

        token_url = f"{app.config['MSAL_AUTHORITY']}/oauth2/v2.0/token"

        response = requests.post(token_url, data={
            'client_id': app.config['MSAL_CLIENT_ID'],
            'client_secret': app.config['MSAL_CLIENT_SECRET'],
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }, verify=get_verify_ssl())

        if response.status_code == 200:
            token_data = response.json()
            session['access_token'] = token_data.get('access_token')
            session['token_expiry'] = datetime.utcnow() + timedelta(seconds=token_data.get('expires_in', 3600))
            print("✅ Access token refreshed")
            return True
        else:
            logger.error(f"Token refresh failed: {response.status_code}")
            session.clear()
            return False

    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return False

# Apply decorator to protected endpoints:
@app.route('/api/policies', methods=['GET'])
@ensure_valid_token
def list_policies():
    # ... existing code ...
```

---

## 3. MEDIUM PRIORITY ISSUES

### 3.1 Add Security Headers

**Fix - Add middleware to `app.py`**:

```python
@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' https://cdn.jsdelivr.net; "
        "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://graph.microsoft.com https://login.microsoftonline.com"
    )
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response
```

---

### 3.2 Add Audit Logging

**Fix - Create `audit_logger.py`**:

```python
import json
import logging
from datetime import datetime

class AuditLogger:
    """Structured audit logging for policy changes"""

    def __init__(self):
        self.logger = logging.getLogger('audit')
        self.logger.setLevel(logging.INFO)

        # File handler
        handler = logging.FileHandler('audit.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)

    def log_policy_change(self, user_id: str, action: str, policy_id: str,
                         policy_name: str, details: dict):
        """Log a policy change"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': action,  # create, update, delete, deploy
            'policy_id': policy_id,
            'policy_name': policy_name,
            'details': details
        }
        self.logger.info(json.dumps(event))

audit_logger = AuditLogger()
```

**Use in endpoints**:

```python
@app.route('/api/policies', methods=['POST'])
def create_policy():
    try:
        policy_data = request.json
        policy_name = policy_data.get('displayName', '')
        user_id = session.get('user_id', 'unknown')

        # ... create policy ...

        # Log the change
        audit_logger.log_policy_change(
            user_id=user_id,
            action='create',
            policy_id=policy.get('id'),
            policy_name=policy_name,
            details={'state': policy.get('state')}
        )

    except Exception as e:
        # ... error handling ...
```

---

### 3.3 Pin Dependencies in requirements.txt

**Current Issue**: No version pinning on transitive dependencies

**Fix**: Use `pip freeze`:

```bash
pip freeze > requirements-pinned.txt
```

**Update `requirements.txt`** with example pinning:

```
flask==3.0.0
werkzeug==3.0.1
msal==1.25.0
requests==2.31.0
beautifulsoup4==4.12.2
pandas==2.1.4
openpyxl==3.1.2
urllib3==2.1.0
gunicorn==21.2.0
python-dotenv==1.0.0
openai>=2.0.0,<5.0.0
redis==5.0.0
flask-session==0.5.0
flask-limiter==3.5.0
flask-wtf==1.2.1
```

---

### 3.4 Add Content Security Policy Headers with SRI

**Fix - Update `templates/index.html`**:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta
      http-equiv="Content-Security-Policy"
      content="
        default-src 'self';
        script-src 'self' https://cdn.jsdelivr.net;
        style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline';
        font-src 'self' https://cdn.jsdelivr.net;
        img-src 'self' data: https:;
        connect-src 'self' https://graph.microsoft.com https://login.microsoftonline.com;
        frame-ancestors 'none';
        base-uri 'self';
        form-action 'self'
    "
    />
    <title>Conditional Access Policy Manager</title>
    <!-- Add SRI hashes to CDN resources -->
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
      rel="stylesheet"
      integrity="sha384-9ndCyUaIbzAi2FUarbnLDtQpJspTtfV2mYIKmymsIY/dHlM/L7NK3+ar5B3ik1HV"
      crossorigin="anonymous"
    />
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css"
      rel="stylesheet"
      integrity="sha384-b6lVOJXQcjSVaUF6Vt6hL34X3d3R9DGbPPpXQxJYCl7VJE/UbnZs1DxsvqFcRN7t"
    />
  </head>
  <!-- ... -->
</html>
```

---

## 4. DEPLOYMENT CHECKLIST

Create `SECURITY_DEPLOYMENT_CHECKLIST.md`:

```markdown
# Security Pre-Deployment Checklist

## Environment Configuration

- [ ] All credentials in environment variables (no hardcoded values)
- [ ] `.env.example` created with template (no actual values)
- [ ] `.gitignore` updated to exclude `.env`
- [ ] `SECRET_KEY` generated with: `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] MSAL_CLIENT_ID set via app configuration
- [ ] MSAL_CLIENT_SECRET configured securely
- [ ] Azure OpenAI keys configured (if AI enabled)

## Code Security

- [ ] No `debug=True` in production
- [ ] CSRF protection enabled: `WTF_CSRF_ENABLED = True`
- [ ] SSL verification enabled: `VERIFY_SSL = True`
- [ ] Security headers middleware added
- [ ] Error responses sanitized (no stack traces)
- [ ] Audit logging implemented

## Authentication & Authorization

- [ ] OAuth uses authorization code + PKCE flow
- [ ] Tokens have expiration handling
- [ ] Refresh token logic implemented
- [ ] State parameter validates CSRF
- [ ] HTTPS enforced (Strict-Transport-Security header)

## API Security

- [ ] Rate limiting configured
- [ ] Input validation on all endpoints
- [ ] File upload validation implemented
- [ ] Request size limits set
- [ ] SQL injection not possible (using ORM or parameterized queries)

## Data Protection

- [ ] Session data stored in Redis (not in-memory)
- [ ] Sensitive data not logged
- [ ] File uploads scanned for malware (optional)
- [ ] Encryption in transit (HTTPS)
- [ ] Encryption at rest configured for storage

## Deployment

- [ ] Using gunicorn or similar WSGI server
- [ ] Multiple workers configured (4+ for production)
- [ ] Port 5000 exposed to load balancer only (not public)
- [ ] Health check endpoint responding
- [ ] Logging to file or monitoring system

## Testing

- [ ] HTTPS certificate valid and not expired
- [ ] CORS properly configured
- [ ] Session timeout works correctly
- [ ] Token refresh flows tested
- [ ] Error messages don't leak secrets
- [ ] File upload restrictions enforced

## Monitoring

- [ ] Application logs sent to centralized logging
- [ ] Error tracking enabled (e.g., Application Insights)
- [ ] Metrics collected (request latency, error rates)
- [ ] Alerts configured for security events
- [ ] Audit logs reviewed regularly
```

---

## SUMMARY OF CHANGES NEEDED

| Priority    | Issue                         | Impact                 | Effort    | Owner        |
| ----------- | ----------------------------- | ---------------------- | --------- | ------------ |
| 🔴 CRITICAL | Remove debug mode             | RCE vulnerability      | 1 hour    | Dev          |
| 🔴 CRITICAL | Remove hardcoded credentials  | Account takeover       | 30 min    | Dev          |
| 🔴 CRITICAL | Fix SSL verification defaults | MITM attacks           | 1 hour    | Dev          |
| 🔴 CRITICAL | Fix session storage           | Data loss, no scaling  | 4 hours   | Dev          |
| 🔴 CRITICAL | Sanitize error responses      | Information disclosure | 2 hours   | Dev          |
| 🔴 CRITICAL | Enable CSRF protection        | CSRF attacks           | 1 hour    | Dev/Frontend |
| 🟠 HIGH     | Add rate limiting             | DOS attacks            | 1 hour    | Dev          |
| 🟠 HIGH     | Validate file uploads         | File upload attacks    | 1.5 hours | Dev          |
| 🟠 HIGH     | Migrate to auth code + PKCE   | OAuth security         | 4 hours   | Dev          |
| 🟠 HIGH     | Add token refresh logic       | Token hijacking        | 2 hours   | Dev          |
| 🟡 MEDIUM   | Add security headers          | XSS, clickjacking      | 1 hour    | Dev          |
| 🟡 MEDIUM   | Add audit logging             | Compliance gaps        | 2 hours   | Dev          |
| 🟡 MEDIUM   | Pin dependencies              | Supply chain attacks   | 1 hour    | Dev          |

**Total Estimated Effort**: 25 hours
**Critical Path**: 10 hours (complete critical issues first)

---

## NEXT STEPS

1. **Week 1**: Implement 7 critical fixes
2. **Week 2**: Implement 5 high-priority fixes
3. **Week 3**: Implement medium-priority fixes + testing
4. **Week 4**: Security testing, penetration testing, compliance review
5. **Publication**: After all fixes implemented and tested
