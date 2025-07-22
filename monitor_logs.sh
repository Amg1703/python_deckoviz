#!/bin/bash

# Simple script to monitor logs in real-time
# Usage: ./monitor_logs.sh [django|fastapi|all]

LOG_TYPE=${1:-all}

case $LOG_TYPE in
    django)
        echo "Monitoring Django logs..."
        tail -f logs/django_requests.log logs/django_app.log
        ;;
    fastapi)
        echo "Monitoring FastAPI logs..."
        tail -f logs/fastapi_requests.log logs/fastapi_app.log
        ;;
    all)
        echo "Monitoring all application logs..."
        tail -f logs/django_requests.log logs/django_app.log logs/fastapi_requests.log logs/fastapi_app.log
        ;;
    *)
        echo "Usage: $0 [django|fastapi|all]"
        echo "  django  - Monitor only Django logs"
        echo "  fastapi - Monitor only FastAPI logs"
        echo "  all     - Monitor all logs (default)"
        exit 1
        ;;
esac
