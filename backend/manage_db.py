#!/usr/bin/env python3
"""
Database management CLI for CloudPulse Monitor
Provides commands for database initialization, migration, and management
"""

import argparse
import sys
import logging
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.init_db import init_database, reset_database
from app.database import check_database_connection, create_tables, drop_tables
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_connection():
    """Check database connection"""
    logger.info("Checking database connection...")
    if check_database_connection():
        logger.info("✅ Database connection successful")
        logger.info(f"Database URL: {settings.database_url}")
        return True
    else:
        logger.error("❌ Database connection failed")
        logger.error(f"Database URL: {settings.database_url}")
        return False


def initialize_db(with_sample_data=False):
    """Initialize database with tables and optional sample data"""
    logger.info("Initializing database...")
    if init_database(create_sample_data=with_sample_data):
        logger.info("✅ Database initialized successfully")
        return True
    else:
        logger.error("❌ Database initialization failed")
        return False


def reset_db():
    """Reset database (drop and recreate all tables)"""
    logger.warning("⚠️  This will delete all data in the database!")
    confirm = input("Are you sure you want to continue? (yes/no): ")
    if confirm.lower() == 'yes':
        logger.info("Resetting database...")
        if reset_database():
            logger.info("✅ Database reset successfully")
            return True
        else:
            logger.error("❌ Database reset failed")
            return False
    else:
        logger.info("Database reset cancelled")
        return False


def create_tables_only():
    """Create tables without sample data"""
    logger.info("Creating database tables...")
    try:
        create_tables()
        logger.info("✅ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        return False


def drop_tables_only():
    """Drop all database tables"""
    logger.warning("⚠️  This will delete all tables and data!")
    confirm = input("Are you sure you want to continue? (yes/no): ")
    if confirm.lower() == 'yes':
        logger.info("Dropping database tables...")
        try:
            drop_tables()
            logger.info("✅ Database tables dropped successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to drop tables: {e}")
            return False
    else:
        logger.info("Drop tables cancelled")
        return False


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="CloudPulse Monitor Database Management")
    parser.add_argument(
        'command',
        choices=['check', 'init', 'init-with-data', 'reset', 'create-tables', 'drop-tables'],
        help='Database management command'
    )
    
    args = parser.parse_args()
    
    # Display current configuration
    logger.info(f"Database Host: {settings.DATABASE_HOST}")
    logger.info(f"Database Port: {settings.DATABASE_PORT}")
    logger.info(f"Database Name: {settings.DATABASE_NAME}")
    logger.info(f"Database User: {settings.DATABASE_USER}")
    logger.info("=" * 50)
    
    success = False
    
    if args.command == 'check':
        success = check_connection()
    elif args.command == 'init':
        success = initialize_db(with_sample_data=False)
    elif args.command == 'init-with-data':
        success = initialize_db(with_sample_data=True)
    elif args.command == 'reset':
        success = reset_db()
    elif args.command == 'create-tables':
        success = create_tables_only()
    elif args.command == 'drop-tables':
        success = drop_tables_only()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()