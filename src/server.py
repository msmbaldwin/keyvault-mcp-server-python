import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

# Configuration from environment variables
KEYVAULT_URL = os.environ.get("KEYVAULT_URL")
if not KEYVAULT_URL:
    raise ValueError("KEYVAULT_URL environment variable is required")

# Initialize Key Vault client with DefaultAzureCredential
# In Azure Container Apps, this uses the assigned managed identity
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=KEYVAULT_URL, credential=credential)

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
