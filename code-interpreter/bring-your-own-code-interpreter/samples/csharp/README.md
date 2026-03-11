# C# BYOC

This BYOC C# sample relies on [.NET Interactive](https://github.com/dotnet/interactive), which is a fully supported Jupyter kernel that can be used with Jupyter Notebook, JupyterLab, and other Jupyter frontends. 

Azure Container Apps itself supports any Linux-based x86-64 (linux/amd64) container image. The BYOC base image's target platform is `linux/amd64`.

## Build

### macOS - Apple silicon
To turn a Docker image you build on macOS (`arm64`) into an image that will run on any x86-64 Linux host (`linux/amd64`), you can rely on Docker BuildKit (already bundled with Docker Desktop) and QEMU user-mode emulation.

```bash
# use --load instead of --push to get the image locally
docker buildx build --platform linux/amd64 -t reponame.azurecr.io/imagename:1.0.0 --push .
```

## Test

`api-tests.yaml` is a self-contained [Insomnia](https://insomnia.rest) workspace to hit your locally running custom container. It covers the main `/executions` and `/files` endpoints

### Quick Start

1. **Run your container locally** (the YAML assumes `http://localhost:6000` – change if needed).  
2. **Open Insomnia (v11+ recommended).**  
3. **Import** the `api-tests.yaml` file  
   - `Workspace → Import/Export → Import Data → From File`  
4. **Select an environment** (top left dropdown) and edit only these fields:  

   ```yaml
   base: http://localhost:6000   # your API base
   token: not-needed-locally     # or real token if running remotely in ACA Dynamic Sessions

## Deploy

.NET Interactive kernel supports asynchronous code execution. However, your custom container resource allocation should have at least 1 CPU core and 2 Gi of memory in order to avoid websocket connection issues between the BYOC REST API proxy and the kernel instances.