# Stage 1: Use code-interpreter base image and provide a custom kernel, set environment variables etc.
# Jupyter kernel: https://github.com/dotnet/interactive

# Pull latest base image from here https://mcr.microsoft.com/v2/k8se/services/codeinterpreter-base/tags/list
FROM mcr.microsoft.com/k8se/services/codeinterpreter-base:0.0.7-ubuntu24.04

# -------------------- [ Step-1 Complete OS package installations as root ] -------------------
USER root

# Install .NET 9 SDK: 
# https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu-install
RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common && \
    add-apt-repository -y ppa:dotnet/backports && \
    apt-get update && \
    apt-get install -y dotnet-sdk-9.0 && \
    rm -rf /var/lib/apt/lists/*

#  --------------- [ Step-2 Juypter kernel installation as ubuntu user ] ---------------
USER ubuntu
ENV HOME=/home/ubuntu
WORKDIR $HOME
ENV DOTNET_INTERACTIVE_CLI_TELEMETRY_OPTOUT=1 \ 
    DOTNET_ROLL_FORWARD_TO_PRERELEASE=1       \
    DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1       \ 
    DOTNET_GENERATE_ASPNET_CERTIFICATE=false

# Install .NET Interactive
RUN dotnet tool install --global Microsoft.dotnet-interactive
ENV PATH="$HOME/.dotnet/tools:$PATH"

# .NET Interactive installs three kernels: .net-csharp, .net-fsharp, .net-powershell
RUN dotnet interactive jupyter install

# -------------------- [Step-3 Set couple of required parameters as root user] -------------------
USER root

COPY codeInterpreterConf.yaml /app/codeInterpreterConf.yaml
ENV CODE_INTERPRETER_CONFIG_FILE_PATH="/app/codeInterpreterConf.yaml"
ENV CODE_INTERPRETER_KERNEL_NAME=".net-csharp"

# Set to true or yes or y or 1, if require egress
ENV ENABLE_EGRESS="1"

# Set working directory to ensure HTTP server is started in the correct directory
WORKDIR /app