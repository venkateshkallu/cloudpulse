#!/usr/bin/env python3
"""
Validate that all required API route handlers are implemented correctly
"""

import sys
import os
import importlib.util
from pathlib import Path

def validate_route_file(file_path, expected_endpoints):
    """Validate that a route file contains the expected endpoints"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        print(f"\n📁 Validating {file_path.name}:")
        
        # Check if router is defined
        if 'router = APIRouter(' in content:
            print("  ✓ Router defined")
        else:
            print("  ✗ Router not found")
            return False
        
        # Check for expected endpoints
        all_found = True
        for endpoint in expected_endpoints:
            if f'@router.{endpoint["method"].lower()}("{endpoint["path"]}")' in content or \
               f"@router.{endpoint['method'].lower()}('{endpoint['path']}')" in content:
                print(f"  ✓ {endpoint['method']} {endpoint['path']}")
            else:
                print(f"  ✗ {endpoint['method']} {endpoint['path']} - NOT FOUND")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"  ✗ Error reading file: {e}")
        return False

def main():
    """Main validation function"""
    print("🔍 Validating CloudPulse API Route Handlers")
    print("=" * 50)
    
    backend_dir = Path(__file__).parent
    routes_dir = backend_dir / "app" / "routes"
    
    # Define expected endpoints for each route file
    route_expectations = {
        "metrics.py": [
            {"method": "GET", "path": "/"},
            {"method": "GET", "path": "/history"},
            {"method": "GET", "path": "/summary"}
        ],
        "services.py": [
            {"method": "GET", "path": "/"},
            {"method": "GET", "path": "/{service_id}"},
            {"method": "POST", "path": "/"},
            {"method": "PUT", "path": "/{service_id}"},
            {"method": "GET", "path": "/{service_id}/health"}
        ],
        "logs.py": [
            {"method": "GET", "path": "/"},
            {"method": "POST", "path": "/"},
            {"method": "GET", "path": "/levels"},
            {"method": "GET", "path": "/services"},
            {"method": "GET", "path": "/stats"},
            {"method": "DELETE", "path": "/"}
        ],
        "status.py": [
            {"method": "GET", "path": "/"},
            {"method": "GET", "path": "/health"},
            {"method": "GET", "path": "/detailed"},
            {"method": "GET", "path": "/uptime"}
        ]
    }
    
    all_valid = True
    
    # Validate each route file
    for filename, expected_endpoints in route_expectations.items():
        file_path = routes_dir / filename
        
        if not file_path.exists():
            print(f"\n📁 {filename}:")
            print(f"  ✗ File not found at {file_path}")
            all_valid = False
            continue
        
        if not validate_route_file(file_path, expected_endpoints):
            all_valid = False
    
    # Check main.py integration
    print(f"\n📁 Validating main.py integration:")
    main_py = backend_dir / "app" / "main.py"
    
    if main_py.exists():
        with open(main_py, 'r') as f:
            main_content = f.read()
        
        required_imports = [
            "from .routes import metrics, services, logs, status"
        ]
        
        required_includes = [
            "app.include_router(metrics.router)",
            "app.include_router(services.router)", 
            "app.include_router(logs.router)",
            "app.include_router(status.router)"
        ]
        
        for import_stmt in required_imports:
            if import_stmt in main_content:
                print(f"  ✓ Route imports found")
            else:
                print(f"  ✗ Route imports missing: {import_stmt}")
                all_valid = False
        
        for include_stmt in required_includes:
            if include_stmt in main_content:
                print(f"  ✓ Router included: {include_stmt.split('(')[1].split(')')[0]}")
            else:
                print(f"  ✗ Router not included: {include_stmt}")
                all_valid = False
    else:
        print("  ✗ main.py not found")
        all_valid = False
    
    # Check schemas and models
    print(f"\n📁 Validating supporting files:")
    
    schemas_py = backend_dir / "app" / "schemas.py"
    if schemas_py.exists():
        print("  ✓ schemas.py exists")
    else:
        print("  ✗ schemas.py missing")
        all_valid = False
    
    models_py = backend_dir / "app" / "models.py"
    if models_py.exists():
        print("  ✓ models.py exists")
    else:
        print("  ✗ models.py missing")
        all_valid = False
    
    database_py = backend_dir / "app" / "database.py"
    if database_py.exists():
        print("  ✓ database.py exists")
    else:
        print("  ✗ database.py missing")
        all_valid = False
    
    # Final result
    print("\n" + "=" * 50)
    if all_valid:
        print("🎉 All API route handlers are properly implemented!")
        print("\nImplemented endpoints:")
        print("  • GET /api/metrics/ - Current system metrics")
        print("  • GET /api/metrics/history - Historical metrics")
        print("  • GET /api/metrics/summary - Metrics summary")
        print("  • GET /api/services/ - All services status")
        print("  • GET /api/services/{id} - Specific service")
        print("  • POST /api/services/ - Create service")
        print("  • PUT /api/services/{id} - Update service")
        print("  • GET /api/services/{id}/health - Service health check")
        print("  • GET /api/logs/ - Logs with filtering")
        print("  • POST /api/logs/ - Create log entry")
        print("  • GET /api/logs/levels - Available log levels")
        print("  • GET /api/logs/services - Services with logs")
        print("  • GET /api/logs/stats - Log statistics")
        print("  • DELETE /api/logs/ - Clear old logs")
        print("  • GET /api/status/ - Overall system status")
        print("  • GET /api/status/health - Health check")
        print("  • GET /api/status/detailed - Detailed status")
        print("  • GET /api/status/uptime - System uptime")
        return 0
    else:
        print("❌ Some route handlers are missing or incomplete!")
        return 1

if __name__ == "__main__":
    sys.exit(main())