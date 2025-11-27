#!/usr/bin/env python3
"""
Flask Web Application for Conditional Access Policy Manager
Supports both local development and Azure App Service deployment
"""

import os
import sys
import json
import tempfile
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Callable

from flask import Flask, render_template, request, jsonify, session, send_file, redirect, url_for, g
from werkzeug.utils import secure_filename
import msal
import requests
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enforce supported Python versions (3.11 - 3.12)
if not ((3, 11) <= sys.version_info[:2] <= (3, 12)):
    logger.error(
        "❌ Unsupported Python version detected: %s. "
        "CA Policy Manager currently supports Python 3.11 and 3.12. "
        "Install a supported version from https://www.python.org/downloads/ and rerun setup.",
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    sys.exit(1)

# Import modules from current directory
from ca_policy_manager import ConditionalAccessManager
from ca_policy_examples import POLICY_TEMPLATES
from utils.report_analyzer import SecurityReportAnalyzer
from utils.ai_assistant import PolicyAIAssistant
from config import get_config
from session_manager import SessionManager

# Initialize Flask app
app = Flask(__name__)

# Load configuration based on environment
try:
    app.config.from_object(get_config())
except ValueError as e:
    logger.error(f"❌ Configuration error: {e}")
    logger.error("Please ensure all required environment variables are set.")
    sys.exit(1)

# Initialize CSRF protection
from flask_wtf.csrf import CSRFProtect, generate_csrf

# Configure CSRF to not check by default - we'll protect specific routes manually
app.config['WTF_CSRF_CHECK_DEFAULT'] = False

csrf = CSRFProtect(app)

# Initialize session manager (Redis or in-memory fallback)
session_manager = SessionManager()

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize AI Assistant
ai_assistant = None
if app.config.get('AI_ENABLED'):
    try:
        # Pass only needed config to avoid Flask config object issues
        ai_config = {
            'AI_ENABLED': app.config.get('AI_ENABLED'),
            'AI_PROVIDER': app.config.get('AI_PROVIDER'),
            'AZURE_OPENAI_ENDPOINT': app.config.get('AZURE_OPENAI_ENDPOINT'),
            'AZURE_OPENAI_API_KEY': app.config.get('AZURE_OPENAI_API_KEY'),
            'AZURE_OPENAI_DEPLOYMENT': app.config.get('AZURE_OPENAI_DEPLOYMENT'),
            'AZURE_OPENAI_API_VERSION': app.config.get('AZURE_OPENAI_API_VERSION'),
            'OPENAI_API_KEY': app.config.get('OPENAI_API_KEY'),
            'OPENAI_MODEL': app.config.get('OPENAI_MODEL'),
            'LOCAL_MODEL': app.config.get('LOCAL_MODEL')
        }
        ai_assistant = PolicyAIAssistant(ai_config)
    except Exception as e:
        logger.warning(f"⚠️  Failed to initialize AI Assistant: {e}")
        logger.info("   AI features will be disabled")
else:
    logger.info("ℹ️  AI features disabled (set AI_ENABLED=true in .env to enable)")

# Add security headers middleware
@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Get nonce from g if available (for auth callback page)
    nonce = getattr(g, 'csp_nonce', None)
    script_src = "script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'"
    if nonce:
        script_src += f" 'nonce-{nonce}'"
    
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        f"{script_src}; "
        "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://graph.microsoft.com https://login.microsoftonline.com https://cdn.jsdelivr.net"
    )
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# Error handling
@app.errorhandler(Exception)
def handle_error(error):
    """Centralized error handling - don't expose sensitive info"""
    logger.error(f"Unhandled exception: {error}", exc_info=True)
    return jsonify({
        'success': False,
        'error': 'An error occurred processing your request. Please try again.',
        'error_code': 'INTERNAL_ERROR'
    }), 500

def safe_error_response(error_msg: str, error_type: str = 'OPERATION_FAILED', status_code: int = 400):
    """Generate safe error response without exposing sensitive details"""
    logger.error(f"{error_type}: {error_msg}")
    return jsonify({
        'success': False,
        'error': 'Operation failed. Check your credentials and permissions.',
        'error_type': error_type
    }), status_code

def get_verify_ssl():
    """Get SSL verification setting from config"""
    return app.config.get('VERIFY_SSL', True)

def get_session_id() -> str:
    """Get or create session ID"""
    if 'id' not in session:
        import secrets
        session['id'] = secrets.token_hex(16)
    return session['id']

def get_ai_stats() -> dict:
    """Get or initialize AI usage stats for current session"""
    session_id = get_session_id()
    stats = session_manager.get_ai_stats(session_id)
    
    if not stats:
        stats = {
            'explanations': 0,
            'tokens_used': 0,
            'total_cost': 0.0,
            'response_times': []
        }
    
    return stats

def update_ai_stats(tokens_input: int, tokens_output: int, response_time: float):
    """Update AI usage statistics"""
    session_id = get_session_id()
    stats = get_ai_stats()
    stats['explanations'] += 1
    stats['tokens_used'] += tokens_input + tokens_output
    
    # Azure OpenAI gpt-4o-mini pricing (as of 2024)
    # Input: $0.15 per 1M tokens, Output: $0.60 per 1M tokens
    input_cost = (tokens_input / 1_000_000) * 0.15
    output_cost = (tokens_output / 1_000_000) * 0.60
    stats['total_cost'] += input_cost + output_cost
    
    stats['response_times'].append(response_time)
    
    session_manager.set_ai_stats(session_id, stats)
    return stats

def get_manager():
    """Get manager for current session"""
    session_id = get_session_id()
    manager_data = session_manager.get_manager(session_id)
    return manager_data

