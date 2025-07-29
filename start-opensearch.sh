#!/bin/bash

echo "🚀 Starting OpenSearch local development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing OpenSearch containers..."
docker-compose down

# Start OpenSearch services
echo "📦 Starting OpenSearch cluster..."
docker-compose up -d

# Wait for OpenSearch to be healthy
echo "⏳ Waiting for OpenSearch to be ready..."
attempt=0
max_attempts=30

while [ $attempt -lt $max_attempts ]; do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:9200/_cluster/health | grep -q "200"; then
        echo "✅ OpenSearch is ready!"
        break
    fi
    
    echo "   Waiting... (attempt $((attempt + 1))/$max_attempts)"
    sleep 5
    attempt=$((attempt + 1))
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ OpenSearch failed to start within the expected time."
    echo "📋 Check the logs with: docker-compose logs opensearch-node1"
    exit 1
fi

# Display cluster information
echo ""
echo "🎉 OpenSearch is running successfully!"
echo ""
echo "📊 Cluster Information:"
curl -s http://localhost:9200/_cluster/health | jq '.' 2>/dev/null || curl -s http://localhost:9200/_cluster/health

echo ""
echo "🔗 Access URLs:"
echo "   OpenSearch API: http://localhost:9200"
echo "   OpenSearch Dashboards: http://localhost:5601"
echo ""
echo "📝 Useful commands:"
echo "   Check cluster health: curl http://localhost:9200/_cluster/health"
echo "   List indices: curl http://localhost:9200/_cat/indices?v"
echo "   Stop services: docker-compose down"
echo "   View logs: docker-compose logs -f opensearch-node1"
echo ""
echo "🧪 To populate with test data, run: ./populate-test-data.sh"