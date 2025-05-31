#!/bin/bash

echo "Starting containers..."
docker-compose up -d

echo "Waiting for database to be ready..."
sleep 10

echo "Creating database tables..."
docker exec -it booking_backend bash -c "PYTHONPATH=/app python create_tables.py"

echo "Database initialization completed!" 