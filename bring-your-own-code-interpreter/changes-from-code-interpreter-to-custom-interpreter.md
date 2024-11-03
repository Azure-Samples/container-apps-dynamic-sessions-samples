# Overview

This article covers the key changes required when:

1. Transitioning from a local container image and testing setup to remote Dynamic Session Pool API executions.
2. Migrating from a built-in Code Interpreter-based session pool to a Custom Container-based session pool.

Please note that these guidelines are not exhaustive; you may need additional adjustments depending on specific use cases.

## Changes Needed for Transitioning from Local Testing to Remote Dynamic Session Pool API Executions

The best and simplest approach for rapid development is to test and validate your container image locally before publishing it to the session pool for remote executions. Follow these steps to ensure your changes are production-ready.

### 1. Update the Session Pool Management API Endpoint
When moving to the Custom Container-based Dynamic Sessions pool, replace `http://localhost:6000` with the provisioned [Dynamic Session Pool Management Endpoint](https://learn.microsoft.com/en-us/azure/container-apps/sessions-code-interpreter#get-the-pool-management-api-endpoint-with-azure-cli).

### 2. Configure Authentication and Authorization
For local testing, authentication and authorization might not be necessary for simplicity. In production, however, proper configuration is essential to ensure secure access. Learn more about configuring authentication [here](https://learn.microsoft.com/en-us/azure/container-apps/sessions-code-interpreter#authentication).

### 3. Use a Valid Session Identifier
Refer to the documentation on [Session Identifiers](https://learn.microsoft.com/en-us/azure/container-apps/sessions-code-interpreter#session-identifiers) to select identifiers suited to your use case, such as user IDs, tenant IDs, or conversation IDs in chatbot scenarios.

With these updates, you can efficiently test your container image locally before deploying to a Custom Container-based Sessions pool.

## Migrating from Code Interpreter based session pool to Custom Container based Session Pool

### 1. Set Up an Azure Container App (ACA) Environment

Unlike the Code Interpreter-based session pool, which doesn’t rely on an ACA environment, the Custom Container-based session pool requires one. This is a key difference in resource provisioning. Once the session pool is set up, it operates similarly to the Code Interpreter-based pool in terms of functionality. There are other benefits which outlined [here](./README.md#overview).

### 2. Update the Session Pool Management API Endpoint
Replace the Code Interpreter-based session pool management API endpoint with the Custom Container-based session pool endpoint. Code Interpreter-based endpoints typically follow the pattern: 

`https://<REGION>.dynamicsessions.io/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>/sessionPools/<SESSION_POOL_NAME>`

For Custom Container-based session pools, the endpoint usually follows this pattern:

`https://<SESSION_POOL_NAME>.<random-string>.<REGION>.azurecontainerapps.io`

Retrieve the Session Pool Management Endpoint with the following command:

```bash
SESSION_POOL_MANAGEMENT_ENDPOINT=$(az containerapp sessionpool show -n $SESSION_POOL_NAME -g $RESOURCE_GROUP_NAME --query "properties.poolManagementEndpoint" -o tsv)
```