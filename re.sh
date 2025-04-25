#增加權限
sudo chmod 666 /dev/ttyS1
sudo usermod -aG dialout user


# 回到原本的 service 資料夾
cd /home/user/service


sudo systemctl daemon-reload
sudo systemctl restart plc.service
sudo systemctl restart modbusProxy.service
sudo systemctl restart snmp.service
sudo systemctl restart restapi.service
sudo systemctl restart webui.service
sudo systemctl restart nginx.service

sudo systemctl status plc webui nginx 
