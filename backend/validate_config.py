#!/usr/bin/env python3
"""
Configuration validation script for CloudPulse Monitor
Validates environment variables and configuration settings
"""

import os
import sys
from typing import List, Dict, Any
from app.config import Settings, Environment


def validate_required_vars() -> List[str]:
    """Validate that all required environment variables are set"""
    errors = []
    
    # Required variables for all environments
    required_vars = [
        "DATABASE_HOST",
        "DATABASE_PORT", 
        "DATABASE_NAME",
        "DATABASE_USER",
        "DATABASE_PASSWORD"
    ]
    
    for var in required_vars:
        if not os.getenv(var):
            errors.append(f"Missing required environment variable: {var}")
    
    return errors


def validate_production_config(settings: Settings) -> List[str]:
    """Validate production-specific configuration"""
    errors = []
    
    if not settings.is_production:
        return errors
    
    # Production security checks
    if settings.SECRET_KEY == "dev-secret-key-change-in-production":
        errors.append("SECRET_KEY must be changed in production")
    
    if len(settings.SECRET_KEY) < 32:
        errors.append("SECRET_KEY should be at least 32 characters long")
    
    if settings.DEBUG:
        errors.append("DEBUG should be False in production")
    
    if settings.DOCS_ENABLED:
        errors.append("DOCS_ENABLED should be False in production for security")
    
    # CORS validation
    if "*" in settings.CORS_ORIGINS:
        errors.append("CORS_ORIGINS should not contain '*' in production")
    
    for origin in settings.CORS_ORIGINS:
        if origin.startswith("http://"):
            errors.append(f"CORS origin should use HTTPS in production: {origin}")
    
    return errors


def validate_database_config(settings: Settings) -> List[str]:
    """Validate database configuration"""
    errors = []
    
    # Database connection validation
    if settings.DATABASE_PORT < 1 or settings.DATABASE_PORT > 65535:
        errors.append(f"Invalid DATABASE_PORT: {settings.DATABASE_PORT}")
    
    if settings.DATABASE_POOL_SIZE < 1:
        errors.append(f"DATABASE_POOL_SIZE must be at least 1: {settings.DATABASE_POOL_SIZE}")
    
    if settings.DATABASE_MAX_OVERFLOW < 0:
        errors.append(f"DATABASE_MAX_OVERFLOW cannot be negative: {settings.DATABASE_MAX_OVERFLOW}")
    
    if settings.DATABASE_POOL_TIMEOUT < 1:
        errors.append(f"DATABASE_POOL_TIMEOUT must be at least 1: {settings.DATABASE_POOL_TIMEOUT}")
    
    return errors


def validate_cors_config(settings: Settings) -> List[str]:
    """Validate CORS configuration"""
    errors = []
    
    if not settings.CORS_ORIGINS:
        errors.append("CORS_ORIGINS cannot be empty")
    
    for origin in settings.CORS_ORIGINS:
        if not origin.startswith(("http://", "https://")):
            errors.append(f"Invalid CORS origin format: {origin}")
    
    return errors


def test_database_connection(settings: Settings) -> List[str]:
    """Test database connection"""
    errors = []
    
    try:
        from app.database import check_database_connection
        if not check_database_connection():
            errors.append("Cannot connect to database with provided credentials")
    except Exception as e:
        errors.append(f"Database connection test failed: {e}")
    
    return errors


def print_config_summary(settings: Settings):
    """Print configuration summary"""
    print("\n" + "="*60)
    print("CLOUDPULSE MONITOR CONFIGURATION SUMMARY")
    print("="*60)
    
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"API Host: {settings.API_HOST}:{settings.API_PORT}")
    print(f"Database: {settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}")
    print(f"CORS Origins: {', '.join(settings.CORS_ORIGINS)}")
    print(f"Log Level: {settings.LOG_LEVEL}")
    print(f"Background Tasks: {'Enabled' if settings.ENABLE_BACKGROUND_TASKS else 'Disabled'}")
    print(f"API Documentation: {'Enabled' if settings.DOCS_ENABLED else 'Disabled'}")
    
    if settings.is_production:
        print("\n⚠️  PRODUCTION MODE - Security features enabled")
    elif settings.is_testing:
        print("\n🧪 TESTING MODE - Optimized for testing")
    else:
        print("\n🔧 DEVELOPMENT MODE - Debug features enabled")


def main():
    """Main validation function"""
    print("CloudPulse Monitor Configuration Validator")
    print("-" * 50)
    
    try:
        # Load settings
        settings = Settings()
        
        # Collect all validation errors
        all_errors = []
        
        # Run validations
        all_errors.extend(validate_required_vars())
        all_errors.extend(validate_production_config(settings))
        all_errors.extend(validate_database_config(settings))
        all_errors.extend(validate_cors_config(settings))
        
        # Test database connection if basic config is valid
        if not all_errors:
            all_errors.extend(test_database_connection(settings))
        
        # Print results
        if all_errors:
            print("\n❌ CONFIGURATION ERRORS FOUND:")
            for i, error in enumerate(all_errors, 1):
                print(f"  {i}. {error}")
            print(f"\nFound {len(all_errors)} configuration error(s)")
            sys.exit(1)
        else:
            print("\n✅ Configuration validation passed!")
            print_config_summary(settings)
            print("\n🚀 Ready to start CloudPulse Monitor!")
            
    except Exception as e:
        print(f"\n❌ Configuration validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()