# Javascript Code Interpreter with a Custom Container

This tutorial walks you through creating a Custom Container-based Dynamic Sessions pool by extending the Bring Your Own Code (BYOC) functionality.

### In this tutorial, you will learn how to:
1. Build a custom container image based on the BYOC base image.
2. Set up a Custom Container-based Dynamic Sessions pool using this custom image.
3. Use Code Interpreter-style REST APIs to interact with the session pool, showing that a Custom Container functions identically to the Code Interpreter once a Dynamic Sessions pool is established.

We will upload a sample JavaScript script to a session and execute it using the Custom Container-based Dynamic Sessions pool code execution APIs. For additional context and explanations of certain concepts, please refer to the equivalent [Python tutorial](./python-custom-container-tutorial.md) as well.

## Prerequisites
- **Azure CLI**: Ensure [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) is installed and configured.

   ```bash
   az upgrade
   az extension add --name containerapp --upgrade --allow-preview true
   ```

- **Microsoft.App Resource Provider**: Register this resource provider.

   ```bash
   az provider register --namespace Microsoft.App
   ```

- **Docker Desktop**: Required for Docker commands. You can download it from [Docker's official site](https://www.docker.com/products/docker-desktop/).


## 1. Set Up Azure CLI and Tutorial Prerequisites

After setting up Azure CLI, you’ll need to define the environment variables used throughout this tutorial.

> [Supported Public Preview Regions](https://learn.microsoft.com/en-us/azure/container-apps/sessions?tabs=azure-cli#preview-limitations)

For example, if you selected the location `West US 2`:

```bash
SUBSCRIPTION=<YOUR_SUBSCRIPTION_ID>
RESOURCE_GROUP_NAME="js-custom-container-rg"
LOCATION="westus2"
ENVIRONMENT="js-custom-container-aca-env"
SESSION_POOL_NAME="js-custom-container-session-pool"
```

If needed, you can query your subscription ID:

```bash
az account list --output table
```

### 1.a Create an Azure Resource Group

Set your subscription and create a resource group:

```bash
az account set -s $SUBSCRIPTION
az group create --name $RESOURCE_GROUP_NAME --location $LOCATION
```

### 1.b Clone the GitHub Samples Repository

Download the sample files from GitHub:

```bash
git clone https://github.com/Azure-Samples/container-apps-dynamic-sessions-samples.git
cd container-apps-dynamic-sessions-samples/bring-your-own-code-interpreter/samples/javascript
```

## 2. Create a Custom Image from the Base BYOC Container Image

For more customization and local debugging, see the detailed instructions [here](../creating-container-image.md). For this tutorial, let’s use the sample files included in the repository.

```bash
docker build -t my-javascript-code-interpreter:0.0.1 -f ./Dockerfile .

# Push the image to a private or public container registry
docker build -t <your-docker-hub-username>/my-javascript-code-interpreter:0.0.1 -f ./Dockerfile .
docker push docker.io/<your-docker-hub-username>/my-javascript-code-interpreter:0.0.1
```

To add more JavaScript packages, update `package.json` as needed. 

If you have noticed that the Dockerfile starts with `FROM mcr.microsoft.com/k8se/services/codeinterpreter-base:0.0.3-ubuntu24.04`, extending the base BYOC container image.

👉 Assuming your published image is `docker.io/rajneeshmitharwal/my-javascript-code-interpreter:0.0.1`.

## 3. Create an Azure Container Apps (ACA) Environment

Since the Custom Container-based Dynamic Sessions pool depends on an Azure Container Apps Environment, let’s provision one:

```bash
az containerapp env create \
  --name $ENVIRONMENT \
  --resource-group $RESOURCE_GROUP_NAME \
  --location $LOCATION \
  --enable-workload-profiles
```

## 4. Set Up a Custom Container-Based Dynamic Sessions Pool

Now, create a Dynamic Sessions Pool using the custom container image you published in the previous step:

```bash
az containerapp sessionpool create -n $SESSION_POOL_NAME -g $RESOURCE_GROUP_NAME \
    --environment $ENVIRONMENT --cpu 0.5 --memory 1Gi --target-port 6000 \
    --container-type CustomContainer \
    --image docker.io/rajneeshmitharwal/my-javascript-code-interpreter:0.0.1 \
    --cooldown-period 360 --max-sessions 5 \
    --network-status EgressEnabled \
    --location $LOCATION
```

Wait until the session pool's provisioning state shows as `Succeeded`. You can check the status with this command or wait for the previous command to finish, which usually takes less than 5 minutes:

```bash
az containerapp sessionpool show -n $SESSION_POOL_NAME  -g $RESOURCE_GROUP_NAME --query "properties.provisioningState" -o tsv
```

To explore additional options and configurations, use the following command:

```bash
az containerapp sessionpool create --help 
```

## 5. Set Up Authentication, Authorization, and Session Pool Management Variables for REST API Calls

For a comprehensive guide on authentication and authorization, refer to the [documentation](https://learn.microsoft.com/en-us/azure/container-apps/sessions-code-interpreter#authentication).

### 5.a Configure Authorization for the Current User
To enable API access, assign the appropriate role to the signed-in user.

```bash
USER_OBJECT_ID=$(az ad signed-in-user show --query id -o tsv)

az role assignment create \
  --role "Azure ContainerApps Session Executor" \
  --assignee-object-id $USER_OBJECT_ID --assignee-principal-type User \
  --scope "/subscriptions/$SUBSCRIPTION/resourceGroups/$RESOURCE_GROUP_NAME/providers/Microsoft.App/sessionPools/$SESSION_POOL_NAME"
```

### 5.b Set Up Required Authentication Variables

For direct access to the session pool’s management API, generate an access token and include it in the `Authorization` header of your requests. Ensure the token contains an audience (`aud`) claim with the value `https://dynamicsessions.io`.

```bash
JWT_ACCESS_TOKEN=$(az account get-access-token --resource https://dynamicsessions.io --query accessToken -o tsv)
AUTH_HEADER="Authorization: Bearer $JWT_ACCESS_TOKEN"
```

### 5.c Retrieve the Session Pool Management Endpoint

```bash
SESSION_POOL_MANAGEMENT_ENDPOINT=$(az containerapp sessionpool show -n $SESSION_POOL_NAME -g $RESOURCE_GROUP_NAME --query "properties.poolManagementEndpoint" -o tsv)
```

### 5.d Test the Setup with a Sample Code Execution

Verify your setup by executing a simple code sample in the session pool.

```bash
curl -v -X 'POST' -H "$AUTH_HEADER" "$SESSION_POOL_MANAGEMENT_ENDPOINT/executions?api-version=2024-10-02-preview&identifier=test" -H 'Content-Type: application/json' -d '
{
    "code": "console.log(\"hello world\")"
}'
```

You should see `"status":"Succeeded"` and `"result.stdout"` with `"hello world\n"` as the output.

From here on, we will use `session-test` as the [identifier](https://learn.microsoft.com/en-us/azure/container-apps/sessions-code-interpreter#session-identifiers) to ensure all operations are executed within the context of the `session-test` session.

### 6. Upload a JavaScript Code Script to the Session

Upload a local JavaScript file to the session using the session file upload API:

```bash
curl -X POST -H "$AUTH_HEADER" -F file=@sample-js-code.js "$SESSION_POOL_MANAGEMENT_ENDPOINT/files?api-version=2024-10-02-preview&identifier=session-test"
```

**Sample Response:**

```json
HTTP 200 OK
{
  "name": "sample-js-code.js",
  "sizeInBytes": 1215,
  "lastModifiedAt": "2024-11-03T09:19:47.110733144Z",
  "contentType": "text/javascript; charset=utf-8",
  "type": "File"
}
```

### 7. Execute the Uploaded JavaScript Code Using the Session Code Execution API

Now, let's execute the previously uploaded JavaScript file using the session code execution API. First, encode the contents of `run-js-script.js` to base-64 using the `base64` command line tool:

```bash
curl -X POST -H "$AUTH_HEADER" "$SESSION_POOL_MANAGEMENT_ENDPOINT/executions?api-version=2024-10-02-preview&identifier=session-test" -H 'Content-Type: application/json' -d "{
  \"code\": \"$(base64 -w 0 run-js-script.js)\",
  \"executionType\": \"Synchronous\",
  \"codeInputType\": \"InlineBase64\"
}"
```

**Sample Response:**

```json
HTTP 202 Accepted
{
  "id": "7b427f95-884a-4ae6-8012-2df7a4e540a3",
  "identifier": "session-test",
  "sessionId": "session-test",
  "executionType": "Synchronous",
  "status": "Succeeded",
  "result": {
    "stdout": "",
    "stderr": "",
    "executionResult": "",
    "executionTimeInMilliseconds": 3
  },
  "rawResult": {
    "hresult": 0,
    "result": "",
    "error_name": "",
    "error_message": "",
    "error_stack_trace": "",
    "stdout": "",
    "stderr": "",
    "diagnosticInfo": {
      "executionRequestTimeInMilliSeconds": 3,
      "executionProcessResponseTimeInMilliSeconds": 0,
      "executionDuration": 3,
      "identifier": "session-test"
    },
    "operationId": "7b427f95-884a-4ae6-8012-2df7a4e540a3"
  }
}
```

### 8. Download the Processed File Using the Session File Download API

Check if the output file `filtered_users.json` exists by using the session’s file metadata API:

```bash
curl -X GET -H "$AUTH_HEADER" "$SESSION_POOL_MANAGEMENT_ENDPOINT/files/filtered_users.json?api-version=2024-10-02-preview&identifier=session-test" 
```

**Sample Response:**

```json
HTTP 200 OK
{
  "name": "filtered_users.json",
  "sizeInBytes": 2,
  "lastModifiedAt": "2024-11-03T09:36:59.542590532Z",
  "contentType": "application/json",
  "type": "File"
}
```

To download the file content, use the session’s file download API:

```bash
curl -X GET -H "$AUTH_HEADER" "$SESSION_POOL_MANAGEMENT_ENDPOINT/files/filtered_users.json/content?api-version=2024-10-02-preview&identifier=session-test" -o filtered_users.json
```

The file `filtered_users.json` on your local storage is the output processed by the Custom Container-based Dynamic Session Pool.

### 9. Cleanup

This command will remove the specified resource group along with all resources created during this tutorial.

```bash
az group delete --name $RESOURCE_GROUP_NAME --yes
```

## Few Gotchas with the iJavascript Kernel

- When defining variables in Node.js, avoid using `const`. Variables declared with `const` are treated as global within a session, which can lead to errors in subsequent runs if the variable has already been defined. Instead, use `var` to declare your variables to prevent these issues.
- Refrain from using `process.exit()` in your code, as it will terminate the session and cause your request to time out.
- If you're working with asynchronous code, make sure to add `$$.async()` at the beginning of your code and `setTimeout($$.done, timeOutInMilliSecond)` at the end. You can read more about `$$.async` and `$$.done` [here](https://n-riesco.github.io/ijavascript/doc/async.ipynb.html).

## Next Steps
- [Creating a Custom container image using base BYOC container Image](../creating-container-image.md)
- [REST API Samples](../api-samples.md)
- [Common FAQs](../FAQs.md)