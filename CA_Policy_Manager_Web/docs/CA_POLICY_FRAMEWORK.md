# Conditional Access Policy Framework - Persona-Based Approach

## Overview

This framework organizes Conditional Access policies by "persona," such as Global, Admins, Internals, Externals, Guests, etc. Each persona may have multiple "policy types" that address different security requirements.

### Policy Types

- **BaseProtection**: Baseline requirement (e.g., require Compliant or Hybrid AD-joined device or MFA)
- **IdentityProtection**: Blocking legacy auth, extra controls based on risk
- **DataandAppProtection**: Requiring approved apps or app protection policies
- **AttackSurfaceReduction**: Blocking unknown platforms, blocking from untrusted locations
- **Compliance**: Terms of Use and other compliance requirements

### Naming Convention

**Pattern**: `CA<Number>-<Persona>-<PolicyType>-<AppScope>-<Platform>-<Grant/Action>`

**Example**: `CA001-Global-BaseProtection-AllApps-AnyPlatform-Block`

This naming approach helps standardize and quickly identify each policy's purpose, scope, and conditions.

---

## Persona-Based CA Policies

| Policy ID | Persona     | Policy Type              | Cloud Apps/Scope                                          | Grant/Action                                         | Brief Description                                                                   | Policy Name (Naming Convention)                                                                                       |
|-----------|------------|--------------------------|------------------------------------------------------------|------------------------------------------------------|--------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| CA001     | Global      | BaseProtection          | All Cloud Apps                                            | Block                                                | Block users not in any categorized persona group.                                   | CA001-Global-BaseProtection-AllApps-AnyPlatform-Block                                                                  |
| CA002     | Global      | AttackSurfaceReduction  | Various targeted apps                                     | Block                                                | Example of blocking certain apps/countries globally.                                 | CA002-Global-AttackSurfaceReduction-VariousApps-AnyPlatform-Block                                                      |
| CA100     | Admins      | BaseProtection          | All Cloud Apps (excl. Intune Enrollment, CMG)             | Require Compliant or Hybrid AD-Joined Device         | Ensures admin devices are managed or hybrid-joined.                                 | CA100-Admins-BaseProtection-AllApps-AnyPlatform-CompliantorAADHJ                                                       |
| CA101     | Admins      | BaseProtection          | All Cloud Apps                                            | MFA                                                  | Requires MFA for admin access.                                                      | CA101-Admins-BaseProtection-AllApps-AnyPlatform-MFA                                                                     |
| CA102     | Admins      | IdentityProtection      | All Cloud Apps / Security Info Registration               | Require Compliant or HAADJ for combined reg          | Secures admins' MFA/SSPR registration.                                              | CA102-Admins-IdentityProtection-AllApps-AnyPlatform-CombinedRegistration                                               |
| CA103     | Admins      | IdentityProtection      | All Cloud Apps                                            | MFA + Password Change if Medium/High User Risk       | Triggers strong re-auth for high user risk.                                         | CA103-Admins-IdentityProtection-AllApps-AnyPlatform-MFAandPWDforMediumandHighUserRisk                                  |
| CA104     | Admins      | IdentityProtection      | All Cloud Apps                                            | MFA if Medium/High Sign-In Risk                     | Extra MFA prompt if sign-in risk is medium/high.                                    | CA104-Admins-IdentityProtection-AllApps-AnyPlatform-MFAforMediumandHighSignInRisk                                      |
| CA105     | Admins      | IdentityProtection      | All Cloud Apps (EAS/Other clients)                        | Block                                                | Block legacy email/auth for admins.                                                 | CA105-Admins-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth                                                    |
| CA106     | Admins      | AppProtection           | Microsoft Intune Enrollment                               | MFA                                                  | Requires MFA to enroll an admin device.                                             | CA106-Admins-AppProtection-MicrosoftIntuneEnrollment-AnyPlatform-MFA                                                   |
| CA107     | Admins      | DataandAppProtection    | All Cloud Apps on iOS/Android (excl. enrollment)          | Require Approved Client or App Protection            | Enforce app protection/approved client for admins on mobile.                        | CA107-Admins-DataandAppProtection-AllApps-iOSorAndroid-ClientAppandAPP                                                |
| CA108     | Admins      | DataandAppProtection    | All Cloud Apps                                            | Sign-in frequency = 4h, no persistent session        | Shortens admin session lifetimes.                                                  | CA108-Admins-DataandAppProtection-AllApps-AnyPlatform-SessionPolicy                                                   |
| CA109     | Admins      | AttackSurfaceReduction  | All Cloud Apps (unknown platforms)                        | Block                                                | Blocks sign-ins from unknown platforms for admins.                                  | CA109-Admins-AttackSurfaceReduction-AllApps-AnyPlatform-BlockUnknownPlatforms                                          |
| CA200     | Internals   | BaseProtection          | All Cloud Apps (excl. Intune Enrollment, CMG)             | Require Compliant or Hybrid AD-Joined Device         | Baseline for internal employees' devices.                                          | CA200-Internals-BaseProtection-AllApps-AnyPlatform-CompliantorAADHJ                                                    |
| CA201     | Internals   | IdentityProtection      | All Cloud Apps / Security Info Registration               | Require Compliant or HAADJ                           | Ensures safe MFA/SSPR registration.                                                | CA201-Internals-IdentityProtection-AllApps-AnyPlatform-CombinedRegistration                                           |
| CA202     | Internals   | IdentityProtection      | All Cloud Apps                                            | MFA + Password Change if High User Risk              | Extra step for high user risk.                                                      | CA202-Internals-IdentityProtection-AllApps-AnyPlatform-MFAandPWDforHighUserRisk                                        |
| CA203     | Internals   | IdentityProtection      | All Cloud Apps                                            | MFA if High Sign-In Risk                             | Adds MFA on high sign-in risk.                                                     | CA203-Internals-IdentityProtection-AllApps-AnyPlatform-MFAforHighSignInRisk                                            |
| CA204     | Internals   | IdentityProtection      | All Cloud Apps (EAS/Other clients)                        | Block                                                | Blocks legacy auth for internal employees.                                         | CA204-Internals-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth                                                |
| CA205     | Internals   | AppProtection           | Microsoft Intune Enrollment                               | MFA                                                  | MFA for device enrollment.                                                         | CA205-Internals-AppProtection-MicrosoftIntuneEnrollment-AnyPlatform-MFA                                               |
| CA206     | Internals   | DataandAppProtection    | Office 365 on iOS/Android                                 | Require Approved Client or App Protection            | Mobile app control for internal employees.                                         | CA206-Internals-DataandAppProtection-AllApps-iOSorAndroid-ClientAppORAPP                                              |
| CA207     | Internals   | AttackSurfaceReduction  | All Cloud Apps (unknown platforms)                        | Block                                                | Block unknown platforms for internals.                                             | CA207-Internals-AttackSurfaceReduction-AllApps-AnyPlatform-BlockUnknownPlatforms                                       |
| CA300     | Externals   | BaseProtection          | All Cloud Apps (excl. Intune Enrollment)                  | Require Compliant/HAADJ                               | Locks down external consultants' devices.                                          | CA300-Externals-BaseProtection-AllApps-AnyPlatform-CompliantorAADHJ                                                   |
| CA301     | Externals   | IdentityProtection      | All Cloud Apps / Security Info Registration               | Require Compliant or HAADJ                           | Requires secure registration for externals.                                        | CA301-Externals-IdentityProtection-AllApps-AnyPlatform-CombinedRegistration                                           |
| CA302     | Externals   | IdentityProtection      | All Cloud Apps                                            | MFA + Password Change if High User Risk              | Stronger reauth for external high user risk.                                       | CA302-Externals-IdentityProtection-AllApps-AnyPlatform-MFAandPWDforHighUserRisk                                       |
| CA303     | Externals   | IdentityProtection      | All Cloud Apps                                            | MFA if High Sign-In Risk                             | Extra MFA when sign-in risk is high.                                               | CA303-Externals-IdentityProtection-AllApps-AnyPlatform-MFAforHighSignInRisk                                           |
| CA304     | Externals   | IdentityProtection      | All Cloud Apps (EAS/Other clients)                        | Block                                                | Block legacy auth for externals.                                                  | CA304-Externals-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth                                                |
| CA305     | Externals   | AppProtection           | Microsoft Intune Enrollment                               | MFA                                                  | Requires MFA for external device enrollment.                                       | CA305-Externals-AppProtection-MicrosoftIntuneEnrollment-AnyPlatform-MFA                                               |
| CA306     | Externals   | DataandAppProtection    | Office 365 on iOS/Android                                 | Require Approved Client or App Protection            | Mobile control for external users.                                                | CA306-Externals-DataandAppProtection-AllApps-iOSorAndroid-ClientAppORAPP                                              |
| CA307     | Externals   | AttackSurfaceReduction  | All Cloud Apps (unknown platforms)                        | Block                                                | Blocks unknown platforms for externals.                                           | CA307-Externals-AttackSurfaceReduction-AllApps-AnyPlatform-BlockUnknownPlatforms                                       |
| CA400     | Guests      | BaseProtection          | All Cloud Apps                                            | MFA                                                  | Requires MFA for all guest users.                                                 | CA400-Guests-BaseProtection-AllApps-AnyPlatform-MFA                                                                    |
| CA401     | Guests      | IdentityProtection      | All Cloud Apps / Security Info Registration              | Terms of Use + Combined Reg (if needed)              | Could enforce TOU acceptance & MFA/SSPR reg.                                       | CA401-Guests-IdentityProtection-AllApps-AnyPlatform-TOU-CombinedRegistration                                          |
| CA402     | Guests      | IdentityProtection      | All Cloud Apps                                            | MFA if Med/High Sign-In Risk                         | Extra MFA for at-risk guest sign-ins.                                             | CA402-Guests-IdentityProtection-AllApps-AnyPlatform-MFAforMediumandHighSignInRisk                                     |
| CA403     | Guests      | IdentityProtection      | All Cloud Apps (EAS/Other clients)                        | Block                                                | Block legacy auth for guests.                                                     | CA403-Guests-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth                                                   |
| CA404     | Guests      | AttackSurfaceReduction  | All Cloud Apps, excluding O365/MyApps                     | Block                                                | Block non–Office 365 app access for guests.                                       | CA404-Guests-AttackSurfaceReduction-AllApps-AnyPlatform-BlockNonGuestAppAccess                                        |
| CA405     | Guests      | Compliance              | All Cloud Apps                                            | Require Terms of Use                                | Guests must accept Terms of Use.                                                  | CA405-Guests-ComplianceProtection-AllApps-AnyPlatform-RequireTOU                                                      |
| CA500     | GuestAdmins | BaseProtection          | All Cloud Apps                                            | MFA                                                  | MFA baseline for guest admins.                                                    | CA500-GuestAdmins-BaseProtection-AllApps-AnyPlatform-MFA                                                              |
| CA501     | GuestAdmins | IdentityProtection      | All Cloud Apps / Security Info Registration               | Possibly ToU + Compliant Registration                | Combined reg policy for guest admins.                                             | CA501-GuestAdmins-IdentityProtection-AllApps-AnyPlatform-CombinedRegistration                                         |
| CA502     | GuestAdmins | IdentityProtection      | All Cloud Apps                                            | MFA if Med/High Sign-In Risk                         | Additional MFA if sign-in risk is detected.                                       | CA502-GuestAdmins-IdentityProtection-AllApps-AnyPlatform-MFAforMediumandHighSignInRisk                                |
| CA503     | GuestAdmins | IdentityProtection      | All Cloud Apps (EAS/Other clients)                        | Block                                                | Block legacy auth for guest admins.                                              | CA503-GuestAdmins-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth                                              |
| CA504     | GuestAdmins | AttackSurfaceReduction  | All Cloud Apps, excluding O365, Azure Mgmt, MyApps        | Block                                                | Blocks broader usage beyond O365/Azure for guest admins.                          | CA504-GuestAdmins-AttackSurfaceReduction-AllApps-AnyPlatform-BlockNonO365andAzureAccess                               |
| CA505     | GuestAdmins | Compliance              | All Cloud Apps                                            | Require Terms of Use                                | Enforce TOU acceptance by guest admins.                                           | CA505-GuestAdmins-ComplianceProtection-AllApps-AnyPlatform-RequireTOU                                                 |
| CA600     | M365SvcAcct | BaseProtection          | All Cloud Apps                                            | Block outside Trusted Locations                     | E.g., only run from known IPs or data centers.                                    | CA600-Microsoft365ServiceAccounts-BaseProtection-AllApps-AnyPlatform-BlockUntrustedLocations                           |
| CA601     | M365SvcAcct | IdentityProtection      | All Cloud Apps (EAS/Other clients)                        | Block                                                | No legacy auth for M365 service accounts.                                         | CA601-Microsoft365ServiceAccounts-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth                               |
| CA602     | M365SvcAcct | AttackSurfaceReduction  | All Cloud Apps, excluding Office 365                      | Block                                                | Restricts usage to Office 365 only.                                               | CA602-Microsoft365ServiceAccounts-AttackSurfaceReduction-O365-AnyPlatform-BlockNonO365                                 |
| CA700     | AzureSvcAcct| BaseProtection          | All Cloud Apps                                            | Block outside Trusted Locations                     | Azure service accounts used only from trusted IPs.                                | CA700-AzureServiceAccounts-BaseProtection-AllApps-AnyPlatform-BlockUntrustedLocations                                 |
| CA701     | AzureSvcAcct| IdentityProtection      | All Cloud Apps (EAS/Other clients)                        | Block                                                | Block legacy auth for Azure service accounts.                                     | CA701-AzureServiceAccounts-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth                                      |
| CA702     | AzureSvcAcct| AttackSurfaceReduction  | All Cloud Apps, excluding Azure Management                | Block                                                | Restricts usage to Azure Management only.                                         | CA702-AzureServiceAccounts-AttackSurfaceReduction-AllApps-AnyPlatform-BlockNonAzure                                   |
| CA800     | CorpSvcAcct | BaseProtection          | All Cloud Apps                                            | Block outside Trusted Locations                     | On-prem corporate service accounts blocked outside known IP.                      | CA800-CorpServiceAccounts-BaseProtection-AllApps-AnyPlatform-BlockUntrustedLocations                                  |
| CA801     | CorpSvcAcct | IdentityProtection      | All Cloud Apps (EAS/Other clients)                        | Block                                                | Block legacy auth for corp-based service accounts.                                | CA801-CorpServiceAccounts-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth                                       |
| CA802     | CorpSvcAcct | AttackSurfaceReduction  | All Cloud Apps, excluding O365/Azure                      | Block                                                | Restricts usage to O365 + Azure only.                                             | CA802-CorpServiceAccounts-AttackSurfaceReduction-AllApps-AnyPlatform-BlockNonO365andAzure                              |
| CA900     | WorkloadIDs | BaseProtection          | All Cloud Apps                                            | Block outside Trusted Locations                     | Protects service principal usage from unknown IP.                                 | CA900-WorkloadIdentities-BaseProtection-AllApps-AnyPlatform-BlockUntrustedLocations                                   |
| CA1000    | Developers  | BaseProtection          | All Cloud Apps (excl. Enrollment apps)                    | Forward to Defender for Cloud Apps (Custom Session)  | Lets devs use device code flow if needed, routes all else via MCAS.               | CA1000-Developers-BaseProtection-AllApps-AnyPlatform-ForwardToDefenderforCloudApps                                     |
| CA1001    | Developers  | BaseProtection          | All Cloud Apps                                            | MFA if Unmanaged Device                              | Requires MFA from devs on non-managed devices.                                    | CA1001-Developers-BaseProtection-AllApps-AnyPlatform-MFAfromUnamagedDevices                                           |
| CA1002    | Developers  | IdentityProtection      | All Cloud Apps / Security Info Registration               | Require Compliant or HAADJ                           | Protects MFA/SSPR from a known device for devs.                                   | CA1002-Developers-IdentityProtection-AllApps-AnyPlatform-CombinedRegistration                                         |
| CA1003    | Developers  | IdentityProtection      | All Cloud Apps                                            | MFA + Password Change if High User Risk             | Extra re-auth for devs high user risk.                                            | CA1003-Developers-IdentityProtection-AllApps-AnyPlatform-MFAandPWDforHighUserRisk                                     |
| CA1004    | Developers  | IdentityProtection      | All Cloud Apps                                            | MFA if High Sign-In Risk                             | Prompts dev for MFA on high sign-in risk.                                         | CA1004-Developers-IdentityProtection-AllApps-AnyPlatform-MFAforHighSignInRisk                                         |
| CA1005    | Developers  | IdentityProtection      | All Cloud Apps (EAS/Other clients)                        | Block                                                | Blocks legacy auth for developers.                                               | CA1005-Developers-IdentityProtection-AllApps-AnyPlatform-BlockLegacyAuth                                              |
| CA1006    | Developers  | AppProtection           | Microsoft Intune Enrollment                               | MFA                                                  | MFA to enroll dev devices.                                                        | CA1006-Developers-AppProtection-MicrosoftIntuneEnrollment-AnyPlatform-MFA                                             |
| CA1007    | Developers  | DataandAppProtection    | Office 365 on iOS/Android                                 | Require Approved Client or App Protection            | Mobile app protection for developer persona.                                      | CA1007-Developers-DataandAppProtection-AllApps-iOSorAndroid-ClientAppORAPP                                            |
| CA1008    | Developers  | AttackSurfaceReduction  | All Cloud Apps (unknown platforms)                        | Block                                                | Blocks unknown platforms for devs.                                                | CA1008-Developers-AttackSurfaceReduction-AllApps-AnyPlatform-BlockUnknownPlatforms                                    |

