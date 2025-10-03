# Logging Enhancement Summary

This document outlines the logging improvements added to the Deckoviz codebase to provide better visibility into API requests and system behavior.

## What Was Added

### 1. Enhanced Django Logging
- **Request logging middleware** (`common/apps/utils/middleware.py`)
- **Structured log configuration** in `common/deckoviz/settings.py`
- **Request-specific logging** with user information, timing, and IP addresses

### 2. FastAPI Request Logging
- **Request logging middleware** (`api/middleware/logging.py`)
- **Enhanced logger configuration** (`api/core/logger.py`)
- **Request timing and error tracking**

### 3. Log File Structure
```
logs/
├── django_app.log          # Django application logs
├── django_requests.log     # Django request/response logs
├── fastapi_app.log         # FastAPI application logs
├── fastapi_requests.log    # FastAPI request/response logs
├── celery/                 # Existing Celery logs
└── tvapp/                  # Existing TV app logs
```

## Log Format

### Request Logs Include:
- **Timestamp** (YYYY-MM-DD HH:MM:SS)
- **HTTP Method** (GET, POST, etc.)
- **Request Path**
- **User Information** (user ID and username when authenticated)
- **Client IP Address**
- **Response Status Code**
- **Request Duration** (in seconds)
- **User Agent** (truncated to 100 chars)

### Example Log Entries:
```
REQUEST 2025-07-22 14:30:15 [INFO] START POST /api/rooms/123/batch | User: user:42(john_doe) | IP: 192.168.1.100 | User-Agent: Mozilla/5.0...
REQUEST 2025-07-22 14:30:15 [INFO] END POST /api/rooms/123/batch | Status: 200 | User: user:42(john_doe) | Duration: 0.245s
```

## Features

### 1. **Non-Intrusive Design**
- Minimal code changes to existing endpoints
- Middleware-based approach
- No modification to business logic

### 2. **Log Rotation**
- Automatic rotation at 10MB per file
- Keeps 5 backup files
- Prevents disk space issues

### 3. **Structured Information**
- Consistent log format across services
- Easy to parse and analyze
- Includes all essential request context

### 4. **Error Tracking**
- Captures exceptions with request context
- Includes timing information for failed requests
- Maintains error details for debugging

## Usage

### Monitoring Logs in Real-Time
```bash
# Monitor all logs
./monitor_logs.sh all

# Monitor only Django logs
./monitor_logs.sh django

# Monitor only FastAPI logs  
./monitor_logs.sh fastapi
```

### Docker Integration
- Logs are automatically mounted from containers to host
- Available in the `logs/` directory
- Persistent across container restarts

## Benefits

1. **Request Traceability**: Every API request is logged with user context
2. **Performance Monitoring**: Request duration tracking helps identify slow endpoints
3. **User Activity Tracking**: Know which users are making which requests
4. **Error Debugging**: Enhanced error context for faster issue resolution
5. **Security Monitoring**: IP tracking and user activity visibility

## Compatibility

- ✅ Works with existing Docker Compose setup
- ✅ Compatible with auto-restart functionality
- ✅ No changes to existing API endpoints
- ✅ Preserves all existing functionality
- ✅ Minimal performance overhead

The logging system is designed to be production-ready and provides comprehensive visibility into your API usage without disrupting the fragile codebase.
