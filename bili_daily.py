# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2022/6/23
# 每日任务
# https://github.com/Pengfei00/ql-bilibili
'''
new Env('每日任务');
10 0 * * * bili_daily.py
'''
import logging
import random
import time
from functools import cached_property

from common import BaseCls


class Daily(BaseCls):
    name = "每日任务"

    def get_my_vip_center(self):
        url = "https://api.bilibili.com/x/vip/web/vip_center/combine"
        resp = self.get(url=url)
        return resp.data

    def get_my_reward(self):
        url = "http://api.bilibili.com/x/member/web/exp/reward"
        return self.get(url=url).data

    def pay_charge(self, mid, count=None):
        """
        B币充电
        """
        url = "http://api.bilibili.com/x/ugcpay/web/v2/trade/elec/pay/quick"
        body = {
            "bp_num": count,
            "is_bp_remains_prior": True,
            "up_mid": mid,
            "otype": "up",
            "oid": mid,
        }
        resp = self.post(url=url, csrf=True, data=body)
        return resp

    def share_video(self, aid=None, bvid=None):
        url = "http://api.bilibili.com/x/web-interface/share/add"
        body = {
            "aid": aid,
            "bvid": bvid,
        }
        resp = self.post(url=url, csrf=True, data=body)
        return resp

    def watch_video(self, aid=None, bvid=None):
        url = "http://api.bilibili.com/x/click-interface/web/heartbeat"
        body = {
            "aid": aid,
            "bvid": bvid,
            "mid": self.user_info['mid'],
        }
        self.post(url=url, data=body)
        seconds = 15
        time.sleep(seconds)
        body = {
            **body,
            "played_time": seconds,
            "realtime": seconds,
        }
        return self.post(url=url, data=body)

    @cached_property
    def random_video(self):
        url = "https://api.bilibili.com/x/web-interface/ranking/v2"
        params = {
            "rid": 0,
            "type": "all"
        }
        data = self.get(url=url, params=params).data
        videos = data['list']
        return videos[random.randint(0, len(videos) - 1)]

    def run(self):
        """
        充电
        """
        data = self.get_my_vip_center()
        wallet = data['wallet']
        count = wallet['coupon']
        if count >= 2:
            info = self.user_info
            mid = info['mid']
            resp = self.pay_charge(mid=mid, count=count)
            if resp.code == 0:
                self.logger.info(f"充电成功:{count}B币")
            else:
                self.logger.info(f"充电失败:{resp.message}B币")
        else:
            self.logger.info("充电失败:B币余量不足")

        """
        每日任务
        """
        data = self.get_my_reward()
        task_map = [
            ("login", "登录", lambda: self.user_info),
            ("watch", "观看视频", lambda: self.watch_video(aid=self.random_video['aid'])),
            ("share", "分享视频", lambda: self.share_video(aid=self.random_video['aid'])),
        ]
        for task in task_map:
            if not data[task[0]]:
                task[2]()
                self.logger.info(f"每日 {task[1]} 成功")
            else:
                self.logger.info(f"每日 {task[1]} 已完成")


if __name__ == '__main__':
    Daily.main_run()
