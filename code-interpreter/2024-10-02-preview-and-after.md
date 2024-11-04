# Overview
This includes sample documentation for API versions starting from `2024-10-02-preview` and later.

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
```

Sample Response: 

```shell
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
```

Sample Response: 

```shell
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

##### Long poll until code execution completion

```shell
curl -X 'GET' 'http://localhost:6000/executions/8963ad02-1d0b-43ef-9863-0cefd18d5fb4?api-version=2024-10-02-preview&identifier=test-identifier' 
```

Sample Response: 

```shell
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
```

Sample Response: 

```shell

* We are completely uploaded and fine
< HTTP/1.1 200 OK
< Content-Type: application/json
< Date: Sat, 02 Nov 2024 12:33:05 GMT
< Content-Length: 148

{"name":"README2.md","sizeInBytes":133,"lastModifiedAt":"2024-11-02T12:33:05.677209683Z","contentType":"text/markdown; charset=utf-8","type":"File"}
```

### Download a session file from a session

```shell
curl -v -O -X GET "http://localhost:6000/files/README2.md/content?api-version=2024-10-02-preview&identifier=test-identifier" 
```

Sample Response: 

```shell

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
curl -v -X GET 'http://localhost:6000/files?api-version=2024-10-02-preview&identifier=test-identifier'
```

Sample Response: 

```shell
< HTTP/1.1 200 OK
< Content-Type: application/json
< Date: Sat, 02 Nov 2024 12:42:30 GMT
< Content-Length: 160
<
{"value":[{"name":"README2.md","sizeInBytes":133,"lastModifiedAt":"2024-11-02T12:33:05.677209683Z","contentType":"text/markdown; charset=utf-8","type":"File"}]}

```

### Get a specific session file of a session 

```shell
curl -v -X GET "http://localhost:6000/files/README2.md?api-version=2024-10-02-preview&identifier=test-identifier"
```

Sample Response: 

```shell
< HTTP/1.1 200 OK
< Content-Type: application/json
< Date: Sat, 02 Nov 2024 12:42:56 GMT
< Content-Length: 148
{"name":"README2.md","sizeInBytes":133,"lastModifiedAt":"2024-11-02T12:33:05.677209683Z","contentType":"text/markdown; charset=utf-8","type":"File"}
```

### Delete a specific session file of a session 

```shell
curl -v -X DELETE "http://localhost:6000/files/README2.md?api-version=2024-10-02-preview&identifier=test-identifier"
```

Sample Response: 

```shell
< HTTP/1.1 204 No Content
< Content-Type: application/json
```