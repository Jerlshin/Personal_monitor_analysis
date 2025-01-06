#!/bin/bash

# Build the Docker images
docker-compose -f docker-compose.yml build

# Start the services
docker-compose -f docker-compose.yml up -d

echo "Django application is running at http://localhost:8000"

