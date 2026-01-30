# Azure Key Vault MCP Server (Python)

A Python MCP server that exposes Azure Key Vault data-plane operations to AI agents. Uses managed identity for authentication and least-privilege RBAC for secure secret access. Deploy to Azure Container Apps and connect from GitHub Copilot Chat agent mode.

## Overview

This sample demonstrates how to build a customer-owned [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that exposes Azure Key Vault data-plane operations to AI agents.

**Three integration patterns:**
- **Agent → Key Vault**: Read secrets through MCP tools
- **Key Vault → Agent**: Trigger agent workflows from Key Vault events (Event Grid)
- **Telemetry → Agent**: Query audit logs for debugging and monitoring

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
| `queryKeyVaultLogs` | Query audit logs for debugging | Azure Monitor Logs API |

> **Note**: The `queryKeyVaultLogs` tool requires additional configuration. See [Enable telemetry queries](#enable-telemetry-queries) below.

## Prerequisites

- Azure subscription - [Create one for free](https://azure.microsoft.com/pricing/purchase-options/azure-account)
- An existing Azure Key Vault with RBAC enabled and at least one secret
- [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli) (v2.50+)

## Getting Started

Choose the path that fits your needs:

| Path | Best for | What you need |
|------|----------|---------------|
| [**Deploy to Azure**](#option-1-deploy-to-azure-recommended) | Production use, team sharing | Azure subscription, `azd` CLI |
| [**Run locally**](#option-2-run-locally) | Quick testing, development | Python 3.10+, Azure CLI |
| [**Codespaces**](#option-3-github-codespaces) | Contributing to this repo | GitHub account |

---

## Option 1: Deploy to Azure (Recommended)

Deploy the MCP server to Azure Container Apps for production use. This gives you a hosted endpoint with managed identity authentication.

### Prerequisites for Azure deployment

- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)

### Steps

**1. Clone and deploy**

```bash
git clone https://github.com/msmbaldwin/keyvault-mcp-server-python.git
cd keyvault-mcp-server-python
azd auth login
azd up
```

You'll be prompted for:
- **Environment name**: A short name like `kv-mcp-dev`
- **Azure subscription**: Select your subscription
- **Azure location**: Select a region
- **Key Vault name**: The name of your existing Key Vault

**2. Configure VS Code**

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

**3. Use in GitHub Copilot Chat**

1. Open GitHub Copilot Chat (`Ctrl+Alt+I`)
2. Select **Agent mode** from the dropdown
3. Click **Tools** to verify `getSecret` and `listSecrets` are available
4. Try a prompt like: "List the secrets in the key vault"

---

## Option 2: Run Locally

Run the MCP server on your local machine for quick testing or development.

### Prerequisites for local development

- [Python 3.10+](https://www.python.org/downloads/)
- [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli) (for authentication)

### Steps

**1. Clone and install dependencies**

```bash
git clone https://github.com/msmbaldwin/keyvault-mcp-server-python.git
cd keyvault-mcp-server-python
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**2. Authenticate and run**

```bash
# Login to Azure (required for DefaultAzureCredential)
az login

# Set your Key Vault URL
export KEYVAULT_URL="https://<your-vault-name>.vault.azure.net/"

# Start the server
python src/server.py
```

The server will start on `http://localhost:3000`.

**3. Configure VS Code**

Add to your VS Code `settings.json`:

```json
{
    "mcp": {
        "servers": {
            "keyvault-mcp-server": {
                "type": "http",
                "url": "http://localhost:3000/mcp"
            }
        }
    }
}
```

**4. Use in GitHub Copilot Chat**

1. Open GitHub Copilot Chat (`Ctrl+Alt+I`)
2. Select **Agent mode** from the dropdown
3. Click **Tools** to verify the tools are available

---

## Option 3: GitHub Codespaces

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/msmbaldwin/keyvault-mcp-server-python)

Codespaces provides a pre-configured development environment. Best for contributors or those who want to explore the code without local setup.

> **Note**: Codespaces still requires Azure authentication and configuration. It's convenient for development, but not a "zero-config" experience.

### Steps

1. Click the badge above to open in Codespaces
2. Once the container starts, authenticate with Azure:
   ```bash
   az login --use-device-code
   ```
3. Find your Key Vault name:
   ```bash
   az keyvault list --query '[].name' -o tsv
   ```
4. Start the server:
   ```bash
   export KEYVAULT_URL="https://<your-vault-name>.vault.azure.net/"
   python src/server.py
   ```
5. The MCP settings are pre-configured. Reload VS Code (`Ctrl+Shift+P` → "Reload Window"), then use Agent mode in Copilot Chat.

---

## Security

This sample follows security best practices:

| Practice | Implementation |
|----------|----------------|
| **Data-plane only** | No management-plane operations exposed |
| **Least privilege** | Uses `Key Vault Secrets User` role only |
| **Managed identity** | No secrets stored in configuration |
| **Single-vault scope** | Role assignment scoped to one vault |

### Required roles

| Role | Scope | Purpose |
|------|-------|--------|
| `Key Vault Secrets User` | Key Vault | Read secrets |
| `Log Analytics Reader` | Log Analytics workspace | Query audit logs (optional) |

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

## Extend the pattern

### Enable telemetry queries

To enable the `queryKeyVaultLogs` tool for agentic debugging:

1. **Enable Key Vault diagnostic logging** to a Log Analytics workspace
2. **Set the environment variable**:
   ```bash
   export LOG_ANALYTICS_WORKSPACE_ID="<your-workspace-id>"
   ```
3. **Assign the Log Analytics Reader role** to the managed identity:
   ```bash
   az role assignment create \
       --role "Log Analytics Reader" \
       --assignee-object-id <principalId> \
       --assignee-principal-type ServicePrincipal \
       --scope /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.OperationalInsights/workspaces/<workspace>
   ```

**Example queries:**

| Scenario | Query |
|----------|-------|
| Failed access | `AzureDiagnostics \| where ResourceProvider == "MICROSOFT.KEYVAULT" and ResultSignature == "Forbidden"` |
| Recent access | `AzureDiagnostics \| where OperationName == "SecretGet" \| summarize count() by CallerIPAddress` |
| Unusual patterns | `AzureDiagnostics \| where ResourceProvider == "MICROSOFT.KEYVAULT" \| summarize count() by bin(TimeGenerated, 1h)` |

### Trigger agents from Key Vault events

Key Vault integrates with [Azure Event Grid](https://learn.microsoft.com/azure/key-vault/general/event-grid-overview) to emit events when secrets, keys, or certificates change. Use these events to trigger agent workflows:

| Event | Agent workflow |
|-------|---------------|
| `SecretNearExpiry` | Agent initiates secret rotation |
| `CertificateNearExpiry` | Agent triggers certificate renewal |
| `SecretNewVersionCreated` | Agent validates and updates dependent apps |

To implement, create an Event Grid subscription:

```bash
az eventgrid event-subscription create \
    --name keyvault-agent-trigger \
    --source-resource-id /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.KeyVault/vaults/<vault> \
    --endpoint-type webhook \
    --endpoint https://<your-agent-endpoint>/api/keyvault-events \
    --included-event-types Microsoft.KeyVault.SecretNearExpiry Microsoft.KeyVault.CertificateNearExpiry
```

> **Note**: Event Grid triggers require a separate webhook endpoint (such as an Azure Function), not the MCP server itself. The MCP server can then be called by the agent to retrieve additional context.

## Related documentation

- [Build a customer-owned MCP server for Azure Key Vault](https://learn.microsoft.com/azure/key-vault/general/build-key-vault-mcp-server)
- [Introduction to Agents and the Model Context Protocol](https://learn.microsoft.com/azure/developer/ai/intro-agents-mcp)
- [Azure Key Vault RBAC guide](https://learn.microsoft.com/azure/key-vault/general/rbac-guide)

## Contributing

This project welcomes contributions and suggestions. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
