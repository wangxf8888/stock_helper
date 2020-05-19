#!/usr/bin/python
# -*- coding: utf-8 -*-

import multiprocessing
import time
import stock
import threading
import config

# 自选股
self_sids = []


def is_open_stock():
    t = int(time.strftime("%H%M%S"))
    day = time.strftime("%A")
    if (t > 91600 and t < 113100) or (t > 130000 and t < 150100) \
            and (day != "Saturday" and day != "Sunday"):
        return True
    else:
        return False


def is_self_stock(sid):
    global self_sids
    for id in self_sids:
        if id["sid"] == sid:
            return True
    return False


def query_data(sid):
    status = True
    info = None
    upTime = 0
    downTime = 0
    self_time = 0
    while True:
        self_time += 1
        t = int(time.strftime("%H%M%S"))
        if is_open_stock():
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
                upTime = 0
                changePrice = float(sinfo["now_price"]) - float(refUpPrice)
                changeRate = changePrice * 100 / float(refUpPrice)
                print_information(sinfo)
            if downTime >= 5:
                downTime = 0
                changePrice = float(sinfo["now_price"]) - float(refDownPrice)
                changeRate = changePrice * 100 / float(refDownPrice)
                print_information(sinfo)
            if self_time > 10:
                self_time = 0
                for self_sid in self_sids:
                    if self_sid["sid"] == info["sid"]:
                        print_information(sinfo)
        else:
            if status == True:
                status = False
                info = stock.get_stock_info(sid)
                print("股市已休市")
                print_information(info)

        time.sleep(3)


def print_information(stock):
    t = time.strftime("%H:%M:%S")
    b = "\033[0m"
    if float(stock["rate"]) > 0:
        a = "\033[0;31;40m"
    if float(stock["rate"]) < 0:
        a = "\033[0;32;40m'"
    if float(stock["rate"]) == 0:
        a = "\033[0;37;40m"
    if is_self_stock(stock["sid"]):
        for sid in self_sids:
            if sid["sid"] == stock["sid"]:
                buy_price = sid["price"]
                buy_count = sid["num"]
        print("{}{}:{} {} 当前价/成本价{}/{}  盈利{:.2f}{}"
              .format(a,
                      t,
                      stock["name"],
                      stock["sid"],
                      float(stock["now_price"]),
                      float(buy_price),
                      float(float(stock["now_price"]) - float(
                          buy_price)) * buy_count,
                      b))
    else:
        print("{}{}:{} {} 当前价格{} 涨跌幅{:.2f}%{}"
              .format(t,
                      stock["name"],
                      stock["sid"],
                      float(stock[
                                "now_price"]),
                      float(stock["rate"]),
                      b))
    # print('\033[0m')


def get_valid_sids():
    global self_sids
    sids = config.info["key_stocks"]
    self_sids = config.info["self_stocks"]
    for sid in self_sids:
        sids.append(sid["sid"])
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
