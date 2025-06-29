
sudo chmod 666 /dev/ttyS1
sudo usermod -aG dialout user

# python3 -m venv /home/user/service/PLC/plcenv
# sudo chmod 777 -R /home/user/service/PLC/plcenv/bin
# source /home/user/service/PLC/plcenv/bin/activate
# cd /home/user/service/PLC
# pip install --no-index --find-links=./wheelhouse --upgrade -r requirements.txt || true

# cd /home/user/service

# SCRIPT_DIR="$(dirname "$0")"


# TARGET_SCRIPT="$SCRIPT_DIR/webUI/install_ntpdate.sh"

# sudo chmod +x "$TARGET_SCRIPT"

# "$TARGET_SCRIPT"


# 設定各個虛擬環境
declare -A services=(
    ["PLC"]="/home/user/service/PLC/plcenv"
    ["webUI"]="/home/user/service/webUI/webvenv"
    ["RestAPI"]="/home/user/service/RestAPI/apienv"
    ["modbus_proxy"]="/home/user/service/modbus_proxy/venv"
    ["snmp"]="/home/user/service/snmp/snmpvenv"
    ["RedFish"]="/home/user/service/redfish-server/redfish_venv"
)

declare -A service_scripts=(
    ["PLC"]="/home/user/service/PLC/plc_service.sh"
    ["webUI"]="/home/user/service/webUI/webui_service.sh"
    ["RestAPI"]="/home/user/service/RestAPI/restapi.sh"
    ["modbus_proxy"]="/home/user/service/modbus_proxy/modbusProxy_service.sh"
    ["snmp"]="/home/user/service/snmp/snmp_service.sh"
    ["RedFish"]="/home/user/service/redfish-server/redfish_start.sh"
)

# 創建 venv（如果不存在）
for service in "${!services[@]}"; do
    VENV_PATH="${services[$service]}"
    SCRIPT_PATH="${service_scripts[$service]}"
    
    if [ ! -d "$VENV_PATH" ]; then
        echo "虛擬環境 $VENV_PATH 不存在，執行 $SCRIPT_PATH 來創建..."
        sudo chmod +x "$SCRIPT_PATH" && "$SCRIPT_PATH"
    else
        echo "虛擬環境 $VENV_PATH 已存在，跳過創建..."
    fi
done

# 安裝 wheelhouse 內的 WHL 套件（不管 venv 是否存在都執行）
for service in "${!services[@]}"; do
    VENV_PATH="${services[$service]}"
    sudo chmod 777 -R "$VENV_PATH/bin"
    source "$VENV_PATH/bin/activate"
    cd "$(dirname "$VENV_PATH")"
    echo "正在安裝 $service 依賴..."
    pip install --no-index --find-links=./wheelhouse --upgrade -r requirements.txt || true
    deactivate
done


# 執行相關腳本
cd /home/user/service
SCRIPT_DIR="$(dirname "$0")"

TARGET_SCRIPT="$SCRIPT_DIR/webUI/install_ntpdate.sh"
sudo chmod +x "$TARGET_SCRIPT" && "$TARGET_SCRIPT"

# TARGET_SCRIPT="$SCRIPT_DIR/new_user_sh/disable_onboard.sh"
# sudo chmod +x "$TARGET_SCRIPT" && "$TARGET_SCRIPT"


###上傳後降低資料夾權限
sudo chown -R user:user /home/user/service

###複製nginx default進入電腦
# Copy the default Nginx configuration to /etc/nginx/sites-available/
sudo cp /home/user/service/nginx/config/default /etc/nginx/sites-available/default
sudo cp /home/user/service/nginx/config/nginx.conf /etc/nginx/

### 暫時刪除資料庫
sudo rm -rf /home/user/service/redfish-server/sidecar-redfish/instance/mydb.sqlite
sudo rm -rf /home/user/service/redfish-server/instance/mydb.sqlite
# sudo systemctl daemon-reload
# sudo systemctl restart plc
# sudo systemctl restart modbusProxy
# sudo systemctl restart snmp
# sudo systemctl restart restapi
# #順序很重要
# sudo systemctl restart webui

# sudo systemctl restart nginx
