# Overview

This BYOC C# sample relies on [.NET Interactive](https://github.com/dotnet/interactive), which is a fully supported Jupyter kernel that can be used with Jupyter Notebook, JupyterLab, and other Jupyter frontends. 

Azure Container Apps itself supports any Linux-based x86-64 (linux/amd64) container image. The BYOC base image's target platform is `linux/amd64`.

## Build and deploy the Docker image to Azure Container Registry

### macOS - Apple silicon
To turn a Docker image you build on macOS (`arm64`) into an image that will run on any x86-64 Linux host (`linux/amd64`), you can rely on Docker BuildKit (already bundled with Docker Desktop) and QEMU user-mode emulation.

```bash
# use --load instead of --push to get the image locally
docker buildx --platform linux/amd64 -t reponame.azurecr.io/imagename:1.0.0 --push .
```

## Create a session pool

```
az containerapp sessionpool create \
    --name csharp-pool \            
    --resource-group csharp-custom-container-rg \
    --environment csharp-custom-container-aca-env \
    --registry-server reponame.azurecr.io \
    --registry-username username \
    --registry-password **** \
    --container-type CustomContainer \
    --image reponame.azurecr.io/imagename:1.0.0 \
    --cpu 0.25 --memory 0.5Gi \
    --target-port 6000 \
    --cooldown-period 300 \
    --network-status EgressDisabled \
    --max-sessions 10 \
    --ready-sessions 5 \
    --location "West US 2"
```

## Troubleshoot the custom container

Check the `/health` endpoint of your custom container with your provisioned Custom Container-based session pool endpoint, an access token, and a session ID.

```bash
TOKEN=$(az account get-access-token \                                                     
--resource https://dynamicsessions.io \
--query accessToken -o tsv)

ID="my-test-session"

POOL="https://<session-pool-name>.<random-string>.<region>.azurecontainerapps.io"

curl -v -H "Authorization: Bearer $TOKEN" "$POOL/health?identifier=$ID" 
```