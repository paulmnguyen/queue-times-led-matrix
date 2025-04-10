#!/bin/bash

# Easy starter script for Queue Times LED Matrix
# Ensures .env exists and runs the script with required permissions

# Get the absolute path to the repository directory
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

# Check if .env exists, create from example if it doesn't
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Created default .env file. Edit it to customize settings."
fi

# Install dependencies if needed
if [ "$1" == "--install" ]; then
    echo "Installing Python dependencies..."
    pip3 install -r requirements.txt
    echo "Dependencies installed."
    shift # Remove the --install argument
fi

# Print helpful message
echo "Starting Queue Times LED Matrix..."
echo "Press Ctrl+C to stop."

# Start the script with sudo (required for LED matrix GPIO access)
# Pass all command line arguments directly to the script
sudo -E python3 queue-times.py "$@"
