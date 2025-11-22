#!/usr/bin/env python3
# ca_policy_manager.py
# Microsoft Graph Conditional Access Policy Manager
# Connects to Microsoft Graph API to create, read, update, and delete CA policies

import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import msal

class ConditionalAccessManager:
    """
    Manager for Microsoft Entra Conditional Access Policies via Microsoft Graph API.
    
    Requires:
    - Azure AD App Registration with Conditional Access permissions
    - Client ID, Tenant ID, and Client Secret
    """
    
    def __init__(self, tenant_id: str, client_id: str, client_secret: str, verify_ssl: bool = True):
        """
        Initialize the CA Policy Manager.
        
        Args:
            tenant_id: Azure AD Tenant ID
            client_id: Azure AD App Registration Client ID
            client_secret: Client Secret for authentication
            verify_ssl: Enable SSL certificate verification (set to False for corporate proxies)
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.scope = ["https://graph.microsoft.com/.default"]
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"
        self.access_token = None
        self.verify_ssl = verify_ssl
        
        # Disable SSL warnings if verification is disabled
        if not verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            print("⚠️  SSL certificate verification disabled")
        
    def authenticate(self) -> bool:
        """
        Authenticate with Microsoft Graph using client credentials flow.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=self.authority,
                client_credential=self.client_secret
            )
            
            result = app.acquire_token_silent(self.scope, account=None)
            if not result:
                result = app.acquire_token_for_client(scopes=self.scope)
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                print("✅ Successfully authenticated with Microsoft Graph")
                return True
            else:
                print(f"❌ Authentication failed: {result.get('error_description', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authentication token."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def validate_application_id(self, app_id: str) -> bool:
        """
        Validate if an application ID exists in the tenant.
        
        Args:
            app_id: Application/Service Principal ID to validate
            
        Returns:
            True if the app exists, False otherwise
        """
        try:
            # Well-known Microsoft apps that always exist
            well_known_apps = {
                "00000003-0000-0000-c000-000000000000": "Microsoft Graph",
                "0000000a-0000-0000-c000-000000000000": "Microsoft Intune (MAM/MDM)"
            }
            
            if app_id in well_known_apps:
                return True
            
            # Check if service principal exists
            url = f"{self.graph_endpoint}/servicePrincipals?$filter=appId eq '{app_id}'"
            response = requests.get(url, headers=self._get_headers(), verify=self.verify_ssl)
            response.raise_for_status()
            
            result = response.json()
            exists = len(result.get("value", [])) > 0
            
            if not exists:
                print(f"⚠️  Application {app_id} not found in tenant")
            
            return exists
            
        except Exception as e:
            print(f"❌ Error validating app {app_id}: {e}")
            return False
    
    def clean_policy_applications(self, policy_definition: Dict) -> Dict:
        """
        Remove invalid application IDs from policy before deployment.
        
        Args:
            policy_definition: Policy configuration dictionary
            
        Returns:
            Cleaned policy definition
        """
        import copy
        cleaned_policy = copy.deepcopy(policy_definition)
        
        try:
            exclude_apps = cleaned_policy.get("conditions", {}).get("applications", {}).get("excludeApplications", [])
            
            if exclude_apps:
                print(f"🔍 Validating {len(exclude_apps)} excluded applications...")
                valid_apps = []
                
                for app_id in exclude_apps:
                    if self.validate_application_id(app_id):
                        valid_apps.append(app_id)
                    else:
                        print(f"   ⚠️  Removing invalid app: {app_id}")
                
                if valid_apps:
                    cleaned_policy["conditions"]["applications"]["excludeApplications"] = valid_apps
                    print(f"   ✅ Kept {len(valid_apps)} valid excluded applications")
                else:
                    # Remove excludeApplications key if no valid apps remain
                    del cleaned_policy["conditions"]["applications"]["excludeApplications"]
                    print(f"   ℹ️  Removed excludeApplications (no valid apps)")
        
        except Exception as e:
            print(f"⚠️  Error cleaning policy applications: {e}")
        
        return cleaned_policy
    
    def list_policies(self) -> List[Dict]:
        """
        List all Conditional Access policies.
        
        Returns:
            List of CA policy objects
        """
        try:
            url = f"{self.graph_endpoint}/identity/conditionalAccess/policies"
            response = requests.get(url, headers=self._get_headers(), verify=self.verify_ssl)
            response.raise_for_status()
            
            policies = response.json().get("value", [])
            print(f"✅ Retrieved {len(policies)} Conditional Access policies")
            return policies
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error listing policies: {e}")
            return []
    
    def get_policy(self, policy_id: str) -> Optional[Dict]:
        """
        Get a specific Conditional Access policy by ID.
        
        Args:
            policy_id: The policy ID (GUID)
            
        Returns:
            Policy object or None if not found
        """
        try:
            url = f"{self.graph_endpoint}/identity/conditionalAccess/policies/{policy_id}"
            response = requests.get(url, headers=self._get_headers(), verify=self.verify_ssl)
            response.raise_for_status()
            
            policy = response.json()
            print(f"✅ Retrieved policy: {policy.get('displayName', 'Unknown')}")
            return policy
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting policy: {e}")
            return None
    
    def create_policy(self, policy_definition: Dict) -> Optional[Dict]:
        """
        Create a new Conditional Access policy.
        
        Args:
            policy_definition: Policy configuration dictionary
            
        Returns:
            Created policy object or None if failed
        """
        try:
            # Clean policy by validating application IDs
            cleaned_policy = self.clean_policy_applications(policy_definition)
            
            url = f"{self.graph_endpoint}/identity/conditionalAccess/policies"
            response = requests.post(
                url,
                headers=self._get_headers(),
                data=json.dumps(cleaned_policy),
                verify=self.verify_ssl
            )
            response.raise_for_status()
            
            policy = response.json()
            print(f"✅ Created policy: {policy.get('displayName', 'Unknown')}")
            return policy
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating policy: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Response: {e.response.text}")
            return None
    
    def update_policy(self, policy_id: str, policy_definition: Dict) -> bool:
        """
        Update an existing Conditional Access policy.
        
        Args:
            policy_id: The policy ID (GUID)
            policy_definition: Updated policy configuration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.graph_endpoint}/identity/conditionalAccess/policies/{policy_id}"
            response = requests.patch(
                url,
                headers=self._get_headers(),
                data=json.dumps(policy_definition),
                verify=self.verify_ssl
            )
            response.raise_for_status()
            
            print(f"✅ Updated policy: {policy_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error updating policy: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Response: {e.response.text}")
            return False
    
    def delete_policy(self, policy_id: str) -> bool:
        """
        Delete a Conditional Access policy.
        
        Args:
            policy_id: The policy ID (GUID)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.graph_endpoint}/identity/conditionalAccess/policies/{policy_id}"
            response = requests.delete(url, headers=self._get_headers(), verify=self.verify_ssl)
            response.raise_for_status()
            
            print(f"✅ Deleted policy: {policy_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error deleting policy: {e}")
            return False
    
    def enable_policy(self, policy_id: str) -> bool:
        """
        Enable a Conditional Access policy (set state to 'enabled').
        
        Args:
            policy_id: The policy ID (GUID)
            
        Returns:
            True if successful, False otherwise
        """
        return self.update_policy(policy_id, {"state": "enabled"})
    
    def disable_policy(self, policy_id: str) -> bool:
        """
        Disable a Conditional Access policy (set state to 'disabled').
        
        Args:
            policy_id: The policy ID (GUID)
            
        Returns:
            True if successful, False otherwise
        """
        return self.update_policy(policy_id, {"state": "disabled"})
    
    def set_report_only(self, policy_id: str) -> bool:
        """
        Set policy to report-only mode (logs actions without enforcing).
        
        Args:
            policy_id: The policy ID (GUID)
            
        Returns:
            True if successful, False otherwise
        """
        return self.update_policy(policy_id, {"state": "enabledForReportingButNotEnforced"})
    
    def export_policies(self, output_file: str = "ca_policies_backup.json") -> bool:
        """
        Export all CA policies to a JSON file for backup.
        
        Args:
            output_file: Output filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            policies = self.list_policies()
            if not policies:
                print("⚠️  No policies to export")
                return False
            
            backup_data = {
                "exported": datetime.utcnow().isoformat(),
                "tenant_id": self.tenant_id,
                "policy_count": len(policies),
                "policies": policies
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2)
            
            print(f"✅ Exported {len(policies)} policies to {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting policies: {e}")
            return False
    
    def import_policy_from_file(self, input_file: str, policy_name: Optional[str] = None) -> bool:
        """
        Import a CA policy from a JSON file.
        
        Args:
            input_file: Input JSON file
            policy_name: Optional - specific policy name to import (if file contains multiple)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle backup file format
            if "policies" in data:
                policies = data["policies"]
            elif isinstance(data, list):
                policies = data
            else:
                policies = [data]
            
            # Filter by name if specified
            if policy_name:
                policies = [p for p in policies if p.get("displayName") == policy_name]
                if not policies:
                    print(f"❌ Policy '{policy_name}' not found in file")
                    return False
            
            success_count = 0
            for policy in policies:
                # Remove read-only fields
                policy_def = self._clean_policy_for_import(policy)
                
                if self.create_policy(policy_def):
                    success_count += 1
            
            print(f"✅ Successfully imported {success_count}/{len(policies)} policies")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Error importing policy: {e}")
            return False
    
    def _clean_policy_for_import(self, policy: Dict) -> Dict:
        """Remove read-only fields from policy for import/create operations."""
        # Fields that cannot be set during creation
        read_only_fields = ["id", "createdDateTime", "modifiedDateTime", "@odata.context"]
        
        clean_policy = {k: v for k, v in policy.items() if k not in read_only_fields}
        return clean_policy
    
    def display_policy_summary(self, policies: List[Dict]) -> None:
        """
        Display a formatted summary of CA policies.
        
        Args:
            policies: List of policy objects
        """
        if not policies:
            print("No policies to display")
            return
        
        print("\n" + "=" * 100)
        print(f"{'Policy Name':<40} {'State':<25} {'Created':<20} {'Modified':<20}")
        print("=" * 100)
        
        for policy in policies:
            name = policy.get("displayName", "Unknown")[:38]
            state = policy.get("state", "Unknown")
            created = policy.get("createdDateTime", "Unknown")
            modified = policy.get("modifiedDateTime", "Unknown")
            
            # Handle None values and format dates
            created = created[:19] if created and created != "Unknown" else "Unknown"
            modified = modified[:19] if modified and modified != "Unknown" else "Unknown"
            
            # Color code state
            state_icon = {
                "enabled": "🟢",
                "disabled": "🔴",
                "enabledForReportingButNotEnforced": "🟡"
            }.get(state, "⚪")
            
            print(f"{name:<40} {state_icon} {state:<23} {created:<20} {modified:<20}")
        
        print("=" * 100)
        print(f"Total: {len(policies)} policies\n")


