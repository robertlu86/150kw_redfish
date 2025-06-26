import platform
import subprocess
import psutil

def set_ntp(enable: bool, ntp_server: str):
    """
    跨平台啓用或停用本機 NTP 同步。
    :param enable: True=啓用, False=停用
    [*] 目前僅支援 ntp.ubuntu.com
    """
    os_name = platform.system()
    if os_name == "Windows":
        print("正在處理 Windows 系統的 NTP 設定...")
        svc = psutil.win_service_get("W32Time")
        if enable:
            subprocess.run(["sc", "config", "W32Time", "start=", "auto"], check=True)
            subprocess.run(["sc", "start",  "W32Time"],               check=True)

            print("已啟用 Windows Time 服務並設為自動啟動")
        else:
            subprocess.run(["sc", "stop",   "W32Time"],               check=True)
            subprocess.run(["sc", "config", "W32Time", "start=", "disabled"], check=True)
            print("已停止並設為停用的 W32Time 服務")

    elif os_name == "Linux":
        print("正在處理 Linux 系統的 NTP 設定...")
        mode = "true" if enable else "false"
        # 使用 timedatectl 控制 systemd-timesyncd
        subprocess.run(["/usr/bin/sudo", "timedatectl", "set-ntp", mode], check=True)
        # 設定 NTP 伺服器
        if ntp_server:
            subprocess.run(["/usr/bin/sudo", "ntpdate", ntp_server], capture_output=True, text=True)
        subprocess.run(["/usr/bin/sudo", "hwclock", "--systohc"], check=True)
        print(f"timedatectl set-ntp {mode} 執行完成")
        # subprocess.run(["timedatectl", "status"], check=True)
         
    else:
        raise RuntimeError(f"不支援的作業系統：{os_name}")

