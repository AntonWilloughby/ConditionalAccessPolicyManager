#!/usr/bin/env python3
# CA Policy Templates based on CA_POLICY_FRAMEWORK.md
# All policies default to Report-Only mode (enabledForReportingButNotEnforced)

POLICY_TEMPLATES = {
    "Global Policies": {
        "CA001-Global-BaseProtection-AllApps-AnyPlatform-Block": {
            "displayName": "CA001-Global-BaseProtection-AllApps-AnyPlatform-Block",
            "state": "enabledForReportingButNotEnforced",
            "conditions": {
                "users": {
                    "includeUsers": ["All"],
                    "excludeGroups": [
                        "CA-BreakGlassAccounts",
                        "CA-Persona-Admins",
                        "CA-Persona-Internals",
                        "CA-Persona-Externals",
                        "CA-Persona-Guests",
                        "CA-Persona-GuestAdmins",
                        "CA-Persona-Microsoft365ServiceAccounts",
                        "CA-Persona-AzureServiceAccounts",
                        "CA-Persona-CorpServiceAccounts",
                        "CA-Persona-WorkloadIdentities",
                        "CA-Persona-Developers"
                    ]
                },
                "applications": {"includeApplications": ["All"]},
                "clientAppTypes": ["all"]
            },
            "grantControls": {"operator": "OR", "builtInControls": ["block"]}
        }
    },
    
    "Admin Policies": {
        "CA100-Admins-BaseProtection-AllApps-AnyPlatform-CompliantorAADHJ": {
            "displayName": "CA100-Admins-BaseProtection-AllApps-AnyPlatform-CompliantorAADHJ",
            "state": "enabledForReportingButNotEnforced",
            "conditions": {
                "users": {
                    "includeGroups": ["CA-Persona-Admins"],
                    "excludeGroups": ["CA-BreakGlassAccounts", "CA-Persona-Admins-BaseProtection-Exclusions"]
                },
                "applications": {
                    "includeApplications": ["All"],
                    "excludeApplications": ["0000000a-0000-0000-c000-000000000000", "d4ebce55-015a-49b5-a083-c84d1797ae8c"]
                },
                "clientAppTypes": ["all"]
            },
            "grantControls": {"operator": "OR", "builtInControls": ["compliantDevice", "domainJoinedDevice"]}
        },
        "CA101-Admins-BaseProtection-AllApps-AnyPlatform-MFA": {
            "displayName": "CA101-Admins-BaseProtection-AllApps-AnyPlatform-MFA",
            "state": "enabledForReportingButNotEnforced",
            "conditions": {
                "users": {
                    "includeGroups": ["CA-Persona-Admins"],
                    "excludeGroups": ["CA-BreakGlassAccounts", "CA-Persona-Admins-BaseProtection-Exclusions"]
                },
                "applications": {"includeApplications": ["All"]},
                "clientAppTypes": ["all"]
            },
            "grantControls": {"operator": "OR", "builtInControls": ["mfa"]}
        },
        "CA105-Admins-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth": {
            "displayName": "CA105-Admins-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth",
            "state": "enabledForReportingButNotEnforced",
            "conditions": {
                "users": {
                    "includeGroups": ["CA-Persona-Admins"],
                    "excludeGroups": ["CA-BreakGlassAccounts", "CA-Persona-Admins-IdentityProtection-Exclusions"]
                },
                "applications": {"includeApplications": ["All"]},
                "clientAppTypes": ["exchangeActiveSync", "other"]
            },
            "grantControls": {"operator": "OR", "builtInControls": ["block"]}
        }
    },
    
    "Internal User Policies": {
        "CA200-Internals-BaseProtection-AllApps-AnyPlatform-CompliantorAADHJ": {
            "displayName": "CA200-Internals-BaseProtection-AllApps-AnyPlatform-CompliantorAADHJ",
            "state": "enabledForReportingButNotEnforced",
            "conditions": {
                "users": {
                    "includeGroups": ["CA-Persona-Internals"],
                    "excludeGroups": ["CA-BreakGlassAccounts", "CA-Persona-Internals-BaseProtection-Exclusions"]
                },
                "applications": {
                    "includeApplications": ["All"],
                    "excludeApplications": ["0000000a-0000-0000-c000-000000000000", "d4ebce55-015a-49b5-a083-c84d1797ae8c"]
                },
                "clientAppTypes": ["all"]
            },
            "grantControls": {"operator": "OR", "builtInControls": ["compliantDevice", "domainJoinedDevice"]}
        },
        "CA201-Internals-IdentityProtection-AllApps-AnyPlatform-CombinedRegistration": {
            "displayName": "CA201-Internals-IdentityProtection-AllApps-AnyPlatform-CombinedRegistration",
            "state": "enabledForReportingButNotEnforced",
            "conditions": {
                "users": {
                    "includeGroups": ["CA-Persona-Internals"],
                    "excludeGroups": ["CA-BreakGlassAccounts", "CA-Persona-Internals-IdentityProtection-Exclusions"]
                },
                "applications": {
                    "includeUserActions": ["urn:user:registersecurityinfo"]
                },
                "platforms": {
                    "includePlatforms": ["all"]
                }
            },
            "grantControls": {"operator": "OR", "builtInControls": ["compliantDevice", "domainJoinedDevice"]}
        },
        "CA202-Internals-IdentityProtection-AllApps-AnyPlatform-MFAandPWDforHighUserRisk": {
            "displayName": "CA202-Internals-IdentityProtection-AllApps-AnyPlatform-MFAandPWDforHighUserRisk",
            "state": "enabledForReportingButNotEnforced",
            "conditions": {
                "users": {
                    "includeGroups": ["CA-Persona-Internals"],
                    "excludeGroups": ["CA-BreakGlassAccounts", "CA-Persona-Internals-IdentityProtection-Exclusions"]
                },
                "applications": {
                    "includeApplications": ["All"]
                },
                "platforms": {
                    "includePlatforms": ["all"]
                },
                "userRiskLevels": ["high"]
            },
            "grantControls": {"operator": "AND", "builtInControls": ["mfa", "passwordChange"]}
        },
        "CA203-Internals-IdentityProtection-AllApps-AnyPlatform-MFAforHighSignInRisk": {
            "displayName": "CA203-Internals-IdentityProtection-AllApps-AnyPlatform-MFAforHighSignInRisk",
            "state": "enabledForReportingButNotEnforced",
            "conditions": {
                "users": {
                    "includeGroups": ["CA-Persona-Internals"],
                    "excludeGroups": ["CA-BreakGlassAccounts", "CA-Persona-Internals-IdentityProtection-Exclusions"]
                },
                "applications": {
                    "includeApplications": ["All"]
                },
                "platforms": {
                    "includePlatforms": ["all"]
                },
                "signInRiskLevels": ["high"]
            },
            "grantControls": {"operator": "OR", "builtInControls": ["mfa"]}
        },
        "CA204-Internals-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth": {
            "displayName": "CA204-Internals-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth",
            "state": "enabledForReportingButNotEnforced",
            "conditions": {
                "users": {
                    "includeGroups": ["CA-Persona-Internals"],
                    "excludeGroups": ["CA-BreakGlassAccounts", "CA-Persona-Internals-IdentityProtection-Exclusions"]
                },
                "applications": {"includeApplications": ["All"]},
                "clientAppTypes": ["exchangeActiveSync", "other"]
            },
            "grantControls": {"operator": "OR", "builtInControls": ["block"]}
        }
    },
    
    "External User Policies": {
        "CA300-Externals-BaseProtection-AllApps-AnyPlatform-CompliantorAADHJ": {
            "displayName": "CA300-Externals-BaseProtection-AllApps-AnyPlatform-CompliantorAADHJ",
            "state": "enabledForReportingButNotEnforced",
            "conditions": {
                "users": {
                    "includeGroups": ["CA-Persona-Externals"],
                    "excludeGroups": ["CA-BreakGlassAccounts", "CA-Persona-Externals-BaseProtection-Exclusions"]
                },
                "applications": {
                    "includeApplications": ["All"],
                    "excludeApplications": ["0000000a-0000-0000-c000-000000000000"]
                },
                "clientAppTypes": ["all"]
            },
            "grantControls": {"operator": "OR", "builtInControls": ["compliantDevice", "domainJoinedDevice"]}
        },
        "CA304-Externals-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth": {
            "displayName": "CA304-Externals-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth",
            "state": "enabledForReportingButNotEnforced",
            "conditions": {
                "users": {
                    "includeGroups": ["CA-Persona-Externals"],
                    "excludeGroups": ["CA-BreakGlassAccounts", "CA-Persona-Externals-IdentityProtection-Exclusions"]
                },
                "applications": {"includeApplications": ["All"]},
                "clientAppTypes": ["exchangeActiveSync", "other"]
            },
            "grantControls": {"operator": "OR", "builtInControls": ["block"]}
        }
    },
    
    "Guest User Policies": {
        "CA400-Guests-BaseProtection-AllApps-AnyPlatform-MFA": {
            "displayName": "CA400-Guests-BaseProtection-AllApps-AnyPlatform-MFA",
            "state": "enabledForReportingButNotEnforced",
            "conditions": {
                "users": {
                    "includeGroups": ["CA-Persona-Guests"],
                    "excludeGroups": ["CA-BreakGlassAccounts", "CA-Persona-Guests-BaseProtection-Exclusions"]
                },
                "applications": {"includeApplications": ["All"]},
                "clientAppTypes": ["all"]
            },
            "grantControls": {"operator": "OR", "builtInControls": ["mfa"]}
        },
        "CA403-Guests-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth": {
            "displayName": "CA403-Guests-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth",
            "state": "enabledForReportingButNotEnforced",
            "conditions": {
                "users": {
                    "includeGroups": ["CA-Persona-Guests"],
                    "excludeGroups": ["CA-BreakGlassAccounts", "CA-Persona-Guests-IdentityProtection-Exclusions"]
                },
                "applications": {"includeApplications": ["All"]},
                "clientAppTypes": ["exchangeActiveSync", "other"]
            },
            "grantControls": {"operator": "OR", "builtInControls": ["block"]}
        }
    },
    
    "Guest Admin Policies": {
        "CA500-GuestAdmins-BaseProtection-AllApps-AnyPlatform-MFA": {
            "displayName": "CA500-GuestAdmins-BaseProtection-AllApps-AnyPlatform-MFA",
            "state": "enabledForReportingButNotEnforced",
            "conditions": {
                "users": {
                    "includeGroups": ["CA-Persona-GuestAdmins"],
                    "excludeGroups": ["CA-BreakGlassAccounts", "CA-Persona-GuestAdmins-BaseProtection-Exclusions"]
                },
                "applications": {"includeApplications": ["All"]},
                "clientAppTypes": ["all"]
            },
            "grantControls": {"operator": "OR", "builtInControls": ["mfa"]}
        },
        "CA503-GuestAdmins-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth": {
            "displayName": "CA503-GuestAdmins-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth",
            "state": "enabledForReportingButNotEnforced",
            "conditions": {
                "users": {
                    "includeGroups": ["CA-Persona-GuestAdmins"],
                    "excludeGroups": ["CA-BreakGlassAccounts", "CA-Persona-GuestAdmins-IdentityProtection-Exclusions"]
                },
                "applications": {"includeApplications": ["All"]},
                "clientAppTypes": ["exchangeActiveSync", "other"]
            },
            "grantControls": {"operator": "OR", "builtInControls": ["block"]}
        }
    },
    
    "Service Account Policies": {
        "CA600-Microsoft365ServiceAccounts-BaseProtection-AllApps-AnyPlatform-BlockUntrustedLocations": {
            "displayName": "CA600-Microsoft365ServiceAccounts-BaseProtection-AllApps-AnyPlatform-BlockUntrustedLocations",
            "state": "enabledForReportingButNotEnforced",
            "conditions": {
                "users": {
                    "includeGroups": ["CA-Persona-Microsoft365ServiceAccounts"],
                    "excludeGroups": ["CA-BreakGlassAccounts", "CA-Persona-Microsoft365ServiceAccounts-BaseProtection-Exclusions"]
                },
                "applications": {"includeApplications": ["All"]},
                "locations": {
                    "includeLocations": ["All"],
                    "excludeLocations": ["AllTrusted"]
                },
                "clientAppTypes": ["all"]
            },
            "grantControls": {"operator": "OR", "builtInControls": ["block"]}
        },
        "CA601-Microsoft365ServiceAccounts-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth": {
            "displayName": "CA601-Microsoft365ServiceAccounts-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth",
            "state": "enabledForReportingButNotEnforced",
            "conditions": {
                "users": {
                    "includeGroups": ["CA-Persona-Microsoft365ServiceAccounts"],
                    "excludeGroups": ["CA-BreakGlassAccounts", "CA-Persona-Microsoft365ServiceAccounts-IdentityProtection-Exclusions"]
                },
                "applications": {"includeApplications": ["All"]},
                "clientAppTypes": ["exchangeActiveSync", "other"]
            },
            "grantControls": {"operator": "OR", "builtInControls": ["block"]}
        },
        "CA700-AzureServiceAccounts-BaseProtection-AllApps-AnyPlatform-BlockUntrustedLocations": {
            "displayName": "CA700-AzureServiceAccounts-BaseProtection-AllApps-AnyPlatform-BlockUntrustedLocations",
            "state": "enabledForReportingButNotEnforced",
            "conditions": {
                "users": {
                    "includeGroups": ["CA-Persona-AzureServiceAccounts"],
                    "excludeGroups": ["CA-BreakGlassAccounts", "CA-Persona-AzureServiceAccounts-BaseProtection-Exclusions"]
                },
                "applications": {"includeApplications": ["All"]},
                "locations": {
                    "includeLocations": ["All"],
                    "excludeLocations": ["AllTrusted"]
                },
                "clientAppTypes": ["all"]
            },
            "grantControls": {"operator": "OR", "builtInControls": ["block"]}
        }
    },
    
    "Developer Policies": {
        "CA1001-Developers-BaseProtection-AllApps-AnyPlatform-MFAfromUnamagedDevices": {
            "displayName": "CA1001-Developers-BaseProtection-AllApps-AnyPlatform-MFAfromUnamagedDevices",
            "state": "enabledForReportingButNotEnforced",
            "conditions": {
                "users": {
                    "includeGroups": ["CA-Persona-Developers"],
                    "excludeGroups": ["CA-BreakGlassAccounts", "CA-Persona-Developers-BaseProtection-Exclusions"]
                },
                "applications": {"includeApplications": ["All"]},
                "clientAppTypes": ["all"],
                "devices": {
                    "deviceFilter": {
                        "mode": "exclude",
                        "rule": "device.isCompliant -eq True -or device.trustType -eq \"ServerAD\""
                    }
                }
            },
            "grantControls": {"operator": "OR", "builtInControls": ["mfa"]}
        },
        "CA1005-Developers-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth": {
            "displayName": "CA1005-Developers-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth",
            "state": "enabledForReportingButNotEnforced",
            "conditions": {
                "users": {
                    "includeGroups": ["CA-Persona-Developers"],
                    "excludeGroups": ["CA-BreakGlassAccounts", "CA-Persona-Developers-IdentityProtection-Exclusions"]
                },
                "applications": {"includeApplications": ["All"]},
                "clientAppTypes": ["exchangeActiveSync", "other"]
            },
            "grantControls": {"operator": "OR", "builtInControls": ["block"]}
        }
    }
}


def get_policy_categories():
    """Return policy categories and their policy names"""
    return {category: list(policies.keys()) for category, policies in POLICY_TEMPLATES.items()}


def get_total_policy_count():
    """Return total number of policy templates"""
    return sum(len(policies) for policies in POLICY_TEMPLATES.values())
