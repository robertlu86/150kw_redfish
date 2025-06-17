import os
import json
import pytest
import sys
import logging
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mylib.models.rf_status_model import RfStatusModel, RfStatusHealth
from mylib.utils.StatusUtil import StatusUtil
from mylib.utils import system_info

def test_get_worst_health_model(client):
    """[TestCase] 取得健康度最差的"""
    status_models = [
        RfStatusModel(Health=RfStatusHealth.OK),
        RfStatusModel(Health=RfStatusHealth.Critical),
        RfStatusModel(Health=RfStatusHealth.Warning),
    ]
    logging.info(f"Testcase basic: status_models: {status_models}")
    worst_health_status = StatusUtil.get_worst_health(status_models)
    assert worst_health_status.Health == RfStatusHealth.Critical
    
    for i in range(0, 10):
        random.shuffle(status_models)
        logging.info(f"Testcase {i+1}: status_models: {status_models}")
        worst_health_status = StatusUtil.get_worst_health(status_models)
        assert worst_health_status.Health == RfStatusHealth.Critical

def test_get_worst_health_dict(client):
    """[TestCase] 取得健康度最差的"""
    status_dicts = [
        { "State": "Enabled", "Health": "OK" },
        { "State": "Enabled", "Health": "Critical" },
        { "State": "Enabled", "Health": "Warning" },
    ]
    logging.info(f"Testcase basic: status_dicts: {status_dicts}")
    worst_health_status = StatusUtil.get_worst_health_dict(status_dicts)
    assert worst_health_status["Health"] == RfStatusHealth.Critical.value
    
    for i in range(0, 10):
        random.shuffle(status_dicts)
        logging.info(f"Testcase {i+1}: status_dicts: {status_dicts}")
        worst_health_status = StatusUtil.get_worst_health_dict(status_dicts)
        assert worst_health_status["Health"] == RfStatusHealth.Critical.value

    # 小寫"state"和"health"
    status_dicts = [
        { "state": "Enabled", "health": "OK" },
        { "state": "Enabled", "health": "Critical" },
        { "state": "Enabled", "health": "Warning" },
    ]
    logging.info(f"Testcase lowercase: status_dicts: {status_dicts}")
    worst_health_status = StatusUtil.get_worst_health_dict(status_dicts)
    assert worst_health_status["Health"] == RfStatusHealth.Critical.value

def test_get_system_uuid(client):
    """[TestCase] 取得系統 UUID"""
    uuid = system_info.get_system_uuid()
    logging.info(f"Testcase basic: uuid: {uuid}")
    assert uuid is not None
    assert len(uuid) == 36
    assert uuid.count("-") == 4