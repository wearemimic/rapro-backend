#!/bin/bash

echo "🔥 Starting RetirementAdvisorPro stack..."
set -e

echo "🚀 Cleaning Vue frontend environment..."

cd frontend || { echo "❌ 'frontend' directory not found"; exit 1; }

rm -rf node_modules package-lock.json dist
echo "✅ Removed node_modules, package-lock.json, and dist"

echo "📦 Installing dependencies..."
npm install

# Ensure we're in the root dir
cd "$(dirname "$0")"

# Function to check if a port is in use and kill the process if it is
check_port() {
  local port=$1
  local pid
  if pid=$(lsof -ti :$port); then
    echo "❌ Port $port is already in use by process $pid."
    echo "Killing process $pid..."
    kill -9 $pid
    echo "✅ Process $pid killed. Port $port is now free."
  else
    echo "✅ Port $port is free."
  fi
}

# Check if specific ports are free before proceeding
PORTS=(3000 8000)  # Example ports, change as needed
for PORT in "${PORTS[@]}"; do
  check_port $PORT
  echo "---"
done

# Function to check if Docker daemon is running
check_docker() {
  if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker daemon is not running. Attempting to start Docker..."
    open --background -a Docker
    # Wait for Docker to start
    while ! docker info > /dev/null 2>&1; do
      sleep 1
    done
    echo "✅ Docker daemon is now running."
  else
    echo "✅ Docker daemon is running."
  fi
}

# Check if Docker daemon is running before proceeding
check_docker

# Build and run containers
echo "🚀 Building and starting Docker containers..."
docker compose -f ../docker/docker-compose.yml up --build


# add in migrations to create the tables
# python manage.py migrate