#!/bin/bash
set -e

echo "Starting FPL MCP Server..."

# Set default environment variables
export PYTHONPATH="${PYTHONPATH:-src}"
export PYTHONUNBUFFERED=1
export PORT="${PORT:-10000}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"

# Check if we're in production
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Production environment detected"
    export LOG_LEVEL="${LOG_LEVEL:-WARNING}"
fi

# Start the web server
echo "Starting web server on port $PORT"
exec python web_server.py