## Python code interpreter execution response headers (Preview)

When executing code using **Python code interpreter sessions** in Azure Container Apps dynamic sessions, the service returns additional HTTP response headers that provide **informational execution timing and session metadata** that can help you understand how a code execution request was processed by the service.

> **Note**
>
> These headers are returned **only** for Python code interpreter execution requests. They are not returned for file operations, session deletion, or custom container sessions.

---

### Execution timing headers

The following headers describe service-side execution timing for a Python code execution request.

| Header name | Description |
|------------|-------------|
| **`X-Ms-Overall-Execution-Time`** | Total execution time for the request, calculated as the difference between when execution begins and when execution ends (`endExecutionTime - beginExecutionTime`). |
| **`X-Ms-Preparation-Time`** | Time spent preparing the execution environment prior to allocating compute resources (for example, environment setup and initialization). |
| **`X-Ms-Execution-Request-Time`** | Time spent handling the execution request before the service begins processing the execution response, calculated as `beginProcessResponseTime - beginRequestTime`. |
| **`X-Ms-Execution-Read-Response-Time`** | Time spent reading and processing the execution response after code execution completes, calculated as `endProcessResponseTime - beginProcessResponseTime`. |

---

### Session metadata headers

The following headers provide metadata about the interpreter session used to execute the request.

| Header name | Description |
|------------|-------------|
| **`X-Ms-Session-Guid`** | Unique identifier for the interpreter session associated with this execution request. This value also corresponds to the underlying pod name used by the service. |

---

### Important considerations

- Timing values represent **service-side measurements** and may overlap across execution phases.
- Custom container sessions do not emit these headers.
