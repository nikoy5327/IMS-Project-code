#!/usr/bin/env python3
import sys
import os

def check_python():
    print("🐍 Python check:")
    print(f"   Python version: {sys.version}")
    print(f"   Virtual env: {os.getenv('VIRTUAL_ENV', 'Not activated')}")
    return True

def check_dependencies():
    print("📦 Dependencies check:")
    dependencies = ['flask', 'flask_cors', 'psycopg2', 'dotenv']
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep} - MISSING")
    return True

def check_app():
    print("🔧 App check:")
    try:
        from app import app
        print("   ✅ Flask app imports successfully")
        return True
    except Exception as e:
        print(f"   ❌ Flask app import failed: {e}")
        return False

def check_database():
    print("🗄️ Database check:")
    try:
        from db import test_db_connection
        success, message = test_db_connection()
        if success:
            print(f"   ✅ {message}")
            return True
        else:
            print(f"   ❌ {message}")
            return False
    except Exception as e:
        print(f"   ❌ Database check failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Running IMS Diagnostics...")
    print("=" * 50)
    
    check_python()
    print()
    check_dependencies()
    print()
    check_app()
    print()
    check_database()
    
    print("=" * 50)
    print("💡 If you see any '❌' above, those need to be fixed.")
