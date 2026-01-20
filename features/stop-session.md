# Stop a session

This guide explains how to stop a session in a custom container session pool using the Stop Session API.

> [!NOTE]
> This API is currently only supported in **Custom Container Session Pools**.

## Overview

Session pools support automatic session management through `lifecycleConfiguration`, which handles session lifecycle based on your configuration automatically. However, there are scenarios where you may need more control—this is where the Stop Session API comes in.

After allocating a session, you can call this API to manually terminate it at any time. This is useful when:

- You need to clean up resources before a session reaches its time-to-live
- Your session pool has reached its maximum concurrent sessions limit and you need to free up capacity for new sessions
- A session has completed its work and you want to release resources immediately

## API reference

### Request

```http
POST {PoolManagementEndpoint}/.management/stopSession?api-version=2025-02-02-preview&identifier={SessionIdentifier}
```

### Parameters

| Parameter     | Type   | Required | Description                                          |
|---------------|--------|----------|------------------------------------------------------|
| `api-version` | string | Yes      | The API version to use (e.g., `2025-02-02-preview`)  |
| `identifier`  | string | Yes      | The unique identifier of the session to stop         |

## Example

### Example request

```http
POST https://{{PoolManagementEndpoint}}/.management/stopSession?api-version=2025-10-02-preview&identifier=testSessionIdentifier
```

### Response

```text
HTTP/1.1 200 OK
Content-Type: text/plain

Session testSessionIdentifier in session pool testSessionPool stopped.
```

## Next steps

- [Create a custom container session pool](../code-interpreter/bring-your-own-code-interpreter/tutorials/python-custom-container-tutorial.md)
- [Custom container session pool overview](../code-interpreter/bring-your-own-code-interpreter/README.md)
