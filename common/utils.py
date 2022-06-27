# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import logging
import os
import urllib.parse
from functools import cached_property

import requests

default_appkey = "27eb53fc9058f8c3"

appkey_table = {
    "07da50c9a0bf829f": "25bdede4e1581c836cab73a48790ca6e",
    "1d8b6e7d45233436": "560c52ccd288fed045859ed18bffd973",
    "178cf125136ca8ea": "34381a26236dd1171185c0beb042e1c6",
    "27eb53fc9058f8c3": "c2ed53a74eeefe3cf99fbd01d8c9c375",
    "37207f2beaebf8d7": "e988e794d4d4b6dd43bc0e89d6e90c43",
    "4409e2ce8ffd12b8": "59b43e04ad6965f34319062b478f83dd",
    "57263273bc6b67f6": "a0488e488d1567960d3a765e8d129f90",
    "7d336ec01856996b": "a1ce6983bc89e20a36c37f40c4f1a0dd",
    "85eb6835b0a1034e": "2ad42749773c441109bdc0191257a664",
    "8e16697a1b4f8121": "f5dd03b752426f2e623d7badb28d190a",
    "aae92bc66f3edfab": "af125a0d5279fd576c1b4418a3e8276d",
    "ae57252b0c09105d": "c75875c596a69eb55bd119e74b07cfe3",
    "bb3101000e232e27": "36efcfed79309338ced0380abd824ac1",
    "bca7e84c2d947ac6": "60698ba2f68e01ce44738920a0ffe768",
}


def appsign(params, appkey=default_appkey, appsec=None):
    '为请求参数进行 api 签名'
    if appsec is None:
        appsec = appkey_table[appkey]
    params.update({'appkey': appkey})
    params = dict(sorted(params.items()))  # 重排序参数 key
    query = urllib.parse.urlencode(params)  # 序列化参数
    sign = hashlib.md5((query + appsec).encode()).hexdigest()  # 计算 api 签名
    params.update({'sign': sign})
    return params


def get_cookie_from_env():
    import os
    cookies = os.getenv("BILIBILI_CK", "").split("&")
    return cookies


class Response:
    def __init__(self, resp):
        self.resp = resp
        data = self.resp.json()
        self.code = data.get("code", 0)
        self.message = data.get("message", "")
        self.ttl = data.get("ttl", 0)
        self.data = data.get("data")


class BaseCls(object):
    name = ""
    default_headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    }
    __cache = {}

    def __init__(self, cookies=None):
        self.cookies = cookies

    @cached_property
    def access_key(self):
        return os.getenv("BILIBILI_ACCESS_KEY")

    @cached_property
    def logger(self):
        if self.__cache.get("logger"):
            logger = self.__cache['logger']
            logger.info("\n----------\n")
            return logger
        from common.handlers import BarkHandlers
        logger = logging.getLogger("bilibili")
        logger.addHandler(logging.StreamHandler())
        bark_push = os.getenv("BARK_PUSH")
        if bark_push:
            handler = BarkHandlers(self.name, bark_url=bark_push)
            logger.addHandler(handler)
        log_level = os.getenv("LOG_LEVEL", None)
        if log_level is not None:
            if log_level.isdigit():
                log_level = int(log_level)
            else:
                log_level = logging.getLevelName(log_level.upper())
        else:
            log_level = logging.INFO
        logger.setLevel(log_level)
        if bool(os.getenv("notify_group", True)):
            self.__cache['logger'] = logger
        return logger

    @cached_property
    def requests(self):
        session = requests.session()
        session.headers.update(self.default_headers)
        if self.cookies:
            session.cookies.update(self.cookies)
        return session

    @cached_property
    def user_info(self):
        url = "http://api.bilibili.com/nav"
        resp = self.get(url=url)
        return resp.data

    def get(self, *, sign_appkey=None, sign_appsec=None, params=None, **kwargs) -> Response:
        if sign_appkey and params:
            params = appsign(params, sign_appkey, sign_appsec)
        return Response(self.requests.get(params=params, **kwargs))

    def post(self, *, sign_appkey=None, sign_appsec=None, csrf=None, json=None, headers=None, data=None,
             **kwargs) -> Response:
        if csrf:
            headers = headers or {}
            if isinstance(csrf, bool):
                if not self.csrf:
                    csrf = hashlib.md5(self.token.encode()).hexdigest()
                else:
                    csrf = self.csrf
            if isinstance(csrf, str):
                headers['x-csrf-token'] = csrf
                self.requests.cookies.set("bili_jct", csrf)
                if json:
                    json['csrf'] = csrf
                elif data:
                    data['csrf'] = csrf
        if sign_appkey:
            if data:
                data = appsign(data, sign_appkey, sign_appsec)
            elif json:
                json = appsign(json, sign_appkey, sign_appsec)
        return Response(self.requests.post(json=json, data=data, headers=headers, **kwargs))

    @property
    def csrf(self):
        return self.requests.cookies.get("bili_jct", None)

    @property
    def token(self):
        return self.requests.cookies.get("SESSDATA", "")

    @property
    def is_vip(self):
        return self.user_info['vipStatus'] == 1

    def run(self):
        raise NotImplementedError

    @classmethod
    def main_run(cls):
        cookies_list = get_cookie_from_env()
        for i in cookies_list:
            cookies = {k.strip(): v.strip() for k, v in (__i.split("=") for __i in (_i for _i in i.split(";")))}
            instance = cls(cookies)
            print(instance.access_key)
            instance.logger.info(f"用户昵称:{instance.user_info['uname']}")
            instance.run()
