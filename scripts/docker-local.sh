#!/bin/bash
# DELTA Platform - Local Docker Development Script
# This script builds and runs the Docker container locally for testing

set -e

IMAGE_NAME="delta-platform"
CONTAINER_NAME="delta-local"
LOCAL_PORT="${1:-8000}"

echo "🐳 DELTA Platform - Local Docker Development"
echo "============================================="

# Stop and remove existing container if it exists
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "🛑 Stopping existing container..."
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
fi

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t $IMAGE_NAME .

# Run the container
echo "🚀 Starting container on port $LOCAL_PORT..."
docker run -d \
    --name $CONTAINER_NAME \
    -p $LOCAL_PORT:$LOCAL_PORT \
    -e PORT=$LOCAL_PORT \
    -e DEBUG=true \
    -e ENVIRONMENT=development \
    $IMAGE_NAME

# Wait for the container to start
echo "⏳ Waiting for container to start..."
sleep 3

# Check if container is running
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo ""
    echo "✅ Container started successfully!"
    echo ""
    echo "📍 Endpoints:"
    echo "   - API:     http://localhost:$LOCAL_PORT"
    echo "   - Health:  http://localhost:$LOCAL_PORT/health"
    echo "   - Docs:    http://localhost:$LOCAL_PORT/docs"
    echo "   - Status:  http://localhost:$LOCAL_PORT/v1/status"
    echo ""
    echo "📋 Commands:"
    echo "   - View logs:     docker logs -f $CONTAINER_NAME"
    echo "   - Stop:          docker stop $CONTAINER_NAME"
    echo "   - Remove:        docker rm $CONTAINER_NAME"
    echo ""
    
    # Test the health endpoint
    echo "🏥 Testing health endpoint..."
    if curl -s "http://localhost:$LOCAL_PORT/health" | grep -q "healthy"; then
        echo "✅ Health check passed!"
    else
        echo "❌ Health check failed. Check logs with: docker logs $CONTAINER_NAME"
        docker logs $CONTAINER_NAME
        exit 1
    fi
else
    echo "❌ Container failed to start. Checking logs..."
    docker logs $CONTAINER_NAME
    exit 1
fi
