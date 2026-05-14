# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install the package and its dependencies
RUN pip install --no-cache-dir .

# The actual server script will be provided at runtime or copied during a build
# For a generic template, we assume the script is passed as an environment variable
# or placed in a specific location.
ENV SERVER_SCRIPT="server_script.py"
ENV PORT=8080

EXPOSE 8080

# Run the server script
CMD ["sh", "-c", f"python {SERVER_SCRIPT}"]