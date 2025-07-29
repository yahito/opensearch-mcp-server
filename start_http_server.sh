#!/bin/bash

echo "🚀 Starting OpenSearch MCP HTTP Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Please configure .env with your OpenSearch settings"
fi

# Activate virtual environment
source venv/bin/activate

# Check if OpenSearch is running
echo "🔍 Checking OpenSearch connection..."
if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:9200/_cluster/health | grep -q "200"; then
    echo "❌ OpenSearch is not running on localhost:9200"
    echo "   Please start OpenSearch first with: ./start-opensearch.sh"
    exit 1
fi

echo "✅ OpenSearch is running"

# Start the HTTP server
echo "📡 Starting HTTP server on port 8091..."
python http_opensearch_server.py