---

## Implementation Notes

### Important Considerations

1. **App Exclusions**: Actual implementation often excludes certain apps (e.g., Intune Enrollment, Windows Azure Service Management API) from the "AllApps" scope in BaseProtection policies.

2. **Break-Glass Accounts**: Many policies exclude emergency break-glass accounts or special service accounts to prevent lockout scenarios.

3. **Licensing Requirements**: Some features require specific Azure AD/Microsoft Entra ID licenses:
   - **Azure AD Premium P1**: Basic Conditional Access, device-based policies
   - **Azure AD Premium P2**: Risk-based policies (Identity Protection), privileged identity management

4. **Phased Rollout**: Consider implementing policies in phases:
   - **Phase 1**: Global baseline and admin policies
   - **Phase 2**: Internal user policies
   - **Phase 3**: External and guest policies
   - **Phase 4**: Service account and developer policies

5. **Testing**: Always test policies in "Report-only" mode before enabling them to understand impact.

6. **Named Locations**: Configure trusted IP ranges before implementing location-based policies.

7. **Device Compliance**: Ensure Intune device compliance policies are configured before requiring compliant devices.

### Customization

Organizations should customize these policies based on:
- Licensing availability
- Risk tolerance
- Regulatory requirements
- User productivity needs
- Existing infrastructure (hybrid, cloud-only)

