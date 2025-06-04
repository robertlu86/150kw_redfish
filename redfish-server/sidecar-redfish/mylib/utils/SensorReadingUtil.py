"""
SensorReadingUtil is to judge whether the sensor reading is approach to target value.
"""
class SensorReadingUtil:
    @classmethod
    def is_values_approach_target(cls, reading_values, target_value, tolerance=1.5, stable_duration=2):
        """
        判斷 sensor 是否成功達到 target_value 並穩定
        :param reading_values: list of float, (ex:每3秒一筆)
        :param target_value: float, 目標值
        :param tolerance: float, 判定範圍
        :param stable_duration: int, 至少穩定幾筆（例如 3筆 = 9秒）
        :return: dict
        """
        close_cnt = 0
        stable_cnt = 0
        fail_cnt = 0
        # Step 1: 是否曾經接近過目標值？
        # any([True, False, True]) -> True
        # any([False, False, False]) -> False
        # reached = any(abs(v - target_value) <= tolerance for v in reading_values)
        # if not reached:
        #     return False
        
        for v in reading_values:
            if abs(v - target_value) <= tolerance:
                close_cnt += 1

        # Step 2: 最後一段是否穩定在 target 附近？
        for v in reversed(reading_values):
            if abs(v - target_value) <= tolerance:
                stable_cnt += 1
            else:
                fail_cnt += 1
        
        return {
            "is_judge_success": (close_cnt > 0) or (stable_cnt >= stable_duration),
            "close_cnt": close_cnt,
            "stable_cnt": stable_cnt,
            "fail_cnt": fail_cnt,
            "is_finally_stabled": (stable_cnt >= stable_duration),
            "reason": ""
        }

    @classmethod
    def run_testcase(cls):
        cases = [
            {
                "reading_values": [50, 50, 50, 51, 51, 60, 69, 71, 70, 70],
                "target_value": 70,
            },
            {
                "reading_values": [20, 20, 30, 41, 61, 59, 51, 50, 49.08, 49.07],
                "target_value": 50,
            },
            {
                "reading_values": [20, 20, 30, 41, 61, 59, 75, 64, 63, 62, 70],
                "target_value": 70,
            },
            {
                "reading_values": [20, 20, 30, 41, 61, 59, 75, 64, 63, 62],
                "target_value": 70,
            },
            {
                "reading_values": [20, 20, 30, 41, 61, 59, 75, 64, 63, 62, 68.7, 69.3],
                "target_value": 70,
            }
        ]

        for case in cases:
            print("- case: ", case)
            result = cls.is_values_approach_target(case["reading_values"], case["target_value"])
            print("  result: ", result)
    