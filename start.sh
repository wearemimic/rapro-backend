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

# Build and run containers
echo "🚀 Building and starting Docker containers..."
docker compose -f ../docker/docker-compose.yml up --build


# add in migrations to create the tables
# python manage.py migrate