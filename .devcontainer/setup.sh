#!/bin/bash
# Post-create setup script for dev containers / Codespaces

set -e

pip install -r requirements.txt

echo ""
echo "=============================================="
echo "  Azure Key Vault MCP Server - Ready"
echo "=============================================="
echo ""
echo "Deploy to Azure (recommended):"
echo "  azd auth login"
echo "  azd up"
echo ""
echo "Or run locally for testing:"
echo "  az login"
echo "  export KEYVAULT_URL=\"https://YOUR-VAULT.vault.azure.net/\""
echo "  python src/server.py"
echo ""
echo "See README.md for full instructions."
echo ""
