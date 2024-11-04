# Use code-interpreter base image and provide a custom kernel, set environment variables etc.
# Uses ijava kernel: https://github.com/SpencerPark/IJava?tab=readme-ov-file#installing

# Pull latest base image from here https://mcr.microsoft.com/v2/k8se/services/codeinterpreter-base/tags/list
FROM mcr.microsoft.com/k8se/services/codeinterpreter-base:0.0.3-ubuntu24.04


# -------------------- [ Step-1 Complete OS package installations as root ] -------------------
USER root

RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    unzip \
    && rm -rf /var/lib/apt/lists/* /tmp/* \
    && apt-get clean

#  --------------- [ Step-2 Juypter kernel installation as ubuntu user ] ---------------
USER ubuntu
ENV HOME="/home/ubuntu"
WORKDIR $HOME

# Install the IJava kernel
RUN wget -q https://github.com/SpencerPark/IJava/releases/download/v1.3.0/ijava-1.3.0.zip && \
    unzip ijava-1.3.0.zip && \
    # Activate the virtual environment for Python and install the IJava kernel
    . snenv/bin/activate && \
    python3 install.py --sys-prefix && \
    # remove unnecessary files
    rm -rf ijava-1.3.0.zip ijava install.py

# Set right permissions for ubuntu user
RUN chown -R ubuntu $HOME

# Set the environment variable for Java kernel
ENV JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"
ENV IJAVA_TIMEOUT="30 SECONDS"

# -------------------- [Step-3 Set couple of required parameters as root user] -------------------
USER root

# copy codeInterpreterConf.yaml file
COPY codeInterpreterConf.yaml /app/codeInterpreterConf.yaml
ENV CODE_INTERPRETER_CONFIG_FILE_PATH="/app/codeInterpreterConf.yaml"

# Set to true or yes or y or 1, if require egress
ENV ENABLE_EGRESS="1"
ENV CODE_INTERPRETER_KERNEL_NAME="java"

# Set working directory to ensure HTTP server is started in the correct directory
WORKDIR /app