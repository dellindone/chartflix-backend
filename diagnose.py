#!/usr/bin/env python
"""
Diagnostic script to identify import errors
"""
import sys
import traceback

print("=" * 80)
print("CHARTFLIX DIAGNOSTIC SCRIPT")
print("=" * 80)

modules_to_test = [
    ("app.core.config", "Configuration"),
    ("app.db.base", "Database Base"),
    ("app.db.engine", "Database Engine"),
    ("app.db.session", "Database Session"),
    ("app.model.user.models", "User Model"),
    ("app.model.token.token", "Token Model"),
    ("app.schemas.auth", "Auth Schemas"),
    ("app.schemas.user", "User Schemas"),
    ("app.modules.auth.deps", "Auth Dependencies"),
    ("app.modules.auth.service", "Auth Service"),
    ("app.modules.auth.router", "Auth Router"),
    ("app.modules.user.router", "User Router"),
    ("app.main", "Main App"),
]

for module_name, description in modules_to_test:
    try:
        print(f"\n[TESTING] {description:<25} ({module_name})")
        __import__(module_name)
        print(f"  ✓ SUCCESS")
    except Exception as e:
        print(f"  ✗ FAILED")
        print(f"  Error: {type(e).__name__}: {e}")
        traceback.print_exc()
        print("\n" + "=" * 80)
        print(f"FAILED AT: {module_name}")
        print("=" * 80)
        sys.exit(1)

print("\n" + "=" * 80)
print("✓ ALL IMPORTS SUCCESSFUL")
print("=" * 80)
