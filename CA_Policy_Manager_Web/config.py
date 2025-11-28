"""
Configuration for CA Policy Manager Web Application
Supports both local development and Azure App Service deployment
"""

import os
from datetime import timedelta

class Config:
    """Base configuration"""
    # Demo mode flag
    DEMO_MODE = os.environ.get('DEMO_MODE', 'false').lower() == 'true'
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError(
            "SECRET_KEY environment variable is required. "
            "Generate with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )
    
    # Session configuration
    SESSION_COOKIE_NAME = 'ca_policy_session'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # File uploads
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'data/uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'.html', '.xlsx', '.csv'}
    ALLOWED_MIMETYPES = {
        'text/html',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/csv'
    }
    
    # Azure AD OAuth - REQUIRED in all environments
    MSAL_CLIENT_ID = os.environ.get('MSAL_CLIENT_ID')
    # Check for demo mode
    DEMO_MODE = os.environ.get('DEMO_MODE', 'false').lower() == 'true'
    
    # Validate required credentials (only if not in demo mode)
    if not DEMO_MODE:
        if not MSAL_CLIENT_ID:
            raise ValueError(
                "MSAL_CLIENT_ID environment variable is required. "
                "Set in .env file or set DEMO_MODE=true for testing. "
                "See docs/QUICK_SETUP.md for Azure App Registration setup."
            )
    
    MSAL_CLIENT_SECRET = os.environ.get('MSAL_CLIENT_SECRET')
    # Note: CLIENT_SECRET is optional for delegated (user sign-in) authentication
    # Only required for application (service-to-service) authentication
    
    MSAL_AUTHORITY = os.environ.get('MSAL_AUTHORITY', 'https://login.microsoftonline.com/organizations')
    MSAL_REDIRECT_PATH = '/auth/callback'
    MSAL_SCOPE = [
        'https://graph.microsoft.com/Policy.Read.All',
        'https://graph.microsoft.com/Policy.ReadWrite.ConditionalAccess',
        'https://graph.microsoft.com/Application.Read.All',
        'https://graph.microsoft.com/Directory.Read.All',
        'https://graph.microsoft.com/Group.ReadWrite.All',
        'https://graph.microsoft.com/User.Read'
    ]
    
    # Microsoft Graph
    GRAPH_ENDPOINT = 'https://graph.microsoft.com/v1.0'
    
    # AI Configuration (optional)
    AZURE_OPENAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT', '')
    AZURE_OPENAI_API_KEY = os.environ.get('AZURE_OPENAI_API_KEY', '')
    AZURE_OPENAI_DEPLOYMENT = os.environ.get('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o-mini')
    AZURE_OPENAI_API_VERSION = '2024-02-15-preview'
    
    # Fallback to OpenAI if Azure not configured
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
    
    # AI Feature Flags
    AI_ENABLED = os.environ.get('AI_ENABLED', 'false').lower() == 'true'
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'azure')  # 'azure' or 'openai' or 'local'
    LOCAL_MODEL = os.environ.get('LOCAL_MODEL', 'phi3')


class DevelopmentConfig(Config):
    """Development configuration - for localhost testing"""
    DEBUG = True
    
    # Security (relaxed for development only)
    SESSION_COOKIE_SECURE = False  # Allow HTTP for localhost
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'  # Lax for development
    
    # SSL Verification - always verify by default
    # To disable for corporate proxy (development only): set VERIFY_SSL=false env var
    VERIFY_SSL = os.environ.get('VERIFY_SSL', 'true').lower() == 'true'
    if not VERIFY_SSL:
        print("⚠️  WARNING: SSL verification disabled - for development with corporate proxy only!")
        print("   To properly handle corporate proxies, use: requests.certs or REQUESTS_CA_BUNDLE")
    
    # OAuth redirect for localhost
    MSAL_REDIRECT_URI = f"http://localhost:{os.environ.get('PORT', '5000')}/auth/callback"
    
    # CSRF (optional in dev for easier testing)
    WTF_CSRF_ENABLED = os.environ.get('ENABLE_CSRF', 'false').lower() == 'true'
    WTF_CSRF_SSL_STRICT = False


class ProductionConfig(Config):
    """Production configuration - for Azure App Service"""
    DEBUG = False
    
    # Security (strict for production)
    SESSION_COOKIE_SECURE = True  # Require HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'  # Lax allows same-site requests (API calls)
    
    # Force HTTPS
    PREFERRED_URL_SCHEME = 'https'
    
    # SSL Verification (always enabled in production)
    VERIFY_SSL = True
    
    # OAuth redirect for Azure App Service
    # Azure App Service sets WEBSITE_HOSTNAME
    MSAL_REDIRECT_URI = (
        f"https://{os.environ.get('WEBSITE_HOSTNAME')}/auth/callback" 
        if os.environ.get('WEBSITE_HOSTNAME') 
        else os.environ.get('BASE_URL', 'http://localhost:5000') + '/auth/callback'
    )
    
    # CSRF (disabled for API-heavy app with session-based auth)
    # Session cookies provide CSRF protection for same-origin requests
    WTF_CSRF_ENABLED = False
    WTF_CSRF_SSL_STRICT = False
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    VERIFY_SSL = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    
    # Azure App Service detection
    if os.environ.get('WEBSITE_HOSTNAME'):
        env = 'production'
    
    return config.get(env, config['default'])
