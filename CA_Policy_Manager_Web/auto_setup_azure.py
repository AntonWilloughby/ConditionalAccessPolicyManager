#!/usr/bin/env python3
"""
Automatic Azure App Registration Setup
Creates app registration with delegated Graph API permissions
"""

import subprocess
import json
import os
import sys
from pathlib import Path

def run_powershell_script():
    """Run the PowerShell script to create app registration"""
    script_path = Path(__file__).parent.parent / 'scripts' / 'Register-EntraApp-Delegated.ps1'
    
    if not script_path.exists():
        return False, "PowerShell registration script not found"
    
    try:
        # Run PowerShell script
        result = subprocess.run(
            ['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', str(script_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            return True, "App registration created successfully"
        else:
            return False, f"Script failed: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return False, "Script timed out (5 minutes)"
    except Exception as e:
        return False, f"Error running script: {str(e)}"

def check_azure_cli():
    """Check if Azure CLI is installed"""
    try:
        result = subprocess.run(['az', '--version'], capture_output=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def interactive_setup():
    """Interactive setup that guides user through Azure app registration"""
    print("\n" + "="*60)
    print("   Azure App Registration - Automatic Setup")
    print("="*60 + "\n")
    
    # Check if Azure CLI is installed
    if not check_azure_cli():
        print("❌ Azure CLI not found!\n")
        print("Please install Azure CLI first:")
        print("   https://aka.ms/azure-cli\n")
        print("Then run this script again.\n")
        return False
    
    print("✅ Azure CLI is installed\n")
    
    # Run the PowerShell script
    print("Creating Azure App Registration...")
    print("You will be prompted to sign in to Azure...\n")
    
    success, message = run_powershell_script()
    
    if success:
        print("\n✅ " + message)
        print("\nYour .env file has been updated with the credentials.")
        print("Restart the Flask app to use the new configuration.\n")
        return True
    else:
        print("\n❌ " + message)
        print("\nManual setup required. See docs/QUICK_SETUP.md\n")
        return False

if __name__ == '__main__':
    success = interactive_setup()
    sys.exit(0 if success else 1)
