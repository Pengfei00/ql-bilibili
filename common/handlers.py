# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2022/6/24
import logging
from io import StringIO
from urllib.parse import urlparse

import requests


class BarkHandlers(logging.StreamHandler):
    stream: StringIO

    def __init__(self, title, bark_url, **kwargs) -> None:
        url_result = urlparse(bark_url)
        self.scheme = url_result.scheme
        self.host = url_result.netloc
        self.device_key = url_result.path.split("/")[1]
        self.push_url = f"{self.scheme}://{self.host}/push"
        self.title = title
        self.bark_kw = {"title": self.title,
                        "device_key": self.device_key}
        if kwargs:
            self.bark_kw.update(kwargs)
        super(BarkHandlers, self).__init__(StringIO())

    def close(self) -> None:
        self.stream.seek(0)
        self.send_bark(self.stream.read())
        super().close()

    def send_bark(self, body):
        requests.post(url=self.push_url, json={**self.bark_kw, "body": body[:-1]})
