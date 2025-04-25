#!/bin/bash

# 自動獲取所有 Ethernet 網卡名稱
ETHERNET_INTERFACES=$(nmcli -t -f DEVICE,TYPE device status | grep ethernet | awk -F: '{print $1}')

# 檢查是否有可用的 Ethernet 介面
if [ -z "$ETHERNET_INTERFACES" ]; then
    echo "No Ethernet interfaces found. Please check your system configuration."
    exit 1
fi


declare -A INTERFACE_TO_IDENTITY=(
    ["enp1s0"]="ethernet1"
    ["enp2s0"]="ethernet2"
)


for INTERFACE in $ETHERNET_INTERFACES; do
    IDENTITY_NAME=${INTERFACE_TO_IDENTITY[$INTERFACE]}
    
    if [ -n "$IDENTITY_NAME" ]; then
        CONNECTION_NAME=$(nmcli -t -f NAME,DEVICE connection show | grep ":$INTERFACE" | awk -F: '{print $1}')
        
        if [ -z "$CONNECTION_NAME" ]; then
            echo "No connection found for interface $INTERFACE."
            continue
        fi
        
        echo "Updating connection for interface $INTERFACE to $IDENTITY_NAME..."
        sudo nmcli con mod "$CONNECTION_NAME" connection.id "$IDENTITY_NAME"
        
        if [ $? -ne 0 ]; then
            echo "Failed to rename connection for $INTERFACE."
            continue
        fi
        
        if [ "$IDENTITY_NAME" == "ethernet1" ] && [ "$INTERFACE" == "enp1s0" ]; then
            echo "Configuring ethernet1 with manual IP settings..."
            sudo nmcli con mod "ethernet1" ifname "enp1s0" ipv4.method manual ipv4.addresses "192.168.3.111/24" ipv4.gateway "192.168.3.1" ipv4.dns "8.8.8.8" ipv4.route-metric 200
        fi

        if [ "$IDENTITY_NAME" == "ethernet2" ] && [ "$INTERFACE" == "enp2s0" ]; then
            echo "Configuring ethernet2 with manual IP settings..."
            sudo nmcli con mod "ethernet2" ifname "enp2s0" ipv4.method manual ipv4.addresses "192.168.3.101/24" ipv4.gateway "192.168.3.1" ipv4.dns "8.8.4.4" ipv4.route-metric 100
        fi

        
        sudo nmcli con up "$IDENTITY_NAME"
        
        if [ $? -ne 0 ]; then
            echo "Failed to bring up connection $IDENTITY_NAME."
            continue
        fi
        
        echo "Successfully updated connection for $INTERFACE to $IDENTITY_NAME."
    fi
done



