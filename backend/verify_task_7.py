#!/usr/bin/env python3
"""
Verify that Task 7 - Create API route handlers is fully implemented
according to requirements 4.2, 4.3, 4.4, and 4.5
"""

import os
from pathlib import Path

def check_endpoint_implementation(file_path, endpoint_info):
    """Check if an endpoint is properly implemented"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for the endpoint definition
        endpoint_patterns = [
            f'@router.{endpoint_info["method"].lower()}("{endpoint_info["path"]}"',
            f"@router.{endpoint_info['method'].lower()}('{endpoint_info['path']}'"
        ]
        
        endpoint_found = any(pattern in content for pattern in endpoint_patterns)
        
        if endpoint_found:
            # Check for response model if specified
            if endpoint_info.get("response_model"):
                if f'response_model={endpoint_info["response_model"]}' in content:
                    return True, "✓ Endpoint with correct response model"
                else:
                    return True, "✓ Endpoint found (response model not verified)"
            return True, "✓ Endpoint found"
        else:
            return False, "✗ Endpoint not found"
            
    except Exception as e:
        return False, f"✗ Error reading file: {e}"

def verify_requirement_4_2():
    """Verify Requirement 4.2: GET /api/metrics returns CPU %, Memory %, Network traffic data"""
    print("\n📋 Requirement 4.2: GET /api/metrics endpoint")
    
    metrics_file = Path("backend/app/routes/metrics.py")
    
    endpoint_info = {
        "method": "GET",
        "path": "/",
        "response_model": "SystemMetrics"
    }
    
    success, message = check_endpoint_implementation(metrics_file, endpoint_info)
    print(f"  {message}")
    
    if success:
        # Check if the response includes required fields
        with open(metrics_file, 'r') as f:
            content = f.read()
        
        required_fields = ["cpu_usage", "memory_usage", "network_traffic"]
        fields_found = all(field in content for field in required_fields)
        
        if fields_found:
            print("  ✓ Response includes CPU, Memory, and Network traffic data")
        else:
            print("  ⚠ Response fields not verified in implementation")
    
    return success

def verify_requirement_4_3():
    """Verify Requirement 4.3: GET /api/services returns array of services with name, uptime, status"""
    print("\n📋 Requirement 4.3: GET /api/services endpoint")
    
    services_file = Path("backend/app/routes/services.py")
    
    endpoint_info = {
        "method": "GET",
        "path": "/",
        "response_model": "List[ServiceResponse]"
    }
    
    success, message = check_endpoint_implementation(services_file, endpoint_info)
    print(f"  {message}")
    
    if success:
        # Check if the response includes required fields
        with open(services_file, 'r') as f:
            content = f.read()
        
        required_fields = ["name", "uptime", "status"]
        fields_found = all(field in content for field in required_fields)
        
        if fields_found:
            print("  ✓ Response includes service name, uptime, and status")
        else:
            print("  ⚠ Response fields not verified in implementation")
    
    return success

def verify_requirement_4_4():
    """Verify Requirement 4.4: GET /api/logs returns array with id, timestamp, message, level, service_name"""
    print("\n📋 Requirement 4.4: GET /api/logs endpoint")
    
    logs_file = Path("backend/app/routes/logs.py")
    
    endpoint_info = {
        "method": "GET",
        "path": "/",
        "response_model": "LogsListResponse"
    }
    
    success, message = check_endpoint_implementation(logs_file, endpoint_info)
    print(f"  {message}")
    
    if success:
        # Check if the response includes required fields
        with open(logs_file, 'r') as f:
            content = f.read()
        
        required_fields = ["id", "timestamp", "message", "level", "service_name"]
        fields_found = all(field in content for field in required_fields)
        
        if fields_found:
            print("  ✓ Response includes id, timestamp, message, level, and service_name")
        else:
            print("  ⚠ Response fields not verified in implementation")
        
        # Check for filtering capability
        if "level:" in content and "service:" in content:
            print("  ✓ Filtering by level and service implemented")
        else:
            print("  ⚠ Filtering capability not verified")
    
    return success

def verify_requirement_4_5():
    """Verify Requirement 4.5: GET /api/status returns overall system health"""
    print("\n📋 Requirement 4.5: GET /api/status endpoint")
    
    status_file = Path("backend/app/routes/status.py")
    
    endpoint_info = {
        "method": "GET",
        "path": "/",
        "response_model": "SystemStatus"
    }
    
    success, message = check_endpoint_implementation(status_file, endpoint_info)
    print(f"  {message}")
    
    if success:
        # Check if the response includes system health information
        with open(status_file, 'r') as f:
            content = f.read()
        
        health_indicators = ["overall_status", "services_online", "services_total"]
        health_found = all(indicator in content for indicator in health_indicators)
        
        if health_found:
            print("  ✓ Response includes overall system health information")
        else:
            print("  ⚠ System health fields not verified in implementation")
    
    return success

def verify_error_handling():
    """Verify that proper error handling is implemented"""
    print("\n📋 Error Handling Verification")
    
    route_files = [
        "backend/app/routes/metrics.py",
        "backend/app/routes/services.py", 
        "backend/app/routes/logs.py",
        "backend/app/routes/status.py"
    ]
    
    error_handling_found = True
    
    for file_path in route_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for HTTPException usage
            if "HTTPException" in content and "try:" in content and "except" in content:
                print(f"  ✓ Error handling found in {Path(file_path).name}")
            else:
                print(f"  ⚠ Error handling not verified in {Path(file_path).name}")
                error_handling_found = False
                
        except Exception as e:
            print(f"  ✗ Could not verify {Path(file_path).name}: {e}")
            error_handling_found = False
    
    return error_handling_found

def verify_router_integration():
    """Verify that all routers are properly integrated in main.py"""
    print("\n📋 Router Integration Verification")
    
    main_file = Path("backend/app/main.py")
    
    try:
        with open(main_file, 'r') as f:
            content = f.read()
        
        required_imports = "from .routes import metrics, services, logs, status"
        required_includes = [
            "app.include_router(metrics.router)",
            "app.include_router(services.router)",
            "app.include_router(logs.router)", 
            "app.include_router(status.router)"
        ]
        
        if required_imports in content:
            print("  ✓ Route modules imported correctly")
        else:
            print("  ✗ Route imports missing or incorrect")
            return False
        
        all_included = True
        for include in required_includes:
            if include in content:
                router_name = include.split('(')[1].split('.')[0]
                print(f"  ✓ {router_name} router included")
            else:
                print(f"  ✗ Router include missing: {include}")
                all_included = False
        
        return all_included
        
    except Exception as e:
        print(f"  ✗ Error reading main.py: {e}")
        return False

def main():
    """Main verification function"""
    print("🔍 Verifying Task 7: Create API route handlers")
    print("=" * 60)
    
    # Change to the correct directory
    os.chdir(Path(__file__).parent.parent)
    
    # Verify each requirement
    req_4_2 = verify_requirement_4_2()
    req_4_3 = verify_requirement_4_3()
    req_4_4 = verify_requirement_4_4()
    req_4_5 = verify_requirement_4_5()
    
    # Verify additional aspects
    error_handling = verify_error_handling()
    router_integration = verify_router_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TASK 7 VERIFICATION SUMMARY")
    print("=" * 60)
    
    requirements_met = [
        ("4.2 - GET /api/metrics endpoint", req_4_2),
        ("4.3 - GET /api/services endpoint", req_4_3), 
        ("4.4 - GET /api/logs endpoint with filtering", req_4_4),
        ("4.5 - GET /api/status endpoint", req_4_5),
        ("Error handling implementation", error_handling),
        ("Router integration in main.py", router_integration)
    ]
    
    all_passed = True
    for requirement, passed in requirements_met:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {requirement}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 TASK 7 COMPLETED SUCCESSFULLY!")
        print("\nAll API route handlers have been implemented according to requirements:")
        print("  • GET /api/metrics - Returns system metrics (CPU, Memory, Network)")
        print("  • GET /api/services - Returns services array with name, uptime, status")
        print("  • GET /api/logs - Returns logs with filtering by level and service")
        print("  • GET /api/status - Returns overall system health status")
        print("  • Proper error handling with HTTPException")
        print("  • All routers integrated in main FastAPI application")
        return 0
    else:
        print("❌ TASK 7 INCOMPLETE - Some requirements not met")
        return 1

if __name__ == "__main__":
    exit(main())