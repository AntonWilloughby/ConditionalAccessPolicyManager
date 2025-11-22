#!/usr/bin/env python3
"""
Script to generate ca_policy_examples.py from CA_POLICY_FRAMEWORK.md
"""

# Complete policy definitions based on the framework
POLICY_TEMPLATES = {
    'Global Policies': {
        'CA001-Global-BaseProtection-AllApps-AnyPlatform-Block': {
            'displayName': 'CA001-Global-BaseProtection-AllApps-AnyPlatform-Block',
            'state': 'enabledForReportingButNotEnforced',
            'conditions': {
                'users': {
                    'includeUsers': ['All'],
                    'excludeGroups': [
                        'CA-BreakGlassAccounts', 'CA-Persona-Admins', 'CA-Persona-Internals', 
                        'CA-Persona-Externals', 'CA-Persona-Guests', 'CA-Persona-GuestAdmins',
                        'CA-Persona-Microsoft365ServiceAccounts', 'CA-Persona-AzureServiceAccounts',
                        'CA-Persona-CorpServiceAccounts', 'CA-Persona-WorkloadIdentities', 'CA-Persona-Developers'
                    ]
                },
                'applications': {'includeApplications': ['All']},
                'clientAppTypes': ['all']
            },
            'grantControls': {'operator': 'OR', 'builtInControls': ['block']}
        }
    },
    
    'Admin Policies': {
        'CA100-Admins-BaseProtection-AllApps-AnyPlatform-CompliantorAADHJ': {
            'displayName': 'CA100-Admins-BaseProtection-AllApps-AnyPlatform-CompliantorAADHJ',
            'state': 'enabledForReportingButNotEnforced',
            'conditions': {
                'users': {
                    'includeGroups': ['CA-Persona-Admins'],
                    'excludeGroups': ['CA-BreakGlassAccounts', 'CA-Persona-Admins-BaseProtection-Exclusions']
                },
                'applications': {
                    'includeApplications': ['All'],
                    'excludeApplications': ['0000000a-0000-0000-c000-000000000000', 'd4ebce55-015a-49b5-a083-c84d1797ae8c']
                },
                'clientAppTypes': ['all']
            },
            'grantControls': {'operator': 'OR', 'builtInControls': ['compliantDevice', 'domainJoinedDevice']}
        },
        'CA101-Admins-BaseProtection-AllApps-AnyPlatform-MFA': {
            'displayName': 'CA101-Admins-BaseProtection-AllApps-AnyPlatform-MFA',
            'state': 'enabledForReportingButNotEnforced',
            'conditions': {
                'users': {
                    'includeGroups': ['CA-Persona-Admins'],
                    'excludeGroups': ['CA-BreakGlassAccounts', 'CA-Persona-Admins-BaseProtection-Exclusions']
                },
                'applications': {'includeApplications': ['All']},
                'clientAppTypes': ['all']
            },
            'grantControls': {'operator': 'OR', 'builtInControls': ['mfa']}
        },
        'CA102-Admins-BaseProtection-RegistrationSecurity-AnyPlatform-CompliantorAADHJ': {
            'displayName': 'CA102-Admins-BaseProtection-RegistrationSecurity-AnyPlatform-CompliantorAADHJ',
            'state': 'enabledForReportingButNotEnforced',
            'conditions': {
                'users': {
                    'includeGroups': ['CA-Persona-Admins'],
                    'excludeGroups': ['CA-BreakGlassAccounts', 'CA-Persona-Admins-BaseProtection-Exclusions']
                },
                'applications': {'includeUserActions': ['urn:user:registersecurityinfo']},
                'clientAppTypes': ['all']
            },
            'grantControls': {'operator': 'OR', 'builtInControls': ['compliantDevice', 'domainJoinedDevice']}
        },
        'CA103-Admins-IdentityProtection-AllApps-AnyPlatform-MFAandPWDforMediumandHighUserRisk': {
            'displayName': 'CA103-Admins-IdentityProtection-AllApps-AnyPlatform-MFAandPWDforMediumandHighUserRisk',
            'state': 'enabledForReportingButNotEnforced',
            'conditions': {
                'users': {
                    'includeGroups': ['CA-Persona-Admins'],
                    'excludeGroups': ['CA-BreakGlassAccounts', 'CA-Persona-Admins-IdentityProtection-Exclusions']
                },
                'applications': {'includeApplications': ['All']},
                'userRiskLevels': ['medium', 'high'],
                'clientAppTypes': ['all']
            },
            'grantControls': {'operator': 'AND', 'builtInControls': ['mfa', 'passwordChange']}
        },
        'CA104-Admins-IdentityProtection-AllApps-AnyPlatform-MFAforMediumandHighSignInRisk': {
            'displayName': 'CA104-Admins-IdentityProtection-AllApps-AnyPlatform-MFAforMediumandHighSignInRisk',
            'state': 'enabledForReportingButNotEnforced',
            'conditions': {
                'users': {
                    'includeGroups': ['CA-Persona-Admins'],
                    'excludeGroups': ['CA-BreakGlassAccounts', 'CA-Persona-Admins-IdentityProtection-Exclusions']
                },
                'applications': {'includeApplications': ['All']},
                'signInRiskLevels': ['medium', 'high'],
                'clientAppTypes': ['all']
            },
            'grantControls': {'operator': 'OR', 'builtInControls': ['mfa']}
        },
        'CA105-Admins-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth': {
            'displayName': 'CA105-Admins-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth',
            'state': 'enabledForReportingButNotEnforced',
            'conditions': {
                'users': {
                    'includeGroups': ['CA-Persona-Admins'],
                    'excludeGroups': [
                        'CA-BreakGlassAccounts', 'CA-Persona-Microsoft365ServiceAccounts',
                        'CA-Persona-AzureServiceAccounts', 'CA-Persona-CorpServiceAccounts',
                        'CA-Persona-Admins-IdentityProtection-Exclusions'
                    ]
                },
                'applications': {'includeApplications': ['All']},
                'clientAppTypes': ['exchangeActiveSync', 'other']
            },
            'grantControls': {'operator': 'OR', 'builtInControls': ['block']}
        },
        'CA106-Admins-IdentityProtection-IntuneEnrollment-AnyPlatform-MFA': {
            'displayName': 'CA106-Admins-IdentityProtection-IntuneEnrollment-AnyPlatform-MFA',
            'state': 'enabledForReportingButNotEnforced',
            'conditions': {
                'users': {
                    'includeGroups': ['CA-Persona-Admins'],
                    'excludeGroups': ['CA-BreakGlassAccounts', 'CA-Persona-Admins-IdentityProtection-Exclusions']
                },
                'applications': {'includeApplications': ['0000000a-0000-0000-c000-000000000000']},
                'clientAppTypes': ['all']
            },
            'grantControls': {'operator': 'OR', 'builtInControls': ['mfa']}
        },
        'CA107-Admins-DataandAppProtection-AllApps-iOSorAndroid-ClientAppandAPP': {
            'displayName': 'CA107-Admins-DataandAppProtection-AllApps-iOSorAndroid-ClientAppandAPP',
            'state': 'enabledForReportingButNotEnforced',
            'conditions': {
                'users': {
                    'includeGroups': ['CA-Persona-Admins'],
                    'excludeGroups': ['CA-BreakGlassAccounts', 'CA-Persona-Admins-DataandAppProtection-Exclusions']
                },
                'applications': {
                    'includeApplications': ['All'],
                    'excludeApplications': ['0000000a-0000-0000-c000-000000000000']
                },
                'platforms': {'includePlatforms': ['iOS', 'android']},
                'clientAppTypes': ['all']
            },
            'grantControls': {'operator': 'OR', 'builtInControls': ['approvedApplication', 'compliantApplication']}
        },
        'CA108-Admins-DataandAppProtection-AllApps-AnyPlatform-SessionPolicy': {
            'displayName': 'CA108-Admins-DataandAppProtection-AllApps-AnyPlatform-SessionPolicy',
            'state': 'enabledForReportingButNotEnforced',
            'conditions': {
                'users': {
                    'includeGroups': ['CA-Persona-Admins'],
                    'excludeGroups': ['CA-BreakGlassAccounts', 'CA-Persona-Admins-DataandAppProtection-Exclusions']
                },
                'applications': {'includeApplications': ['All']},
                'clientAppTypes': ['all']
            },
            'sessionControls': {
                'signInFrequency': {'value': 4, 'type': 'hours', 'isEnabled': True}
            }
        },
        'CA109-Admins-AttackSurfaceReduction-AllApps-AnyPlatform-BlockUnknownPlatforms': {
            'displayName': 'CA109-Admins-AttackSurfaceReduction-AllApps-AnyPlatform-BlockUnknownPlatforms',
            'state': 'enabledForReportingButNotEnforced',
            'conditions': {
                'users': {
                    'includeGroups': ['CA-Persona-Admins'],
                    'excludeGroups': ['CA-BreakGlassAccounts', 'CA-Persona-Admins-AttackSurfaceReduction-Exclusions']
                },
                'applications': {'includeApplications': ['All']},
                'platforms': {
                    'includePlatforms': ['all'],
                    'excludePlatforms': ['windows', 'macOS', 'iOS', 'android', 'linux']
                },
                'clientAppTypes': ['all']
            },
            'grantControls': {'operator': 'OR', 'builtInControls': ['block']}
        }
    }
}

# Write to file
if __name__ == '__main__':
    with open('ca_policy_examples.py', 'w', encoding='utf-8') as f:
        f.write('#!/usr/bin/env python3\n')
        f.write('# CA Policy Templates based on CA_POLICY_FRAMEWORK.md\n')
        f.write('# All policies default to Report-Only mode for safe testing\n\n')
        f.write('POLICY_TEMPLATES = ')
        
        # Write with proper formatting
        import pprint
        pp = pprint.PrettyPrinter(width=120, compact=False, indent=4)
        policy_str = pp.pformat(POLICY_TEMPLATES)
        f.write(policy_str)
        f.write('\n\n')
        
        # Add helper functions
        f.write('def get_policy_categories():\n')
        f.write('    """Return policy categories and their policy names"""\n')
        f.write('    return {category: list(policies.keys()) for category, policies in POLICY_TEMPLATES.items()}\n\n')
        
        f.write('def get_total_policy_count():\n')
        f.write('    """Return total number of policy templates"""\n')
        f.write('    return sum(len(policies) for policies in POLICY_TEMPLATES.values())\n')
    
    print(f'Successfully generated ca_policy_examples.py with {sum(len(v) for v in POLICY_TEMPLATES.values())} policies')
