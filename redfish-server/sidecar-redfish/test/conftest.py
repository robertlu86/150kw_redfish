'''
conftest.py 是 pytest 的特殊設定檔，用來集中定義「測試共用的 fixture 或 hook function」，
不需要在每個測試檔案中 import 就可以自動套用，這是它的主要用途與優勢。
'''
import os
import sys
from dotenv import load_dotenv
proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(proj_root)
print(f"Testing with .env-test: {os.path.join(proj_root, '.env-test')}")
load_dotenv(dotenv_path=f"{os.path.join(proj_root, '.env-test')}", verbose=True, override=True)

import base64
import pytest
import logging
from pytest_metadata.plugin import metadata_key
from app import app

# 讓 logging 輸出到 stdout，pytest-html 才能接收到docstring
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def pytest_configure(config):
    """會顯示在 html report 的 Environment 部分"""
    for key, value in os.environ.items():
        if key.startswith("ITG_") or key.startswith("REDFISH_"):
            logging.info(f"{key}: {value}")
            # config._metadata[key] = value # Deprecated
            config.stash[metadata_key][key] = value


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def basic_auth_header():
    def make_basic_auth_header(username, password):
        token = base64.b64encode(f"{username}:{password}".encode()).decode()
        return {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json"
        }
    return make_basic_auth_header("admin", "admin")

@pytest.fixture(autouse=True)
def log_docstring_for_testcase(request):
    """
    自動印出每個test case的docstring
    """
    doc = request.function.__doc__
    if doc:
        logging.info(f"{doc.strip()}")
    else:
        logging.info("<無 docstring>")



@pytest.fixture
def common_payload():
    """Fixture: Generates a payload."""
    payload = {}
    return payload


