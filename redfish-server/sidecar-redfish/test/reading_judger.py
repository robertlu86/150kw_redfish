'''
conftest.py 是 pytest 的特殊設定檔，用來集中定義「測試共用的 fixture 或 hook function」，
不需要在每個測試檔案中 import 就可以自動套用，這是它的主要用途與優勢。
'''
import os
import sys
import json
import time
from abc import ABC, abstractmethod
from mylib.utils.SensorReadingUtil import SensorReadingUtil
        
class ReadingJudgerBase(ABC):
    """
    判讀reading值是否有效、正確
    @note: 我們每2秒讀一次modbus
    """

    def __init__(self, client, uri, basic_auth_header, params={}):
        """
        :uri: Should be Redfish api
        :params: is following key:
          - judge_cnt {Integer}: Default 4
          - judge_interval {Integer}: Default 3 (seconds)
          - judge_tolerance {Integer}: Default 1.5
        """
        self.name = ""
        self.description = "判讀reading值是否有效、正確"
        self.client = client
        self.uri = uri
        self.basic_auth_header = basic_auth_header
        self.params = params
        self.judge_cnt = params.get("judge_cnt", 4)
        self.judge_interval = params.get("judge_interval", 3) # 秒
        self.judge_tolerance = params.get("judge_tolerance", 1.5) # 1.5 for fan, 30 for pump

    @abstractmethod
    def judge(self):
        raise NotImplementedError
    
    def parse_reading(self, resp_json: dict) -> float:
        if "Reading" in resp_json: 
            # for "/redfish/v1/Chassis/1/Sensors/Fan1"
            return resp_json["Reading"] 
        elif "PumpSpeedPercent" in resp_json: 
            # for "/redfish/v1/ThermalEquipment/CDUs/1/Pumps/1"
            return resp_json["PumpSpeedPercent"]["Reading"]
        else:
            return None

class ReadingJudgerPolicy1(ReadingJudgerBase):
    def __init__(self, client, uri, basic_auth_header, params={}):
        super().__init__(client, uri, basic_auth_header, params)
        self.name = "JUDGE-3-TIMES"
        self.description = "三次讀值，值不可一致，而且必須差在5%以內"

    @classmethod
    def validate_sensor_value_in_reasonable_vibration(cls, sensor_value: float, target_value: float) -> bool:
        # return target_value*0.985 <= sensor_value <= target_value*1.015
        return (target_value - 1.5) <= sensor_value <= (target_value + 1.5)

    def judge(self) -> bool:
        ret = {
            "is_judge_success": False,
            "confidence": 0,
            "reason": ""
        }
        reading_values = []
        for i in range(self.judge_cnt):
            response = self.client.get(self.uri, headers=self.basic_auth_header)
            resp_json = response.json
            reading = resp_json.get('Reading') 
            print(f"[ReadingJudgerPolicy1][uri={self.uri}] Reading {i+1}: {reading}")
            if reading == 0:
                print(f"[ReadingJudgerPolicy1] judge return False because reading is 0.")
                ret["is_judge_success"] = False
                ret["confidence"] = 0.9
                ret["reason"] = "reading值不該為例，但卻讀到0"
                return ret # to save testing time
            reading_values.append(reading)
            time.sleep(self.judge_interval)

        # 三次值都不一樣
        if len(set(reading_values)) == self.judge_cnt:
            min_value = min(reading_values)
            max_value = max(reading_values)
            #return abs(max_value - min_value) / max_value <= 0.05
            ret["is_judge_success"] = abs(max_value - min_value) / max_value <= 0.05
            ret["confidence"] = 0.95
            ret["reason"] = "3次值都不一樣，且最大、最小值差值在目標值的5%以內"
        
        # 3次有2次一樣
        if len(set(reading_values)) == self.judge_cnt - 1:
            min_value = min(reading_values)
            max_value = max(reading_values)
            #return abs(max_value - min_value) / max_value <= 0.03
            ret["is_judge_success"] = abs(max_value - min_value) / max_value <= 0.03
            ret["confidence"] = 0.80
            ret["reason"] = "3次值有2次一樣，且最大、最小值差值在目標值的3%以內"
        
        # 所有值都一樣
        if len(set(reading_values)) == 1:
            ret["is_judge_success"] = False
            ret["confidence"] = 0.50
            ret["reason"] = "所有值都一樣"
        
        return False

