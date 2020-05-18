#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import argparse
import urllib2
import json
import sys
import time
import paramiko
import threading
import textwrap
import MySQLdb
import signal
import subprocess
import random
import tempfile
import curses
from curses import wrapper
import logging
from logging.handlers import RotatingFileHandler

########################## migration ui ##########################
max_tilte_pad_row = 2
max_list_pad_row = 1000
max_statistics_pad_row = 5
max_pad_column = 200
g_ui_running = True
g_title_pad_rect_height = 1
g_statisticas_pad_rect_height = 3
g_fmt = "{:<3s} {:^20s} {:^20s} {:^22s} {:^20s} {:^20s} {:^40s}\n"


def get_short_volume_id(vol_id):
    if len(vol_id) > 20:
        return vol_id[0:16] + "..."

    return vol_id


class Pad:
    prow = 0
    pcol = 0
    sminrow = 0
    smincol = 0
    smaxrow = 0
    smaxcol = 0
    name = ""

    def __init__(self, logger, height, width, name=""):
        self.logger = logger
        self.height = height
        self.width = width
        self.name = name
        self.__pad = curses.newpad(height, width)

    def refresh(self):
        # self.logger.info("{} to refresh({}, {}, {}, {}, {}, {})".format(self.name, self.prow, self.pcol, self.sminrow, self.smincol, self.smaxrow, self.smaxcol))
        try:
            self.__pad.refresh(self.prow, self.pcol, self.sminrow, self.smincol,
                               self.smaxrow, self.smaxcol)
        except BaseException as e:
            self.logger.error("{}".format(e))

    def setRect(self, prow, pcol, sminrow, smincol, smaxrow, smaxcol):
        # self.logger.info("{} to setRect({}, {}, {}, {}, {}, {})".format(self.name, prow, pcol, sminrow, smincol, smaxrow, smaxcol))
        self.prow = prow
        self.pcol = pcol
        self.sminrow = sminrow
        self.smincol = smincol
        self.smaxrow = smaxrow
        self.smaxcol = smaxcol

    def clear(self):
        try:
            self.__pad.clear()
        except BaseException as e:
            self.logger.error("{}".format(e))

    def getHeight(self):
        return self.height

    def addStr(self, str, fmt=curses.A_NORMAL):
        try:
            self.__pad.addstr(str, fmt)
        except BaseException as e:
            self.logger.error("{} {}".format(self.name, e))

    def scroll(self, enable):
        try:
            self.__pad.scrollok(enable)
        except BaseException as e:
            self.logger.error("{}".format(e))


class TxtPad(Pad):
    text = ""
    fmt = curses.A_NORMAL

    def __init__(self, logger, height, width, name=""):
        Pad.__init__(self, logger, height, width, name)

    def addText(self, str, fmt=curses.A_NORMAL):
        self.text += str
        self.fmt = fmt
        # self.logger.info("{} to addText({}), strLen= {}".format(self.name, str, len(str)))
        if len(str) < self.width:
            Pad.addStr(self, str, fmt)
        else:
            self.logger.error(
                "{} to addText, the length of text too long".format(self.name))

    def setText(self, str, fmt=curses.A_NORMAL):
        # self.logger.info("{} to setText({})".format(self.name, str))
        Pad.clear(self)
        self.text = ""
        self.addText(str, fmt)

    def clear(self):
        self.text = ""
        self.fmt = curses.A_NORMAL
        Pad.clear(self)


class ListPad(Pad):
    itemcount = 0

    def __init__(self, logger, height, width, name=""):
        # logger.info("ListPad(height: {}, width: {})".format(height, width))
        Pad.__init__(self, logger, height, width, name)
        Pad.scroll(self, True)

    def clearAllItem(self):
        Pad.clear(self)
        self.itemcount = 0

    def addItem(self, str):
        # self.logger.info("addItem({}), strLen={}".format(str, len(str)))
        Pad.addStr(self, str)
        self.itemcount += 1

    def scrollUp(self):
        # if self.itemcount > self.height and self.itemcount - self.height - 1 > self.prow and self.prow < self.itemcount - 1:
        if self.prow < self.itemcount - 1:
            self.prow += 1
            Pad.refresh(self)

    def scrollDown(self):
        if self.prow > 0:
            self.prow -= 1
            Pad.refresh(self)


