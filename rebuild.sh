#!/bin/bash

# Check if script is run with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo"
    exit 1
fi

# Container name and port
CONTAINER_NAME="document-search"
PORT=5000

# Function to check and clear Docker containers using the port
clear_docker_port() {
    local containers=$(docker ps -q --filter "publish=$PORT")
    if [ ! -z "$containers" ]; then
        echo "Found Docker containers using port $PORT. Stopping them..."
        docker stop $containers
        docker rm $containers
    fi
}

# Function to check and clear system processes using the port
clear_system_port() {
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
        echo "Port $PORT is in use by system process. Killing process..."
        sudo lsof -ti :$PORT | xargs sudo kill -9
        sleep 2
    fi
}

# Clear any existing containers with our name
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Stopping container: ${CONTAINER_NAME}"
    docker stop ${CONTAINER_NAME}
    echo "Removing container: ${CONTAINER_NAME}"
    docker rm ${CONTAINER_NAME}
fi

# Clear port from both Docker and system processes
clear_docker_port
clear_system_port

# Build with timestamp to bust cache
echo "Building new image..."
docker build -t document-search -f develop.Dockerfile .

# Wait a moment to ensure port is fully cleared
sleep 2

# Run the new container
echo "Starting new container..."
docker run -d \
    --name ${CONTAINER_NAME} \
    -p ${PORT}:${PORT} \
    -v $(pwd)/.env:/app/.env \
    document-search

# Verify container is running
if docker ps | grep -q ${CONTAINER_NAME}; then
    echo "Container started successfully!"
else
    echo "Container failed to start. Check logs with: docker logs ${CONTAINER_NAME}"
fi

echo "Rebuild complete!"