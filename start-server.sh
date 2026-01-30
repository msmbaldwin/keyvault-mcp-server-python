#!/bin/bash
# Start the MCP server with environment variables from .env file

set -e

# Load environment variables from .env if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check if KEYVAULT_URL is set
if [ -z "$KEYVAULT_URL" ]; then
    echo "ERROR: KEYVAULT_URL environment variable is not set."
    echo ""
    echo "Please set it in one of these ways:"
    echo "  1. Edit the .env file: KEYVAULT_URL=https://your-vault.vault.azure.net/"
    echo "  2. Export it: export KEYVAULT_URL=https://your-vault.vault.azure.net/"
    echo ""
    exit 1
fi

echo "Starting MCP server..."
echo "Key Vault URL: $KEYVAULT_URL"
echo "Server will be available at http://localhost:3000/mcp"
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

python src/server.py
