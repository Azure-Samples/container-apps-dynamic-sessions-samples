# Code Interpreter API Specification — Python Image

## Overview

The Python Code Interpreter service executes Python code via Jupyter kernels and provides file management operations. It runs in **Jupyter mode** (`spec.kernel.enabled: true`).

**Default Port**: `6000`  
**Base URL**: `http(s)://<host>:6000`

---

## Running the Docker Container

```bash
docker run -it --rm \
  -p 6000:6000 \
  <image-name>
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENABLE_ASYNC_EXECUTION` | No | — | Enable asynchronous execution kernel (`true` / `false`) |

---

## Data Models

### ExecutionRequest

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `code` | string | Yes | — | Code to execute |
| `timeoutInSeconds` | int | No | `120` | Maximum execution time in seconds |
| `executionType` | string | No | `"synchronous"` | `"synchronous"` or `"asynchronous"` |
| `outputStreamsMaxLength` | int | No | `4096` | Maximum length of stdout/stderr in the response |
| `useEmptyKernel` | bool | No | `false` | Use a kernel without preloaded libraries (faster startup) |
| `returnJupyterFormatExecutionResult` | bool | No | `false` | Return execution result in Jupyter native format |

### ExecutionResponse

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Operation ID (use to poll async results) |
| `identifier` | string | Request identifier passed in query parameter |
| `executionType` | string | `"synchronous"` or `"asynchronous"` |
| `status` | string | Execution status (see [Status Values](#execution-status-values)) |
| `result.stdout` | string | Standard output |
| `result.stderr` | string | Standard error (includes error details on failure) |
| `result.executionResult` | object/null | Return value of the executed code |
| `result.executionTimeInMilliseconds` | int64 | Execution duration in milliseconds |

#### Execution Status Values

| Status | Description |
|--------|-------------|
| `NotStarted` | Execution has not started (async: queued) |
| `Running` | Execution in progress |
| `Succeeded` | Completed successfully |
| `Failed` | Execution failed |

### SessionResourceFile

File endpoints return one or more objects with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | File or directory name |
| `type` | string | `"file"` or `"directory"` |
| `sizeInBytes` | int64 | Size in bytes |
| `lastModifiedAt` | string | Last modification time (RFC 3339) |
| `directory` | string | Parent directory path |
| `contentType` | string | MIME content type |

---

## Endpoints

### Health Checks

#### GET `/health`

Validates kernel states via the Jupyter API. Returns healthy if kernels are in `idle` or `busy` execution state.

**Response** (200 OK):
```
"healthy"
```

**Response** (500 Internal Server Error):
```
"unhealthy"
```

---

#### GET `/health/startup`

Returns 200 only when **all** required kernels have completed initialization. Use for Kubernetes startup probes.

**Response** (200 OK):
```
"healthy"
```

**Response** (500 Internal Server Error):
```
"unhealthy"
```

---

### Code Execution

#### Execute Code — POST `/executions`

Execute code on a Jupyter kernel. Supports both synchronous and asynchronous execution.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `identifier` | string | No | Unique identifier for request tracking and log correlation |

**Request Body**: [ExecutionRequest](#executionrequest)

**Response**: [ExecutionResponse](#executionresponse)

**Error Response** (400):
```
"`Code` field is required in the request"
```

---

#### Get Execution Result — GET `/executions/{operationId}`

Retrieve the result of an asynchronous execution.

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `operationId` | string | Yes | Operation ID returned from async execution |

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `identifier` | string | No | Unique identifier for request tracking and log correlation |

**Response**: [ExecutionResponse](#executionresponse)

**Error Response** (404):
```
"No execution available for operation Id: <operationId>"
```

---

### File Operations

All file operations are scoped to `/mnt/data` inside the container.

#### Common Parameters

| Parameter | In | Type | Required | Description |
|-----------|----|------|----------|-------------|
| `identifier` | query | string | No | Unique identifier for request tracking and log correlation |
| `path` | query | string | No | Subdirectory path relative to `/mnt/data` |
| `filename` | path | string | Yes* | Name of the file or directory (\*required for single-file operations) |
| `recursive` | query | string | No | Set to `"true"` for recursive listing (List Files only) |

---

#### List Files — GET `/files`

List files and directories.

**Parameters**: `identifier`, `path`, `recursive`

**Response** (200 OK): Array of [SessionResourceFile](#sessionresourcefile)

---

#### Upload File — POST `/files`

Upload a file.

**Parameters**: `identifier`, `path`

**Content-Type**: `multipart/form-data`

| Form Field | Type | Description |
|------------|------|-------------|
| `file` | file | File to upload (max 250 MB by default) |

**Response** (200 OK): Array of [SessionResourceFile](#sessionresourcefile)

---

#### Get File Metadata — GET `/files/{filename}`

Get file metadata.

**Parameters**: `identifier`, `path`, `filename`

**Response** (200 OK): [SessionResourceFile](#sessionresourcefile)

---

#### Download File Content — GET `/files/{filename}/content`

Download file content.

**Parameters**: `identifier`, `filename`

**Response** (200 OK):
- **Content-Type**: Determined by file type
- **Body**: File content (binary)

---

#### Delete File — DELETE `/files/{filename}`

Delete a file or directory.

**Parameters**: `identifier`, `path`, `filename`

**Response** (204 No Content): Empty response body on successful deletion.

---

## Error Codes

### Code Execution Errors

| Error Name | Description |
|------------|-------------|
| `Timeout` | Request timed out waiting for execution to complete |
| `ConnectionClosed` | Failed to establish connection, connection is closed |
| `ConnectionError` | Failed to initialize websocket connection |
| `InternalServerError` | Internal server error reading message |
| `WebsocketError` | Failed to create websocket connection |
| `MessageProcessingError` | Error processing message from Jupyter |

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 204 | No Content — successful deletion |
| 400 | Bad Request — invalid input or missing required fields |
| 404 | Not Found — resource not found |
| 500 | Internal Server Error |

---

## Examples

### Execute Python Code (Synchronous)

```bash
curl -X POST "http://localhost:6000/executions?identifier=my-request-id" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import numpy as np\nprint(np.array([1,2,3]))\n2+2",
    "timeoutInSeconds": 30,
    "executionType": "synchronous"
  }'
```

**Response**:
```json
{
  "id": "op-12345",
  "identifier": "my-request-id",
  "executionType": "synchronous",
  "status": "Succeeded",
  "result": {
    "stdout": "[1 2 3]\n",
    "stderr": "",
    "executionResult": 4,
    "executionTimeInMilliseconds": 125
  }
}
```

### Execute Python Code (Asynchronous)

```bash
# Step 1: Submit async execution
curl -X POST "http://localhost:6000/executions?identifier=async-job-1" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import time\ntime.sleep(2)\nprint(\"Done\")",
    "timeoutInSeconds": 30,
    "executionType": "asynchronous"
  }'
```

**Response** (immediate):
```json
{
  "id": "guid-operation-id",
  "identifier": "async-job-1",
  "executionType": "asynchronous",
  "status": "NotStarted",
  "result": {
    "stdout": "guid-operation-id",
    "stderr": "",
    "executionResult": null,
    "executionTimeInMilliseconds": 0
  }
}
```

```bash
# Step 2: Poll for results
curl -X GET "http://localhost:6000/executions/guid-operation-id?identifier=async-job-1"
```

**Response** (when completed):
```json
{
  "id": "guid-operation-id",
  "identifier": "",
  "executionType": "asynchronous",
  "status": "Succeeded",
  "result": {
    "stdout": "Done\n",
    "stderr": "",
    "executionResult": null,
    "executionTimeInMilliseconds": 2015
  }
}
```

### Use Empty Kernel

```bash
curl -X POST "http://localhost:6000/executions" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(1+1)",
    "useEmptyKernel": true
  }'
```

### List Files

```bash
curl -X GET "http://localhost:6000/files?identifier=list-files-1"
```

**Response**:
```json
[
  {
    "name": "data.csv",
    "type": "file",
    "sizeInBytes": 2048,
    "lastModifiedAt": "2026-01-11T10:30:00Z",
    "directory": ".",
    "contentType": "text/csv"
  }
]
```

### Upload File

```bash
curl -X POST "http://localhost:6000/files?identifier=upload-file-1" \
  -F "file=@/path/to/local/file.txt"
```

**Response**:
```json
[
  {
    "name": "file.txt",
    "type": "file",
    "sizeInBytes": 1024,
    "lastModifiedAt": "2026-01-11T11:00:00Z",
    "directory": ".",
    "contentType": "text/plain"
  }
]
```

### Get File Metadata

```bash
curl -X GET "http://localhost:6000/files/data.csv?identifier=get-meta-1" \
```

### Download File

```bash
curl -X GET "http://localhost:6000/files/data.csv/content?identifier=download-1" \
  -o data.csv
```

### Delete File

```bash
# Returns 204 No Content on success
curl -X DELETE "http://localhost:6000/files/data.csv?identifier=delete-1"
```

---

## Notes

1. **File Paths**: All file operations are relative to `/mnt/data` (an emptyDir volume in Kubernetes)
2. **Timeouts**: Default execution timeout is 120 seconds (configurable)
3. **Output Limits**: Default `outputStreamsMaxLength` is 4096 characters
4. **Upload Limit**: Max file upload size is 250 MB by default
5. **Kernel Types**: Three kernel types are available — synchronous (with preloaded libraries), empty (no preloaded libraries), and asynchronous