def set_manager(manager):
    """Store manager for current session"""
    session_id = get_session_id()
    # Store manager reference (in production, store config, not the object)
    if manager:
        manager_data = {
            'tenant_id': manager.tenant_id,
            'client_id': manager.client_id,
            'client_secret': manager.client_secret,
            'verify_ssl': manager.verify_ssl
        }
        session_manager.set_manager(session_id, manager_data)
    else:
        session_manager.set_manager(session_id, None)

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/auth/login', methods=['GET'])
def auth_login():
    """Initiate Entra ID authentication flow with implicit grant"""
    try:
        # Check if in demo mode
        demo_mode = app.config.get('DEMO_MODE', False)
        
        if demo_mode:
            return jsonify({
                'success': False,
                'error': 'Demo mode is enabled. To use authentication, please set up Azure credentials.',
                'demo_mode': True,
                'setup_url': '/setup/azure'
            }), 400
        
        # Build authorization URL for implicit flow (token in fragment)
        auth_url = (
            f"{app.config['MSAL_AUTHORITY']}/oauth2/v2.0/authorize?"
            f"client_id={app.config['MSAL_CLIENT_ID']}&"
            f"response_type=token&"
            f"redirect_uri={app.config['MSAL_REDIRECT_URI']}&"
            f"scope={'%20'.join(app.config['MSAL_SCOPE'])}&"
            f"response_mode=fragment"
        )
        
        return jsonify({
            'success': True,
            'auth_url': auth_url
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/auth/callback')
def auth_callback():
    """Handle Entra ID authentication callback - just render page, token handled client-side"""
    # For implicit flow, the token comes in the URL fragment (after #)
    # JavaScript will extract it and send it to the server
    # Generate nonce for CSP to allow inline script
    import secrets
    nonce = secrets.token_urlsafe(16)
    g.csp_nonce = nonce
    return render_template('auth_callback.html', csp_nonce=nonce)

@app.route('/setup/azure', methods=['GET', 'POST'])
def setup_azure():
    """Automatic Azure App Registration setup"""
    if request.method == 'GET':
        # Show setup page
        return render_template('azure_setup.html')
    
    try:
        import subprocess
        from pathlib import Path
        
        # Path to PowerShell registration script
        script_path = Path(__file__).parent.parent / 'scripts' / 'Register-EntraApp-Delegated.ps1'
        
        if not script_path.exists():
            return jsonify({
                'success': False,
                'error': 'Registration script not found. Please use manual setup.',
                'manual_guide': '/docs/QUICK_SETUP.md'
            }), 404
        
        # Check if Azure CLI is installed
        try:
            subprocess.run(['az', '--version'], capture_output=True, timeout=5, check=True)
        except:
            return jsonify({
                'success': False,
                'error': 'Azure CLI not installed. Please install from https://aka.ms/azure-cli',
                'manual_guide': '/docs/QUICK_SETUP.md'
            }), 400
        
        # Run the PowerShell script
        logger.info("Running Azure App Registration script...")
        result = subprocess.run(
            ['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', str(script_path)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Azure App Registration created successfully!',
                'next_steps': 'Please restart the Flask app to use the new configuration.'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Script execution failed',
                'details': result.stderr,
                'manual_guide': '/docs/QUICK_SETUP.md'
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Setup timed out (5 minutes)',
            'manual_guide': '/docs/QUICK_SETUP.md'
        }), 500
    except Exception as e:
        logger.error(f"Azure setup error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'manual_guide': '/docs/QUICK_SETUP.md'
        }), 500

@app.route('/api/auth/token', methods=['POST'])
def receive_token():
    """Receive token from client-side authentication"""
    try:
        data = request.get_json()
        access_token = data.get('access_token')
        
        if not access_token:
            return jsonify({'success': False, 'error': 'No access token provided'}), 400
        
        # Store token in session
        session['access_token'] = access_token
        session['auth_method'] = 'delegated'
        
        # Test the token by getting policies
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{app.config['GRAPH_ENDPOINT']}/identity/conditionalAccess/policies",
            headers=headers,
            verify=get_verify_ssl()
        )
        
        if response.status_code == 200:
            policies = response.json().get('value', [])
            return jsonify({'success': True, 'count': len(policies)})
        else:
            return jsonify({'success': False, 'error': 'Unable to retrieve policies'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/disconnect', methods=['POST'])
def disconnect():
    """Disconnect and clear session"""
    try:
        session_id = get_session_id()
        
        # Clear the manager from session
        session_manager.set_manager(session_id, None)
        
        # Clear session data (including access_token for delegated auth)
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Disconnected successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/connect', methods=['POST'])
def connect():
    """Connect to Microsoft Graph API"""
    try:
        data = request.json
        tenant_id = data.get('tenant_id')
        client_id = data.get('client_id')
        client_secret = data.get('client_secret')
        verify_ssl = data.get('verify_ssl', False)  # Default to False for development
        
        if not all([tenant_id, client_id, client_secret]):
            return jsonify({'success': False, 'error': 'Missing required credentials'}), 400
        
        # Create manager
        manager = ConditionalAccessManager(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
            verify_ssl=verify_ssl
        )
        
        # Authenticate first
        if not manager.authenticate():
            logger.warning(f"Authentication failed for tenant {tenant_id}")
            return jsonify({
                'success': False, 
                'error': 'Authentication failed. Check your credentials.'
            }), 401
        
        # Test connection by getting policies
        policies = manager.list_policies()
        
        if policies is None or len(policies) == 0:
            # Check if it's a permissions issue
            error_msg = ('Connected but unable to retrieve policies. '
                        'This usually means the App Registration is missing required permissions.\n\n'
                        '⚠️ Required API Permissions:\n'
                        '• Policy.Read.All\n'
                        '• Policy.ReadWrite.ConditionalAccess\n\n'
                        'Steps to fix:\n'
                        '1. Go to Azure Portal → App Registrations\n'
                        '2. Select your app\n'
                        '3. Go to "API permissions"\n'
                        '4. Add Microsoft Graph → Application permissions:\n'
                        '   - Policy.Read.All\n'
                        '   - Policy.ReadWrite.ConditionalAccess\n'
                        '5. Click "Grant admin consent"\n'
                        '6. Wait 5 minutes and try again')
            
            logger.warning(f"Permission denied for tenant {tenant_id}")
            return jsonify({
                'success': False,
                'error': error_msg,
                'error_type': 'permissions'
            }), 403
        
        # Store manager in session
        set_manager(manager)
        
        return jsonify({
            'success': True,
            'message': f'Connected successfully! Retrieved {len(policies)} policies.',
            'policy_count': len(policies)
        })
        
    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        return safe_error_response(str(e), 'CONNECTION_FAILED', 500)

@app.route('/api/policies', methods=['GET'])
def list_policies():
    """Get all policies - supports both client credentials and delegated auth"""
    try:
        # Check if using delegated auth
        if session.get('auth_method') == 'delegated' and session.get('access_token'):
            # Use delegated token directly
            headers = {
                'Authorization': f'Bearer {session["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies',
                headers=headers,
                verify=get_verify_ssl()
            )
            
            if response.status_code == 200:
                policies = response.json().get('value', [])
                return jsonify({
                    'success': True,
                    'policies': policies,
                    'count': len(policies)
                })
            else:
                return jsonify({
                    'success': False, 
                    'error': f'Failed to retrieve policies: {response.status_code}'
                }), response.status_code
        
        # Otherwise use client credentials manager
        manager = get_manager()
        if not manager:
            return jsonify({'success': False, 'error': 'Not connected'}), 401
        
        policies = manager.list_policies()
        
        return jsonify({
            'success': True,
            'policies': policies,
            'count': len(policies)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/policies/<policy_id>', methods=['GET'])
def get_policy(policy_id):
    """Get specific policy details - supports both client credentials and delegated auth"""
    try:
        # Check if using delegated auth
        if session.get('auth_method') == 'delegated' and session.get('access_token'):
            # Use delegated token directly
            headers = {
                'Authorization': f'Bearer {session["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f'https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/{policy_id}',
                headers=headers,
                verify=get_verify_ssl()
            )
            
            if response.status_code == 200:
                policy = response.json()
                return jsonify({
                    'success': True,
                    'policy': policy
                })
            else:
                return jsonify({
                    'success': False, 
                    'error': f'Failed to retrieve policy: {response.status_code}'
                }), response.status_code
        
        # Otherwise use client credentials manager
        manager = get_manager()
        if not manager:
            return jsonify({'success': False, 'error': 'Not connected'}), 401
        
        policy = manager.get_policy(policy_id)
        
        return jsonify({
            'success': True,
            'policy': policy
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/policies', methods=['POST'])
def create_policy():
    """Create new policy - supports both client credentials and delegated auth"""
    try:
        policy_data = request.json
        policy_name = policy_data.get('displayName', '')
        
        # Check if using delegated auth
        if session.get('auth_method') == 'delegated' and session.get('access_token'):
            # Use delegated token directly
            headers = {
                'Authorization': f'Bearer {session["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            # First, check if a policy with the same name already exists
            check_response = requests.get(
                'https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies',
                headers=headers,
                verify=get_verify_ssl()
            )
            
            if check_response.status_code == 200:
                existing_policies = check_response.json().get('value', [])
                duplicate = next((p for p in existing_policies if p.get('displayName') == policy_name), None)
                
                if duplicate:
                    return jsonify({
                        'success': False,
                        'error': f'A policy with the name "{policy_name}" already exists. Please use a different name or update the existing policy.',
                        'duplicate_policy_id': duplicate.get('id')
                    }), 409  # 409 Conflict
            
            response = requests.post(
                'https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies',
                headers=headers,
                json=policy_data,
                verify=get_verify_ssl()
            )
            
            if response.status_code in [200, 201]:
                policy = response.json()
                logger.info(f"Created policy: {policy_name}")
                return jsonify({
                    'success': True,
                    'policy': policy,
                    'message': 'Policy created successfully'
                })
            else:
                logger.error(f"Failed to create policy: {response.status_code}")
                return jsonify({
                    'success': False, 
                    'error': 'Failed to create policy. Check the policy format and your permissions.'
                }), response.status_code
        
        # Otherwise use client credentials manager
        manager = get_manager()
        if not manager:
            return jsonify({'success': False, 'error': 'Not connected'}), 401
        
        # Check for duplicate policy name with client credentials
        try:
            existing_policies = manager.list_policies()
            duplicate = next((p for p in existing_policies if p.get('displayName') == policy_name), None)
            
            if duplicate:
                return jsonify({
                    'success': False,
                    'error': f'A policy with the name "{policy_name}" already exists. Please use a different name or update the existing policy.',
                    'duplicate_policy_id': duplicate.get('id')
                }), 409  # 409 Conflict
        except Exception as check_error:
            logger.warning(f"Could not check for duplicate policies: {check_error}")
        
        result = manager.create_policy(policy_data)
        
        return jsonify({
            'success': True,
            'policy': result,
            'message': 'Policy created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating policy: {str(e)}")
        return safe_error_response(str(e), 'POLICY_CREATE_FAILED', 500)

@app.route('/api/policies/<policy_id>', methods=['PUT'])
def update_policy(policy_id):
    """Update existing policy - supports both client credentials and delegated auth"""
    try:
        policy_data = request.json
        
        # Check if using delegated auth
        if session.get('auth_method') == 'delegated' and session.get('access_token'):
            # Use delegated token directly
            headers = {
                'Authorization': f'Bearer {session["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            response = requests.patch(
                f'https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/{policy_id}',
                headers=headers,
                json=policy_data,
                verify=get_verify_ssl()
            )
            
            if response.status_code in [200, 204]:
                # Get updated policy
                get_response = requests.get(
                    f'https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/{policy_id}',
                    headers=headers,
                    verify=get_verify_ssl()
                )
                if get_response.status_code == 200:
                    return jsonify({
                        'success': True,
                        'policy': get_response.json(),
                        'message': 'Policy updated successfully'
                    })
                else:
                    return jsonify({
                        'success': True,
                        'message': 'Policy updated successfully'
                    })
            else:
                return jsonify({
                    'success': False, 
                    'error': f'Failed to update policy: {response.status_code} - {response.text}'
                }), response.status_code
        
        # Otherwise use client credentials manager
        manager = get_manager()
        if not manager:
            return jsonify({'success': False, 'error': 'Not connected'}), 401
        
        result = manager.update_policy(policy_id, policy_data)
        
        return jsonify({
            'success': True,
            'policy': result,
            'message': 'Policy updated successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/policies/<policy_id>', methods=['DELETE'])
def delete_policy(policy_id):
    """Delete policy - supports both client credentials and delegated auth"""
    try:
        # Check if using delegated auth
        if session.get('auth_method') == 'delegated' and session.get('access_token'):
            # Use delegated token directly
            headers = {
                'Authorization': f'Bearer {session["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            response = requests.delete(
                f'https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/{policy_id}',
                headers=headers,
                verify=get_verify_ssl()
            )
            
            if response.status_code in [200, 204]:
                return jsonify({
                    'success': True,
                    'message': 'Policy deleted successfully'
                })
            else:
                return jsonify({
                    'success': False, 
                    'error': f'Failed to delete policy: {response.status_code} - {response.text}'
                }), response.status_code
        
        # Otherwise use client credentials manager
        manager = get_manager()
        if not manager:
            return jsonify({'success': False, 'error': 'Not connected'}), 401
        
        manager.delete_policy(policy_id)
        
        return jsonify({
            'success': True,
            'message': 'Policy deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def enrich_policy_with_group_names(policy, access_token):
    """Enrich policy JSON with group display names for better AI explanations"""
    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Helper to batch lookup group names
        def lookup_group_names(group_ids):
            if not group_ids:
                return []
            
            group_info = []
            for group_id in group_ids:
                try:
                    response = requests.get(
                        f'https://graph.microsoft.com/v1.0/groups/{group_id}?$select=id,displayName',
                        headers=headers,
                        verify=get_verify_ssl(),
                        timeout=5
                    )
                    if response.status_code == 200:
                        group_data = response.json()
                        group_info.append({
                            'id': group_id,
                            'displayName': group_data.get('displayName', group_id)
                        })
                    else:
                        # Keep ID if lookup fails
                        group_info.append({
                            'id': group_id,
                            'displayName': group_id
                        })
                except Exception as e:
                    logger.warning(f"Failed to lookup group {group_id}: {str(e)}")
                    group_info.append({
                        'id': group_id,
                        'displayName': group_id
                    })
            return group_info
        
        # Enrich includeGroups and excludeGroups
        if 'conditions' in policy and 'users' in policy['conditions']:
            users = policy['conditions']['users']
            
            if 'includeGroups' in users and users['includeGroups']:
                users['includeGroupsWithNames'] = lookup_group_names(users['includeGroups'])
            
            if 'excludeGroups' in users and users['excludeGroups']:
                users['excludeGroupsWithNames'] = lookup_group_names(users['excludeGroups'])
        
        return policy
    except Exception as e:
        logger.warning(f"Failed to enrich policy with group names: {str(e)}")
        return policy  # Return original policy if enrichment fails

@app.route('/api/policies/<policy_id>/explain', methods=['GET'])
def explain_policy(policy_id):
    """Get AI explanation of a policy"""
    if not session.get('access_token'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Get the policy from Graph API
        headers = {
            'Authorization': f"Bearer {session.get('access_token')}",
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{app.config['GRAPH_ENDPOINT']}/identity/conditionalAccess/policies/{policy_id}",
            headers=headers,
            verify=get_verify_ssl()
        )
        
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch policy', 'details': response.text}), response.status_code
        
        policy = response.json()
        
        # Enrich policy with group display names for better AI explanations
        policy = enrich_policy_with_group_names(policy, session.get('access_token'))
        
        # Get AI explanation
        if ai_assistant and ai_assistant.ai_enabled:
            import time
            start_time = time.time()
            
            explanation = ai_assistant.explain_policy(policy)
            
            response_time = time.time() - start_time
            
            # Track usage if we got token info (only for real AI responses)
            if explanation.get('ai_enabled') and explanation.get('usage'):
                usage = explanation['usage']
                update_ai_stats(
                    tokens_input=usage.get('prompt_tokens', 0),
                    tokens_output=usage.get('completion_tokens', 0),
                    response_time=response_time
                )
                
                # Add usage stats to response
                stats = get_ai_stats()
                explanation['session_stats'] = {
                    'total_explanations': stats['explanations'],
                    'total_tokens': stats['tokens_used'],
                    'total_cost': round(stats['total_cost'], 4),
                    'avg_response_time': round(sum(stats['response_times']) / len(stats['response_times']), 2) if stats['response_times'] else 0
                }
        else:
            explanation = {
                'explanation': '**AI Features Not Enabled**\n\nTo enable AI policy explanations:\n\n1. Set `AI_ENABLED=true` in your .env file\n2. Configure AI provider (Azure OpenAI recommended)\n3. Add your API credentials\n4. Restart the application\n\nSee the documentation for setup instructions.',
                'impact': '',
                'recommendations': [],
                'ai_enabled': False
            }
        
        return jsonify(explanation)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/stats', methods=['GET'])
def get_ai_statistics():
    """Get AI usage statistics for current session"""
    stats = get_ai_stats()
    
    return jsonify({
        'explanations': stats['explanations'],
        'tokens_used': stats['tokens_used'],
        'total_cost': round(stats['total_cost'], 4),
        'avg_response_time': round(sum(stats['response_times']) / len(stats['response_times']), 2) if stats['response_times'] else 0,
        'ai_enabled': ai_assistant and ai_assistant.ai_enabled if ai_assistant else False
    })

@app.route('/api/named-locations', methods=['GET'])
def get_named_locations():
    """Get all Conditional Access named locations"""
    if not session.get('access_token'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        headers = {
            'Authorization': f"Bearer {session.get('access_token')}",
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{app.config['GRAPH_ENDPOINT']}/identity/conditionalAccess/namedLocations",
            headers=headers,
            verify=get_verify_ssl()
        )
        
        if response.status_code != 200:
            return jsonify({
                'error': 'Failed to fetch named locations',
                'status': response.status_code,
                'details': response.text
            }), response.status_code
        
        locations_data = response.json().get('value', [])
        
        # Normalize different location types
        normalized_locations = []
        for loc in locations_data:
            loc_type = loc.get('@odata.type', '')
            
            if 'ipNamedLocation' in loc_type:
                normalized_locations.append({
                    'id': loc.get('id'),
                    'displayName': loc.get('displayName'),
                    'type': 'IP Ranges',
                    'isTrusted': loc.get('isTrusted', False),
                    'ipRanges': [r.get('cidrAddress') for r in loc.get('ipRanges', [])],
                    'countriesAndRegions': [],
                    'includeUnknownCountriesAndRegions': False
                })
            elif 'countryNamedLocation' in loc_type:
                normalized_locations.append({
                    'id': loc.get('id'),
                    'displayName': loc.get('displayName'),
                    'type': 'Countries/Regions',
                    'isTrusted': False,
                    'ipRanges': [],
                    'countriesAndRegions': loc.get('countriesAndRegions', []),
                    'includeUnknownCountriesAndRegions': loc.get('includeUnknownCountriesAndRegions', False)
                })
            else:
                # Unknown type - include anyway
                normalized_locations.append({
                    'id': loc.get('id'),
                    'displayName': loc.get('displayName'),
                    'type': 'Unknown',
                    'isTrusted': loc.get('isTrusted', False),
                    'ipRanges': [],
                    'countriesAndRegions': [],
                    'includeUnknownCountriesAndRegions': False
                })
        
        return jsonify({'locations': normalized_locations})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/policies/bulk-delete', methods=['POST'])
def bulk_delete_policies():
    """Delete multiple policies - supports both client credentials and delegated auth"""
    try:
        policy_ids = request.json.get('policy_ids', [])
        
        success_count = 0
        errors = []
        
        # Check if using delegated auth
        if session.get('auth_method') == 'delegated' and session.get('access_token'):
            # Use delegated token directly
            headers = {
                'Authorization': f'Bearer {session["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            for policy_id in policy_ids:
                try:
                    response = requests.delete(
                        f'https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/{policy_id}',
                        headers=headers,
                        verify=get_verify_ssl()
                    )
                    
                    if response.status_code in [200, 204]:
                        success_count += 1
                    else:
                        errors.append(f"Failed to delete {policy_id}: {response.status_code}")
                except Exception as e:
                    errors.append(f"Failed to delete {policy_id}: {str(e)}")
        else:
            # Use client credentials manager
            manager = get_manager()
            if not manager:
                return jsonify({'success': False, 'error': 'Not connected'}), 401
            
            for policy_id in policy_ids:
                try:
                    manager.delete_policy(policy_id)
                    success_count += 1
                except Exception as e:
                    errors.append(f"Failed to delete {policy_id}: {str(e)}")
        
        return jsonify({
            'success': True,
            'deleted': success_count,
            'total': len(policy_ids),
            'errors': errors,
            'message': f'Deleted {success_count} of {len(policy_ids)} policies'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def resolve_group_names_to_ids(policy_data, access_token):
    """Replace group names with Object IDs in policy data"""
    import copy
    policy = copy.deepcopy(policy_data)
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Helper to resolve a list of group names
    def resolve_groups(group_list):
        if not group_list:
            return []
        
        resolved = []
        for group_name in group_list:
            # If already a GUID, keep it
            if len(group_name) == 36 and '-' in group_name:
                resolved.append(group_name)
                continue
            
            # Look up group by name
            try:
                response = requests.get(
                    f'https://graph.microsoft.com/v1.0/groups?$filter=displayName eq \'{group_name}\'&$select=id,displayName',
                    headers=headers,
                    verify=get_verify_ssl()
                )
                if response.status_code == 200:
                    groups = response.json().get('value', [])
                    if groups:
                        resolved.append(groups[0]['id'])
                    else:
                        print(f"⚠️  Group not found: {group_name}")
                        resolved.append(group_name)  # Keep original if not found
                else:
                    print(f"⚠️  Failed to lookup group {group_name}: {response.status_code}")
                    resolved.append(group_name)
            except Exception as e:
                print(f"⚠️  Error looking up group {group_name}: {str(e)}")
                resolved.append(group_name)
        
        return resolved
    
    # Resolve groups in conditions.users
    if 'conditions' in policy and 'users' in policy['conditions']:
        users = policy['conditions']['users']
        
        if 'includeGroups' in users:
            users['includeGroups'] = resolve_groups(users['includeGroups'])
        
        if 'excludeGroups' in users:
            users['excludeGroups'] = resolve_groups(users['excludeGroups'])
    
    return policy

def validate_and_clean_applications(policy_data, access_token):
    """Validate and remove invalid application IDs from policy before deployment"""
    import copy
    policy = copy.deepcopy(policy_data)
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Well-known Microsoft apps that always exist
    well_known_apps = {
        "00000003-0000-0000-c000-000000000000": "Microsoft Graph",
        "0000000a-0000-0000-c000-000000000000": "Microsoft Intune (MAM/MDM)"
    }
    
    def validate_app_id(app_id):
        """Check if an application exists in the tenant"""
        try:
            if app_id in well_known_apps:
                return True
            
            # Check if service principal exists
            response = requests.get(
                f'https://graph.microsoft.com/v1.0/servicePrincipals?$filter=appId eq \'{app_id}\'',
                headers=headers,
                verify=get_verify_ssl()
            )
            
            if response.status_code == 200:
                result = response.json()
                exists = len(result.get("value", [])) > 0
                if not exists:
                    print(f"⚠️  Application {app_id} not found in tenant")
                return exists
            else:
                print(f"⚠️  Failed to validate app {app_id}: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error validating app {app_id}: {e}")
            return False
    
    try:
        exclude_apps = policy.get("conditions", {}).get("applications", {}).get("excludeApplications", [])
        
        if exclude_apps:
            print(f"🔍 Validating {len(exclude_apps)} excluded applications...")
            valid_apps = []
            
            for app_id in exclude_apps:
                if validate_app_id(app_id):
                    valid_apps.append(app_id)
                else:
                    print(f"   ⚠️  Removing invalid app: {app_id}")
            
            if valid_apps:
                policy["conditions"]["applications"]["excludeApplications"] = valid_apps
                print(f"   ✅ Kept {len(valid_apps)} valid excluded applications")
            else:
                # Remove excludeApplications key if no valid apps remain
                del policy["conditions"]["applications"]["excludeApplications"]
                print(f"   ℹ️  Removed excludeApplications (no valid apps)")
    
    except Exception as e:
        print(f"⚠️  Error cleaning policy applications: {e}")
    
    return policy

@app.route('/api/templates', methods=['GET'])
def list_templates():
    """Get all policy templates"""
    try:
        templates = []
        
        for category, category_templates in POLICY_TEMPLATES.items():
            for template_name, template in category_templates.items():
                templates.append({
                    'category': category,
                    'name': template_name,
                    'display_name': template.get('displayName', template_name),
                    'state': template.get('state', 'Unknown'),
                    'template': template
                })
        
        return jsonify({
            'success': True,
            'templates': templates,
            'count': len(templates),
            'categories': list(POLICY_TEMPLATES.keys())
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/templates/deploy', methods=['POST'])
def deploy_template():
    """Deploy a policy template - supports both client credentials and delegated auth"""
    try:
        template_data = request.json.get('template')
        if not template_data:
            return jsonify({'success': False, 'error': 'No template provided'}), 400
        
        policy_name = template_data.get('displayName', '')
        
        # Check if using delegated auth
        if session.get('auth_method') == 'delegated' and session.get('access_token'):
            # Resolve group names to IDs
            template_data = resolve_group_names_to_ids(template_data, session['access_token'])
            
            # Validate and clean application IDs
            template_data = validate_and_clean_applications(template_data, session['access_token'])
            
            # Use delegated token directly
            headers = {
                'Authorization': f'Bearer {session["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            # Check if a policy with the same name already exists
            check_response = requests.get(
                'https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies',
                headers=headers,
                verify=get_verify_ssl()
            )
            
            if check_response.status_code == 200:
                existing_policies = check_response.json().get('value', [])
                duplicate = next((p for p in existing_policies if p.get('displayName') == policy_name), None)
                
                if duplicate:
                    return jsonify({
                        'success': False,
                        'error': f'A policy with the name "{policy_name}" already exists. Please delete the existing policy first or rename the template.',
                        'duplicate_policy_id': duplicate.get('id')
                    }), 409  # 409 Conflict
            
            response = requests.post(
                'https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies',
                headers=headers,
                json=template_data,
                verify=get_verify_ssl()
            )
            
            if response.status_code in [200, 201]:
                policy = response.json()
                return jsonify({
                    'success': True,
                    'policy': policy,
                    'message': 'Template deployed successfully'
                })
            else:
                return jsonify({
                    'success': False, 
                    'error': f'Failed to deploy template: {response.status_code} - {response.text}'
                }), response.status_code
        
        # Otherwise use client credentials manager
        manager = get_manager()
        if not manager:
            return jsonify({'success': False, 'error': 'Not connected'}), 401
        
        # Check for duplicate policy name with client credentials
        try:
            existing_policies = manager.list_policies()
            duplicate = next((p for p in existing_policies if p.get('displayName') == policy_name), None)
            
            if duplicate:
                return jsonify({
                    'success': False,
                    'error': f'A policy with the name "{policy_name}" already exists. Please delete the existing policy first or rename the template.',
                    'duplicate_policy_id': duplicate.get('id')
                }), 409  # 409 Conflict
        except Exception as check_error:
            # If we can't check for duplicates, log it but proceed
            print(f"Warning: Could not check for duplicate policies: {check_error}")
        
        result = manager.create_policy(template_data)
        
        return jsonify({
            'success': True,
            'policy': result,
            'message': 'Template deployed successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/templates/deploy-all', methods=['POST'])
def deploy_all_templates():
    """Deploy all templates in a category or all - supports both client credentials and delegated auth"""
    try:
        category = request.json.get('category')
        
        success_count = 0
        errors = []
        skipped_count = 0
        
        if category and category in POLICY_TEMPLATES:
            templates_to_deploy = POLICY_TEMPLATES[category]
        else:
            # Deploy all templates
            templates_to_deploy = {}
            for cat_templates in POLICY_TEMPLATES.values():
                templates_to_deploy.update(cat_templates)
        
        # Check if using delegated auth
        if session.get('auth_method') == 'delegated' and session.get('access_token'):
            # Use delegated token directly
            headers = {
                'Authorization': f'Bearer {session["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            # Get existing policies once for efficiency
            check_response = requests.get(
                'https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies',
                headers=headers,
                verify=get_verify_ssl()
            )
            existing_policies = check_response.json().get('value', []) if check_response.status_code == 200 else []
            existing_names = {p.get('displayName') for p in existing_policies}
            
            for template_name, template in templates_to_deploy.items():
                try:
                    policy_name = template.get('displayName', '')
                    
                    # Skip if duplicate
                    if policy_name in existing_names:
                        skipped_count += 1
                        errors.append(f"Skipped {policy_name}: Already exists")
                        continue
                    
                    response = requests.post(
                        'https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies',
                        headers=headers,
                        json=template,
                        verify=get_verify_ssl()
                    )
                    
                    if response.status_code in [200, 201]:
                        success_count += 1
                        existing_names.add(policy_name)  # Add to set to prevent duplicates in same batch
                    else:
                        errors.append(f"Failed to deploy {template_name}: {response.status_code}")
                except Exception as e:
                    errors.append(f"Failed to deploy {template_name}: {str(e)}")
        else:
            # Use client credentials manager
            manager = get_manager()
            if not manager:
                return jsonify({'success': False, 'error': 'Not connected'}), 401
            
            # Get existing policies once for efficiency
            try:
                existing_policies = manager.list_policies()
                existing_names = {p.get('displayName') for p in existing_policies}
            except Exception:
                existing_names = set()
            
            for template_name, template in templates_to_deploy.items():
                try:
                    policy_name = template.get('displayName', '')
                    
                    # Skip if duplicate
                    if policy_name in existing_names:
                        skipped_count += 1
                        errors.append(f"Skipped {policy_name}: Already exists")
                        continue
                    
                    manager.create_policy(template)
                    success_count += 1
                    existing_names.add(policy_name)  # Add to set to prevent duplicates in same batch
                except Exception as e:
                    errors.append(f"Failed to deploy {template_name}: {str(e)}")
        
        return jsonify({
            'success': True,
            'deployed': success_count,
            'skipped': skipped_count,
            'total': len(templates_to_deploy),
            'errors': errors,
            'message': f'Deployed {success_count} of {len(templates_to_deploy)} templates' + (f' ({skipped_count} skipped - already exist)' if skipped_count > 0 else '')
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/groups/create-ca-groups', methods=['POST'])
def create_ca_groups():
    """Create all required CA policy groups - supports both client credentials and delegated auth"""
    try:
        # Define all required groups
        persona_groups = [
            {'name': 'CA-BreakGlassAccounts', 'description': 'Emergency break-glass admin accounts excluded from all CA policies'},
            {'name': 'CA-Persona-Admins', 'description': 'Administrative users persona group for CA policies'},
            {'name': 'CA-Persona-Internals', 'description': 'Internal employees persona group for CA policies'},
            {'name': 'CA-Persona-Externals', 'description': 'External contractors/consultants persona group for CA policies'},
            {'name': 'CA-Persona-Guests', 'description': 'Guest users (B2B) persona group for CA policies'},
            {'name': 'CA-Persona-GuestAdmins', 'description': 'Guest administrators persona group for CA policies'},
            {'name': 'CA-Persona-Microsoft365ServiceAccounts', 'description': 'Microsoft 365 service accounts persona group for CA policies'},
            {'name': 'CA-Persona-AzureServiceAccounts', 'description': 'Azure service accounts persona group for CA policies'},
            {'name': 'CA-Persona-CorpServiceAccounts', 'description': 'Corporate service accounts persona group for CA policies'},
            {'name': 'CA-Persona-WorkloadIdentities', 'description': 'Workload identities persona group for CA policies'},
            {'name': 'CA-Persona-Developers', 'description': 'Developer users persona group for CA policies'}
        ]
        
        # Define exclusion groups for each persona and policy type
        exclusion_groups = []
        personas = ['Admins', 'Internals', 'Externals', 'Guests', 'GuestAdmins', 
                   'Microsoft365ServiceAccounts', 'AzureServiceAccounts', 'CorpServiceAccounts', 
                   'WorkloadIdentities', 'Developers']
        policy_types = ['BaseProtection', 'IdentityProtection', 'DataandAppProtection', 
                       'AttackSurfaceReduction', 'Compliance']
        
        for persona in personas:
            for policy_type in policy_types:
                exclusion_groups.append({
                    'name': f'CA-Persona-{persona}-{policy_type}-Exclusions',
                    'description': f'Exclusions for {persona} {policy_type} CA policies'
                })
        
        all_groups = persona_groups + exclusion_groups
        
        created_count = 0
        skipped_count = 0
        errors = []
        
        # Check if using delegated auth
        if session.get('auth_method') == 'delegated' and session.get('access_token'):
            headers = {
                'Authorization': f'Bearer {session["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            for group in all_groups:
                try:
                    # Check if group already exists
                    check_response = requests.get(
                        f'https://graph.microsoft.com/v1.0/groups?$filter=displayName eq \'{group["name"]}\'',
                        headers=headers,
                        verify=get_verify_ssl()
                    )
                    
                    if check_response.status_code == 200:
                        existing = check_response.json().get('value', [])
                        if existing:
                            skipped_count += 1
                            continue
                    
                    # Create the group
                    group_data = {
                        'displayName': group['name'],
                        'mailNickname': group['name'].replace('-', ''),
                        'description': group['description'],
                        'mailEnabled': False,
                        'securityEnabled': True
                    }
                    
                    response = requests.post(
                        'https://graph.microsoft.com/v1.0/groups',
                        headers=headers,
                        json=group_data,
                        verify=get_verify_ssl()
                    )
                    
                    if response.status_code == 201:
                        created_count += 1
                    else:
                        errors.append(f"Failed to create {group['name']}: {response.status_code} - {response.text}")
                        
                except Exception as e:
                    errors.append(f"Error creating {group['name']}: {str(e)}")
        else:
            # Use client credentials - not implemented in original manager, will need Graph API calls
            return jsonify({
                'success': False, 
                'error': 'Group creation requires delegated authentication. Please sign in with Entra ID first.'
            }), 400
        
        return jsonify({
            'success': True,
            'created': created_count,
            'skipped': skipped_count,
            'total': len(all_groups),
            'errors': errors,
            'message': f'Created {created_count} groups, skipped {skipped_count} existing groups'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/report/upload', methods=['POST'])
def upload_report():
    """Upload security assessment report"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Validate file size
        file_content = file.read()
        if len(file_content) > app.config['MAX_CONTENT_LENGTH']:
            return jsonify({
                'success': False, 
                'error': f'File too large (max {app.config["MAX_CONTENT_LENGTH"] / 1024 / 1024}MB)'
            }), 413
        
        file.seek(0)  # Reset file pointer
        
        # Validate file extension
        filename = secure_filename(file.filename)
        _, ext = os.path.splitext(filename)
        
        if ext.lower() not in app.config['ALLOWED_EXTENSIONS']:
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Allowed: {", ".join(app.config["ALLOWED_EXTENSIONS"])}'
            }), 400
        
        # Validate MIME type
        mime_type = file.content_type
        if mime_type not in app.config['ALLOWED_MIMETYPES']:
            return jsonify({
                'success': False,
                'error': 'Invalid file type'
            }), 400
        
        # Save file
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        session['report_path'] = filepath
        
        logger.info(f"Uploaded report: {filename}")
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'Report uploaded successfully'
        })
        
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        return safe_error_response(str(e), 'UPLOAD_FAILED', 500)

@app.route('/api/report/analyze', methods=['POST'])
def analyze_report():
    """Analyze uploaded security report"""
    try:
        report_path = session.get('report_path')
        
        if not report_path or not os.path.exists(report_path):
            return jsonify({'success': False, 'error': 'No report uploaded'}), 400
        
        # Create analyzer
        analyzer = SecurityReportAnalyzer(report_path)
        
        # Parse and extract findings
        if not analyzer.parse_html():
            return jsonify({'success': False, 'error': 'Failed to parse report'}), 500
        
        findings = analyzer.extract_findings()
        stats = analyzer.get_statistics()
        
        # Debug: Show first few findings with their mapped policies
        print(f"\n🔍 Checking first 3 findings:")
        for i, finding in enumerate(findings[:3]):
            print(f"  Finding {i+1}: {finding['title'][:80]}")
            print(f"    Mapped policies: {finding.get('mapped_policies', [])}")
        
        # Get recommendations
        import ca_policy_examples
        print(f"📊 Policy templates available: {list(ca_policy_examples.POLICY_TEMPLATES.keys())}")
        print(f"📊 Total templates: {sum(len(v) for v in ca_policy_examples.POLICY_TEMPLATES.values())}")
        
        try:
            recommendations = analyzer.get_policy_recommendations(ca_policy_examples)
            print(f"📊 Generated {len(recommendations)} recommendations")
            if recommendations:
                print(f"📊 Sample recommendation: {recommendations[0]['policy_display_name']}")
        except Exception as e:
            print(f"❌ Error in get_policy_recommendations: {e}")
            import traceback
            traceback.print_exc()
            recommendations = []
        
        # Store minimal data in session (session cookie has 4KB limit)
        # Only store IDs/indices for findings, not full data
        session['findings_count'] = len(findings)
        session['recommendations_count'] = len(recommendations)
        session['stats'] = stats
        
        return jsonify({
            'success': True,
            'findings': findings,
            'recommendations': recommendations,
            'stats': stats,
            'message': f'Analyzed report: {len(findings)} findings, {len(recommendations)} recommendations'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/report/deploy-recommendations', methods=['POST'])
def deploy_recommendations():
    """Deploy selected recommendations from report"""
    try:
        manager = get_manager()
        if not manager:
            return jsonify({'success': False, 'error': 'Not connected'}), 401
        
        recommendation_indices = request.json.get('indices', [])
        recommendations = session.get('recommendations', [])
        
        if not recommendations:
            return jsonify({'success': False, 'error': 'No recommendations available'}), 400
        
        success_count = 0
        errors = []
        
        for idx in recommendation_indices:
            if 0 <= idx < len(recommendations):
                rec = recommendations[idx]
                template = rec.get('template')
                
                if template:
                    try:
                        manager.create_policy(template)
                        success_count += 1
                    except Exception as e:
                        errors.append(f"Failed to deploy {rec.get('policy_display_name')}: {str(e)}")
        
        return jsonify({
            'success': True,
            'deployed': success_count,
            'total': len(recommendation_indices),
            'errors': errors,
            'message': f'Deployed {success_count} of {len(recommendation_indices)} recommendations'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/report/export', methods=['GET'])
def export_findings():
    """Export findings to Excel"""
    try:
        findings = session.get('findings', [])
        recommendations = session.get('recommendations', [])
        
        if not findings:
            return jsonify({'success': False, 'error': 'No findings available'}), 400
        
        try:
            import pandas as pd
        except ImportError:
            return jsonify({'success': False, 'error': 'Excel export requires pandas (optional dependency not installed)'}), 500
        
        # Create temporary Excel file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        
        # Create DataFrame
        df_findings = pd.DataFrame(findings)
        df_recommendations = pd.DataFrame(recommendations) if recommendations else pd.DataFrame()
        
        # Write to Excel
        with pd.ExcelWriter(temp_file.name, engine='openpyxl') as writer:
            df_findings.to_excel(writer, sheet_name='Findings', index=False)
            if not df_recommendations.empty:
                df_recommendations.to_excel(writer, sheet_name='Recommendations', index=False)
        
        return send_file(
            temp_file.name,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'security_findings_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    manager = get_manager()
    return jsonify({
        'success': True,
        'connected': manager is not None,
        'session_id': session.get('id')
    })

@app.route('/api/user/info', methods=['GET'])
def get_user_info():
    """Get current user information"""
    try:
        # Check if using delegated auth
        if session.get('auth_method') == 'delegated' and session.get('access_token'):
            headers = {
                'Authorization': f'Bearer {session["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            # Get user profile from Microsoft Graph
            user_response = requests.get(
                'https://graph.microsoft.com/v1.0/me',
                headers=headers,
                verify=get_verify_ssl()
            )
            
            # Get organization info
            org_response = requests.get(
                'https://graph.microsoft.com/v1.0/organization',
                headers=headers,
                verify=get_verify_ssl()
            )
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                org_data = org_response.json() if org_response.status_code == 200 else {}
                
                org_info = org_data.get('value', [{}])[0] if org_data.get('value') else {}
                
                return jsonify({
                    'success': True,
                    'user': {
                        'displayName': user_data.get('displayName'),
                        'userPrincipalName': user_data.get('userPrincipalName'),
                        'mail': user_data.get('mail'),
                        'id': user_data.get('id')
                    },
                    'tenant': {
                        'id': org_info.get('id'),
                        'displayName': org_info.get('displayName'),
                        'tenantType': org_info.get('tenantType')
                    }
                })
            else:
                return jsonify({'success': False, 'error': 'Unable to retrieve user info'}), 401
        else:
            return jsonify({
                'success': False,
                'error': 'Not authenticated with delegated credentials'
            }), 401
            
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/favicon.ico')
def favicon():
    """Return 204 for favicon to prevent 500 errors"""
    return '', 204

if __name__ == '__main__':
    # DEVELOPMENT ONLY
    # For production, use gunicorn or waitress:
    #   gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
    # 
    # Set environment: FLASK_ENV=production
    # Or in Azure App Service, set startup command to:
    #   gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
    
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5000))
    
    if debug_mode:
        logger.warning("⚠️  Running in DEVELOPMENT mode - do not use in production!")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode,
        use_reloader=debug_mode
    )
