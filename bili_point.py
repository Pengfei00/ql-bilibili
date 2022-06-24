# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2022/06/23
# 大积分任务
# https://github.com/Pengfei00/ql-bilibili
'''
new Env('大积分任务');
5 0 * * * bili_point.py
'''

import time

from common import BaseCls


class Point(BaseCls):
    name = "大积分任务"

    def get_combine(self):
        params = {
            "ts": int(time.time())
        }
        url = "https://api.bilibili.com/x/vip_point/task/combine"
        resp = self.get(url=url, params=params)
        return resp

    def complete_task(self, code, countdown=0):
        if countdown:
            time.sleep(countdown)
        url = "https://api.bilibili.com/pgc/activity/score/task/complete"
        body = {"ts": int(time.time()), "taskCode": code}
        resp = self.post(url=url, json=body,
                         headers={"referer": "https://big.bilibili.com/mobile/bigPoint/task"})
        return resp

    def receive_task(self, code):
        url = "https://api.bilibili.com/pgc/activity/score/task/receive"
        body = {"ts": int(time.time()), "taskCode": code}
        resp = self.post(url=url, json=body,
                         headers={"referer": "https://big.bilibili.com/mobile/bigPoint/task"})
        return resp

    def daily_sign(self):
        url = "https://api.bilibili.com/pgc/activity/score/task/sign"
        body = {
            "ts": int(time.time()),
            "access_key": self.access_key
        }
        resp = self.post(url=url, data=body, csrf=True, sign_appkey="27eb53fc9058f8c3")
        return resp

    def run(self):
        skip_code = {"vipmallbuy", "tvodbuy", "ogvwatch"}
        combine = self.get_combine()
        if self.access_key:
            for i in combine.data['task_info']['sing_task_item']['histories']:
                if i.get("is_today"):
                    if i['score'] > 0:
                        self.logger.info("大积分每日签到 已完成")
                        break
                    else:
                        self.daily_sign()
                        self.logger.info("大积分每日签到 完成")
                        break
        else:
            self.logger.info("未提供access key 跳过大积分每日签到")

        for i in combine.data['task_info']['modules']:
            for task in i['common_task_item']:
                task_code = task['task_code']
                title = task['title']
                complete_times = task['complete_times']
                max_times = task['max_times']
                state = task['state']  # 0领取任务 1去完成 3已完成
                vip_limit = task['vip_limit']
                if vip_limit and not self.is_vip:
                    self.logger.info(f"{title} vip任务 跳过")
                    continue
                if complete_times >= max_times:
                    self.logger.info(f"{title} 已完成 跳过")
                    continue
                if state == 0:
                    # 领取任务
                    resp = self.receive_task(task_code)
                    if resp.code == 0:
                        self.logger.info(f"{title} 领取")
                elif state == 1:
                    # 去完成
                    if task_code in skip_code:
                        self.logger.info(f"{title} 已领取 跳过")
                        continue
                    task_countdown = 10
                    for i in range(max_times - complete_times):
                        resp = self.complete_task(task_code, task_countdown)
                        if resp.code == 0:
                            self.logger.info(f"{title} 完成{complete_times + 1}/{max_times}")
                elif state == 3:
                    # 已完成
                    self.logger.info(f"{title} 已完成")


if __name__ == '__main__':
    Point.main_run()
