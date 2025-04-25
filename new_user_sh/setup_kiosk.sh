#!/bin/bash

# 創建一個名為kiosk的新用戶
sudo adduser kiosk

sudo apt update || true 
sudo apt install -y chromium-browser gnome-shell-extensions gnome-shell-extension-manager || true
sudo mkdir -p /usr/share/gnome-shell/extensions
sudo cp -r /home/user/service/new_user_sh/disable-gestures-2021@verycrazydog.gmail.com /usr/share/gnome-shell/extensions/
sudo cp -r /home/user/service/new_user_sh/block-caribou-36@lxylxy123456.ercli.dev /usr/share/gnome-shell/extensions/

# 配置自動登錄
# 編輯GDM配置文件，設置自動登錄用戶為kiosk
# 修改AutomaticLoginEnable設置
if grep -q "^#\s*AutomaticLoginEnable\s*=" /etc/gdm3/custom.conf; then
  sudo sed -i 's/^#\s*AutomaticLoginEnable\s*=.*/AutomaticLoginEnable=true/' /etc/gdm3/custom.conf
else
  if grep -q "^AutomaticLoginEnable\s*=" /etc/gdm3/custom.conf; then
    sudo sed -i 's/^AutomaticLoginEnable\s*=.*/AutomaticLoginEnable=true/' /etc/gdm3/custom.conf
  else
    echo "AutomaticLoginEnable=true" | sudo tee -a /etc/gdm3/custom.conf
  fi
fi

# 修改AutomaticLogin設置
if grep -q "^#\s*AutomaticLogin\s*=" /etc/gdm3/custom.conf; then
  sudo sed -i 's/^#\s*AutomaticLogin\s*=.*/AutomaticLogin=kiosk/' /etc/gdm3/custom.conf
else
  if grep -q "^AutomaticLogin\s*=" /etc/gdm3/custom.conf; then
    sudo sed -i 's/^AutomaticLogin\s*=.*/AutomaticLogin=kiosk/' /etc/gdm3/custom.conf
  else
    echo "AutomaticLogin=kiosk" | sudo tee -a /etc/gdm3/custom.conf
  fi
fi

# 修改WaylandEnable設置
if grep -q "^#\s*WaylandEnable\s*=" /etc/gdm3/custom.conf; then
  sudo sed -i 's/^#\s*WaylandEnable\s*=.*/WaylandEnable=false/' /etc/gdm3/custom.conf
else
  if grep -q "^WaylandEnable\s*=" /etc/gdm3/custom.conf; then
    sudo sed -i 's/^WaylandEnable\s*=.*/WaylandEnable=false/' /etc/gdm3/custom.conf
  else
    echo "WaylandEnable=false" | sudo tee -a /etc/gdm3/custom.conf
  fi
fi


# 創建自動啟動配置文件
sudo -u kiosk mkdir -p /home/kiosk/.config/autostart
sudo bash -c 'cat <<EOF > /home/kiosk/.config/autostart/kiosk.desktop
[Desktop Entry]
Type=Application
Exec=bash -c "gnome-extensions enable disable-gestures-2021@verycrazydog.gmail.com && gnome-extensions enable block-caribou-36@lxylxy123456.ercli.dev && sleep 2 && chromium-browser --kiosk --noerrdialogs --no-first-run --start-maximized --disable-infobars --enable-touch-events --enable-viewport --incognito --disable-pinch --disable-web-security --ignore-certificate-errors --disable-session-crashed-bubble --disable-features=IsolateOrigins,site-per-process,SwipeNavigation https://127.0.0.1/?username=kiosk"
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name[en_US]=Kiosk
Name=Kiosk
Comment[en_US]=
Comment=
EOF'


sudo bash -c 'cat <<EOF > /home/kiosk/.xprofile
xset s off
xset -dpms
xset s noblank

gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout 0
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-battery-timeout 0
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type "nothing"
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-battery-type "nothing"
gsettings set org.gnome.desktop.screensaver lock-enabled false
gsettings set org.gnome.settings-daemon.plugins.power power-saver-profile-on-low-battery false
gsettings set org.gnome.desktop.session idle-delay 0
EOF'


sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target

# 可選：修改GRUB配置以禁用啟動畫面
sudo bash -c 'sed -i "s/GRUB_CMDLINE_LINUX_DEFAULT=.*/GRUB_CMDLINE_LINUX_DEFAULT=\"quiet splash vt.handoff=7 loglevel=3\"/" /etc/default/grub'


# 更新GRUB配置
sudo update-grub

# 重新啟動系統以應用更改
# sudo reboot