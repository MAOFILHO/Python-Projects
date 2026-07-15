// main.bicep - Azure Container Apps deployment for microservices-lab.
//
// Scope: resource group (the resource group itself is created by
// azure/scripts/deploy.sh BEFORE this template is deployed, via
// `az group create`, not by this template).
//
// Deploys: 1 Azure Container Registry, 1 Log Analytics Workspace,
// 1 Container Apps Environment, and 5 Container Apps
// (sum-service, mul-service, monolith, history-service, gateway).
//
// Cost-conscious defaults: every app scales to zero (minReplicas: 0)
// except where explicitly noted otherwise for the gateway (see comment
// near the gateway app below). ACR Basic SKU with admin user disabled -
// `az acr build` (ACR Tasks) does not require admin credentials, and
// Container Apps pulls via managed identity + AcrPull role assignment.

targetScope = 'resourceGroup'

@description('Azure region for all resources.')
param location string = 'eastus'

@description('Short project name used to derive resource names. Azure Container App names are capped at 32 characters, and the longest suffix used below is "-history-service" (16 chars), so this must stay <= 16 characters or the deployment will fail preflight validation (as "microservices-lab" - 18 chars - originally did).')
@maxLength(16)
param projectName string = 'ms-lab'

@description('Image tag to deploy for all 5 services.')
param imageTag string = 'latest'

@description('Placeholder public image used only on the very first deployment, before any real images have been built into the ACR via `az acr build`. Once real images exist, deploy.sh re-runs this template (or `az containerapp update`) so the apps point at the real images.')
param placeholderImage string = 'mcr.microsoft.com/k8se/quickstart:latest'

@description('Set true once real images (sum-service, mul-service, monolith, history-service, gateway) have been built into the ACR via `az acr build`. When false, every Container App runs the public placeholder image so the very first deployment (before any image exists) succeeds.')
param useRealImages bool = false

// -----------------------------------------------------------------------
// Naming
// -----------------------------------------------------------------------

var uniqueSuffix = uniqueString(resourceGroup().id)
var namePrefix = toLower(projectName)

// ACR names must be globally unique, alphanumeric only, <= 50 chars.
var acrName = '${replace(namePrefix, '-', '')}acr${uniqueSuffix}'
var logAnalyticsName = '${namePrefix}-logs'
var containerAppsEnvName = '${namePrefix}-env'

// -----------------------------------------------------------------------
// Azure Container Registry (Basic, admin disabled)
// -----------------------------------------------------------------------

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
  }
}

// -----------------------------------------------------------------------
// Managed identity for pulling from the ACR
//
// Admin user is disabled on the ACR above (least privilege - nobody needs
// a shared admin credential for this), so every Container App instead
// pulls images using ONE shared user-assigned managed identity that's
// granted the built-in "AcrPull" role, scoped ONLY to this ACR (not the
// whole resource group/subscription). This identity can pull container
// images and nothing else.
// -----------------------------------------------------------------------

resource acrPullIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${namePrefix}-acrpull-identity'
  location: location
}

var acrPullRoleDefinitionId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '7f951dda-4ed3-4680-a7ca-43fe172d538d' // built-in "AcrPull" role
)

resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, acrPullIdentity.id, 'AcrPull')
  scope: acr
  properties: {
    principalId: acrPullIdentity.properties.principalId
    roleDefinitionId: acrPullRoleDefinitionId
    principalType: 'ServicePrincipal'
  }
}

// -----------------------------------------------------------------------
// Log Analytics Workspace
// Required plumbing for the Container Apps Environment (it needs a log
// destination). This does carry a small cost (pay-as-you-go ingestion +
// retention) but there is no way to run a Container Apps Environment
// without one. Retention kept at the practical minimum (30 days) to
// limit storage cost for a demo project.
// -----------------------------------------------------------------------

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// -----------------------------------------------------------------------
// Container Apps Environment
// -----------------------------------------------------------------------

resource containerAppsEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: containerAppsEnvName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

// Internal DNS suffix for apps with internal-only ingress:
//   https://<app-name>.internal.<environment-default-domain>
var internalDomainSuffix = 'internal.${containerAppsEnv.properties.defaultDomain}'

// -----------------------------------------------------------------------
// Helper values shared by every Container App
// -----------------------------------------------------------------------

var acrLoginServer = acr.properties.loginServer

// Bicep user-defined functions can't reference outer-scope resources/vars,
// so this is a plain variable (computed per-service) rather than a func.
var sumImage = useRealImages ? '${acrLoginServer}/sum-service:${imageTag}' : placeholderImage
var mulImage = useRealImages ? '${acrLoginServer}/mul-service:${imageTag}' : placeholderImage
var monolithImage = useRealImages ? '${acrLoginServer}/monolith:${imageTag}' : placeholderImage
var historyImage = useRealImages ? '${acrLoginServer}/history-service:${imageTag}' : placeholderImage
var gatewayImage = useRealImages ? '${acrLoginServer}/gateway:${imageTag}' : placeholderImage

// -----------------------------------------------------------------------
// sum-service (internal-only, scale-to-zero)
// -----------------------------------------------------------------------

