"""
Security Report Analyzer - Enhanced for Zero Trust Assessment Reports
Imports HTML security reports and maps recommendations to CA policies
"""

from bs4 import BeautifulSoup
import re
import json
from typing import List, Dict, Tuple

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    pd = None  # type: ignore
    PANDAS_AVAILABLE = False

class SecurityReportAnalyzer:
    """Analyzes security assessment reports and maps to CA policies."""
    
    # Enhanced mapping for Zero Trust controls - using old category names for matching
    CONTROL_MAPPINGS = {
        # Zero Trust specific
        "zero trust": ["baseline", "risk", "device"],
        "identity verification": ["mfa", "authentication", "risk"],
        "device trust": ["device", "compliance"],
        "least privilege": ["baseline", "access"],
        
        # Authentication & MFA
        "multi-factor": ["mfa", "authentication"],
        "mfa": ["mfa", "authentication"],
        "2fa": ["mfa", "authentication"],
        "authentication": ["mfa", "authentication"],
        "phishing-resistant": ["mfa", "authentication"],
        "passwordless": ["mfa", "authentication"],
        
        # Conditional Access
        "conditional access": ["baseline", "access"],
        "location-based": ["location", "access"],
        "ip-based": ["location", "access"],
        "trusted location": ["location", "access"],
        "network location": ["location", "access"],
        
        # Device compliance
        "device compliance": ["device", "compliance"],
        "compliant device": ["device", "compliance"],
        "hybrid join": ["device", "compliance"],
        "intune": ["device", "compliance"],
        "mdm": ["device", "compliance"],
        "mobile device": ["device", "compliance"],
        
        # Risk-based
        "risk-based": ["risk", "identity"],
        "identity protection": ["risk", "identity"],
        "sign-in risk": ["risk", "identity"],
        "user risk": ["risk", "identity"],
        "risky": ["risk", "identity"],
        
        # Session controls
        "session": ["session", "access"],
        "persistent browser": ["session", "access"],
        "sign-in frequency": ["session", "access"],
        
        # Application controls
        "app protection": ["application", "access"],
        "cloud app": ["application", "access"],
        "approved app": ["application", "device"],
        
        # Legacy authentication
        "legacy auth": ["baseline", "authentication"],
        "basic auth": ["baseline", "authentication"],
        "legacy protocol": ["baseline", "authentication"],
        
        # Guest access
        "guest": ["guest", "access"],
        "external": ["guest", "access"],
        "b2b": ["guest", "access"],
        
        # Admin protection
        "privileged": ["baseline", "risk"],
        "admin": ["baseline", "risk"],
        "administrator": ["baseline", "risk"],
        "elevated": ["baseline", "risk"],
    }
    
    # Map old category names to new framework category names
    CATEGORY_TRANSLATION = {
        "baseline": ["Global Policies", "Admin Policies", "Internal User Policies"],
        "mfa": ["Admin Policies", "Internal User Policies", "External User Policies"],
        "authentication": ["Admin Policies", "Internal User Policies"],
        "device": ["Admin Policies", "Internal User Policies"],
        "compliance": ["Admin Policies", "Internal User Policies"],
        "risk": ["Admin Policies", "Internal User Policies"],
        "identity": ["Admin Policies", "Internal User Policies"],
        "location": ["Admin Policies", "Internal User Policies"],
        "access": ["Admin Policies", "Internal User Policies", "External User Policies"],
        "session": ["Admin Policies", "Internal User Policies"],
        "application": ["Internal User Policies", "Service Account Policies"],
        "guest": ["Guest User Policies", "Guest Admin Policies"],
    }
    
    def __init__(self, html_path: str):
        """Initialize with path to HTML report."""
        self.html_path = html_path
        self.soup = None
        self.findings = []
        self.report_data = None
        
    def parse_html(self) -> bool:
        """Parse HTML report and extract security findings."""
        try:
            with open(self.html_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.soup = BeautifulSoup(content, 'html.parser')
                
            # Try to extract embedded JSON data from React app
            self._extract_react_data(content)
            
            return True
        except Exception as e:
            print(f"Error parsing HTML: {e}")
            return False
    
    def _extract_react_data(self, content: str):
        """Extract data from React app's embedded JSON."""
        try:
            # Look for the reportData object in script tags
            script_tags = self.soup.find_all('script')
            
            for script in script_tags:
                script_content = script.string
                if script_content and 'reportData' in script_content:
                    print("Found reportData in script!")
                    
                    # Find the reportData object - it's a massive inline object
                    # Pattern: reportData= { ... };
                    # Need to find the matching closing brace
                    start_idx = script_content.find('reportData=')
                    if start_idx == -1:
                        continue
                    
                    # Find the opening brace
                    brace_start = script_content.find('{', start_idx)
                    if brace_start == -1:
                        continue
                    
                    # Find the matching closing brace by counting
                    brace_count = 0
                    brace_end = -1
                    in_string = False
                    escape_next = False
                    
                    for i in range(brace_start, len(script_content)):
                        char = script_content[i]
                        
                        if escape_next:
                            escape_next = False
                            continue
                        
                        if char == '\\':
                            escape_next = True
                            continue
                        
                        if char == '"' and not in_string:
                            in_string = True
                        elif char == '"' and in_string:
                            in_string = False
                        elif not in_string:
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    brace_end = i
                                    break
                    
                    if brace_end != -1:
                        json_str = script_content[brace_start:brace_end+1]
                        print(f"Extracted reportData object ({len(json_str)} chars)")
                        
                        try:
                            # Try to parse as JSON
                            data = json.loads(json_str)
                            self.report_data = data
                            print(f"Successfully parsed reportData with {len(data.get('Tests', []))} tests")
                            return
                        except json.JSONDecodeError as e:
                            print(f"JSON parse error at position {e.pos}: {e.msg}")
                            # Try manual extraction of Tests array
                            self._extract_tests_from_script(script_content)
                            return
            
            print("reportData not found in script tags")
                    
        except Exception as e:
            print(f"Could not extract React data: {e}")
            import traceback
            traceback.print_exc()
    
    def _extract_tests_from_script(self, script_content: str):
        """Manually extract test objects from script when JSON parsing fails."""
        try:
            print("Attempting manual extraction of Tests array...")
            
            # Find the Tests array
            tests_match = re.search(r'"Tests"\s*:\s*\[([^\]]+)\]', script_content, re.DOTALL)
            
            if not tests_match:
                print("Could not find Tests array")
                return
            
            tests_content = tests_match.group(1)
            
            # Extract individual test objects
            test_objects = re.findall(r'\{[^{}]+\}', tests_content)
            
            tests = []
            for test_obj_str in test_objects[:50]:  # Limit to first 50 for testing
                # Extract fields manually
                test = {}
                
                # Extract common fields
                for field in ['TestTitle', 'TestStatus', 'TestDescription', 'TestResult', 
                             'TestPillar', 'TestCategory', 'TestRisk', 'TestSfiPillar']:
                    pattern = f'"{field}"\\s*:\\s*"([^"]*)"'
                    match = re.search(pattern, test_obj_str)
                    if match:
                        test[field] = match.group(1)
                
                if test.get('TestTitle'):
                    tests.append(test)
            
            print(f"Manually extracted {len(tests)} tests")
            self.report_data = {'Tests': tests}
            
        except Exception as e:
            print(f"Manual extraction error: {e}")
            import traceback
            traceback.print_exc()
    
    def extract_findings(self) -> List[Dict]:
        """Extract security findings from HTML."""
        if not self.soup:
            return []
        
        findings = []
        
        # If we extracted structured data, use it
        if self.report_data:
            findings.extend(self._parse_structured_data())
        
        # Fallback: Parse visible text content
        if not findings:
            findings.extend(self._parse_text_content())
        
        self.findings = findings
        return findings
    
    def _parse_structured_data(self) -> List[Dict]:
        """Parse structured JSON data from report."""
        findings = []
        
        if not self.report_data:
            return findings
        
        # Handle Zero Trust Assessment report with Tests array
        if 'Tests' in self.report_data:
            print(f"Found {len(self.report_data['Tests'])} tests in report")
            tests = self.report_data['Tests']
            for test in tests:
                if isinstance(test, dict):
                    finding = self._normalize_zero_trust_finding(test)
                    if finding:
                        findings.append(finding)
            print(f"Extracted {len(findings)} findings from tests")
        
        # Handle other JSON structures
        for key in ['findings', 'recommendations', 'controls', 'gaps', 'issues']:
            if key in self.report_data:
                items = self.report_data[key]
                if isinstance(items, list):
                    for item in items:
                        finding = self._normalize_finding(item)
                        if finding:
                            findings.append(finding)
                elif isinstance(items, dict):
                    for item_key, item_value in items.items():
                        finding = self._normalize_finding(item_value, title=item_key)
                        if finding:
                            findings.append(finding)
        
        return findings
    
    def _normalize_finding(self, item: Dict, title: str = None) -> Dict:
        """Normalize a finding from various formats."""
        if not isinstance(item, dict):
            return None
        
        finding = {
            'title': title or item.get('title') or item.get('name') or item.get('control') or 'Unknown',
            'description': item.get('description') or item.get('detail') or item.get('message') or '',
            'severity': self._normalize_severity(item.get('severity') or item.get('risk') or item.get('priority') or 'Medium'),
            'status': item.get('status') or item.get('state') or 'Open',
            'recommendation': item.get('recommendation') or item.get('remediation') or item.get('action') or '',
            'mapped_policies': []
        }
        
        # Map to CA policies
        search_text = f"{finding['title']} {finding['description']} {finding['recommendation']}".lower()
        finding['mapped_policies'] = self._map_to_policies(search_text)
        
        return finding
    
    def _normalize_zero_trust_finding(self, test: Dict) -> Dict:
        """Normalize a finding from Zero Trust Assessment report."""
        if not isinstance(test, dict):
            return None
        
        # Extract fields from Zero Trust format
        title = test.get('TestTitle', 'Unknown Test')
        status = test.get('TestStatus', 'Unknown')
        description = test.get('TestDescription', '')
        result = test.get('TestResult', '')
        risk = test.get('TestRisk', 'Medium')
        pillar = test.get('TestPillar', '')
        sfi_pillar = test.get('TestSfiPillar', '')
        
        finding = {
            'title': title,
            'description': f"{description}\n{result}".strip(),
            'severity': self._normalize_severity(risk),
            'status': status,
            'recommendation': '',  # Zero Trust reports don't always have specific recommendations
            'pillar': pillar,
            'sfi_pillar': sfi_pillar,
            'mapped_policies': []
        }
        
        # Map to CA policies based on test title and description
        search_text = f"{title} {description} {result}".lower()
        
        # Debug: Show first 5 findings
        if len(self.findings) < 5:
            print(f"\n🔍 Finding #{len(self.findings) + 1}:")
            print(f"   Title: {title[:100]}")
            print(f"   Search text: {search_text[:200]}")
        
        finding['mapped_policies'] = self._map_to_policies(search_text)
        
        return finding
    
    def _normalize_severity(self, severity: str) -> str:
        """Normalize severity levels."""
        severity_lower = str(severity).lower()
        if any(word in severity_lower for word in ['critical', 'high', 'severe']):
            return 'Critical' if 'critical' in severity_lower else 'High'
        elif any(word in severity_lower for word in ['medium', 'moderate']):
            return 'Medium'
        elif any(word in severity_lower for word in ['low', 'minor']):
            return 'Low'
        else:
            return 'Medium'
    
    def _parse_text_content(self) -> List[Dict]:
        """Parse findings from visible text content."""
        findings = []
        
        # Look for common patterns in text
        text_content = self.soup.get_text(separator=' ', strip=True)
        
        # Split into potential findings
        sections = re.split(r'(?:Finding|Recommendation|Control|Issue)\s*\d+:', text_content, flags=re.IGNORECASE)
        
        for section in sections[1:]:  # Skip first split
            if len(section) < 20:  # Skip too short sections
                continue
                
            # Extract title (first sentence)
            sentences = section.split('.')
            title = sentences[0].strip() if sentences else section[:100]
            
            finding = {
                'title': title,
                'description': section[:500],
                'severity': self._extract_severity_from_text(section),
                'status': 'Open',
                'recommendation': section,
                'mapped_policies': self._map_to_policies(section.lower())
            }
            findings.append(finding)
        
        return findings
    
    def _extract_severity_from_text(self, text: str) -> str:
        """Extract severity from text content."""
        text_lower = text.lower()
        if any(word in text_lower for word in ['critical', 'severe']):
            return 'Critical'
        elif 'high' in text_lower:
            return 'High'
        elif 'low' in text_lower:
            return 'Low'
        else:
            return 'Medium'
    
    def _map_to_policies(self, text: str) -> List[str]:
        """Map finding text to CA policy categories."""
        matched_categories = set()
        
        # Debug: show what we're searching
        if "conditional" in text.lower() or "mfa" in text.lower() or "auth" in text.lower():
            print(f"🔍 Searching text: {text[:200]}...")
        
        for keyword, categories in self.CONTROL_MAPPINGS.items():
            if keyword in text:
                matched_categories.update(categories)
                print(f"✅ Matched keyword '{keyword}' -> {categories}")
        
        result = list(matched_categories)
        if result:
            print(f"📋 Total matched categories: {result}")
        
        return result
    
    def get_policy_recommendations(self, ca_policy_examples) -> List[Dict]:
        """
        Match findings to specific CA policy templates.
        Returns list of recommended policies to deploy.
        """
        print(f"🔍 get_policy_recommendations called with {len(self.findings)} findings")
        recommendations = []
        
        # Get POLICY_TEMPLATES dictionary from the module
        if not hasattr(ca_policy_examples, 'POLICY_TEMPLATES'):
            print("Warning: ca_policy_examples module does not have POLICY_TEMPLATES")
            return recommendations
        
        policy_templates = ca_policy_examples.POLICY_TEMPLATES
        
        # Debug: Check first finding
        if self.findings:
            print(f"\n🔍 DEBUG first finding:")
            print(f"  Old categories: {self.findings[0]['mapped_policies']}")
            test_old = self.findings[0]['mapped_policies']
            test_new = set()
            for old_cat in test_old:
                if old_cat in self.CATEGORY_TRANSLATION:
                    test_new.update(self.CATEGORY_TRANSLATION[old_cat])
                    print(f"  '{old_cat}' → {self.CATEGORY_TRANSLATION[old_cat]}")
            print(f"  New categories: {test_new}")
            print(f"  Available template categories: {list(policy_templates.keys())}")
        
        for finding in self.findings:
            # Get relevant policy categories (old format: baseline, mfa, device, etc.)
            old_categories = finding['mapped_policies']
            
            # Translate to new framework categories
            new_categories = set()
            for old_cat in old_categories:
                if old_cat in self.CATEGORY_TRANSLATION:
                    new_categories.update(self.CATEGORY_TRANSLATION[old_cat])
            
            # Find matching templates in new categories
            for new_category in new_categories:
                if new_category in policy_templates:
                    templates = policy_templates[new_category]
                    for template_name, template in templates.items():
                        relevance = self._calculate_relevance(finding, template)
                        if relevance > 0:  # Only include if there's some relevance
                            recommendations.append({
                                'finding_title': finding['title'],
                                'finding_severity': finding['severity'],
                                'finding_status': finding['status'],
                                'policy_category': new_category,
                                'policy_name': template_name,
                                'policy_display_name': template.get('displayName', template_name),
                                'relevance_score': relevance,
                                'template': template  # Include full template for deployment
                            })
        
        # Sort by relevance and remove duplicates
        recommendations = sorted(recommendations, key=lambda x: x['relevance_score'], reverse=True)
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            key = rec['policy_name']
            if key not in seen:
                seen.add(key)
                unique_recommendations.append(rec)
        
        return unique_recommendations
    
    def _calculate_relevance(self, finding: Dict, policy: Dict) -> float:
        """Calculate how relevant a policy is to a finding (0-1)."""
        # Start with a baseline score since the finding already matched the category
        score = 0.3
        
        search_text = f"{finding['title']} {finding['description']} {finding['recommendation']}".lower()
        policy_text = policy.get('displayName', '').lower()
        
        # Check for keyword matches (bonus points)
        keywords = search_text.split()
        for keyword in keywords:
            if len(keyword) > 3 and keyword in policy_text:
                score += 0.05  # Reduced from 0.1 since this is just a bonus
        
        # Boost score for severity (this is the main differentiator)
        severity_boost = {
            'critical': 0.3,
            'high': 0.2,
            'medium': 0.1,
            'low': 0.05
        }
        score += severity_boost.get(finding['severity'].lower(), 0.1)
        
        return min(score, 1.0)
    
    def export_summary(self):
        """Export findings summary.

        Returns a pandas DataFrame when pandas is available, otherwise the
        raw findings list. Callers that require DataFrame operations should
        ensure pandas is installed.
        """
        if not PANDAS_AVAILABLE:
            return self.findings
        return pd.DataFrame(self.findings)
    
    def get_statistics(self) -> Dict:
        """Get summary statistics about findings."""
        if not self.findings:
            return {
                'total_findings': 0,
                'by_severity': {},
                'by_status': {},
                'mapped_policy_types': 0,
                'unmapped_findings': 0,
                'report_type': 'Zero Trust Assessment' if 'zero trust' in str(self.report_data).lower() else 'Security Assessment'
            }
        
        if not PANDAS_AVAILABLE:
            by_severity: Dict[str, int] = {}
            by_status: Dict[str, int] = {}
            for finding in self.findings:
                severity = finding.get('severity', 'Unknown')
                status = finding.get('status', 'Unknown')
                by_severity[severity] = by_severity.get(severity, 0) + 1
                by_status[status] = by_status.get(status, 0) + 1
        else:
            df = pd.DataFrame(self.findings)
            by_severity = df['severity'].value_counts().to_dict() if 'severity' in df else {}
            by_status = df['status'].value_counts().to_dict() if 'status' in df else {}
        
        return {
            'total_findings': len(self.findings),
            'by_severity': by_severity,
            'by_status': by_status,
            'mapped_policy_types': len(set([cat for f in self.findings for cat in f['mapped_policies']])),
            'unmapped_findings': len([f for f in self.findings if not f['mapped_policies']]),
            'report_type': 'Zero Trust Assessment' if 'zero trust' in str(self.report_data).lower() else 'Security Assessment'
        }