def create_sample_policy() -> Dict:
    """
    Create a sample CA policy template for reference.
    
    Returns:
        Sample policy definition
    """
    return {
        "displayName": "Sample: Block Legacy Authentication",
        "state": "enabledForReportingButNotEnforced",  # Start in report-only mode
        "conditions": {
            "users": {
                "includeUsers": ["All"]
            },
            "applications": {
                "includeApplications": ["All"]
            },
            "clientAppTypes": [
                "exchangeActiveSync",
                "other"  # Legacy authentication
            ]
        },
        "grantControls": {
            "operator": "OR",
            "builtInControls": ["block"]
        }
    }


def interactive_menu(manager: ConditionalAccessManager):
    """
    Interactive menu for managing CA policies.
    
    Args:
        manager: ConditionalAccessManager instance
    """
    while True:
        print("\n" + "=" * 60)
        print("Microsoft Conditional Access Policy Manager")
        print("=" * 60)
        print("1. List all policies")
        print("2. Get specific policy")
        print("3. Create new policy from JSON")
        print("4. Deploy policy from template library")
        print("5. Deploy ALL templates (bulk deployment)")
        print("6. Update policy")
        print("7. Delete policy")
        print("8. Enable policy")
        print("9. Disable policy")
        print("10. Set policy to report-only")
        print("11. Export all policies to file")
        print("12. Import policy from file")
        print("13. Show sample policy template")
        print("0. Exit")
        print("=" * 60)
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "1":
            policies = manager.list_policies()
            manager.display_policy_summary(policies)
            
        elif choice == "2":
            policy_id = input("Enter policy ID: ").strip()
            policy = manager.get_policy(policy_id)
            if policy:
                print(json.dumps(policy, indent=2))
                
        elif choice == "3":
            print("\nEnter policy definition (JSON format) or press Ctrl+C to cancel:")
            print("Tip: Use option 4 to deploy from template library")
            try:
                policy_json = input("Policy JSON: ").strip()
                policy_def = json.loads(policy_json)
                manager.create_policy(policy_def)
            except json.JSONDecodeError:
                print("❌ Invalid JSON format")
            except KeyboardInterrupt:
                print("\n⚠️  Cancelled")
                
        elif choice == "4":
            # Deploy from template library
            try:
                from ca_policy_examples import POLICY_TEMPLATES
                
                print("\nAvailable Template Categories:")
                categories = list(POLICY_TEMPLATES.keys())
                for i, cat in enumerate(categories, 1):
                    print(f"{i}. {cat.upper()}")
                
                cat_choice = input("\nSelect category (number): ").strip()
                try:
                    cat_idx = int(cat_choice) - 1
                    if 0 <= cat_idx < len(categories):
                        category = categories[cat_idx]
                        templates = POLICY_TEMPLATES[category]
                        
                        print(f"\nAvailable Templates in {category.upper()}:")
                        template_names = list(templates.keys())
                        for i, name in enumerate(template_names, 1):
                            display_name = templates[name].get("displayName", "Unknown")
                            print(f"{i}. {name} - {display_name}")
                        
                        tmpl_choice = input("\nSelect template (number): ").strip()
                        tmpl_idx = int(tmpl_choice) - 1
                        if 0 <= tmpl_idx < len(template_names):
                            template_name = template_names[tmpl_idx]
                            policy_template = templates[template_name].copy()
                            
                            print(f"\nTemplate: {policy_template.get('displayName')}")
                            print(json.dumps(policy_template, indent=2))
                            
                            confirm = input("\nDeploy this policy? (yes/no): ").strip().lower()
                            if confirm == "yes":
                                manager.create_policy(policy_template)
                            else:
                                print("⚠️  Cancelled")
                        else:
                            print("❌ Invalid template selection")
                    else:
                        print("❌ Invalid category selection")
                except (ValueError, IndexError):
                    print("❌ Invalid selection")
            except ImportError:
                print("❌ ca_policy_examples.py not found")
                
        elif choice == "5":
            # Deploy all templates
            try:
                from ca_policy_examples import POLICY_TEMPLATES
                
                print("\n⚠️  BULK DEPLOYMENT WARNING ⚠️")
                print("This will deploy ALL policy templates from the library.")
                print("All policies will be created in REPORT-ONLY mode for safety.")
                print("\nTemplate Summary:")
                
                total_count = 0
                for category, templates in POLICY_TEMPLATES.items():
                    count = len(templates)
                    total_count += count
                    print(f"  {category.upper()}: {count} policies")
                
                print(f"\nTotal policies to deploy: {total_count}")
                
                confirm = input("\nDo you want to proceed? (yes/no): ").strip().lower()
                if confirm != "yes":
                    print("⚠️  Cancelled")
                else:
                    print("\n🚀 Starting bulk deployment...\n")
                    success_count = 0
                    fail_count = 0
                    
                    for category, templates in POLICY_TEMPLATES.items():
                        print(f"\n📁 Deploying {category.upper()} policies...")
                        for template_name, policy_template in templates.items():
                            # Make a copy and set to report-only for safety
                            policy = policy_template.copy()
                            policy["state"] = "enabledForReportingButNotEnforced"
                            
                            print(f"  ➤ {policy.get('displayName', template_name)}... ", end="")
                            result = manager.create_policy(policy)
                            if result:
                                success_count += 1
                                print("✅")
                            else:
                                fail_count += 1
                                print("❌")
                    
                    print("\n" + "=" * 60)
                    print(f"✅ Successfully deployed: {success_count}")
                    print(f"❌ Failed: {fail_count}")
                    print(f"📊 Total: {total_count}")
                    print("=" * 60)
                    print("\n⚠️  All policies were created in REPORT-ONLY mode.")
                    print("Review them in Azure Portal before enabling enforcement.")
                    
            except ImportError:
                print("❌ ca_policy_examples.py not found")
                
        elif choice == "6":
            policy_id = input("Enter policy ID: ").strip()
            print("Enter updated policy definition (JSON):")
            try:
                policy_json = input("Policy JSON: ").strip()
                policy_def = json.loads(policy_json)
                manager.update_policy(policy_id, policy_def)
            except json.JSONDecodeError:
                print("❌ Invalid JSON format")
                
        elif choice == "7":
            policy_id = input("Enter policy ID to delete: ").strip()
            confirm = input(f"⚠️  Are you sure you want to delete policy {policy_id}? (yes/no): ")
            if confirm.lower() == "yes":
                manager.delete_policy(policy_id)
            else:
                print("⚠️  Cancelled")
                
        elif choice == "8":
            policy_id = input("Enter policy ID to enable: ").strip()
            manager.enable_policy(policy_id)
            
        elif choice == "9":
            policy_id = input("Enter policy ID to disable: ").strip()
            manager.disable_policy(policy_id)
            
        elif choice == "10":
            policy_id = input("Enter policy ID to set to report-only: ").strip()
            manager.set_report_only(policy_id)
            
        elif choice == "11":
            filename = input("Enter output filename (default: ca_policies_backup.json): ").strip()
            if not filename:
                filename = "ca_policies_backup.json"
            manager.export_policies(filename)
            
        elif choice == "12":
            filename = input("Enter input filename: ").strip()
            manager.import_policy_from_file(filename)
            
        elif choice == "13":
            sample = create_sample_policy()
            print("\nSample CA Policy Template:")
            print(json.dumps(sample, indent=2))
            
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice, please try again")


