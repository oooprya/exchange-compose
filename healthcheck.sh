#!/bin/bash

# Docker Compose Health Check Script

check_service() {
    local service=$1
    local command=$2
    
    echo -n "Checking $service... "
    if eval "$command" &>/dev/null; then
        echo "✅ OK"
        return 0
    else
        echo "❌ FAILED"
        return 1
    fi
}

failed=0

# Check backend
check_service "Backend" "docker-compose exec -T backend curl -f http://localhost:8000/admin/ > /dev/null" || failed=$((failed+1))

# Check database
check_service "PostgreSQL" "docker-compose exec -T db psql -U django_user -d django_db -c 'SELECT 1' > /dev/null" || failed=$((failed+1))

# Check Redis
check_service "Redis" "docker-compose exec -T redis redis-cli ping > /dev/null" || failed=$((failed+1))

# Check Celery Worker
check_service "Celery Worker" "docker-compose ps celery_worker | grep Up" || failed=$((failed+1))

echo ""
if [ $failed -eq 0 ]; then
    echo "✅ All services are healthy!"
else
    echo "❌ $failed service(s) failed health check"
    echo ""
    echo "Troubleshooting tips:"
    echo "- Check logs: docker-compose logs <service>"
    echo "- Restart service: docker-compose restart <service>"
    echo "- Full status: docker-compose ps"
fi

exit $failed
