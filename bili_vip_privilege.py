# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2022/06/23
# 卡券领取
# https://github.com/Pengfei00/ql-bilibili
'''
new Env('卡券领取');
5 0 * * * bili_vip_point.py
'''

from common import BaseCls


class VipPrivilege(BaseCls):
    name = "每月卡劵领取"

    def get_list(self):
        url = "https://api.bilibili.com/x/vip/privilege/my"
        resp = self.get(url=url)
        for i in resp.data['list']:
            yield i

    def receive(self, _type):
        url = "https://api.bilibili.com/x/vip/privilege/receive"
        body = {"type": _type}
        resp = self.post(url=url, data=body, csrf=True)
        return resp

    def run(self):
        if not self.is_vip:
            return
        code_err_map = {-101: "账号未登录", -111: "csrf 校验失败", -400: "请求错误", 69800: "网络繁忙 请稍后重试", 69801: "你已领取过该权益"}
        for privilege in self.get_list():
            _type = privilege['type']
            state = privilege['state']
            coupon_name = {1: "B币", 2: "会员购优惠券", 3: "漫画福利券", 4: "会员购运费券"}.get(_type, None)
            if state == 1:
                # 已兑换
                self.logger.info(f"{coupon_name}已领取")
                continue
            if _type == 1:
                # B币
                pass
            elif _type == 2:
                # 会员购优惠券
                pass
            elif _type == 3:
                # 漫画福利券
                pass
            elif _type == 4:
                # 会员购运费券
                pass
            else:
                # 不知道是啥
                continue
            resp = self.receive(_type)
            code = resp.code
            if resp.code != 0:
                msg = code_err_map.get(code, code)
                self.logger.info(msg)
            else:
                self.logger.info(f"{coupon_name}领取成功")


if __name__ == '__main__':
    VipPrivilege.main_run()
