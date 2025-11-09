FROM mcr.microsoft.com/devcontainers/python:3.12

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Install PostgreSQL client
RUN apt-get update && apt-get install -y postgresql-client

# Install Python development tools
RUN pip install --upgrade pip setuptools wheel

# Create workspace directory
WORKDIR /workspace
