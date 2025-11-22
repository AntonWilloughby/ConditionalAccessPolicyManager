#!/usr/bin/env python3
"""
Flask Web Application for Conditional Access Policy Manager
Supports both local development and Azure App Service deployment
"""

from flask import Flask, render_template, request, jsonify, session, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import os
import sys
import json
import tempfile
from datetime import datetime
import msal
import requests
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Import modules from current directory
from ca_policy_manager import ConditionalAccessManager
from ca_policy_examples import POLICY_TEMPLATES
from utils.report_analyzer import SecurityReportAnalyzer
from utils.ai_assistant import PolicyAIAssistant
from config import get_config

# Initialize Flask app
app = Flask(__name__)

# Load configuration based on environment
app.config.from_object(get_config())

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
        print(f"⚠️  Failed to initialize AI Assistant: {e}")
        print("   AI features will be disabled")
else:
    print("ℹ️  AI features disabled (set AI_ENABLED=true in .env to enable)")

# Security: Disable SSL verification warning if explicitly disabled in development
if not app.config.get('VERIFY_SSL', True):
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    print("⚠️  WARNING: SSL verification disabled - for development only!")
    print("   Enable SSL verification for production deployment.")

# Store manager instances per session (in production, use Redis or similar)
managers = {}

# AI usage tracking per session
ai_usage_stats = {}

def get_verify_ssl():
    """Get SSL verification setting from config"""
    return app.config.get('VERIFY_SSL', True)

def get_ai_stats():
    """Get or initialize AI usage stats for current session"""
    session_id = session.get('id')
    if not session_id:
        session['id'] = os.urandom(16).hex()
        session_id = session['id']
    
    if session_id not in ai_usage_stats:
        ai_usage_stats[session_id] = {
            'explanations': 0,
            'tokens_used': 0,
            'total_cost': 0.0,
            'response_times': []
        }
    
    return ai_usage_stats[session_id]

def update_ai_stats(tokens_input, tokens_output, response_time):
    """Update AI usage statistics"""
    stats = get_ai_stats()
    stats['explanations'] += 1
    stats['tokens_used'] += tokens_input + tokens_output
    
    # Azure OpenAI gpt-4o-mini pricing (as of 2024)
    # Input: $0.15 per 1M tokens, Output: $0.60 per 1M tokens
    input_cost = (tokens_input / 1_000_000) * 0.15
    output_cost = (tokens_output / 1_000_000) * 0.60
    stats['total_cost'] += input_cost + output_cost
    
    stats['response_times'].append(response_time)
    
    return stats

def get_manager():
    """Get or create manager for current session"""
    session_id = session.get('id')
    if not session_id:
        session['id'] = os.urandom(16).hex()
        session_id = session['id']
    
    if session_id not in managers:
        managers[session_id] = None
    
    return managers[session_id]

def set_manager(manager):
    """Store manager for current session"""
    session_id = session.get('id')
    if not session_id:
        session['id'] = os.urandom(16).hex()
        session_id = session['id']
    
    managers[session_id] = manager

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/auth/login', methods=['GET'])
def auth_login():
    """Initiate Entra ID authentication flow with implicit grant"""
    try:
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
    return render_template('auth_callback.html')

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
        session_id = session.get('id')
        
        # Clear the manager
        if session_id and session_id in managers:
            managers[session_id] = None
        
        # Clear session data
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
            return jsonify({'success': False, 'error': 'Missing credentials'}), 400
        
        # Create manager
        manager = ConditionalAccessManager(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
            verify_ssl=verify_ssl
        )
        
        # Authenticate first
        if not manager.authenticate():
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
        return jsonify({'success': False, 'error': str(e)}), 500

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
                return jsonify({
                    'success': True,
                    'policy': policy,
                    'message': 'Policy created successfully'
                })
            else:
                return jsonify({
                    'success': False, 
                    'error': f'Failed to create policy: {response.status_code} - {response.text}'
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
            # If we can't check for duplicates, log it but proceed
            print(f"Warning: Could not check for duplicate policies: {check_error}")
        
        result = manager.create_policy(policy_data)
        
        return jsonify({
            'success': True,
            'policy': result,
            'message': 'Policy created successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Store filepath in session
            session['report_path'] = filepath
            
            return jsonify({
                'success': True,
                'filename': filename,
                'message': 'Report uploaded successfully'
            })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
        
        import pandas as pd
        
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

if __name__ == '__main__':
    # Development server - DO NOT use in production!
    # For production, use gunicorn or waitress
    app.run(host='0.0.0.0', port=5000, debug=True)