---

## Policy Management Best Practices

### 1. Use Consistent Naming
Follow the naming convention strictly to make policies easily identifiable and manageable at scale.

### 2. Document Exclusions
Maintain clear documentation of:
- Emergency break-glass accounts
- Service accounts excluded from policies
- Special user groups with policy exemptions

### 3. Regular Reviews
- Quarterly review of all policies
- Validate exclusions are still necessary
- Check for new Microsoft recommendations

### 4. Monitor Sign-In Logs
Regularly review Azure AD sign-in logs to:
- Identify blocked users who should have access
- Detect policy gaps
- Optimize user experience

### 5. Maintain Emergency Access
- Create 2-3 break-glass accounts excluded from all CA policies
- Store credentials securely offline
- Test quarterly to ensure they work

---

## Quick Reference - Persona Groups

| Persona | Typical Members | Key Security Requirements |
|---------|----------------|--------------------------|
| **Global** | All users not in other groups | Catch-all blocking policy |
| **Admins** | Global Admins, Privileged Role Admins | Strictest controls: MFA, compliant devices, 4h sessions |
| **Internals** | Full-time employees | Compliant devices, MFA for risk, app protection |
| **Externals** | Contractors, consultants | Similar to internals but tighter controls |
| **Guests** | External collaborators (B2B) | MFA, limited app access, Terms of Use |
| **GuestAdmins** | External users with admin roles | MFA, very limited app access, TOU |
| **M365SvcAcct** | Service accounts for M365 workloads | Location-restricted, no legacy auth, O365 only |
| **AzureSvcAcct** | Service accounts for Azure | Location-restricted, no legacy auth, Azure only |
| **CorpSvcAcct** | On-premises service accounts | Location-restricted, no legacy auth |
| **WorkloadIDs** | Service principals, managed identities | Location-restricted |
| **Developers** | Software developers | Defender for Cloud Apps, MFA from unmanaged devices |

---

## Common Grant Controls Explained

| Grant Control | Description | Use Case |
|--------------|-------------|----------|
| **Block** | Explicitly deny access | High-risk scenarios, policy violations |
| **MFA** | Require multi-factor authentication | Additional verification for sensitive access |
| **Compliant Device** | Device must meet Intune compliance policies | Corporate device management |
| **Hybrid Azure AD Joined** | Device must be domain-joined and synced | On-premises AD integration |
| **Approved Client App** | Must use specific mobile apps (Outlook, Teams, etc.) | Mobile app management |
| **App Protection Policy** | Require Intune APP/MAM policy | BYOD scenarios with data protection |
| **Terms of Use** | Accept legal agreement | Compliance and legal requirements |
| **Password Change** | Force password reset | High user risk scenarios |

---

## References

- [Microsoft Entra Conditional Access Documentation](https://learn.microsoft.com/en-us/azure/active-directory/conditional-access/)
- [Zero Trust Security Model](https://www.microsoft.com/en-us/security/business/zero-trust)
- [Conditional Access Best Practices](https://learn.microsoft.com/en-us/azure/active-directory/conditional-access/best-practices)

---

**Last Updated**: November 2025  
**Version**: 1.0
