#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import re
import requests
import db


class StockQuery:
    def __init__(self, id):
        self.id = id
        self.info = None
        self.init_db()

    def init_db(self):
        host = "114.67.229.59"
        port = 3306
        db = "ais"
        user = "ais"
        passwd = "ais"
        self.db = db.DbUtils(host, port, db, user, passwd)

    def get_stock_basic_info(self):
        url = "http://qt.gtimg.cn/q={}".format(self.id)
        rsp = requests.get(url)
        return self.parse_qt_response(rsp.text)

    def get_stock_ff_info(self):
        url = "http://qt.gtimg.cn/q=ff_{}".format(self.id)
        rsp = requests.get(url)
        return self.parse_qt_response(rsp.text)

    def parse_qt_response(self, info):
        pattern = re.compile('s[h,z][0-9]{6}')
        id = pattern.findall(info)
        if not id:
            print("stock {} query failed".format(self.id))
            return
        pattern = re.compile('"(.*)"')
        str = pattern.findall(info)
        s = str[0].split("~")
        return s

    def get_stock_info(self):
        basic_info = self.get_stock_basic_info()
        ff_info = self.get_stock_ff_info()

        time = basic_info[30]
        s1 = ff_info[14].split("^")
        s2 = ff_info[15].split("^")
        s3 = ff_info[16].split("^")
        s4 = ff_info[17].split("^")

        self.info = {
            "id": self.id,  # 股票代码
            "name": basic_info[1],  # 股票名称
            "updated_date": time[:8],  # 更新日期
            "open_price": basic_info[5],  # 今日开盘价格
            "close_price": basic_info[4],  # 昨日收盘价格
            "now_price": basic_info[3],  # 当前股价
            "high_price": basic_info[33],  # 今日最高股价
            "low_price": basic_info[34],  # 今日最低股价
            "high_limit": basic_info[47],  # 涨停价
            "low_limit": basic_info[48],  # 跌停价
            "changes": basic_info[31],  # 涨跌
            "rate": basic_info[32],  # 涨跌幅
            "volume": basic_info[36],  # 成交量
            "amount": basic_info[37],  # 成交额
            "swap_rate": basic_info[38],  # 换手率
            "per": basic_info[39],  # 市盈率
            "amplitude": basic_info[43],  # 振幅
            "market_value": basic_info[44],  # 流通市值
            "total_value": basic_info[45],  # 总市值
            "qrr": basic_info[49],  # 量比
            "pbr": basic_info[46],  # 市净率
            "buy_price": basic_info[9],  # 买一价格
            "buy_count": basic_info[10],  # 买一手数
            "sold_price": basic_info[19],  # 卖一价格
            "sold_count": basic_info[20],  # 卖一手数
            "big_in_1": ff_info[1],  # 今日大单流入
            "big_out_1": ff_info[2],  # 今日大单流出
            "big_in_2": s1[1],  # 前1日大单流入
            "big_out_2": s1[2],  # 前1日大单流出
            "big_in_3": s2[1],  # 前2日大单流入
            "big_out_3": s2[2],  # 前2日大单流出
            "big_in_4": s3[1],  # 前3日大单流入
            "big_out_4": s3[2],  # 前3日大单流出
            "big_in_5": s4[1],  # 前4日大单流入
            "big_out_5": s4[2],  # 前4日大单流出
        }

        return self.info

    def db_store_stock_info(self):
        self.db.create_stock(self.info)

    def store_stock_info(self):
        self.get_stock_info()
        if self.info:
            self.db_store_stock_info()

if __name__ == "__main__":
    id = "sh603012"
    s = StockQuery(id)
    s.get_stock_info()
