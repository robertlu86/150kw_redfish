sudo bash -c 'cat <<EOF > /home/kiosk/.config/autostart/onboard.desktop
[Desktop Entry]
Type=Application
Exec=bash -c "gsettings set org.onboard.auto-show enabled false && gsettings set org.onboard layout '/usr/share/onboard/layouts/Phone.onboard' && gsettings set org.onboard.window docking-enabled false && gsettings set org.onboard.icon-palette in-use true && sleep 2 && onboard"
Hidden=true
NoDisplay=true
X-GNOME-Autostart-enabled=false
Name[en_US]=Onboard
Name=Onboard
Comment[en_US]=
Comment=
EOF'
