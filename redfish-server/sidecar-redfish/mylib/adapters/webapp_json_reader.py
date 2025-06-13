import os
from typing import Dict
from http import HTTPStatus
from flask import abort
import json
from mylib.utils.HttpRequestUtil import HttpRequestUtil
from mylib.common.proj_error import ProjError
from mylib.utils.FileUtil import FileUtil

"""
讀取 /home/user/service/webUI/json/ 裡的json檔
error log (latest 500 entries): signal_records.json
"""
class WebAppJsonReader:

    @classmethod
    def _error_log_path(cls) -> str:
        json_root = os.getenv('ITG_WEBAPP_JSON_ROOT')
        if json_root is None:
            raise ProjError(HTTPStatus.BAD_REQUEST.value, "`ITG_WEBAPP_JSON_ROOT` should in .env file")
        
        json_filepath = os.path.join(json_root, "signal_records.json")

        if FileUtil.exists(json_filepath) and FileUtil.is_file(json_filepath):
            return json_filepath
        else:
            raise ProjError(HTTPStatus.NOT_FOUND.value, f"{json_filepath} is not exist!")

    @classmethod
    def read_all_errorlog_entries(cls) -> dict:
        """Read all error logs
        """
        error_log_path = cls._error_log_path()
        log_entries = json.loads(FileUtil.read(error_log_path))
        return log_entries

 