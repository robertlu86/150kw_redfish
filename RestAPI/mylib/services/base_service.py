from mylib.utils.HttpRequestUtil import HttpRequestUtil

class BaseService:

    @classmethod
    def send_get(cls, url, params={}):
        return HttpRequestUtil.send_get(url, params)

    @classmethod
    def send_get_as_json(cls, url, params={}):
        return HttpRequestUtil.send_get_as_json(url, params)

    @classmethod
    def send_post(cls, url, req_body, opts={}):
        return HttpRequestUtil.send_post(url, req_body, opts)

    @classmethod
    def send_post_as_json(cls, url, req_body, opts={}):
        return HttpRequestUtil.send_post_as_json(url, req_body, opts)