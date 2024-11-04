# Overview
This provides sample documentation for API versions up to and including `2024-08-02-preview`.

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

Sample Response: 

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
```

Sample Response: 

```shell
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

```

Sample Response: 

```shell
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

```

Sample Response: 

```shell
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

```

Sample Response: 

```shell
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

```

Sample Response: 

```shell
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

```

Sample Response: 

```shell
< HTTP/1.1 200 OK
< Content-Type: application/json
< Date: Sat, 02 Nov 2024 12:12:59 GMT
< Content-Length: 40
<
{"message": "file deleted successfully"}
```