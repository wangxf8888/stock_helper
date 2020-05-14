#!/usr/bin/python
# -*- coding: utf-8 -*-

import multiprocessing
import time
import stock
import threading
import config

# 所有股票代码
sids = []
db = stock.StockDB()


def query_data(sid):
    status = True
    info = None
    upTime = 0
    downTime = 0
    upRate = 0
    refPrice = 0
    while True:
        t = int(time.strftime("%H%M%S"))
        day = time.strftime("%A")
        if (t > 91600 and t < 113100) or (t > 130000 and t < 150100) \
                and (day != "Saturday" and day != "Sunday"):
            sinfo = stock.get_stock_info(sid)
            if not info:
                info = sinfo
            if float(sinfo["now_price"]) > float(info["now_price"]):
                if upTime == 0:
                    refUpPrice = info["now_price"]
                upTime += 1
                info = sinfo
                downTime = 0
            elif float(sinfo["now_price"]) < float(info["now_price"]):
                if downTime == 0:
                    refDownPrice = info["now_price"]
                downTime += 1
                upTime = 0
                info = sinfo
            else:
                upTime = 0
                downTime = 0
                info = sinfo

            if upTime >= 5:
                changePrice = float(sinfo["now_price"]) - float(refUpPrice)
                changeRate = changePrice * 100 / float(refUpPrice)
                print("{}:{}{}持续拉升，当前价格{}，上升幅度{:.2f}%".format(t,
                                                              sinfo["name"],
                                                              sinfo["sid"],
                                                              sinfo[
                                                                  "now_price"],
                                                              changeRate))
            if downTime >= 5:
                changePrice = float(sinfo["now_price"]) - float(refDownPrice)
                changeRate = changePrice * 100 / float(refDownPrice)
                print("{}:{}{}持续下跌，当前价格{}，下跌幅度{:.2f}%".format(t,
                                                              sinfo["name"],
                                                              sinfo["sid"],
                                                              sinfo[
                                                                  "now_price"],
                                                              changeRate))

        else:
            if status == True:
                status = False
                info = stock.get_stock_info(sid)
                print("股市已休市 sid {}，今日涨跌幅 {} %".format(sid,
                                                       info["rate"]))
        time.sleep(3)


def get_valid_sids():
    sids = config.info["key_stocks"]
    print(sids)


if __name__ == "__main__":
    get_valid_sids()
    sids.append("sz300432")
    sids.append("sh600789")
    thread_list = []

    for sid in sids:
        t = multiprocessing.Process(target=query_data,
                                    args=(sid,))
        thread_list.append(t)
        t.start()

    for t in thread_list:
        t.join()
