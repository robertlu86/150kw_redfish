import os
from mylib.utils.HttpRequestUtil import HttpRequestUtil
from typing import Dict
from mylib.models.rf_resource_model import RfResetType
from mylib.common.proj_error import ProjError
from http import HTTPStatus
from flask import abort

"""
webapp 就是 大家稱為webUI的東西
名字容易讓人誤會成UI的服務，但事實上就是web app for cdu

@note:
    `webUI` is a confused naming. in fact it is a CDU web app, including backend api.
"""
class WebAppAPIAdapter:

    @classmethod
    def reset_to_defaults(cls, reset_type: str) -> dict:
        """Reset to defaults
        @note:
            Fetch /restore_factory_setting_all from webUI
            {
            }
        """
        url = f"{os.environ['ITG_WEBAPP_HOST']}/restore_factory_setting_all"
        post_body = {
            "ResetType": reset_type
        }
        response = HttpRequestUtil.send_post(url, post_body)
        return response

    @classmethod
    def reset(cls, reset_type: str=RfResetType.ForceRestart.value) -> dict:
        """Reset
        @note:
            Fetch scc api: /api/v1/reboot
        """
        if reset_type == RfResetType.ForceRestart.value:
            url = f"{os.environ['ITG_WEBAPP_HOST']}/api/v1/reboot"
        elif reset_type == RfResetType.GracefulRestart.value:
            url = f"{os.environ['ITG_WEBAPP_HOST']}/api/v1/reboot"
        else:
            # abort(HTTPStatus.BAD_REQUEST, f"Invalid reset type: {reset_type}")
            raise ProjError(HTTPStatus.BAD_REQUEST.value, f"Invalid reset type: {reset_type}")
        response = HttpRequestUtil.send_get(url)
        return response

    @classmethod
    def shutdown(cls, reset_type: str=RfResetType.ForceRestart.value) -> dict:
        """Reset
        @note:
            Fetch scc api: /api/v1/shutdown
        """
        if reset_type == RfResetType.ForceRestart.value:
            url = f"{os.environ['ITG_WEBAPP_HOST']}/api/v1/shutdown"
        elif reset_type == RfResetType.GracefulRestart.value:
            url = f"{os.environ['ITG_WEBAPP_HOST']}/api/v1/shutdown"
        else:
            raise ProjError(HTTPStatus.BAD_REQUEST.value, f"Invalid reset type: {reset_type}")
        response = HttpRequestUtil.send_get(url)
        return response