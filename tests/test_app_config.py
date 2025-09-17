#!/usr/bin/env python3
"""
Quick test to verify the Flask app loads the correct WordPress credentials
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.routes import WP_SITE, WP_USER, WP_APP_PASSWORD

print("🔍 Flask App WordPress Configuration:")
print(f"   Site: {WP_SITE}")
print(f"   User: {WP_USER}")
print(f"   Password: {WP_APP_PASSWORD[:8]}..." if WP_APP_PASSWORD else "   Password: <EMPTY>")

if WP_APP_PASSWORD == "LgTw Bd3y UcJy aOZR q9Zr Nd9r":
    print("   ✅ Password matches config file")
else:
    print("   ❌ Password doesn't match config file")
    print(f"   Expected: LgTw Bd3y UcJy aOZR q9Zr Nd9r")
    print(f"   Got: {WP_APP_PASSWORD}")