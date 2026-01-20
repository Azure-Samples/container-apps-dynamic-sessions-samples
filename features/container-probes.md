# Container probes for session pools

This guide explains how to configure health probes for custom container session pools to monitor and maintain healthy session instances.

> [!NOTE]
> Container probes are only supported in **Custom Container Session Pools** and require API version `2025-02-02-preview` or later.

## Overview

Container probes allow you to define health checks for your session containers, similar to how probes work in Azure Container Apps. When configured, the session pool monitors the health of each session instance and automatically removes unhealthy ones.

The session pool will:

- Ensure all ready session instances are healthy
- Automatically remove any unhealthy session instances
- Scale up to maintain the configured `readySessionInstances` count with healthy sessions

This helps maintain a reliable pool of ready sessions for your workload.

Session pools support **Liveness** and **Startup** probe types. For more information about how health probes work, see [Health probes in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/health-probes?tabs=arm-template).

## Configuration

When creating or updating a session pool, specify probes in the `properties.customContainerTemplate.containers` section of your request payload.

For the full API specification, see the [SessionPools API spec](https://learn.microsoft.com/en-us/rest/api/resource-manager/containerapps/container-apps-session-pools/create-or-update?view=rest-resource-manager-containerapps-2025-07-01&tabs=HTTP).

### Example

```json
{
  "properties": {
    "customContainerTemplate": {
      "containers": [
        {
          "name": "my-session-container",
          "image": "myregistry.azurecr.io/my-session-image:latest",
          "probes": [
            {
              "type": "Liveness",
              "httpGet": {
                "path": "/health",
                "port": 8080
              },
              "periodSeconds": 10,
              "failureThreshold": 3
            },
            {
              "type": "Startup",
              "httpGet": {
                "path": "/ready",
                "port": 8080
              },
              "periodSeconds": 5,
              "failureThreshold": 30
            }
          ]
        }
      ]
    },
    "dynamicPoolConfiguration": {
      "readySessionInstances": 5
    }
  }
}
```

## Troubleshooting

If your session pool is not maintaining the expected number of healthy `readySessionInstances`, consider the following:

1. **Check container logs** - Review your session container logs to identify issues with probe endpoints or container startup. See [View logs for custom container session pools](../code-interpreter/bring-your-own-code-interpreter/tutorials/custom-container-logs.md) for details.

2. **Verify probe configuration** - Ensure your probe paths, ports, and thresholds are correctly configured for your application.

3. **Review container health** - Check if there are issues inside your container that prevent the probe endpoints from responding successfully.

## Next steps

- [Create a custom container session pool](../code-interpreter/bring-your-own-code-interpreter/tutorials/python-custom-container-tutorial.md)
- [View session pool logs](../code-interpreter/bring-your-own-code-interpreter/tutorials/custom-container-logs.md)
- [Stop a session](stop-session.md)
