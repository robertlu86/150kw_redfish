SERVICE_NAME=sidecar-redfish.service
SYSTEMD_PATH=/etc/systemd/system/$SERVICE_NAME


sudo chmod 644 $SYSTEMD_PATH
sudo systemctl daemon-reload
sudo systemctl start $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME
sudo systemctl status $SERVICE_NAME
#deactivate