class UpdateDataThread(threading.Thread):
    def __init__(self, logger, title_pad, list_pad, statistics_pad, lock):
        threading.Thread.__init__(self)
        self.logger = logger
        self.title_pad = title_pad
        self.list_pad = list_pad
        self.statistics_pad = statistics_pad
        self.lock = lock

    def run(self):
        global g_ui_running
        global g_fmt
        global g_migrate_volume

        # 当前命令
        cmd = ""
        for s in sys.argv:
            cmd += " " + s

        while g_ui_running:
            try:
                i = 0
                failed_cnt = 0
                success_cnt = 0

                self.lock.acquire()
                self.list_pad.clearAllItem()
                for dest_cluster_name, dict_pool in g_migrate_volume.items():
                    for dest_pool_id, dict_tenant in dict_pool.items():
                        for tenant_id, dict_vol in dict_tenant.items():
                            for vol_id, t in dict_vol.items():
                                msg = "-"
                                short_vol_id = get_short_volume_id(vol_id)
                                if not t:
                                    self.list_pad.addItem(
                                        g_fmt.format(str(i), short_vol_id, "-",
                                                     "-", "-", "-", "-"))
                                else:
                                    result = t.get_migrate_result()
                                    if result == False:
                                        failed_cnt += 1
                                        msg = t.get_migrate_errmsg()
                                    elif result == True:
                                        success_cnt += 1
                                        msg = "success"

                                    m = t.get_migration()
                                    if m:
                                        short_vol_id = get_short_volume_id(
                                            m["volume_id"])
                                        self.list_pad.addItem(
                                            g_fmt.format(str(i), short_vol_id,
                                                         m["id"], m["step"],
                                                         m["status"],
                                                         str(m["percent"]),
                                                         msg))
                                    else:
                                        self.list_pad.addItem(
                                            g_fmt.format(str(i), short_vol_id,
                                                         "-", "-", "-", "-",
                                                         msg))

                                i += 1

                self.statistics_pad.clear()
                self.statistics_pad.addText(cmd.strip() + "\n")
                self.statistics_pad.addText(
                    "migration statistics: successCnt/TotalCnt={}/{}, failedCnt/TotalCnt={}/{}, unfinishedCnt/TotalCnt={}/{}\n".format(
                        success_cnt, i, failed_cnt, i,
                        i - success_cnt - failed_cnt, i),
                    curses.A_BOLD | curses.A_REVERSE)
                self.statistics_pad.addText(
                    "migration completed, press key 'q' to exit",
                    curses.color_pair(1) | curses.A_BOLD | curses.A_BLINK)
                self.lock.release()
                time.sleep(1)

            except BaseException as e:
                self.logger.warning("{}".format(e))
                break


def init_pad(logger):
    global g_fmt
    global g_title_pad_rect_height
    global g_statisticas_pad_rect_height

    screen_row, screen_column = screen.getmaxyx()
    title_pad = TxtPad(logger, max_tilte_pad_row, max_pad_column, "title_pad")
    title_pad.setText(
        g_fmt.format("seq", "volume_id", "migrate_id", "step", "status",
                     "percent", "result"), curses.A_BOLD | curses.A_UNDERLINE)
    list_pad = ListPad(logger, max_list_pad_row, max_pad_column, "list_pad")
    statistics_pad = TxtPad(logger, max_statistics_pad_row, max_pad_column,
                            "statistics_pad")
    return title_pad, list_pad, statistics_pad


