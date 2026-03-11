# Code Interpreter API Specification — Shell Image

## Overview

The Shell Code Interpreter service executes shell commands (bash/sh) via a PTY-backed execution engine and provides file management operations. It runs in **shell-only mode** 

**Default Port**: `6003`  
**Base URL**: `http(s)://<host>:6003`

---

## Running the Docker Container

```bash
docker run -it --rm \
  -p 6003:6003 \
  <image-name>
```

---

## Data Models

### ShellExecutionRequest

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `shellType` | string | No | `bash` | Shell type: `"bash"` or `"sh"` |
| `shellCommand` | string | No* | — | Single command string to execute |
| `execCommandAndArgs` | []string | No* | — | Executable and arguments array (e.g., `["ls", "-la", "/tmp"]`) |
| `identifier` | string | No | — | Request identifier for tracking |
| `timeoutInSeconds` | int | No | `180` | Maximum execution time in seconds |
| `outputStreamsMaxLength` | int | No | `4096` | Maximum length of stdout/stderr in the response |

> \* At least one of `shellCommand` or `execCommandAndArgs` must be provided. Do not provide both simultaneously.

**Optional Request Headers**:

| Header | Type | Description |
|--------|------|-------------|
| `X-Execution-Identifier` | string | Alternative way to pass the identifier |
| `X-Shell-Type` | string | Alternative way to specify shell type (`bash` / `sh`) |

### ShellExecutionResponse

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Execution status (see [Status Values](#shell-status-values)) |
| `errorName` | string | Error type name (empty on success) |
| `errorMessage` | string | Error description (empty on success) |
| `exitCode` | int | Process exit code (0 = success, -1 = error/timeout) |
| `identifier` | string | Request identifier |
| `result.stdout` | string | Standard output |
| `result.stderr` | string | Standard error |
| `result.executionTimeInMilliseconds` | int64 | Execution duration in milliseconds |

#### Shell Status Values

| Status | Description |
|--------|-------------|
| `Succeeded` | Completed successfully |
| `Failed` | Execution failed or timed out |

### SessionResourceFile

File endpoints return one or more objects with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | File or directory name |
| `type` | string | `"file"` or `"directory"` |
| `sizeInBytes` | int64 | Size in bytes |
| `lastModifiedAt` | string | Last modification time (RFC 3339) |
| `contentType` | string | MIME content type |

---

## Endpoints

### Health Check

#### GET `/health`

Runs a periodic shell command (`echo 1`) to verify the container is responsive.

**Response** (200 OK):
```
"healthy"
```

**Response** (500 Internal Server Error):
```
"unhealthy"
```

---

### Shell Execution

#### Execute Shell Command — POST `/shellExecute`

Execute a shell command or script.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `identifier` | string | No | Unique identifier for request tracking and log correlation |

**Request Body**: [ShellExecutionRequest](#shellexecutionrequest)

**Response**: [ShellExecutionResponse](#shellexecutionresponse)

**Error Response** (400):
```
"no command provided in the request, at least one of the 'shellCommand' or 'ExecCommandAndArgs' fields should be provided"
```

---

#### Stream Shell Execution — WebSocket `/shellExecuteWs`

Execute shell commands via WebSocket for streaming output.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `identifier` | string | No | Unique identifier for request tracking and log correlation |

**Connection**: Upgrade to WebSocket protocol.

**Message Format** (Client → Server): Same JSON structure as [ShellExecutionRequest](#shellexecutionrequest).

**Message Format** (Server → Client): Streams stdout/stderr in real-time.

---

### File Operations

All file operations are scoped to `/mnt/data` inside the container. The shell image has `enableFullPathAccess: true`, allowing operations outside `/mnt/data` as well.

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

### Shell Execution Errors

| Error Name | Description |
|------------|-------------|
| `CommandStartError` | Failed to start the shell command |
| `ExecutionTimeout` | Command execution timed out |

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

### Execute a Shell Command

```bash
curl -X POST "http://localhost:6003/shellExecute?identifier=shell-cmd-1" \
  -H "Content-Type: application/json" \
  -d '{
    "shellCommand": "ls -la /mnt/data",
    "timeoutInSeconds": 10
  }'
```

**Response**:
```json
{
  "status": "Succeeded",
  "errorName": "",
  "errorMessage": "",
  "exitCode": 0,
  "identifier": "",
  "result": {
    "stdout": "total 0\ndrwxr-xr-x 2 root root 40 Jan 11 10:00 .\ndrwxr-xr-x 1 root root 40 Jan 11 10:00 ..\n",
    "stderr": "",
    "executionTimeInMilliseconds": 15
  }
}
```

### Execute with Exec Command and Args

```bash
curl -X POST "http://localhost:6003/shellExecute?identifier=exec-args-1" \
  -H "Content-Type: application/json" \
  -d '{
    "execCommandAndArgs": ["python3", "-c", "print(1+1)"],
    "timeoutInSeconds": 30
  }'
```

**Response**:
```json
{
  "status": "Succeeded",
  "errorName": "",
  "errorMessage": "",
  "exitCode": 0,
  "identifier": "",
  "result": {
    "stdout": "2\n",
    "stderr": "",
    "executionTimeInMilliseconds": 120
  }
}
```

### Execute with Custom Shell Type

```bash
curl -X POST "http://localhost:6003/shellExecute?identifier=custom-sh-1" \
  -H "Content-Type: application/json" \
  -H "X-Shell-Type: sh" \
  -d '{
    "shellCommand": "echo $0",
    "timeoutInSeconds": 10
  }'
```

### List Files

```bash
curl -X GET "http://localhost:6003/files?identifier=list-files-1"
```

**Response**:
```json
[
  {
    "name": "output.log",
    "type": "file",
    "sizeInBytes": 512,
    "lastModifiedAt": "2026-01-11T10:30:00Z",
    "contentType": "application/octet-stream"
  }
]
```

### Upload File

```bash
curl -X POST "http://localhost:6003/files?identifier=upload-file-1" \
  -F "file=@/path/to/local/script.sh"
```

### Download File

```bash
curl -X GET "http://localhost:6003/files/output.log/content?identifier=download-1" \
  -o output.log
```

### Delete File

```bash
# Returns 204 No Content on success
curl -X DELETE "http://localhost:6003/files/output.log?identifier=delete-1"
```

---

## Notes

1. **File Paths**: By default, file operations are relative to `/mnt/data`. The shell image has `enableFullPathAccess: true`, which allows operations on the full OS path
2. **Timeouts**: Default shell execution timeout is 180 seconds (3 minutes)
3. **Output Limits**: Default `outputStreamsMaxLength` is 4096 characters
4. **Upload Limit**: Max file upload size is 250 MB by default
5. **Supported Shells**: `bash` (`/bin/bash`) and `sh` (`/bin/sh`)
6. **Dangerous Commands**: Certain dangerous commands (e.g., `dd if=/dev/random`, fork bombs) are blocked
7. **Health Check**: A periodic `echo 1` shell command runs to verify container health
8. **Execution Endpoints**: Shell image exposes `/shellExecute` and `/shellExecuteWs` for execution
