# Use the latest Python Code Interpreter base image from https://mcr.microsoft.com/v2/k8se/services/codeinterpreter-base/tags/list 
# The versioning convention is <code-interpreter-version>-python<python-version>-base.  
# This image includes the BYOC proxy and entrypoint.
# Update the <code-interpreter-version> and <python-version> below accordingly
FROM mcr.microsoft.com/k8se/services/codeinterpreter-base:<code-interpreter-version>-python<python-version>-base

# -------------------- [ Step-1 Complete OS package installations as root ] -------------------
# No additional packages required for this as of now

#  --------------- [ Step-2 Juypter kernel installation as ubuntu user ] ---------------
USER ubuntu
WORKDIR /home/ubuntu

# => NOTE: No need to install Python as it is already available in the base image

# copy the requirements file
COPY --chown=ubuntu requirements.txt /home/ubuntu/requirements.txt

# Install Additional Python packages
RUN /home/ubuntu/snenv/bin/pip3  install --no-cache-dir -r /home/ubuntu/requirements.txt

# -------------------- [Step-3 Set couple of required parameters as root user] -------------------
USER root

# copy codeInterpreterConf.yaml file
COPY codeInterpreterConf.yaml /app/codeInterpreterConf.yaml
ENV CODE_INTERPRETER_CONFIG_FILE_PATH="/app/codeInterpreterConf.yaml"

ENV CODE_INTERPRETER_KERNEL_NAME="python3"
ENV ENABLE_EGRESS="1"


# Set working directory to ensure HTTP server is started in the correct directory
WORKDIR /app
