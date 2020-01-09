#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import re
import requests

config = {
    "sh": ["sh603012", "sh600001"],
    "sz": ["sz300003", "sz300001"],
}


class Stock:
    def __init__(self, config):
        self.stock_list = []
        self.stock_list.extend(config["sh"])
        self.stock_list.extend(config["sz"])
        self.stock_info = []

    def show_all_stocks(self):
        stocks = ",".join(str(i) for i in self.stock_list)
        return stocks

    def get_current_info(self):
        url = "http://hq.sinajs.cn/list={}".format(self.show_all_stocks())
        rsp = requests.get(url)
        arr = rsp.text.split(";")
        for i in range(len(arr)):
            self.parse_info(arr[i])
        return self.stock_info

    def parse_info(self, info):
        pattern = re.compile('s[h,z][0-9]{6}')
        id = pattern.findall(info)
        if not id:
            return

        pattern = re.compile('"(.*)"')
        str = pattern.findall(info)
        s = str[0].split(",")
        m = {
            "id": id[0],  # 股票代码
            "name": s[0],  # 股票名称
            "open_price": s[1],  # 今日开盘价格
            "close_price": s[2],  # 昨日收盘价格
            "now_price": s[3],  # 当前股价
            "high_price": s[4],  # 今日最高股价
            "low_price": s[5],  # 今日最低股价
            # "buy1_price": s[6],  # 买一股价
            # "sold1_price": s[7],  # 卖一股价
            "amount": s[8],  # 交易总额
            "count": s[9],  # 交易量
            "buy1_count": s[10],  # 买1数量
            "buy1_price": s[11],  # 买1股价
            "buy2_count": s[12],  # 买2数量
            "buy2_price": s[13],  # 买2股价
            "buy3_count": s[14],  # 买3数量
            "buy3_price": s[15],  # 买3股价
            "buy4_count": s[16],  # 买4数量
            "buy4_price": s[17],  # 买4股价
            "buy5_count": s[18],  # 买5数量
            "buy5_price": s[19],  # 买5股价
            "sold1_count": s[20],  # 卖1数量
            "sold1_price": s[21],  # 卖1股价
            "sold2_count": s[22],  # 卖2数量
            "sold2_price": s[23],  # 卖2股价
            "sold3_count": s[24],  # 卖3数量
            "sold3_price": s[25],  # 卖3股价
            "sold4_count": s[26],  # 卖4数量
            "sold4_price": s[27],  # 卖4股价
            "sold5_count": s[28],  # 卖5数量
            "sold5_price": s[29],  # 卖5股价
            "date": s[30],  # 日期
            "time": s[31],  # 时间
        }

        self.stock_info.append(m)

    # TODO: 遍历改为从数据库获取信息
    def get_stock_info(self, id):
        for i in range(len(self.stock_info)):
            if self.stock_info[i]["id"] == id:
                return self.stock_info[i]


if __name__ == "__main__":
    id = "sh603012"
    s = Stock(config)
    r = s.get_current_info()
    print(r)
    r = s.get_stock_info(id)
    print(r)
