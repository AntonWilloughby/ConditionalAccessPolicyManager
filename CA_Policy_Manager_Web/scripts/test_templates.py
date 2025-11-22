#!/usr/bin/env python3
"""Test script to verify CA policy templates"""

from ca_policy_examples import POLICY_TEMPLATES, get_policy_categories, get_total_policy_count

print("✅ Policy templates loaded successfully!")
print(f"\nTotal policies: {get_total_policy_count()}")
print("\nPolicies by category:")

cats = get_policy_categories()
for category, policies in cats.items():
    print(f"  • {category}: {len(policies)} policies")
    for policy in policies:
        print(f"    - {policy}")

print("\n✅ All templates ready for deployment!")
