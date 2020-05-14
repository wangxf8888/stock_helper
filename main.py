#!/usr/bin/python
# -*- coding: utf-8 -*-

import multiprocessing
import time
import stock
import threading
import config

# 所有股票代码
sids = []


def query_data(sid):
    status = True
    info = None
    upTime = 0
    downTime = 0
    nochangeTime = 0
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
                nochangeTime += 1
                info = sinfo

            if upTime >= 5:
                upTime = 0
                changePrice = float(sinfo["now_price"]) - float(refUpPrice)
                changeRate = changePrice * 100 / float(refUpPrice)
                print_information(t, sinfo)
            if downTime >= 5:
                downTime = 0
                changePrice = float(sinfo["now_price"]) - float(refDownPrice)
                changeRate = changePrice * 100 / float(refDownPrice)
                print_information(t, sinfo)
            if nochangeTime >= 10:
                nochangeTime = 0
                print_information(t, sinfo)
        else:
            if status == True:
                status = False
                info = stock.get_stock_info(sid)
                print("股市已休市")
                print_information(t, info)
        time.sleep(3)


def print_information(t, stock):
    if float(stock["rate"]) > 0:
        print('\033[0;31;40m')
    if float(stock["rate"]) < 0:
        print('\033[0;32;40m')
    if float(stock["rate"]) == 0:
        print('\033[0;37;40m')
    print("{}:{} {} 当前价格{} 涨跌幅{:.2f}%".format(t,
                                              stock["name"],
                                              stock["sid"],
                                              float(stock["now_price"]),
                                              float(stock["rate"])))
    print('\033[0m')


def get_valid_sids():
    sids = config.info["key_stocks"]
    print(sids)
    return sids


if __name__ == "__main__":
    sids = get_valid_sids()
    thread_list = []

    for sid in sids:
        t = multiprocessing.Process(target=query_data,
                                    args=(sid,))
        thread_list.append(t)
        t.start()

    for t in thread_list:
        t.join()
