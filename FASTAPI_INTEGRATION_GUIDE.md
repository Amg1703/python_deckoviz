# FastAPI Integration Guide for Enhanced Usage Tracking

## The Problem
Your user history still shows old format because FastAPI endpoints are not sending `response_body` when completing usage tracking.

## Current FastAPI Call (Old Format)
```python
# What FastAPI is currently doing
await complete_usage_tracking({
    "usage_id": usage_id,
    "output_data": {
        "headers": {"content-type": "application/json"},
        "status_code": 200,
        "processing_time": processing_time
    },
    "status": "completed"
})
```

## Updated FastAPI Call (New Format)
```python
# What FastAPI should be doing
await complete_usage_tracking({
    "usage_id": usage_id,
    "output_data": {
        "headers": {"content-type": "application/json"},
        "status_code": 200,
        "processing_time": processing_time
    },
    "response_body": actual_api_response,  # ← ADD THIS
    "status": "completed"
})
```

## Example for Poster Endpoint

### Before (Current)
```python
# In your FastAPI poster endpoint
async def generate_poster(request_data):
    # ... generate poster logic ...
    
    response = {
        "success": True,
        "image_url": "https://s3.bucket.com/poster.jpg",
        "prompt": request_data["message"],
        "style": request_data["style"],
        "width": request_data["width"],
        "height": request_data["height"]
    }
    
    # Complete tracking (OLD WAY)
    await complete_usage_tracking({
        "usage_id": usage_id,
        "output_data": {
            "headers": {"content-type": "application/json"},
            "status_code": 200,
            "processing_time": processing_time
        },
        "status": "completed"
    })
    
    return response
```

### After (Enhanced)
```python
# In your FastAPI poster endpoint
async def generate_poster(request_data):
    # ... generate poster logic ...
    
    response = {
        "success": True,
        "image_url": "https://s3.bucket.com/poster.jpg",
        "prompt": request_data["message"],
        "style": request_data["style"],
        "width": request_data["width"],
        "height": request_data["height"]
    }
    
    # Complete tracking (NEW WAY - with response_body)
    await complete_usage_tracking({
        "usage_id": usage_id,
        "output_data": {
            "headers": {"content-type": "application/json"},
            "status_code": 200,
            "processing_time": processing_time
        },
        "response_body": response,  # ← Include actual response
        "status": "completed"
    })
    
    return response
```

## Implementation Steps

### 1. Find Your FastAPI Poster Endpoint
Look for files in the `api/` directory that handle poster generation.

### 2. Locate the complete_usage_tracking Call
Find where your poster endpoint calls the Django analytics API to complete tracking.

### 3. Add response_body Parameter
Include the actual API response in the tracking call.

### 4. Test the Change
Use the test script (`test_enhanced_tracking.py`) to verify it works.

## Expected Result

After updating FastAPI, your user history will show:

```json
{
  "output_data": {
    "headers": {"content-type": "application/json"},
    "status_code": 200,
    "processing_time": 16.997,
    "response_body": {
      "success": true,
      "image_url": "https://s3.bucket.com/poster.jpg",
      "prompt": "Gandhi ji",
      "style": "Modern surreal minimalism",
      "width": 768,
      "height": 1024
    }
  }
}
```

## Common Patterns

### For Image Generation APIs
```python
response_body = {
    "success": True,
    "image_url": generated_image_url,
    "prompt": input_prompt,
    "style": input_style,
    "width": width,
    "height": height
}
```

### For Text Generation APIs
```python
response_body = {
    "success": True,
    "generated_text": result_text,
    "input_prompt": input_prompt,
    "model_used": model_name
}
```

### For Error Cases
```python
# For failed requests, you can still include response_body
await complete_usage_tracking({
    "usage_id": usage_id,
    "output_data": {
        "headers": {"content-type": "application/json"},
        "status_code": 500,
        "processing_time": processing_time
    },
    "response_body": {
        "success": False,
        "error": "Generation failed",
        "error_code": "GENERATION_ERROR"
    },
    "status": "failed"
})
```

## Security Notes

- Don't include API keys or secrets in `response_body`
- Be mindful of sensitive user data
- Large response bodies will increase database storage

## Verification

1. Run the test script to verify Django changes work
2. Update your FastAPI poster endpoint
3. Test poster generation via Postman
4. Check user history API - should now include `response_body`

The Django side is ready - you just need to update FastAPI to send the response data!
