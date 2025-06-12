from typing import Any, Dict
from dotenv import load_dotenv
import requests
import os
# -------------- 取得資料 --------------
def load_raw_from_api(
    url: str,
    params: Dict[str, Any] = None,
    timeout: float = 5.0
) -> Dict:
    """
    從本機 API 拿回整張 JSON 並轉成 dict
    """
    resp = requests.get(url, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.json()

# curl資料
CDU_BASE = os.environ.get("ITG_REST_HOST", "http://192.168.3.137:5001")
ITG_WEBAPP_HOST = os.environ.get("ITG_WEBAPP_HOST", "http://127.0.0.1:5501")