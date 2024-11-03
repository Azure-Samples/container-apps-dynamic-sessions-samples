# Stage 1: Use code-interpreter base image and provide a custom kernel, set environment variables etc.
# Jupyter kernel: https://github.com/zabirauf/icsharp

# Uses icsharp kernel installation: https://github.com/3Dcube/docker-jupyter-icsharp/blob/master/Dockerfile
# and, https://github.com/zabirauf/icsharp/wiki/Install-on-Unix-(Debian-7.8)

# Pull latest base image from here https://mcr.microsoft.com/v2/k8se/services/codeinterpreter-base/tags/list
FROM mcr.microsoft.com/k8se/services/codeinterpreter-base:0.0.3-ubuntu24.04

# -------------------- [ Step-1 Complete OS package installations as root ] -------------------
USER root

ENV MONO_VERSION="5.0.1.1"

RUN apt-get update && apt-get install -y \ 
  git \
  && rm -rf /var/lib/apt/lists/* /tmp/* \
  && apt-get clean

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF && \
  echo "deb http://download.mono-project.com/repo/debian jessie/snapshots/$MONO_VERSION main" > /etc/apt/sources.list.d/mono-official.list \
  && apt-get update \
  && apt-get install -y binutils mono-devel ca-certificates-mono fsharp mono-vbnc nuget referenceassemblies-pcl \
  && rm -rf /var/lib/apt/lists/* /tmp/* \
  && apt-get clean

ENV CSHARP_DIR="/home/ubuntu/icsharp"

RUN mkdir -p ${CSHARP_DIR} && chown -R ubuntu ${CSHARP_DIR}

#  --------------- [ Step-2 Juypter kernel installation as ubuntu user ] ---------------
USER ubuntu

WORKDIR ${CSHARP_DIR}

RUN git clone --recursive https://github.com/zabirauf/icsharp.git ${CSHARP_DIR}

# # Build scriptcs
RUN cd Engine && \
  mozroots --import --sync --quiet &&\
  mono ./.nuget/NuGet.exe restore ./ScriptCs.sln &&\
  mkdir -p artifacts/Release/bin

# Build iCSharp
RUN mozroots --import --sync --quiet &&\
  mono ./.nuget/NuGet.exe restore ./iCSharp.sln &&\
  mkdir -p build/Release/bin &&\
  xbuild ./iCSharp.sln /property:Configuration=Release /nologo /verbosity:normal

# Copy files safely
RUN for line in $(find ./*/bin/Release/*); do cp $line ./build/Release/bin; done

# Install kernel
COPY kernel.json ${CSHARP_DIR}/kernel-spec/kernel.json

# Note: name 'csharp' must match the kernel name in codeInterpreterConf.yaml
# Use shell form of RUN to chain commands
RUN /bin/bash -c "source /home/ubuntu/snenv/bin/activate && jupyter-kernelspec install --user kernel-spec --name csharp"

# -------------------- [Step-3 Set couple of required parameters as root user] -------------------
USER root

# copy codeInterpreterConf.yaml file
COPY codeInterpreterConf.yaml /app/codeInterpreterConf.yaml
ENV CODE_INTERPRETER_CONFIG_FILE_PATH="/app/codeInterpreterConf.yaml"

WORKDIR /app

# Set to true or yes or y or 1, if require egress
ENV ENABLE_EGRESS="1"
ENV CODE_INTERPRETER_KERNEL_NAME="csharp"