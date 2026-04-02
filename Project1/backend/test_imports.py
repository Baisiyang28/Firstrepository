#!/usr/bin/env python3
"""
简化测试脚本
"""

try:
    print("Testing imports...")
    from flask import Flask
    print("✅ Flask imported")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")
    exit(1)

try:
    from flask_sqlalchemy import SQLAlchemy
    print("✅ SQLAlchemy imported")
except ImportError as e:
    print(f"❌ SQLAlchemy import failed: {e}")
    exit(1)

try:
    from flask_cors import CORS
    print("✅ CORS imported")
except ImportError as e:
    print(f"❌ CORS import failed: {e}")
    exit(1)

try:
    from flask_restful import Api
    print("✅ RESTful imported")
except ImportError as e:
    print(f"❌ RESTful import failed: {e}")
    exit(1)

try:
    import jwt
    print("✅ PyJWT imported")
except ImportError as e:
    print(f"❌ PyJWT import failed: {e}")
    exit(1)

print("\n🎉 All imports successful!")

# Test app creation
try:
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SECRET_KEY'] = 'test_key'
    print("✅ Flask app created")
except Exception as e:
    print(f"❌ Flask app creation failed: {e}")
    exit(1)

print("🚀 Basic setup test passed!")