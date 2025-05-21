#!/bin/bash

# Define variables
SERVICE_NAME="redfish"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
EXEC_START="/home/user/service/refish-server/refish-server/rf-serv"
WORKING_DIR="/home/user/service/refish-server/refish-server"
USER_NAME="user"

# Create the systemd service file
sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Run rf-serv on startup
After=network.target

[Service]
Type=simple
ExecStart=$EXEC_START
WorkingDirectory=$WORKING_DIR
User=$USER_NAME
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd configuration
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable $SERVICE_NAME.service

# Start the service immediately
sudo systemctl start $SERVICE_NAME.service

# Check the status of the service
sudo systemctl status $SERVICE_NAME.service
