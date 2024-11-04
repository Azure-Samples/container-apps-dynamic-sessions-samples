# Overview

The Code Interpreter Dynamic Sessions currently support API versions `2024-02-02-preview`, `2024-08-02-preview`, and `2024-10-02-preview`. 

Beginning with version `2024-10-02-preview`, the API contract has undergone significant changes. If you are starting fresh, it is recommended to use the latest version, as earlier preview versions will be deprecated soon once a stable release is available.

For the Code Interpreter Dynamic Sessions pool, API responses are further enriched with additional information, such as headers indicating concurrent session execution details. This added information may not be present in Custom Container-based Dynamic Sessions, though the high-level structure remains similar.


Refer these [guidelines](./changes-from-code-interpreter-to-custom-interpreter.md) for transitioning from a local container image and testing setup to remote Dynamic Session Pool API executions.


# Samples

## API version 2024-08-02-preview and before
You find details of exposed APIs [here](https://learn.microsoft.com/en-us/azure/container-apps/sessions-code-interpreter#management-api-endpoints) 


### Code execution
```shell
curl -X 'POST' 'http://localhost:6000/code/execute?api-version=2024-08-02-preview&identifier=test-identifier'   -H 'Content-Type: application/json' -d '{
    "properties": {
        "identifier": "test-identifier",
        "codeInputType": "inline",
        "executionType": "Synchronous",
        "code": "print(\"inline-synchronous\")",
        "timeoutInSeconds": 100
    }
}'
```

```shell
< HTTP/1.1 202 Accepted
< Content-Type: application/json
< Operation-Id: d04f566c-9a27-44cc-9b66-bfad404a7921
< X-Ms-Container-Execution-Duration: 5011
< X-Ms-Execution-Request-Time: 5010.000000
< X-Ms-Overall-Execution-Time: 42m56.970311818s
< X-Ms-Session-Guid: d04f566c-9a27-44cc-9b66-bfad404a7921

{
  "properties": {
    "$id": "d04f566c-9a27-44cc-9b66-bfad404a7921",
    "status": "Success",
    "stdout": "inline-synchronous\n",
    "stderr": "",
    "executionResult": "",
    "executionTimeInMilliseconds": 9
  }
}
```

```shell
curl -X 'POST' 'http://localhost:6000/code/execute?api-version=2024-08-02-preview&identifier=test-identifier'   -H 'Content-Type: application/json' -d '{
    "properties": {
        "identifier": "test-identifier",
        "codeInputType": "inline",
        "executionType": "Synchronous",
        "code": "import time \ntime.sleep(5) \nprint(\"Done Sleeping\")",
        "timeoutInSeconds": 100
    }
}'

{
  "properties": {
    "$id": "22b9cb2c-47e5-4b57-a90e-ba57de00599f",
    "status": "Success",
    "stdout": "Done Sleeping\n",
    "stderr": "",
    "executionResult": "",
    "executionTimeInMilliseconds": 5010
  }
}
```

### Upload a session file to a session

```shell
curl -v -X POST -F "file=@/path/to/your/file/README.md" 'http://localhost:6000/upload'

> POST /upload?api-version=2024-08-02-preview HTTP/1.1
> Host: localhost:6000
> User-Agent: curl/8.5.0
> Accept: */*
> Content-Length: 5258
> Content-Type: multipart/form-data; boundary=------------------------cq27GtlV57bqNA2u909dnE
>
* We are completely uploaded and fine
< HTTP/1.1 200 OK
< Content-Type: application/json
< Date: Sat, 02 Nov 2024 11:54:35 GMT
< Content-Length: 168
<
[{"name":"README.md","type":"file","filename":"README.md","size":5045,"last_modified_time":"2024-11-02T11:54:35.595707834Z","mime_type":"text/markdown; charset=utf-8"}]
```

### Download a session file from a session

```shell
curl -v -O -X GET "http://localhost:6000/files/content/README.md/content?api-version=2024-08-02-preview&identifier=test-identifier" 

* Connected to localhost (::1) port 6000
> GET /files/content/README.md?api-version=2024-08-02-preview&identifier=test-identifier HTTP/1.1
> Host: localhost:6000
> User-Agent: curl/8.5.0
> Accept: */*
>
< HTTP/1.1 200 OK
< Accept-Ranges: bytes
< Content-Length: 5045
< Content-Type: text/markdown; charset=utf-8
< Last-Modified: Sat, 02 Nov 2024 11:54:35 GMT
< Date: Sat, 02 Nov 2024 12:09:45 GMT
<
[5045 bytes data]
100  5045  100  5045    0     0   790k      0 --:--:-- --:--:-- --:--:--  821k
```

### List the session files of a session

```shell
curl -v -X GET 'http://localhost:6000/files?api-version=2024-08-02-preview&identifier=test-identifier'

< HTTP/1.1 200 OK
< Content-Type: application/json
< Date: Sat, 02 Nov 2024 12:02:51 GMT
< Content-Length: 168
<
[{"name":"README.md","type":"file","filename":"README.md","size":5045,"last_modified_time":"2024-11-02T11:54:35.595707834Z","mime_type":"text/markdown; charset=utf-8"}]

```

### Get a specific session file of a session 

```shell
curl -v -X GET "http://localhost:6000/files/README.md?api-version=2024-08-02-preview&identifier=test-identifier"

< HTTP/1.1 200 OK
< Content-Type: application/json
< Date: Sat, 02 Nov 2024 12:12:14 GMT
< Content-Length: 133
<
{"value":[{"$id":"","properties":{"$id":"","filename":"README.md","size":5045,"lastModifiedTime":"2024-11-02T11:54:35.595707834Z"}}]}
```

### Delete a specific session file of a session 

```shell
curl -v -X DELETE "http://localhost:6000/files/README.md?api-version=2024-08-02-preview&identifier=test-identifier"

< HTTP/1.1 200 OK
< Content-Type: application/json
< Date: Sat, 02 Nov 2024 12:12:59 GMT
< Content-Length: 40
<
{"message": "file deleted successfully"}
```

----

## API version 2024-10-02-preview and onwards

### Code execution
#### Synchronous code execution
```shell
curl -X 'POST' 'http://localhost:6000/executions?api-version=2024-10-02-preview&identifier=test-identifier'   -H 'Content-Type: application/json' -d '{
        "identifier": "test-identifier",
        "codeInputType": "inline",
        "executionType": "Synchronous",
        "code": "print(\"inline-synchronous\")",
        "timeoutInSeconds": 100
}'

< HTTP/1.1 202 Accepted
< Content-Type: application/json
{
  "id": "553e972b-2925-442b-ad67-28970e2d5c53",
  "identifier": "test-identifier",
  "sessionId": "test-identifier",
  "executionType": "synchronous",
  "status": "Succeeded",
  "result": {
    "stdout": "inline-synchronous\n",
    "stderr": "",
    "executionResult": "",
    "executionTimeInMilliseconds": 9
  },
  "rawResult": {
    "hresult": 0,
    "result": "",
    "error_name": "",
    "error_message": "",
    "error_stack_trace": "",
    "stdout": "inline-synchronous\n",
    "stderr": "",
    "diagnosticInfo": {
      "executionRequestTimeInMilliSeconds": 9,
      "executionProcessResponseTimeInMilliSeconds": 0,
      "executionDuration": 9,
      "identifier": "test-identifier"
    },
    "operationId": "553e972b-2925-442b-ad67-28970e2d5c53"
  }
}
```

#### Asynchronous code execution

##### Submit the code execution request
```shell
curl -X 'POST' 'http://localhost:6000/executions?api-version=2024-10-02-preview&identifier=test-identifier'   -H 'Content-Type: application/json' -d '{
        "identifier": "test-identifier",
        "codeInputType": "inline",
        "executionType": "Asynchronous",
        "code": "import time\\ntime.sleep(2)\\nprint(\"Hello from async code\")",
        "timeoutInSeconds": 100
}'

< HTTP/1.1 202 Accepted
< Content-Type: application/json
< Operation-Id: 8963ad02-1d0b-43ef-9863-0cefd18d5fb4
< Operation-Location: /executions/8963ad02-1d0b-43ef-9863-0cefd18d5fb4?api-version=2024-10-02-preview&identifier=test-identifier
{
  "id": "8963ad02-1d0b-43ef-9863-0cefd18d5fb4",
  "identifier": "test-identifier",
  "sessionId": "test-identifier",
  "executionType": "Asynchronous",
  "status": "Running",
  "rawResult": {
    "hresult": 0,
    "result": null,
    "error_name": "",
    "error_message": "",
    "error_stack_trace": "",
    "stdout": "8963ad02-1d0b-43ef-9863-0cefd18d5fb4",
    "stderr": "",
    "diagnosticInfo": {
      "executionRequestTimeInMilliSeconds": 0,
      "executionProcessResponseTimeInMilliSeconds": 0,
      "executionDuration": 75,
      "identifier": "10"
    },
    "operationId": "8963ad02-1d0b-43ef-9863-0cefd18d5fb4"
  }
}
```

##### Long poll till code execution completion

```shell
curl -X 'GET' 'http://localhost:6000/executions/8963ad02-1d0b-43ef-9863-0cefd18d5fb4?api-version=2024-10-02-preview&identifier=test-identifier' 

< HTTP/1.1 200 OK
< Content-Type: application/json
{
  "id": "8963ad02-1d0b-43ef-9863-0cefd18d5fb4",
  "identifier": "test-identifier",
  "sessionId": "test-identifier",
  "executionType": "Asynchronous",
  "status": "Succeeded",
  "result": {
    "stdout": "Hello from async code\n",
    "stderr": "",
    "executionResult": "",
    "executionTimeInMilliseconds": 380
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
      "executionRequestTimeInMilliSeconds": 0,
      "executionProcessResponseTimeInMilliSeconds": 0,
      "executionDuration": 0,
      "identifier": ""
    },
    "operationId": ""
  }
}
```

### Upload a session file to a session

```shell
curl -v  -X POST -F "file=@/path/to/your/file/README.md" 'http://localhost:6000/files?api-version=2024-10-02-preview&identifier=test-identifier&path=/mnt/data'

> POST /files?api-version=2024-10-02-preview&identifier=test-identifier&path=/mnt/data HTTP/1.1
> Host: localhost:6000
> User-Agent: curl/8.5.0
> Accept: */*
> Content-Length: 347
> Content-Type: multipart/form-data; boundary=------------------------B7Jj4ag7wLRxPTOkY7HyIQ
>
* We are completely uploaded and fine
< HTTP/1.1 200 OK
< Content-Type: application/json
< Date: Sat, 02 Nov 2024 12:33:05 GMT
< Content-Length: 148

{"name":"README2.md","sizeInBytes":133,"lastModifiedAt":"2024-11-02T12:33:05.677209683Z","contentType":"text/markdown; charset=utf-8","type":"File"}
```

### Download a session file from a session

```shell
curl -v -O -X GET "http://localhost:6000/files/README2.md/content?api-version=2024-10-02-preview&identifier=test-identifier&path=/mnt/data" 

> GET /files/README2.md?api-version=2024-10-02-preview&identifier=test-identifier&path=/mnt/data HTTP/1.1
> Host: localhost:6000
> User-Agent: curl/8.5.0
> Accept: */*
>
< HTTP/1.1 200 OK
< Content-Type: application/json
< Date: Sat, 02 Nov 2024 12:41:22 GMT
< Content-Length: 148
<
{ [148 bytes data]
100   148  100   148    0     0  16387      0 --:--:-- --:--:-- --:--:-- 18500
```

### List the session files of a session

```shell
curl -v -X GET 'http://localhost:6000/files?api-version=2024-10-02-preview&identifier=test-identifier&path=/mnt/data'

< HTTP/1.1 200 OK
< Content-Type: application/json
< Date: Sat, 02 Nov 2024 12:42:30 GMT
< Content-Length: 160
<
{"value":[{"name":"README2.md","sizeInBytes":133,"lastModifiedAt":"2024-11-02T12:33:05.677209683Z","contentType":"text/markdown; charset=utf-8","type":"File"}]}

```

### Get a specific session file of a session 

```shell
curl -v -X GET "http://localhost:6000/files/README2.md?api-version=2024-10-02-preview&identifier=test-identifier&path=/mnt/data"

< HTTP/1.1 200 OK
< Content-Type: application/json
< Date: Sat, 02 Nov 2024 12:42:56 GMT
< Content-Length: 148
<
{"name":"README2.md","sizeInBytes":133,"lastModifiedAt":"2024-11-02T12:33:05.677209683Z","contentType":"text/markdown; charset=utf-8","type":"File"}
```

### Delete a specific session file of a session 

```shell
curl -v -X DELETE "http://localhost:6000/files/README2.md?api-version=2024-10-02-preview&identifier=test-identifier&path=/mnt/data"

< HTTP/1.1 204 No Content
< Content-Type: application/json
```