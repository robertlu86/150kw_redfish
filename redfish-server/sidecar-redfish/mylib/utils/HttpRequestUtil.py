import requests
from typing import Optional

class HttpRequestUtil:
    @classmethod
    def send_get(cls, url: str, opts: dict = {}) -> dict:
        """
        :param url: str
        :param opts: dict
            opts['header']: dict
        :return: str
        """
        try:
            headers = opts.get('headers', {})
            response = requests.get(url, headers=headers)
            # return response.text
            return response
        except Exception as e:
            print(f"HttpRequestUtil get error: {e}")
            raise e
    
    @classmethod
    def send_get_as_json(cls, url: str, opts: dict = {}) -> dict:
        return cls.send_get(url, opts).json()

    @classmethod
    def send_post(cls, url: str, req_body: dict = {}, opts: dict = {}) -> dict:
        """
        :param url: str
        :param opts: dict
            opts['header']: dict
        :return: str
        """
        try:
            headers = opts.get('header', {})
            response = requests.post(url, headers=headers, data=req_body)
            return response
        except Exception as e:
            print(f"HttpRequestUtil post error: {e}")
            raise e
    
    @classmethod
    def send_post_as_json(cls, url: str, req_body: dict = {}, opts: dict = {}) -> dict:
        return cls.send_post(url, req_body, opts).json()
    