# Frequently Asked Questions

## Why do I need a Custom Container-based Dynamic Session Pool if I'm already using the Built-in Code Interpreter-based Dynamic Session Pool?
The Built-in Code Interpreter-based Dynamic Session Pool is optimized for performance and scalability, making it ideal for most code interpreter use cases for languages that we support. However, there are additional benefits to using the Custom Container-based session pool, especially for specific scenarios where customization and flexibility are needed. You can read more about these advantages [here](./README.md#overview).

## Can I use a Private ACR for my Custom Image instead of a Public Registry?
Yes, you can use a Private Azure Container Registry (ACR) by configuring the Managed Identity of your Custom Container-based session pool. During session pool provisioning, provide the necessary details for ACR access. Using a private ACR is recommended for production scenarios to enhance security and control over publicly available images.

## Can I Extend Code Interpreter Scenarios for Languages Not Included in the Samples?
Yes, you can. The BYOC REST API Proxy included in the base BYOC setup is independent of the specific Jupyter Kernel language runtime. You are free to use any kernel that supports the Jupyter Messaging Protocol, as explained [here](./README.md#concepts), or even create a custom kernel if needed. For additional guidance, see the information provided [here](./samples/README.md).

## What is the Release Cadence for Base BYOC Images?
There is no fixed release cadence for base BYOC images, but updates are published as needed for bug fixes or security patches. Internally, these base BYOC container images are also used with slight modifications for first party Built-in Code Interpreter scenarios. To pull the latest BYOC base image, use this [link](https://mcr.microsoft.com/v2/k8se/services/codeinterpreter-base/tags/list).

## What Changes Are Needed to Transition from the Built-in Code Interpreter to a Custom Container-based Dynamic Session Pool?
A detailed guide on transitioning from the Built-in Code Interpreter to a Custom Container-based Dynamic Session Pool is available [here](./changes-from-code-interpreter-to-custom-interpreter.md).

## What’s the Best Way to Get Help or Support for Custom Container-based Dynamic Session Pool on the Base BYOC Image?
For support, refer to the [support documentation](../SUPPORT.md). When raising an issue in the ACA public GitHub project, include `[Sessions]` and `[BYOC]` in the title to ensure it’s routed to the appropriate team.