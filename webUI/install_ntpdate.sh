#!/bin/bash

# 設置 .deb 檔案的路徑
DEB_DIR="/home/user/service/webUI/ntpdate"

# 檢查是否已安裝 ntpdate
if dpkg -l | grep -q "^ii  ntpdate "; then
    echo "ntpdate 已經安裝，無需重複安裝。"
    exit 0
fi

# 檢查是否存在 .deb 檔案
if ls "$DEB_DIR"/*.deb 1> /dev/null 2>&1; then
    echo "發現以下 .deb 檔案，將開始安裝："
    ls "$DEB_DIR"/*.deb

    # 嘗試安裝所有 .deb 文件
    echo "安裝中..."
    sudo dpkg -i "$DEB_DIR"/*.deb

    # 檢查是否有依賴錯誤
    if [ $? -ne 0 ]; then
        echo "發現依賴問題，重新安裝所有 .deb 文件以修復..."
        sudo dpkg -i "$DEB_DIR"/*.deb
    fi

    echo "ntpdate 安裝完成！"
else
    echo "在 $DEB_DIR 中沒有找到 .deb 檔案。請確認已下載相關檔案。"
    exit 1
fi
