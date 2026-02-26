# Python Code Interpreter with a Custom Container

This tutorial walks you through creating a Custom Container-based Dynamic Sessions pool by extending the Bring Your Own Code (BYOC) functionality.

### In this tutorial, you will learn how to:
1. Build a custom container image based on the BYOC base image.
2. Set up a Custom Container-based Dynamic Sessions pool using this custom image.
3. Use Code Interpreter-style REST APIs to interact with the session pool, showing that a Custom Container functions identically to the Code Interpreter once a Dynamic Sessions pool is established.

We'll install the Python [pillow](https://pillow.readthedocs.io/en/stable/handbook/tutorial.html) package, upload an image to the session, crop the image using code execution in the session, and then download the cropped image.

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
RESOURCE_GROUP_NAME="python-custom-container-rg"
LOCATION="westus2"
ENVIRONMENT="python-custom-container-aca-env"
SESSION_POOL_NAME="py-custom-container-session-pool"
```

If needed, you can query your subscription ID:

```bash
az account list --output table
```

### Create an Azure Resource Group

Set your subscription and create a resource group:

```bash
az account set -s $SUBSCRIPTION
az group create --name $RESOURCE_GROUP_NAME --location $LOCATION
```

### Clone the GitHub Samples Repository

Download the sample files from GitHub:

```bash
git clone https://github.com/Azure-Samples/container-apps-dynamic-sessions-samples.git
cd container-apps-dynamic-sessions-samples/code-interpreter/bring-your-own-code-interpreter/samples/python
```

## 2. Create a Custom Image from the Base BYOC Container Image

For more customization and local debugging, see the detailed instructions [here](../creating-container-image.md). For this tutorial, let’s use the sample files included in the repository.

```bash
docker build -t my-python-code-interpreter:0.0.1 -f ./Dockerfile .

# Push the image to a private or public container registry
docker build -t <your-docker-hub-username>/my-python-code-interpreter:0.0.1 -f ./Dockerfile .
docker push docker.io/<your-docker-hub-username>/my-python-code-interpreter:0.0.1
```

To add more Python packages, update `requirements.txt` as needed. 

If you have noticed that the Dockerfile starts with `FROM mcr.microsoft.com/k8se/services/codeinterpreter:0.11.2-python3.12-base`, extending the base BYOC container image.

👉 Assuming your published image is `docker.io/rajneeshmitharwal/my-python-code-interpreter:0.0.1`.

## 3. Create an Azure Container Apps (ACA) Environment

Since the Custom Container-based Dynamic Sessions pool depends on an Azure Container Apps Environment, let’s provision one:

```bash
az containerapp env create \
  --name $ENVIRONMENT \
  --resource-group $RESOURCE_GROUP_NAME \
  --location $LOCATION \
  --enable-workload-profiles
```

This tutorial uses Azure CLI to provision the ACA environment, but you can also use the Azure Portal, ARM templates, and other options. For additional parameters, see [Managed Environment API Documentation](https://learn.microsoft.com/en-us/rest/api/containerapps/managed-environments/create-or-update?view=rest-containerapps-2024-03-01&tabs=HTTP).

## 4. Set Up a Custom Container-Based Dynamic Sessions Pool

Now, create a Dynamic Sessions Pool using the custom container image you published in the previous step:

```bash
az containerapp sessionpool create -n $SESSION_POOL_NAME -g $RESOURCE_GROUP_NAME \
    --environment $ENVIRONMENT --cpu 0.5 --memory 1Gi --target-port 6000 \
    --container-type CustomContainer \
    --image docker.io/rajneeshmitharwal/my-python-code-interpreter:0.0.1 \
    --cooldown-period 360 --max-sessions 5 \
    --network-status EgressEnabled \
    --location $LOCATION
```

Wait until the session pool's provisioning state shows as `Succeeded`. You can check the status with this command or wait for the previous command to finish, which usually takes less than 5 minutes:

```bash
az containerapp sessionpool show -n $SESSION_POOL_NAME  -g $RESOURCE_GROUP_NAME --query "properties.provisioningState" -o tsv
```

To explore additional options and configurations, use the following command or refer to the [Session Pool API Documentation](https://learn.microsoft.com/en-us/rest/api/containerapps/container-apps-session-pools/create-or-update?view=rest-containerapps-2024-08-02-preview&tabs=HTTP) for a complete list of parameters:

```bash
az containerapp sessionpool create --help 
```

## 5. Set Up Authentication, Authorization, and Session Pool Management Variables for REST API Calls

For a comprehensive guide on authentication and authorization, refer to the [documentation](https://learn.microsoft.com/en-us/azure/container-apps/sessions-code-interpreter#authentication).

### Configure Authorization for the Current User
To enable API access, assign the appropriate role to the signed-in user.

```bash
USER_OBJECT_ID=$(az ad signed-in-user show --query id -o tsv)

