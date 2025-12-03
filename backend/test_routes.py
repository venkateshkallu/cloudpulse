#!/usr/bin/env python3
"""
Test script to verify API route handlers are working correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from fastapi.testclient import TestClient
from app.main import app

def test_routes():
    """Test all API route handlers"""
    client = TestClient(app)
    
    # Test main endpoints
    endpoints = [
        '/api/metrics/',
        '/api/services/',
        '/api/logs/',
        '/api/status/'
    ]
    
    print('Testing main API endpoints...')
    for endpoint in endpoints:
        try:
            response = client.get(endpoint)
            status = "✓ OK" if response.status_code == 200 else f"✗ ERROR (Status: {response.status_code})"
            print(f'{endpoint:<20} {status}')
        except Exception as e:
            print(f'{endpoint:<20} ✗ ERROR - {str(e)}')
    
    print('\nTesting additional endpoints...')
    additional_endpoints = [
        '/api/metrics/summary',
        '/api/services/api-gateway',
        '/api/logs/levels',
        '/api/status/health',
        '/health'
    ]
    
    for endpoint in additional_endpoints:
        try:
            response = client.get(endpoint)
            status = "✓ OK" if response.status_code == 200 else f"✗ ERROR (Status: {response.status_code})"
            print(f'{endpoint:<25} {status}')
        except Exception as e:
            print(f'{endpoint:<25} ✗ ERROR - {str(e)}')
    
    print('\nTesting endpoint responses...')
    
    # Test metrics endpoint response structure
    try:
        response = client.get('/api/metrics/')
        if response.status_code == 200:
            data = response.json()
            required_fields = ['cpu_usage', 'memory_usage', 'network_traffic', 'container_count', 'overall_health', 'timestamp']
            missing_fields = [field for field in required_fields if field not in data]
            if not missing_fields:
                print('Metrics response structure: ✓ OK')
            else:
                print(f'Metrics response structure: ✗ Missing fields: {missing_fields}')
        else:
            print(f'Metrics response structure: ✗ HTTP {response.status_code}')
    except Exception as e:
        print(f'Metrics response structure: ✗ ERROR - {str(e)}')
    
    # Test services endpoint response structure
    try:
        response = client.get('/api/services/')
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                service = data[0]
                required_fields = ['id', 'name', 'status', 'uptime', 'last_checked']
                missing_fields = [field for field in required_fields if field not in service]
                if not missing_fields:
                    print('Services response structure: ✓ OK')
                else:
                    print(f'Services response structure: ✗ Missing fields: {missing_fields}')
            else:
                print('Services response structure: ✗ Empty or invalid response')
        else:
            print(f'Services response structure: ✗ HTTP {response.status_code}')
    except Exception as e:
        print(f'Services response structure: ✗ ERROR - {str(e)}')
    
    # Test logs endpoint response structure
    try:
        response = client.get('/api/logs/')
        if response.status_code == 200:
            data = response.json()
            required_fields = ['logs', 'total', 'limit', 'offset']
            missing_fields = [field for field in required_fields if field not in data]
            if not missing_fields:
                print('Logs response structure: ✓ OK')
            else:
                print(f'Logs response structure: ✗ Missing fields: {missing_fields}')
        else:
            print(f'Logs response structure: ✗ HTTP {response.status_code}')
    except Exception as e:
        print(f'Logs response structure: ✗ ERROR - {str(e)}')
    
    # Test status endpoint response structure
    try:
        response = client.get('/api/status/')
        if response.status_code == 200:
            data = response.json()
            required_fields = ['overall_status', 'services_online', 'services_total', 'critical_alerts', 'last_updated']
            missing_fields = [field for field in required_fields if field not in data]
            if not missing_fields:
                print('Status response structure: ✓ OK')
            else:
                print(f'Status response structure: ✗ Missing fields: {missing_fields}')
        else:
            print(f'Status response structure: ✗ HTTP {response.status_code}')
    except Exception as e:
        print(f'Status response structure: ✗ ERROR - {str(e)}')

if __name__ == "__main__":
    test_routes()