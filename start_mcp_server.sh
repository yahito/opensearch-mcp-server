#!/bin/bash

echo "🚀 Starting OpenSearch MCP Server..."

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h          Show this help message"
    echo "  --check-deps        Check and install dependencies"
    echo "  --setup             Setup environment (create venv, install deps, copy .env)"
    echo "  --http              Start HTTP server (default)"
    echo "  --stdio             Start STDIO server"
    echo ""
    echo "Examples:"
    echo "  $0                  # Start HTTP server"
    echo "  $0 --setup          # Setup environment first"
    echo "  $0 --stdio          # Start STDIO server for direct MCP"
    echo ""
}

# Function to setup environment
setup_environment() {
    echo "🔧 Setting up environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    
    # Copy .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        echo "⚙️  Creating .env file..."
        cp .env.example .env
        echo "✅ .env file created. Please configure your OpenSearch settings."
    fi
    
    echo "✅ Environment setup complete!"
}

# Function to check dependencies
check_dependencies() {
    echo "🔍 Checking dependencies..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "❌ Virtual environment not found"
        return 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        echo "❌ .env file not found"
        return 1
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check if required packages are installed
    python -c "import opensearchpy, fastapi, uvicorn, mcp" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "❌ Required packages not installed"
        return 1
    fi
    
    echo "✅ All dependencies are ready"
    return 0
}

# Function to check OpenSearch connection
check_opensearch() {
    echo "🔍 Checking OpenSearch connection..."
    
    # Load environment variables
    if [ -f ".env" ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
    
    OPENSEARCH_HOST=${OPENSEARCH_HOST:-localhost}
    OPENSEARCH_PORT=${OPENSEARCH_PORT:-9200}
    OPENSEARCH_USE_SSL=${OPENSEARCH_USE_SSL:-false}
    
    if [ "$OPENSEARCH_USE_SSL" = "true" ]; then
        PROTOCOL="https"
    else
        PROTOCOL="http"
    fi
    
    OPENSEARCH_URL="$PROTOCOL://$OPENSEARCH_HOST:$OPENSEARCH_PORT"
    
    if curl -s -o /dev/null -w "%{http_code}" "$OPENSEARCH_URL/_cluster/health" | grep -q "200"; then
        echo "✅ OpenSearch is running at $OPENSEARCH_URL"
        return 0
    else
        echo "❌ OpenSearch is not accessible at $OPENSEARCH_URL"
        echo "   Please start OpenSearch first with: ./start-opensearch.sh"
        return 1
    fi
}

# Function to start HTTP server
start_http_server() {
    echo "📡 Starting OpenSearch MCP HTTP Server on port 8091..."
    source venv/bin/activate
    python http_opensearch_server.py
}

# Function to start STDIO server
start_stdio_server() {
    echo "📡 Starting OpenSearch MCP STDIO Server..."
    source venv/bin/activate
    python mcp_opensearch_server.py
}

# Parse command line arguments
MODE="http"
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_usage
            exit 0
            ;;
        --setup)
            setup_environment
            exit 0
            ;;
        --check-deps)
            check_dependencies
            exit $?
            ;;
        --http)
            MODE="http"
            shift
            ;;
        --stdio)
            MODE="stdio"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
echo "OpenSearch MCP Server Startup Script"
echo "===================================="

# Check dependencies
if ! check_dependencies; then
    echo ""
    echo "💡 Run '$0 --setup' to set up the environment"
    exit 1
fi

# Check OpenSearch connection
if ! check_opensearch; then
    echo ""
    echo "💡 Make sure OpenSearch is running:"
    echo "   ./start-opensearch.sh"
    exit 1
fi

# Start the appropriate server
case $MODE in
    http)
        start_http_server
        ;;
    stdio)
        start_stdio_server
        ;;
    *)
        echo "Invalid mode: $MODE"
        exit 1
        ;;
esac