def pad_refresh(logger, title_pad, list_pad, statistics_pad, lock):
    global g_migrate_running
    global g_title_pad_rect_height
    global g_statisticas_pad_rect_height
    screen_row, screen_column = screen.getmaxyx()

    # title_pad
    title_pad.setRect(0, 0, 0, 0, g_title_pad_rect_height - 1,
                      screen_column - 1)

    # list_pad
    sminrow = g_title_pad_rect_height
    if screen_row > g_statisticas_pad_rect_height + 1:
        smaxrow = screen_row - g_statisticas_pad_rect_height - 1
        if sminrow >= smaxrow:
            smaxrow = sminrow
    else:
        smaxrow = g_statisticas_pad_rect_height + 1 - screen_row

    if sminrow >= screen_row:
        sminrow = screen_row - 1
        smaxrow = screen_row - 1
    elif smaxrow >= screen_row:
        smaxrow = screen_row - 1
    list_pad.setRect(list_pad.prow, list_pad.pcol, sminrow, 0, smaxrow,
                     screen_column - 1)

    # statistics_pad
    if screen_row > 2:
        if g_migrate_running:
            statistics_pad.setRect(0, 0,
                                   screen_row - g_statisticas_pad_rect_height + 1,
                                   0, screen_row - 1, screen_column - 1)
        else:
            statistics_pad.setRect(0, 0,
                                   screen_row - g_statisticas_pad_rect_height,
                                   0, screen_row - 1, screen_column - 1)
    else:
        statistics_pad.setRect(0, 0, 0, 0, 0, screen_column - 1)

    lock.acquire()
    title_pad.refresh()
    statistics_pad.refresh()
    list_pad.refresh()
    lock.release()


def display(screen):
    pad_lock = threading.Lock()
    global logger
    global g_migrate_running
    global g_ui_running
    try:
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        title_pad, list_pad, statistics_pad = init_pad(logger)

        t = UpdateDataThread(logger, title_pad, list_pad, statistics_pad,
                             pad_lock)
        t.start()

        screen.timeout(1000)
        while True:
            c = screen.getch()
            if not g_migrate_running and c == ord('q'):
                g_ui_running = False
                break
            if c == curses.KEY_DOWN:
                logger.info("scrollUp")
                list_pad.scrollUp()
            elif c == curses.KEY_UP:
                list_pad.scrollDown()
                logger.info("scrollDown")

            pad_refresh(logger, title_pad, list_pad, statistics_pad, pad_lock)

    except BaseException as e:
        logger.error("{}".format(e))

    finally:
        curses.curs_set(1)
        curses.endwin()
        t.join()
##################### end of migration ui #########################

def init_logger(logger, log_cfg):
    # 若日志文件目录不存在则创建
    date_time = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
    tup = date_time.split("_")
    seq = (log_cfg["filepath"], tup[0])
    path = "/".join(seq)
    if not os.path.isdir(path):
        os.makedirs(path, 0755)

    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(asctime)s - %(filename)s [line:%(lineno)d] - %(levelname)s - %(message)s')

    # 定义一个RotatingFileHandler，设置日志文件个数和最大大小
    filename = path +"/migration.log"
    rHandler = RotatingFileHandler(filename, maxBytes = log_cfg["filesize"], backupCount = log_cfg["max_file_count"])
    rHandler.setLevel(logging.INFO)
    rHandler.setFormatter(fmt)
    logger.addHandler(rHandler)
    return filename


def new_console_hdr():
    # 将日志输出到屏幕上
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    fmt = logging.Formatter('%(message)s')
    console.setFormatter(fmt)
    return console


def logger_add_hdr(logger, hdr):
    logger.addHandler(hdr)


def logger_remove_hdr(logger, hdr):
    logger.removeHandler(hdr)


def print_migrate_result(logger, migrate_volume, log_file):
    success_migrate = []
    failed_migrate = []
    unfinished_migrate = []
    for _, dict_pool in migrate_volume.items():
        for _, dict_tenant in dict_pool.items():
            for _, dict_vol in dict_tenant.items():
                for vol_id, t in dict_vol.items():
                    if t:
                        result = t.get_migrate_result()
                        if result == True:
                            success_migrate.append(vol_id)
                        elif result == False:
                            failed_migrate.append(vol_id)
                        elif result == None:
                            unfinished_migrate.append(vol_id)
    logger.info("success: {}".format(success_migrate))
    logger.info("failed: {}".format(failed_migrate))
    logger.info("unfinished: {}".format(unfinished_migrate))
    logger.info("read the migration log file for detail information: {}".format(log_file))

if __name__ == "__main__":
    console = new_console_hdr()

    logger_remove_hdr(logger, console)
    screen = curses.initscr()
    wrapper(display)
    logger_add_hdr(logger, console)

    t.join()
    print_migrate_result(logger, g_migrate_volume, log_file)
    logger.info("migration completed!")
    sys.exit(0)
