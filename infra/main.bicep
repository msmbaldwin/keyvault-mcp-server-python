targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Name of the existing Key Vault to access')
param keyVaultName string

@description('Resource group of the existing Key Vault')
param keyVaultResourceGroup string = ''

var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

// Resource group for the MCP server
resource rg 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: 'rg-${environmentName}'
  location: location
  tags: tags
}

// User-assigned managed identity for the MCP server
module identity './modules/identity.bicep' = {
  name: 'identity'
  scope: rg
  params: {
    name: '${abbrs.managedIdentityUserAssignedIdentities}${resourceToken}'
    location: location
    tags: tags
  }
}

// Container Apps environment
module containerAppsEnvironment './modules/container-apps-environment.bicep' = {
  name: 'container-apps-environment'
  scope: rg
  params: {
    name: '${abbrs.appManagedEnvironments}${resourceToken}'
    location: location
    tags: tags
  }
}

// Container registry
module containerRegistry './modules/container-registry.bicep' = {
  name: 'container-registry'
  scope: rg
  params: {
    name: '${abbrs.containerRegistryRegistries}${resourceToken}'
    location: location
    tags: tags
  }
}

// MCP Server Container App
module mcpServer './modules/container-app.bicep' = {
  name: 'mcp-server'
  scope: rg
  params: {
    name: '${abbrs.appContainerApps}mcp-${resourceToken}'
    location: location
    tags: tags
    containerAppsEnvironmentName: containerAppsEnvironment.outputs.name
    containerRegistryName: containerRegistry.outputs.name
    identityName: identity.outputs.name
    keyVaultUrl: 'https://${keyVaultName}.vault.azure.net/'
  }
}

// Role assignment for Key Vault Secrets User
module keyVaultRoleAssignment './modules/keyvault-role-assignment.bicep' = {
  name: 'keyvault-role-assignment'
  scope: resourceGroup(empty(keyVaultResourceGroup) ? rg.name : keyVaultResourceGroup)
  params: {
    keyVaultName: keyVaultName
    principalId: identity.outputs.principalId
  }
}

output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.outputs.loginServer
output AZURE_CONTAINER_APP_URL string = mcpServer.outputs.url
output AZURE_MANAGED_IDENTITY_CLIENT_ID string = identity.outputs.clientId