az role assignment create \
  --role "Azure ContainerApps Session Executor" \
  --assignee-object-id $USER_OBJECT_ID --assignee-principal-type User \
  --scope "/subscriptions/$SUBSCRIPTION/resourceGroups/$RESOURCE_GROUP_NAME/providers/Microsoft.App/sessionPools/$SESSION_POOL_NAME"
```

### Set Up Required Authentication Variables

For direct access to the session pool’s management API, generate an access token and include it in the `Authorization` header of your requests. Ensure the token contains an audience (`aud`) claim with the value `https://dynamicsessions.io`.

```bash
JWT_ACCESS_TOKEN=$(az account get-access-token --resource https://dynamicsessions.io --query accessToken -o tsv)
AUTH_HEADER="Authorization: Bearer $JWT_ACCESS_TOKEN"
```

### Retrieve the Session Pool Management Endpoint

```bash
SESSION_POOL_MANAGEMENT_ENDPOINT=$(az containerapp sessionpool show -n $SESSION_POOL_NAME -g $RESOURCE_GROUP_NAME --query "properties.poolManagementEndpoint" -o tsv)
```

### Available REST API Endpoints (Azure REST API Spec)

The following table lists all REST API endpoints aligned with the Azure REST API spec, as implemented in the code interpreter service:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/executions` | Execute code synchronously or asynchronously |
| `GET` | `/executions/{executionId}` | Get results of an asynchronous execution |
| `GET` | `/files` | List all files in the session |
| `POST` | `/files` | Upload a file to the session |
| `GET` | `/files/{filename}` | Get file metadata |
| `GET` | `/files/{filename}/content` | Download file content |
| `DELETE` | `/files/{filename}` | Delete a file from the session |

All endpoints require the `identifier` query parameter to specify the session.

### Test the Setup with a Sample Code Execution

Verify your setup by executing a simple code sample in the session pool.

```bash
curl -v -X 'POST' -H "$AUTH_HEADER" "$SESSION_POOL_MANAGEMENT_ENDPOINT/executions?identifier=test" -H 'Content-Type: application/json' -d '
{
    "code": "print(\"hello world\")",
    "timeoutInSeconds": 60
}'
```

Sample Response:

```json
HTTP 200 OK
{
  "id": "<execution-id>",
  "identifier": "test",
  "executionType": "synchronous",
  "status": "Succeeded",
  "result": {
    "stdout": "hello world\n",
    "stderr": "",
    "executionResult": null,
    "executionTimeInMilliseconds": 15
  }
}
```

From here on, we will use `session-test` as the [identifier](https://learn.microsoft.com/en-us/azure/container-apps/sessions-code-interpreter#session-identifiers) to ensure all operations are executed within the context of the `session-test` session.

## 6. Upload a Sample Image to the Session

### Download a Sample Image or Use Your Own

```bash
curl -o sample.jpg "https://upload.wikimedia.org/wikipedia/commons/1/16/HDRI_Sample_Scene_Balls_%28JPEG-HDR%29.jpg"
```

### Upload the Local File to the Session Using the Session File Upload API

```bash
curl -X POST -H "$AUTH_HEADER" -F file=@sample.jpg "$SESSION_POOL_MANAGEMENT_ENDPOINT/files?identifier=session-test"
```

Sample Response:

```json
HTTP 200 OK
[
  {
    "name": "sample.jpg",
    "type": "file",
    "sizeInBytes": 146534,
    "lastModifiedAt": "2024-11-03T06:59:11Z",
    "directory": ".",
    "contentType": "image/jpeg"
  }
]
```

### List Files in the Session to Verify Upload

Use the `GET /files` endpoint to list all files in the session and confirm the upload was successful:

```bash
curl -X GET -H "$AUTH_HEADER" "$SESSION_POOL_MANAGEMENT_ENDPOINT/files?identifier=session-test"
```

Sample Response:

```json
HTTP 200 OK
[
  {
    "name": "sample.jpg",
    "type": "file",
    "sizeInBytes": 146534,
    "lastModifiedAt": "2024-11-03T06:59:11Z",
    "directory": ".",
    "contentType": "image/jpeg"
  }
]
```

## 7. Crop the Uploaded Image Using the Session Code Execution API

```bash
curl -v -X POST -H "$AUTH_HEADER" "$SESSION_POOL_MANAGEMENT_ENDPOINT/executions?identifier=session-test" -H 'Content-Type: application/json' -d '
{
    "code": "from PIL import Image\nImage.open(\"/mnt/data/sample.jpg\").crop((100, 100, 400, 400)).save(\"/mnt/data/cropped_sample.jpg\")",
    "executionType": "synchronous",
    "timeoutInSeconds": 60
}'
```

Sample Response:

```json
HTTP 200 OK
{
  "id": "ae2e682e-3690-4df2-bd6e-536b06afd1d6",
  "identifier": "session-test",
  "executionType": "synchronous",
  "status": "Succeeded",
  "result": {
    "stdout": "",
    "stderr": "",
    "executionResult": null,
    "executionTimeInMilliseconds": 16
  }
}
```

## 8. Download the Cropped File Using the Session File Download API

### Check File Metadata

To check if `cropped_sample.jpg` exists, use the session's file metadata API call:

```bash
curl -X GET -H "$AUTH_HEADER" "$SESSION_POOL_MANAGEMENT_ENDPOINT/files/cropped_sample.jpg?identifier=session-test" 
```

Sample Response:

```json
HTTP 200 OK
{
  "name": "cropped_sample.jpg",
  "type": "file",
  "sizeInBytes": 10969,
  "lastModifiedAt": "2024-11-03T07:06:25Z",
  "directory": ".",
  "contentType": "image/jpeg"
}
```

### Download File Content

To download the actual file content, use the session's file download API call:

```bash
curl -X GET -H "$AUTH_HEADER" "$SESSION_POOL_MANAGEMENT_ENDPOINT/files/cropped_sample.jpg/content?identifier=session-test" -o cropped_sample.jpg
```

The file `cropped_sample.jpg` on your local storage is the cropped image processed by the Custom Container-based Dynamic Session Pool.

## 9. Delete a File from the Session

Use `DELETE /files/{filename}` to remove a file from the session:

```bash
curl -X DELETE -H "$AUTH_HEADER" "$SESSION_POOL_MANAGEMENT_ENDPOINT/files/cropped_sample.jpg?identifier=session-test"
```

Sample Response:

```
HTTP 204 No Content
```

## 10. Asynchronous Code Execution and Getting Results

You can also execute code asynchronously by setting `executionType` to `asynchronous`. The API returns immediately with an execution ID that you can use to poll for results.

### Submit an Asynchronous Execution

```bash
curl -v -X POST -H "$AUTH_HEADER" "$SESSION_POOL_MANAGEMENT_ENDPOINT/executions?identifier=session-test" -H 'Content-Type: application/json' -d '
{
    "code": "import time\ntime.sleep(2)\nprint(\"async task completed\")",
    "executionType": "asynchronous",
    "timeoutInSeconds": 60
}'
```

Sample Response:

```json
HTTP 200 OK
{
  "id": "b3e4f5a6-7890-4abc-def1-234567890abc",
  "identifier": "session-test",
  "executionType": "asynchronous",
  "status": "NotStarted"
}
```

### Get Async Execution Results

Use the execution ID from the response to retrieve the results via `GET /executions/{executionId}`:

```bash
curl -X GET -H "$AUTH_HEADER" "$SESSION_POOL_MANAGEMENT_ENDPOINT/executions/b3e4f5a6-7890-4abc-def1-234567890abc?identifier=session-test"
```

Sample Response:

```json
HTTP 200 OK
{
  "id": "b3e4f5a6-7890-4abc-def1-234567890abc",
  "identifier": "session-test",
  "executionType": "asynchronous",
  "status": "Succeeded",
  "result": {
    "stdout": "async task completed\n",
    "stderr": "",
    "executionResult": null,
    "executionTimeInMilliseconds": 2015
  }
}
```

## 11. Cleanup

This command will remove the specified resource group along with all resources created during this tutorial.

```bash
az group delete --name $RESOURCE_GROUP_NAME --yes
```

## Next Steps
- [Creating a Custom container image using base BYOC container Image](../creating-container-image.md)
- [REST API Samples](../api-samples.md)
- [Common FAQs](../FAQs.md)