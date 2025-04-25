# #!/bin/bash

# # 設置 .deb 檔案的路徑
# DEB_DIR="/home/user/service/new_user_sh/onboard"

# # 檢查是否存在 .deb 檔案
# if ls "$DEB_DIR"/*.deb 1> /dev/null 2>&1; then
#     echo "發現以下 .deb 檔案，將開始安裝："
#     ls "$DEB_DIR"/*.deb

#     # 安裝 .deb 檔案
#     echo "安裝中..."
#     sudo dpkg -i "$DEB_DIR"/*.deb

#     # 修復依賴問題（如果有的話）
#     echo "修復依賴中..."
#     sudo apt-get install -f

#     echo "onboard 安裝完成！"
# else
#     echo "在 $DEB_DIR 中沒有找到 .deb 檔案。請確認已下載相關檔案。"
# fi