resource sumService 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${namePrefix}-sum-service'
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${acrPullIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnv.id
    configuration: {
      ingress: {
        external: false
        targetPort: 8001
        transport: 'auto'
      }
      registries: [
        {
          server: acrLoginServer
          identity: acrPullIdentity.id
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'sum-service'
          image: sumImage
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          probes: [
            {
              type: 'Liveness'
              httpGet: { path: '/health', port: 8001 }
            }
            {
              type: 'Readiness'
              httpGet: { path: '/health', port: 8001 }
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
      }
    }
  }
  dependsOn: [
    acrPullRoleAssignment
  ]
}

// -----------------------------------------------------------------------
// mul-service (internal-only, scale-to-zero)
// -----------------------------------------------------------------------

resource mulService 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${namePrefix}-mul-service'
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${acrPullIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnv.id
    configuration: {
      ingress: {
        external: false
        targetPort: 8002
        transport: 'auto'
      }
      registries: [
        {
          server: acrLoginServer
          identity: acrPullIdentity.id
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'mul-service'
          image: mulImage
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          probes: [
            {
              type: 'Liveness'
              httpGet: { path: '/health', port: 8002 }
            }
            {
              type: 'Readiness'
              httpGet: { path: '/health', port: 8002 }
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
      }
    }
  }
  dependsOn: [
    acrPullRoleAssignment
  ]
}

// -----------------------------------------------------------------------
// monolith (internal-only, scale-to-zero)
// -----------------------------------------------------------------------

resource monolith 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${namePrefix}-monolith'
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${acrPullIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnv.id
    configuration: {
      ingress: {
        external: false
        targetPort: 8000
        transport: 'auto'
      }
      registries: [
        {
          server: acrLoginServer
          identity: acrPullIdentity.id
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'monolith'
          image: monolithImage
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          probes: [
            {
              type: 'Liveness'
              httpGet: { path: '/health', port: 8000 }
            }
            {
              type: 'Readiness'
              httpGet: { path: '/health', port: 8000 }
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
      }
    }
  }
  dependsOn: [
    acrPullRoleAssignment
  ]
}

// -----------------------------------------------------------------------
// history-service (internal-only, scale-to-zero)
// -----------------------------------------------------------------------

resource historyService 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${namePrefix}-history-service'
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${acrPullIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnv.id
    configuration: {
      ingress: {
        external: false
        targetPort: 8003
        transport: 'auto'
      }
      registries: [
        {
          server: acrLoginServer
          identity: acrPullIdentity.id
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'history-service'
          image: historyImage
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          probes: [
            {
              type: 'Liveness'
              httpGet: { path: '/health', port: 8003 }
            }
            {
              type: 'Readiness'
              httpGet: { path: '/health', port: 8003 }
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
      }
    }
  }
  dependsOn: [
    acrPullRoleAssignment
  ]
}

// -----------------------------------------------------------------------
// gateway (external ingress, public FQDN)
//
// Cost-conscious default is minReplicas: 0 like every other app, meaning
// the FIRST request after idle incurs a cold start (image pull + FastAPI
// boot - typically a few seconds for these lightweight images). If you
// want the gateway to always answer instantly (e.g. showing this off
// live in a demo/meeting) and don't mind a small always-on cost, comment
// out the "minReplicas: 0" line below and uncomment the "minReplicas: 1"
// alternative above it.
// -----------------------------------------------------------------------

resource gateway 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${namePrefix}-gateway'
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${acrPullIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8080
        transport: 'auto'
      }
      registries: [
        {
          server: acrLoginServer
          identity: acrPullIdentity.id
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'gateway'
          image: gatewayImage
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          env: [
            { name: 'SUM_URL', value: 'https://${sumService.name}.${internalDomainSuffix}' }
            { name: 'MUL_URL', value: 'https://${mulService.name}.${internalDomainSuffix}' }
            { name: 'HISTORY_URL', value: 'https://${historyService.name}.${internalDomainSuffix}' }
            { name: 'MONOLITH_URL', value: 'https://${monolith.name}.${internalDomainSuffix}' }
            // Matches the gateway Dockerfile, which bakes the built
            // frontend into /app/static and sets STATIC_DIR the same way
            // (see services/gateway/Dockerfile, "ENV STATIC_DIR=/app/static").
            { name: 'STATIC_DIR', value: '/app/static' }
          ]
          // Gateway's own health endpoint is under the /api prefix
          // (see services/gateway/app/routers/health.py -> GET /api/health),
          // unlike the other 4 services which expose plain /health.
          probes: [
            {
              type: 'Liveness'
              httpGet: { path: '/api/health', port: 8080 }
            }
            {
              type: 'Readiness'
              httpGet: { path: '/api/health', port: 8080 }
            }
          ]
        }
      ]
      scale: {
        // --- Alternative: always-warm gateway, no cold start ---
        // minReplicas: 1
        minReplicas: 0
        maxReplicas: 1
      }
    }
  }
  dependsOn: [
    acrPullRoleAssignment
  ]
}

// -----------------------------------------------------------------------
// Outputs
// -----------------------------------------------------------------------

output acrLoginServer string = acr.properties.loginServer
output acrName string = acr.name
output containerAppsEnvironmentName string = containerAppsEnv.name
output gatewayFqdn string = gateway.properties.configuration.ingress.fqdn
output gatewayUrl string = 'https://${gateway.properties.configuration.ingress.fqdn}'
