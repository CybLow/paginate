#!/bin/bash
# Setup PostgreSQL with pgvector for MCP servers and CocoIndex

set -e

CONTAINER_NAME="opencode-postgres"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

echo "=== OpenCode PostgreSQL Setup ==="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Start Docker first:"
    echo "  sudo systemctl start docker"
    exit 1
fi

# Check if container already exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Container '${CONTAINER_NAME}' already exists."

    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo "Container is already running."
    else
        echo "Starting existing container..."
        docker start "${CONTAINER_NAME}"
    fi
else
    echo "Creating new PostgreSQL container with pgvector..."
    docker run -d \
        --name "${CONTAINER_NAME}" \
        -e POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
        -e POSTGRES_USER="${POSTGRES_USER}" \
        -e POSTGRES_DB="${POSTGRES_DB}" \
        -p "${POSTGRES_PORT}:5432" \
        -v opencode-postgres-data:/var/lib/postgresql/data \
        pgvector/pgvector:pg16

    echo "Waiting for PostgreSQL to be ready..."
    sleep 5

    # Enable pgvector extension
    echo "Enabling pgvector extension..."
    docker exec "${CONTAINER_NAME}" psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -c "CREATE EXTENSION IF NOT EXISTS vector;"
fi

echo ""
echo "=== PostgreSQL is ready! ==="
echo ""
echo "Connection details:"
echo "  Host:     localhost"
echo "  Port:     ${POSTGRES_PORT}"
echo "  User:     ${POSTGRES_USER}"
echo "  Password: ${POSTGRES_PASSWORD}"
echo "  Database: ${POSTGRES_DB}"
echo ""
echo "DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:${POSTGRES_PORT}/${POSTGRES_DB}"
echo ""
echo "To stop:  docker stop ${CONTAINER_NAME}"
echo "To start: docker start ${CONTAINER_NAME}"
echo "To remove: docker rm -f ${CONTAINER_NAME} && docker volume rm opencode-postgres-data"
