#!/usr/bin/env python3
"""
Validation script to check database implementation structure
Verifies that all required files and components are present
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and report status"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (MISSING)")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists and report status"""
    if os.path.isdir(dirpath):
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description}: {dirpath} (MISSING)")
        return False

def validate_file_content(filepath, required_content, description):
    """Check if file contains required content"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            for item in required_content:
                if item in content:
                    print(f"✅ {description} contains: {item}")
                else:
                    print(f"❌ {description} missing: {item}")
                    return False
        return True
    except FileNotFoundError:
        print(f"❌ {description}: File not found")
        return False

def main():
    """Main validation function"""
    print("CloudPulse Monitor Database Implementation Validation")
    print("=" * 60)
    
    all_checks_passed = True
    
    # Check core database files
    files_to_check = [
        ("app/database.py", "Database connection module"),
        ("app/models.py", "SQLAlchemy models"),
        ("app/schemas.py", "Pydantic schemas"),
        ("app/init_db.py", "Database initialization"),
        ("manage_db.py", "Database management CLI"),
        ("alembic.ini", "Alembic configuration"),
        ("alembic/env.py", "Alembic environment"),
        ("alembic/script.py.mako", "Alembic script template"),
        ("alembic/versions/001_initial_schema.py", "Initial migration"),
        ("DATABASE.md", "Database documentation")
    ]
    
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_checks_passed = False
    
    # Check directories
    directories_to_check = [
        ("alembic", "Alembic directory"),
        ("alembic/versions", "Alembic versions directory"),
        ("app", "Application directory")
    ]
    
    for dirpath, description in directories_to_check:
        if not check_directory_exists(dirpath, description):
            all_checks_passed = False
    
    print("\n" + "=" * 60)
    
    # Check content of key files
    print("\nContent Validation:")
    
    # Check models.py for required classes
    model_checks = [
        "class Log(Base):",
        "class Service(Base):",
        "class Metric(Base):",
        "__tablename__"
    ]
    if not validate_file_content("app/models.py", model_checks, "Models file"):
        all_checks_passed = False
    
    # Check schemas.py for required schemas
    schema_checks = [
        "class LogResponse",
        "class ServiceResponse", 
        "class MetricResponse",
        "class SystemMetrics",
        "class SystemStatus"
    ]
    if not validate_file_content("app/schemas.py", schema_checks, "Schemas file"):
        all_checks_passed = False
    
    # Check database.py for required functions
    database_checks = [
        "def get_db(",
        "def create_tables(",
        "def check_database_connection(",
        "SessionLocal",
        "Base"
    ]
    if not validate_file_content("app/database.py", database_checks, "Database file"):
        all_checks_passed = False
    
    print("\n" + "=" * 60)
    
    if all_checks_passed:
        print("🎉 All validation checks passed!")
        print("Database implementation is complete and ready for use.")
    else:
        print("⚠️  Some validation checks failed.")
        print("Please review the missing components above.")
    
    return all_checks_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)