#!/usr/bin/python
# -*- coding: utf-8 -*-

import multiprocessing
import time
import stock_query
import threading

config = {
    "header": ["sh000", "sh002", "sh600", "sz000", "sz002", "sz300"]
}

# 所有股票代码
sids = []


def store_data(sid):
    pass


def parse_data(sid):
    pass


def check_valid_sid(sid):
    r = stock_query.get_stock_basic_info(sid)
    if r:
        sids.append(sid)


def get_valid_sids():
    thread_list = []
    for s in config["header"]:
        for code in range(0, 999):
            sid = "{}{:0>3d}".format(s, code)
            t = threading.Thread(target=check_valid_sid,
                                 args=(sid,))
            thread_list.append(t)
            t.start()

    for t in thread_list:
        t.join()


if __name__ == "__main__":
    get_valid_sids()
    t1 = multiprocessing.Process(target=store_data)
    t1.start()
    t2 = multiprocessing.Process(target=parse_data)
    t2.start()
    t1.join()
    t2.join()
