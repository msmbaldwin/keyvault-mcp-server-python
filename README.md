# Azure Key Vault MCP Server (Python)

A Python MCP server that exposes Azure Key Vault data-plane operations to AI agents. Uses managed identity for authentication and least-privilege RBAC for secure secret access. Deploy to Azure Container Apps and connect from GitHub Copilot Chat agent mode.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Azure-Samples/keyvault-mcp-server-python)

## Overview

This sample demonstrates how to build a customer-owned [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that exposes Azure Key Vault data-plane operations to AI agents. 

**Key features:**
- **Data-plane only**: Exposes only secret read operations, no management-plane access
- **Managed identity**: Uses `DefaultAzureCredential` for secure authentication
- **Least privilege**: Requires only `Key Vault Secrets User` role
- **Container Apps hosting**: Deploys to Azure Container Apps with `azd up`

> [!IMPORTANT]
> This MCP server uses the Key Vault **data plane** only. It does not and should not have access to management-plane operations like creating vaults, configuring networking, or assigning RBAC roles.

## MCP Tools

| Tool | Description | Key Vault API |
|------|-------------|---------------|
| `getSecret` | Retrieve a secret value | `GET /secrets/{name}` |
| `listSecrets` | List secret names (not values) | `GET /secrets` |

## Prerequisites

- Azure subscription - [Create one for free](https://azure.microsoft.com/pricing/purchase-options/azure-account)
- [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli) (v2.50+)
- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- [Python 3.10+](https://www.python.org/downloads/)
- An existing Azure Key Vault with RBAC enabled and at least one secret

## Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/Azure-Samples/keyvault-mcp-server-python.git
cd keyvault-mcp-server-python
```

### 2. Set up your environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Deploy to Azure

```bash
azd auth login
azd up
```

You'll be prompted for:
- **Environment name**: A short name like `kv-mcp-dev`
- **Azure subscription**: Select your subscription
- **Azure location**: Select a region
- **Key Vault name**: The name of your existing Key Vault

### 4. Configure VS Code

After deployment, add the MCP server to your VS Code settings:

1. Open VS Code Settings (`Ctrl+,`)
2. Search for "mcp"
3. Edit `settings.json` and add:

```json
{
    "mcp": {
        "servers": {
            "keyvault-mcp-server": {
                "type": "http",
                "url": "https://<your-container-app-url>/mcp"
            }
        }
    }
}
```

Replace `<your-container-app-url>` with the URL from the `azd up` output.

### 5. Use in GitHub Copilot Chat

1. Open GitHub Copilot Chat (`Ctrl+Alt+I`)
2. Select **Agent mode** from the dropdown
3. Click **Tools** to verify `getSecret` and `listSecrets` are available
4. Try a prompt like: "List the secrets in the key vault"

## Local Development

### Run locally with Azure credentials

```bash
# Set environment variables
export KEYVAULT_URL="https://<your-vault-name>.vault.azure.net/"

# Login to Azure (for DefaultAzureCredential)
az login

# Run the server
python src/server.py
```

### Run in GitHub Codespaces

Click the button at the top of this README to open in Codespaces. The dev container includes all dependencies.

## Security

This sample follows security best practices:

| Practice | Implementation |
|----------|----------------|
| **Data-plane only** | No management-plane operations exposed |
| **Least privilege** | Uses `Key Vault Secrets User` role only |
| **Managed identity** | No secrets stored in configuration |
| **Single-vault scope** | Role assignment scoped to one vault |

### Roles to avoid

Do **not** grant these roles to the MCP server identity:
- `Key Vault Contributor` (control-plane access)
- `Key Vault Administrator` (full data-plane access)
- `Owner` or `Contributor` at any scope

## Troubleshooting

| Error | Cause | Resolution |
|-------|-------|------------|
| `403 Forbidden` | Missing RBAC role | Assign `Key Vault Secrets User` to the managed identity |
| `401 Unauthorized` | Identity not resolving | Verify managed identity is attached to Container App |
| `404 Not Found` | Wrong vault URL | Check `KEYVAULT_URL` format |

## Clean up

```bash
azd down --purge --force
```

## Related documentation

- [Build a customer-owned MCP server for Azure Key Vault](https://learn.microsoft.com/azure/key-vault/general/build-key-vault-mcp-server)
- [Introduction to Agents and the Model Context Protocol](https://learn.microsoft.com/azure/developer/ai/intro-agents-mcp)
- [Azure Key Vault RBAC guide](https://learn.microsoft.com/azure/key-vault/general/rbac-guide)

## Contributing

This project welcomes contributions and suggestions. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
