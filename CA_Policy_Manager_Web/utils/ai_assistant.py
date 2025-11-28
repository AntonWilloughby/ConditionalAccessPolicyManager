"""
AI Assistant for Conditional Access Policy Analysis
Supports Azure OpenAI, OpenAI, and local models
"""

import os
import json
from typing import Dict, Any, Optional

class PolicyAIAssistant:
    """AI-powered assistant for CA policy analysis and explanation"""
    
    def __init__(self, config):
        self.config = config
        self.ai_enabled = config.get('AI_ENABLED', False)
        self.provider = config.get('AI_PROVIDER', 'azure')
        self.client = None
        
        if self.ai_enabled:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate AI client based on provider"""
        try:
            if self.provider == 'azure':
                from openai import AzureOpenAI
                
                # Only pass supported parameters to avoid issues
                client_params = {
                    'api_key': self.config['AZURE_OPENAI_API_KEY'],
                    'api_version': self.config['AZURE_OPENAI_API_VERSION'],
                    'azure_endpoint': self.config['AZURE_OPENAI_ENDPOINT']
                }
                
                self.client = AzureOpenAI(**client_params)
                self.model = self.config['AZURE_OPENAI_DEPLOYMENT']
                print(f"✨ AI Assistant initialized (Azure OpenAI - {self.model})")
            
            elif self.provider == 'openai':
                from openai import OpenAI
                self.client = OpenAI(api_key=self.config['OPENAI_API_KEY'])
                self.model = self.config['OPENAI_MODEL']
                print(f"✨ AI Assistant initialized (OpenAI - {self.model})")
            
            elif self.provider == 'local':
                # For local models like Ollama
                try:
                    import ollama
                    self.client = ollama
                    self.model = self.config.get('LOCAL_MODEL', 'phi3')
                    print(f"✨ AI Assistant initialized (Local - {self.model})")
                except ImportError:
                    print("⚠️  Ollama not installed. Install with: pip install ollama")
                    self.ai_enabled = False
        
        except Exception as e:
            print(f"⚠️  Failed to initialize AI client: {e}")
            self.ai_enabled = False
    
    def explain_policy(self, policy_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a plain-English explanation of a Conditional Access policy
        
        Args:
            policy_json: The CA policy JSON object
            
        Returns:
            Dictionary with explanation, impact, and recommendations
        """
        if not self.ai_enabled or not self.client:
            return {
                'explanation': 'AI features are not enabled. To enable:\n\n1. Set AI_ENABLED=true in .env\n2. Configure AI provider (Azure OpenAI or OpenAI)\n3. Add API keys\n4. Restart the application',
                'impact': '',
                'recommendations': [],
                'ai_enabled': False
            }
        
        try:
            # Build the prompt
            prompt = self._build_explanation_prompt(policy_json)
            
            # Call AI service
            if self.provider in ['azure', 'openai']:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": self._get_system_prompt()
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=3000
                )
                result_text = response.choices[0].message.content
                
                # Extract usage information
                usage_info = {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            
            elif self.provider == 'local':
                response = self.client.chat(
                    model=self.model,
                    messages=[
                        {
                            'role': 'system',
                            'content': self._get_system_prompt()
                        },
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ]
                )
                result_text = response['message']['content']
                usage_info = None  # Local models don't track tokens
            
            # Parse the response
            result = self._parse_explanation_response(result_text)
            
            # Add usage information if available
            if self.provider in ['azure', 'openai'] and usage_info:
                result['usage'] = usage_info
            
            return result
        
        except Exception as e:
            return {
                'explanation': f'Error generating explanation: {str(e)}',
                'impact': '',
                'recommendations': [],
                'ai_enabled': True,
                'error': str(e)
            }
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI assistant"""
        return """You are an expert in Microsoft Entra ID (Azure AD) Conditional Access policies. 
Your job is to explain complex security policies in simple, business-friendly language.

When explaining a policy:
1. Start with a one-sentence summary of what the policy does
2. Explain WHO it affects (which users/groups) with specific examples
3. Explain WHEN it applies (conditions like platforms, locations, sign-in risk) with detailed scenarios
4. Explain WHAT happens (grant controls or blocks) and the technical reasoning
5. Describe the BUSINESS IMPACT with concrete examples of how users experience this in their daily work
6. Suggest IMPROVEMENTS with specific recommendations and rationale

Be thorough and detailed in your explanations. Provide specific examples and scenarios to illustrate each point.
Explain not just WHAT the policy does, but WHY it matters and HOW it affects the organization.
Include practical examples of user workflows and how they're impacted.
Format your response with clear sections using **bold** for headers.
Aim for comprehensive explanations that help stakeholders fully understand the policy's purpose and impact."""
    
    def _build_explanation_prompt(self, policy_json: Dict[str, Any]) -> str:
        """Build the prompt for policy explanation"""
        return f"""Explain this Conditional Access policy in plain English:

Policy Name: {policy_json.get('displayName', 'Unnamed Policy')}
State: {policy_json.get('state', 'unknown')}

Configuration:
{json.dumps(policy_json, indent=2)}

IMPORTANT: When referencing groups, use the displayName from the 'includeGroupsWithNames' or 'excludeGroupsWithNames' arrays if available, NOT the group IDs.
For example, if you see:
  "includeGroupsWithNames": [{{"id": "abc-123", "displayName": "External Users"}}]
Then refer to the group as "External Users" (not the ID abc-123).

Provide your response in this format:

**Summary:** (one sentence explaining what this policy does)

**Who it affects:**
- (list the users, groups, or roles using their display names, not IDs)

**When it applies:**
- (list all conditions: platforms, apps, locations, risks, etc.)

**What happens:**
- (describe the grant controls, blocks, or session controls)

**User impact:**
- (describe in detail how users will experience this policy in their daily work)
- (provide specific scenarios and examples of affected workflows)
- (explain both positive security benefits and potential friction points)

**Recommendations:**
- (provide detailed suggestions for improvements, security enhancements, or potential issues)
- (explain the rationale behind each recommendation)
- (include best practices and industry standards where applicable)
"""
    
    def _parse_explanation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the AI response into structured data"""
        sections = {
            'explanation': '',
            'impact': '',
            'recommendations': [],
            'ai_enabled': True
        }
        
        lines = response_text.split('\n')
        current_section = 'explanation'
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # Detect section headers
            if '**User impact:**' in line_stripped or '**User Impact:**' in line_stripped:
                current_section = 'impact'
                continue
            elif '**Recommendations:**' in line_stripped or '**Recommendation:**' in line_stripped:
                current_section = 'recommendations'
                continue
            
            # Add content to appropriate section
            if current_section == 'explanation':
                sections['explanation'] += line + '\n'
            elif current_section == 'impact':
                sections['impact'] += line + '\n'
            elif current_section == 'recommendations':
                if line_stripped.startswith('-') or line_stripped.startswith('•') or line_stripped.startswith('*'):
                    sections['recommendations'].append(line_stripped[1:].strip())
                elif line_stripped and not line_stripped.startswith('**'):
                    sections['recommendations'].append(line_stripped)
        
        sections['explanation'] = sections['explanation'].strip()
        sections['impact'] = sections['impact'].strip()
        
        return sections
