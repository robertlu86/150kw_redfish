#!/bin/bash
# setup_and_run.sh
#更改LF
sudo chmod 666 /dev/ttyS1
sudo usermod -aG dialout user

# sudo apt update
# sudo apt install -y onboard

# 更新 Journal 设置
sudo bash -c 'cat > /etc/systemd/journald.conf <<EOF
[Journal]
SystemMaxUse=500M
SystemKeepFree=100M
SystemMaxFileSize=100M
EOF'

#重新启动 systemd-journald 服务以应用新的配置
sudo systemctl restart systemd-journald

# Install Nginx (assuming sudo privileges are available)
sudo apt update
sudo apt install curl
sudo apt install -y nginx

# Copy the default Nginx configuration to /etc/nginx/sites-available/
sudo cp /home/user/service/nginx/config/default /etc/nginx/sites-available/default
sudo cp /home/user/service/nginx/config/nginx.conf /etc/nginx/

# Define the path to the script that needs to be executed
SCRIPT_DIR="$(dirname "$0")"

#Modbus Proxy Server
TARGET_SCRIPT="$SCRIPT_DIR/modbus_proxy/modbusProxy_service.sh"


# Change the permissions to make the script executable
chmod +x "$TARGET_SCRIPT"

# Execute the script
"$TARGET_SCRIPT"

# Optional: Check the exit status of the executed script
if [ $? -eq 0 ]; then
    echo "Script executed successfully"
else
    echo "Script failed with exit status $?"
fi

#SNMP Service
TARGET_SCRIPT="$SCRIPT_DIR/snmp/snmp_service.sh"

# Change the permissions to make the script executable
chmod +x "$TARGET_SCRIPT"

# Execute the script
"$TARGET_SCRIPT"

# Optional: Check the exit status of the executed script
if [ $? -eq 0 ]; then
    echo "Script executed successfully"
else
    echo "Script failed with exit status $?"
fi

#refish Service
TARGET_SCRIPT="$SCRIPT_DIR/redfish-server/redfish_start.sh"

# Change the permissions to make the script executable
chmod +x "$TARGET_SCRIPT"

# Execute the script
"$TARGET_SCRIPT"

# Optional: Check the exit status of the executed script
if [ $? -eq 0 ]; then
    echo "Script executed successfully"
else
    echo "Script failed with exit status $?"
fi

#network
TARGET_SCRIPT="$SCRIPT_DIR/network.sh"

# Change the permissions to make the script executable
chmod +x "$TARGET_SCRIPT"

# Execute the script
"$TARGET_SCRIPT"

# Optional: Check the exit status of the executed script
if [ $? -eq 0 ]; then
    echo "Script executed successfully"
else
    echo "Script failed with exit status $?"
fi

#RestAPI Service
TARGET_SCRIPT="$SCRIPT_DIR/RestAPI/restapi.sh"

# Change the permissions to make the script executable
chmod +x "$TARGET_SCRIPT"

# Execute the script
"$TARGET_SCRIPT"

# Optional: Check the exit status of the executed script
if [ $? -eq 0 ]; then
    echo "Script executed successfully"
else
    echo "Script failed with exit status $?"
fi

#PLC Service
TARGET_SCRIPT="$SCRIPT_DIR/PLC/plc_service.sh"


# Change the permissions to make the script executable
chmod +x "$TARGET_SCRIPT"

# Execute the script
"$TARGET_SCRIPT"

# Optional: Check the exit status of the executed script
if [ $? -eq 0 ]; then
    echo "Script executed successfully"
else
    echo "Script failed with exit status $?"
fi

#WebUI Service
TARGET_SCRIPT="$SCRIPT_DIR/webUI/webui_service.sh"


# Change the permissions to make the script executable
chmod +x "$TARGET_SCRIPT"

# Execute the script
"$TARGET_SCRIPT"

# Optional: Check the exit status of the executed script
if [ $? -eq 0 ]; then
    echo "Script executed successfully"
else
    echo "Script failed with exit status $?"
fi
