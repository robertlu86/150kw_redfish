#!/bin/bash


TARGET_DIR=/home/user/service/webUI
SERVICE_NAME=webui.service
VENV_PATH=$TARGET_DIR/webvenv
SCRIPT_PATH=$TARGET_DIR/web/app.py
SYSTEMD_PATH=/etc/systemd/system/$SERVICE_NAME


cd $TARGET_DIR
sudo apt install python3.10-venv
python3 -m venv $VENV_PATH
source $VENV_PATH/bin/activate
pip install --no-index --find-links=./wheelhouse --upgrade -r requirements.txt || true



cat <<EOL | sudo tee $SYSTEMD_PATH
[Unit]
Description=WebUI Service
After=network.target


[Service]
#User=user
WorkingDirectory=$TARGET_DIR
Environment="PATH=$VENV_PATH/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$VENV_PATH/bin/gunicorn --config $TARGET_DIR/web/gunicorn_config.py web.app:app
#ExecStart=$VENV_PATH/bin/python $SCRIPT_PATH
Restart=always
RestartSec=5
StandardOutput=file:/home/user/service/webUI/logfile.log
StandardError=file:/home/user/service/webUI/logfile.log
[Install]
WantedBy=multi-user.target
EOL

sudo chmod 644 $SYSTEMD_PATH
sudo systemctl daemon-reload
sudo systemctl start $SERVICE_NAME
sudo systemctl enable $SERVICE_NAME
sudo systemctl status $SERVICE_NAME
#deactivate