class ReadingJudgerPolicy2(ReadingJudgerBase):
    def __init__(self, client, uri, basic_auth_header, params={}):
        super().__init__(client, uri, basic_auth_header, params)
        self.name = "JUDGE-SHOULD_APPROACH_TARGET_VALUE"
        self.description = "三次讀值，值必須每次更接近目標值"

    def judge(self, target_value: float=None) -> dict:
        ret = {
            "is_judge_success": False,
            "confidence": 0,
            "reason": ""
        }

        if target_value is None:
            ret["is_judge_success"] = False
            ret["confidence"] = 1.0
            ret["reason"] = "必須提供目標值"
            return ret

        reading_values = []
        for i in range(self.judge_cnt):
            response = self.client.get(self.uri, headers=self.basic_auth_header)
            resp_json = response.json
            reading = self.parse_reading(resp_json)
            print(f"[ReadingJudgerPolicy2][uri={self.uri}] Reading {i+1}: {reading}")
            reading_values.append(reading)
            time.sleep(self.judge_interval)

        # 每次值都更接近目標值
        prev_value = reading_values[0]
        succ_cnt = 0
        fail_cnt = 0
        is_close_to_target_value = False
        close_cnt = 0
        reading_cnt = len(reading_values)
        for i in range(1, reading_cnt):
            if (reading_values[i] == target_value) or abs(reading_values[i] - target_value) < 1.5:
                is_close_to_target_value = True
                close_cnt += 1
                continue

            if abs(reading_values[i] - target_value) < abs(prev_value - target_value):
                succ_cnt += 1
            else:
                fail_cnt += 1
                    
            prev_value = reading_values[i]
        
        # 接近目標值的次數比例超過75% 
        if (close_cnt >= 0.75 * reading_cnt) or (close_cnt > succ_cnt):
            ret["is_judge_success"] = True
            ret["confidence"] = 0.75
            ret["reason"] = "接近目標值的次數比例超過75%"
        # 每次值都更接近目標值: 成功數>失敗數
        elif succ_cnt > fail_cnt:
            ret["is_judge_success"] = True
            ret["confidence"] = 1.0 - (fail_cnt / reading_cnt)
            ret["reason"] = "每次值都更接近目標值，且成功數>失敗數"
        else:
            ret["is_judge_success"] = False
            ret["confidence"] = 1.0 - (fail_cnt / reading_cnt)
            ret["reason"] = "每次值都更接近目標值，但失敗數>=成功數"
        
        return ret


            
class ReadingJudgerPolicy3(ReadingJudgerBase):
    def __init__(self, client, uri, basic_auth_header, params={}):
        super().__init__(client, uri, basic_auth_header, params)
        self.name = "JUDGE-SHOULD_STABLE"
        self.description = "趨勢收歛判斷"
        if self.judge_cnt < 10:
            self.judge_cnt = 10 # 要判斷趨勢，至少要測10次
    
    def judge(self, target_value: float=None) -> dict:
        ret = {
            "is_judge_success": False,
            "confidence": 0,
            "reason": ""
        }

        if target_value is None:
            ret["is_judge_success"] = False
            ret["reason"] = "必須提供目標值"
            return ret

        reading_values = []
        for i in range(self.judge_cnt):
            response = self.client.get(self.uri, headers=self.basic_auth_header)
            resp_json = response.json
            reading = self.parse_reading(resp_json)
            print(f"[ReadingJudgerPolicy3][uri={self.uri}] Reading {i+1}: {reading}")
            reading_values.append(reading)
            time.sleep(self.judge_interval)

        return self.judge_by_reading_values(target_value, reading_values)
    
    def judge_by_reading_values(self, target_value, reading_values: []) -> dict:
        # 判斷趨勢收歛
        result = SensorReadingUtil.is_values_approach_target(
            reading_values=reading_values, 
            target_value=target_value,
            tolerance=self.judge_tolerance
        )

        if result['close_cnt'] > 0:
            result["reason"] = "曾經接近目標值"
        elif result['is_finally_stabled'] > 0:
            result["reason"] = "最後有收歛至目標值"
        else:
            result["reason"] = "reading未曾接近目標值，或最後未收歛"
        
        result["reading_values"] = reading_values
        return result

