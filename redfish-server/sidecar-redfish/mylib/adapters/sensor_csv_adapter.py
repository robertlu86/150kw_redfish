import os
from mylib.utils.HttpRequestUtil import HttpRequestUtil
from typing import Dict
from http import HTTPStatus
from mylib.models.rf_resource_model import RfResetType
from mylib.common.proj_error import ProjError
from mylib.utils.FileUtil import FileUtil
from flask import abort

"""
讀取 webUI/logs/sensor 裡的CSV檔
"""
class SensorCsvAdapter:
    SENSOR_ROOT = os.getenv('TELEMETRY_SENSOR_LOG_ROOT')

    @classmethod
    def _root_path(cls) -> str:
        sensor_root = os.getenv('TELEMETRY_SENSOR_LOG_ROOT')
        if sensor_root is None:
            raise ProjError(HTTPStatus.BAD_REQUEST.value, "`TELEMETRY_SENSOR_LOG_ROOT` should in .env file")

        if FileUtil.exists(sensor_root) and FileUtil.is_dir(sensor_root):
            return sensor_root
        else:
            raise ProjError(HTTPStatus.NOT_FOUND.value, f"{sensor_root} is not exist!")

    @classmethod
    def list_all(cls) -> dict:
        """List all sensor csv files
        """
        root_path = cls._root_path()
        filepaths = FileUtil.list_files(root_path)
        csv_filenames = []
        for filepath in filepaths:
            filename = os.path.basename(filepath)
            if filename.endswith(".csv"):
                csv_filenames.append(filename)

        return {
            "sensor_root": root_path,
            "filenames": csv_filenames
        }

    @classmethod
    def list_latest_n_days(cls, n: int) -> dict:
        pass