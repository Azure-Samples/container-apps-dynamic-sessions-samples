# Use code-interpreter base image and provide a custom kernel, set environment variables etc.
# Uses ijavascript kernel: https://github.com/n-riesco/ijavascript

# Pull latest base image from here https://mcr.microsoft.com/v2/k8se/services/codeinterpreter-base/tags/list
FROM mcr.microsoft.com/k8se/services/codeinterpreter-base:0.0.3-ubuntu24.04

# -------------------- [ Step-1 Complete OS package installations as root ] -------------------
# No additional packages required for this as of now


#  --------------- [ Step-2 Juypter kernel installation as ubuntu user ] ---------------
USER ubuntu
ENV HOME="/home/ubuntu"
WORKDIR $HOME

ENV NVM_DIR="$HOME/.nvm"
ENV NODE_VERSION="20.17.0"
ENV NODE_PATH="$NVM_DIR/versions/node/v$NODE_VERSION/bin"
ENV PATH="$NODE_PATH:$PATH"

# Install NVM, Node.js 20
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash \
    && export NVM_DIR="$HOME/.nvm" \
    && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" \
    && [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion" \
    && nvm install $NODE_VERSION \
    && nvm use $NODE_VERSION \
    && nvm alias default $NODE_VERSION

# Install ijavascript kernel for Jupyter
RUN npm install -g ijavascript \
    && ijsinstall --spec-path=full

# Install Additional npm packages
COPY --chown=ubuntu package.json /home/ubuntu/package.json
RUN npm install

# Set right permissions for ubuntu user
RUN chmod -R a+rw ${HOME}/.local && \
    mkdir -p ${HOME}/.cache && \
    chown -R ubuntu ${HOME}/.cache && \
    mkdir -p "/home/ubuntu/.npm" && \
    chown -R ubuntu "/home/ubuntu/.npm"

# -------------------- [Step-3 Set couple of required parameters as root user] -------------------
USER root

# copy codeInterpreterConf.yaml file
COPY codeInterpreterConf.yaml /app/codeInterpreterConf.yaml
ENV CODE_INTERPRETER_CONFIG_FILE_PATH="/app/codeInterpreterConf.yaml"

# Set to true or yes or y or 1, if require egress
ENV ENABLE_EGRESS="1"
ENV CODE_INTERPRETER_KERNEL_NAME="javascript"

# Set working directory to ensure HTTP server is started in the correct directory
WORKDIR /app