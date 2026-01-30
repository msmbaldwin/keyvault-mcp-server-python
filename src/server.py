import os
from datetime import timedelta
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.monitor.query import LogsQueryClient
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

# Configuration from environment variables
KEYVAULT_URL = os.environ.get("KEYVAULT_URL")
if not KEYVAULT_URL:
    raise ValueError("KEYVAULT_URL environment variable is required")

LOG_ANALYTICS_WORKSPACE_ID = os.environ.get("LOG_ANALYTICS_WORKSPACE_ID")

# Initialize clients with DefaultAzureCredential
# In Azure Container Apps, this uses the assigned managed identity
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=KEYVAULT_URL, credential=credential)
logs_client = LogsQueryClient(credential) if LOG_ANALYTICS_WORKSPACE_ID else None

# Create the MCP server with FastMCP
# stateless_http=True enables HTTP transport without session persistence
# json_response=True returns JSON instead of SSE streams
mcp = FastMCP("keyvault-mcp-server", stateless_http=True, json_response=True)


@mcp.tool()
def getSecret(secretName: str) -> dict:
    """Retrieve a secret value from Azure Key Vault."""
    secret = secret_client.get_secret(secretName)
    return {
        "name": secret.name,
        "value": secret.value,
        "contentType": secret.properties.content_type,
        "createdOn": (
            secret.properties.created_on.isoformat()
            if secret.properties.created_on
            else None
        ),
        "updatedOn": (
            secret.properties.updated_on.isoformat()
            if secret.properties.updated_on
            else None
        ),
    }


@mcp.tool()
def listSecrets() -> dict:
    """List the names of secrets in Azure Key Vault (not values)."""
    secrets = []
    for secret_properties in secret_client.list_properties_of_secrets():
        secrets.append(secret_properties.name)
    return {"secrets": secrets}


@mcp.tool()
def queryKeyVaultLogs(query: str, timeSpanHours: int = 24) -> dict:
    """Query Key Vault audit logs from Azure Monitor for troubleshooting.
    
    Requires LOG_ANALYTICS_WORKSPACE_ID environment variable and 
    Log Analytics Reader role on the workspace.
    
    Example queries:
    - Failed access: AzureDiagnostics | where ResourceProvider == "MICROSOFT.KEYVAULT" and ResultSignature == "Forbidden"
    - Recent access: AzureDiagnostics | where OperationName == "SecretGet" | summarize count() by CallerIPAddress
    """
    if not logs_client or not LOG_ANALYTICS_WORKSPACE_ID:
        return {
            "error": "Log Analytics not configured. Set LOG_ANALYTICS_WORKSPACE_ID environment variable."
        }
    
    response = logs_client.query_workspace(
        workspace_id=LOG_ANALYTICS_WORKSPACE_ID,
        query=query,
        timespan=timedelta(hours=timeSpanHours)
    )
    
    results = []
    for table in response.tables:
        for row in table.rows:
            results.append(dict(zip([col.name for col in table.columns], row)))
    
    return {"results": results, "count": len(results)}


if __name__ == "__main__":
    # For remote hosting (behind a reverse proxy like Azure Container Apps),
    # disable DNS rebinding protection since the Host header won't match localhost
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 3000
    mcp.settings.transport_security = TransportSecuritySettings(
        enable_dns_rebinding_protection=False
    )
    
    # Run with streamable-http transport for remote hosting
    mcp.run(transport="streamable-http")
