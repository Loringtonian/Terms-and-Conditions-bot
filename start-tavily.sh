#!/bin/bash

# Load the .env file
export $(grep -v '^#' .env | xargs)

# Check if API key is set
if [ -z "$TAVILY_API_KEY" ]; then
  echo "Error: TAVILY_API_KEY not found in .env file"
  exit 1
fi

echo "Starting Tavily MCP server with API key: ${TAVILY_API_KEY:0:8}..."

# Start the Tavily MCP server with the API key from .env
TAVILY_API_KEY="$TAVILY_API_KEY" npx -y tavily-mcp@0.1.3
