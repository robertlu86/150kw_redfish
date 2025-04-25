#!/bin/bash

# 指定目標資料夾
TARGET_DIR=/home/user/service/RestAPI
SERVICE_NAME=restapi.service
VENV_PATH=$TARGET_DIR/apienv
SCRIPT_PATH=$TARGET_DIR/app.py
SYSTEMD_PATH=/etc/systemd/system/$SERVICE_NAME

# 進入目標資料夾
cd $TARGET_DIR

#安裝python3-venv
sudo apt install python3.10-venv

# 建立 venv 環境
python3 -m venv $VENV_PATH

# 啟動 virtual environment
source $VENV_PATH/bin/activate

# 安裝 requirements.txt 中的依賴
pip install --no-index --find-links=./wheelhouse --upgrade -r requirements.txt || true


# 創建 service 檔案
cat <<EOL | sudo tee $SYSTEMD_PATH
[Unit]
Description=RestAPI Service
After=network.target

[Service]
User=user
Group=user
WorkingDirectory=$TARGET_DIR
Environment="PATH=$VENV_PATH/bin"
ExecStart=$VENV_PATH/bin/python3 $SCRIPT_PATH

# Restart options
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

# 設定檔案權限
sudo chmod 644 $SYSTEMD_PATH

# 重新載入 systemd 管理設定檔
sudo systemctl daemon-reload

# 啟動 service
sudo systemctl start $SERVICE_NAME

# 設定 service 開機自動啟動
sudo systemctl enable $SERVICE_NAME

# 顯示 service 狀態
sudo systemctl status $SERVICE_NAME

# 退出 virtual environment
deactivate