def main():
    """Main entry point."""
    print("=" * 60)
    print("Microsoft Conditional Access Policy Manager")
    print("=" * 60)
    
    # Try to load credentials from config.json first
    config_file = "config.json"
    tenant_id = None
    client_id = None
    client_secret = None
    verify_ssl = True  # Default to True for security
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                tenant_id = config.get('tenant_id', '').strip()
                client_id = config.get('client_id', '').strip()
                client_secret = config.get('client_secret', '').strip()
                verify_ssl = config.get('verify_ssl', True)  # Load SSL setting from config
                
                if all([tenant_id, client_id, client_secret]):
                    print(f"✅ Loaded credentials from {config_file}")
                    if not verify_ssl:
                        print("⚠️  SSL verification disabled (from config)")
                else:
                    print(f"⚠️  {config_file} exists but missing required fields")
                    tenant_id = client_id = client_secret = None
        except Exception as e:
            print(f"⚠️  Error reading {config_file}: {e}")
    
    # If config file doesn't exist or is incomplete, prompt for credentials
    if not all([tenant_id, client_id, client_secret]):
        print("\nEnter credentials manually:")
        tenant_id = input("Enter Tenant ID: ").strip()
        client_id = input("Enter Client ID: ").strip()
        client_secret = input("Enter Client Secret: ").strip()
    
    if not all([tenant_id, client_id, client_secret]):
        print("❌ Missing required credentials")
        return
    
    # Ask about SSL verification only if not loaded from config
    if os.path.exists(config_file) and 'verify_ssl' in json.load(open(config_file)):
        # SSL setting already loaded from config, skip prompt
        pass
    else:
        # Prompt for SSL verification
        ssl_verify = input("\nVerify SSL certificates? (Y/n) [Y]: ").strip().lower()
        verify_ssl = ssl_verify != 'n'
    
    # Initialize manager and authenticate
    manager = ConditionalAccessManager(tenant_id, client_id, client_secret, verify_ssl=verify_ssl)
    
    if not manager.authenticate():
        print("❌ Authentication failed. Please check your credentials and app permissions.")
        return
    
    # Start interactive menu
    interactive_menu(manager)


if __name__ == "__main__":
    main()
