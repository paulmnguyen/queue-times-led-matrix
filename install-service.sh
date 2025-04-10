#!/bin/bash

# Service installer for Queue Times LED Matrix
# Creates a systemd service for automatic startup

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="queue-times-matrix"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo "Installing Queue Times LED Matrix service..."

# Create service file
cat > /tmp/${SERVICE_NAME}.service << EOF
[Unit]
Description=Queue Times LED Matrix
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=${REPO_DIR}
ExecStart=${REPO_DIR}/start-matrix.sh
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

# Install service file
sudo mv /tmp/${SERVICE_NAME}.service ${SERVICE_FILE}
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}

echo "Service installed! You can start it with:"
echo "sudo systemctl start ${SERVICE_NAME}"
echo
echo "Check status with:"
echo "sudo systemctl status ${SERVICE_NAME}"
echo
echo "To start automatically on boot, run:"
echo "sudo systemctl enable ${SERVICE_NAME}"