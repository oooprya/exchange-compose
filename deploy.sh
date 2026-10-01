#!/bin/bash

# Exchange-Compose VPS Deployment Script
# Usage: ./deploy.sh <server_ip> <server_user>

set -e

SERVER_IP=${1:-85.238.113.16}
SERVER_USER=${2:-root}
PROJECT_PATH="/srv/exchange-compose"

echo "🚀 Starting deployment to $SERVER_USER@$SERVER_IP..."

# Step 1: Connect to VPS and pull latest code
echo "📦 Pulling latest code from Git..."
ssh $SERVER_USER@$SERVER_IP << 'EOF'
    set -e
    cd $PROJECT_PATH || mkdir -p $PROJECT_PATH
    
    if [ -d "$PROJECT_PATH/.git" ]; then
        cd $PROJECT_PATH
        git pull origin main
    else
        cd /srv
        git clone <your-repo-url> exchange-compose
    fi
EOF

# Step 2: Build and start Docker containers
echo "🐳 Building Docker containers..."
ssh $SERVER_USER@$SERVER_IP << 'EOF'
    set -e
    cd $PROJECT_PATH
    docker-compose -f docker-compose_prod.yml build
    docker-compose -f docker-compose_prod.yml down || true
    docker-compose -f docker-compose_prod.yml up -d
EOF

# Step 3: Run migrations
echo "🔄 Running migrations..."
ssh $SERVER_USER@$SERVER_IP << 'EOF'
    set -e
    cd $PROJECT_PATH
    docker-compose -f docker-compose_prod.yml exec -T backend python manage.py migrate --noinput
    docker-compose -f docker-compose_prod.yml exec -T backend python manage.py collectstatic --noinput
EOF

# Step 4: Create superuser (if needed)
echo "✅ Deployment completed!"
echo "🌐 Access your site: https://exprivat.com.ua"
echo "📊 Admin: https://exprivat.com.ua/admin"
