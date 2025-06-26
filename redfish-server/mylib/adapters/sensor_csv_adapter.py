# mylib/adapters/sensor_csv_adapter.py

import os
import glob
import csv
from datetime import datetime
from functools import lru_cache
from mylib.models.sensor_log_model import SensorLogModel
from mylib.models.sensor_log_model_factory import SensorLogModelFactory


class SensorCsvAdapter:
    """
    負責讀取和解析 sensor CSV 檔案的數據適配器。
    """

    # 從環境變數讀取日誌路徑，若未設定則提供一個預設值
    SENSOR_ROOT = os.getenv(
        "TELEMETRY_SENSOR_LOG_ROOT", "home/user/service/webUI/logs/sensor"
    )

    # 新增配置：要讀取的最近天數，可以設為環境變數
    DAYS_TO_LOAD = int(os.getenv("TELEMETRY_DAYS_TO_LOAD", "7"))  # 默認為7天

    @classmethod
    def _get_root_path(cls) -> str | None:
        """獲取並驗證日誌根目錄是否存在。"""
        if not os.path.isdir(cls.SENSOR_ROOT):
            print(f"Warning: Telemetry log directory not found at '{cls.SENSOR_ROOT}'")
            return None
        return cls.SENSOR_ROOT

    @classmethod
    @lru_cache(maxsize=1)  # 使用LRU快取，避免重複讀取和處理檔案
    def get_all_sensor_data_as_list_of_dicts(cls) -> list[dict]:
        """
        掃描日誌目錄，讀取最近 N 天的 CSV 檔案，並將它們合併成一個按時間排序的字典列表。

        Returns:
            A list of dictionaries containing all sensor data, or an empty list if no data found.
        """
        root_path = cls._get_root_path()
        if not root_path:
            return []

        all_files = sorted(
            glob.glob(os.path.join(root_path, "sensor.log.*.csv")), reverse=True
        )
        files_to_process = all_files[: cls.DAYS_TO_LOAD]

        if not files_to_process:
            print(f"Warning: No sensor CSV files found to process.")
            return []

        print(
            f"Total files found: {len(all_files)}. Processing the latest {len(files_to_process)} files (up to {cls.DAYS_TO_LOAD} days)."
        )

        all_records = []
        for path in reversed(files_to_process):
            try:
                with open(path, mode="r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)  # 使用 DictReader 自動處理 header
                    for row in reader:
                        # 核心步驟：將 'time' 字串轉換為 datetime 物件
                        try:
                            row["time"] = datetime.fromisoformat(row["time"])
                        except (ValueError, KeyError):
                            # 如果時間格式錯誤或沒有 'time' 欄位，則跳過此行
                            continue
                        # select fields: fan1-6 for customer SMC
                        # sensor_log = SensorLogModel.model_validate(row) # parse_obj() is deprecated
                        sensor_log = SensorLogModelFactory.create_model("SensorLogModel", row)
                        all_records.append(sensor_log.to_dict())
            except Exception as e:
                print(f"Error reading or processing file {path}: {e}")
                continue

        # 確保所有記錄都按時間排序，這是後續處理的基礎
        all_records.sort(key=lambda x: x["time"])

        print(
            f"Successfully processed and merged all sensor data. Total records: {len(all_records)}"
        )
        return all_records
