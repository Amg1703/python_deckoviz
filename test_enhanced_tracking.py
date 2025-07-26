"""
Test script to verify the enhanced usage tracking works
Run this against your Django API to test the response_body enhancement
"""

import requests
import json

# Test data
DJANGO_BASE_URL = "http://localhost:8000"  # Adjust as needed

def test_enhanced_usage_tracking():
    """Test the enhanced usage tracking with response_body"""
    
    # Step 1: Start usage tracking
    start_data = {
        "user_id": "ae3a7351-095d-4cae-ac04-123330f95c95",  # Your test user ID
        "feature_name": "poster",
        "input_data": {
            "body": {
                "style": "Modern surreal minimalism",
                "width": 768,
                "height": 1024,
                "message": "TEST - Enhanced Response Tracking"
            },
            "path": "/poster/",
            "method": "POST"
        },
        "endpoint_path": "/poster/"
    }
    
    print("1. Starting usage tracking...")
    start_response = requests.post(
        f"{DJANGO_BASE_URL}/api/analytics/internal/start-usage/",
        json=start_data
    )
    
    if start_response.status_code != 200:
        print(f"Failed to start tracking: {start_response.text}")
        return
    
    start_result = start_response.json()
    usage_id = start_result.get('usage_id')
    print(f"   Started tracking with usage_id: {usage_id}")
    
    # Step 2: Complete usage tracking WITH response_body
    complete_data = {
        "usage_id": usage_id,
        "output_data": {
            "headers": {"content-type": "application/json"},
            "status_code": 200,
            "processing_time": 15.5
        },
        "response_body": {  # ← This is the actual API response
            "success": True,
            "image_url": "https://example.com/test-poster.jpg",
            "prompt": "TEST - Enhanced Response Tracking",
            "style": "Modern surreal minimalism",
            "width": 768,
            "height": 1024,
            "processing_time": 15.5
        },
        "status": "completed"
    }
    
    print("2. Completing usage tracking with response_body...")
    complete_response = requests.post(
        f"{DJANGO_BASE_URL}/api/analytics/internal/complete-usage/",
        json=complete_data
    )
    
    if complete_response.status_code != 200:
        print(f"Failed to complete tracking: {complete_response.text}")
        return
    
    print("   ✅ Successfully completed tracking with response_body")
    
    # Step 3: Verify the result in user history
    print("3. Checking user history...")
    
    # You'll need to add authentication headers for this call
    headers = {
        "Authorization": "Bearer YOUR_TOKEN_HERE"  # Replace with actual token
    }
    
    history_response = requests.get(
        f"{DJANGO_BASE_URL}/api/analytics/user/usage-history/",
        headers=headers
    )
    
    if history_response.status_code == 200:
        history = history_response.json()
        # Find our test record
        for record in history.get('results', []):
            if record.get('id') == usage_id:
                output_data = record.get('output_data', {})
                if 'response_body' in output_data:
                    print("   ✅ SUCCESS: response_body found in user history!")
                    print(f"   Response body: {output_data['response_body']}")
                else:
                    print("   ❌ FAILED: response_body not found in output_data")
                    print(f"   Output data: {output_data}")
                break
        else:
            print(f"   Could not find record with usage_id: {usage_id}")
    else:
        print(f"   Could not fetch history: {history_response.text}")

if __name__ == "__main__":
    test_enhanced_usage_tracking()
