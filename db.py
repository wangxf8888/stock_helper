#!/usr/bin/python
# -*- coding: utf-8 -*-

import queue
import logging
import time

import pymysql
import stock_query

table_spec = {
    "stock": (
        "sid", "name", "updated_date", "now_price", "open_price", "close_price",
        "high_price", "low_price", "high_limit", "low_limit", "change", "rate",
        "volume", "amount", "swap_rate", "per", "amplitude", "market_value",
        "total_value", "qrr", "pbr", "buy_price", "buy_count", "sold_price",
        "sold_count", "big_in_1", "big_in_2", "big_in_3", "big_in_4",
        "big_in_5", "big_out_1", "big_out_2", "big_out_3", "big_out_4",
        "big_out_5"
    ),
    "user": (
        "id", "password", "level"
    ),
    "self_stock": (
        "id", "user_id", "stock_id", "hold_count", "buy_price", "buy_date"
    )
}


def _mapping_field(record, fields):
    if record is not None and len(record) == len(fields):
        result_dict = {}
        for idx, field in enumerate(fields):
            result_dict[field] = record[idx]
        return result_dict
    return None


class DbUtils:

    def __init__(self, host, port, db, user, passwd, maxsize=1):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.dbName = db
        maxsize = min(maxsize, 300)
        chunk_size = 100
        self.conn_queue = queue.Queue(maxsize=maxsize)
        import threading
        for _ in range(0, maxsize - chunk_size, chunk_size):
            ts = []
            for idx in range(chunk_size):
                t = threading.Thread(target=self._init_conn)
                ts.append(t)
                t.start()

            for t in ts:
                t.join()

        ts = []
        for idx in range(maxsize - self.conn_queue.qsize()):
            t = threading.Thread(target=self._init_conn)
            ts.append(t)
            t.start()

        for t in ts:
            t.join()

    def _init_conn(self):
        while True:
            try:
                conn = self._create_conn()
                self.conn_queue.put(conn)
                break
            except BaseException as e:
                print("init db error, %s" % e)
                time.sleep(1)

    def _create_conn(self):
        return pymysql.connect(host=self.host, port=self.port, user=self.user,
                               passwd=self.passwd,
                               db=self.dbName, charset="utf8",
                               connect_timeout=10)

    def _check_conn(self, conn):
        cursor = conn.cursor()
        try:
            cursor.execute("select 1")
            cursor.fetchone()
            conn.commit()
        except BaseException as e:
            print("check conn exception, %s" % e)
            return False
        finally:
            cursor.close()
        return True

    def borrow_conn(self):
        while True:
            conn = self.conn_queue.get()
            if self._check_conn(conn):
                return conn
            self._init_conn()

    def return_conn(self, conn):
        conn.commit()
        self.conn_queue.put(conn)

    def _query_table(self, table, fields, uniqField, uniq_id):
        sql = "select %s from %s where %s = %s;" % (
            ",".join(fields), table, uniqField, "%s")
        conn = self.borrow_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (uniq_id,))
            record = cursor.fetchone()
            return _mapping_field(record, fields)
        except BaseException as e:
            if not self.logger:
                self.logger.error("query %s by id error %s ", table, e.message)
            print
            e.message
        finally:
            cursor.close()
            self.return_conn(conn)
        return None

    def _list_table(self, table, fields, **filters):
        params = []
        values = [",".join(fields), table]
        sql = "select %s from %s where"
        first_filter = True
        for key, value in filters.items():
            not_filter = False
            if key.startswith("_"):
                not_filter = True
                key = key[1:]
            if not first_filter:
                sql += " and"
            first_filter = False
            if (isinstance(value, list) or isinstance(value, tuple)) and len(
                    value) > 0:
                values.append(key)
                if not_filter:
                    sql += " %s not in ("
                else:
                    sql += " %s in ("

                params.extend(value)
                for _ in range(len(value)):
                    sql += "%s,"
                    values.append("%s")
                sql = sql[:-1] + ")"
            else:
                values.append(key)
                params.append(value)

                values.append("%s")
                if not_filter:
                    sql += " %s != %s"
                else:
                    sql += " %s = %s"

        sql = sql % tuple(values)
        # print sql
        conn = self.borrow_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, tuple(params))
            records = cursor.fetchall()
            if records is not None:
                results = []
                for record in records:
                    results.append(_mapping_field(record, fields))
                return results
        except BaseException as e:
            if not self.logger:
                self.logger.error("list %s error %s ", table, e.message)
        finally:
            cursor.close()
            self.return_conn(conn)
        return None

    def _update_table(self, table, filters, values):
        new_values = []
        params = []
        for key, value in values.items():
            new_values.append("{}={}".format(key, "%s"))
            params.append(value)
        new_values = ",".join(new_values)
        values = [table, new_values]
        sql = "update %s set %s where"
        first_filter = True
        for key, value in filters.items():
            if not first_filter:
                sql += " and"
            first_filter = False
            if (isinstance(value, list) or isinstance(value, tuple)) and len(
                    value) > 0:
                values.append(key)
                sql += " %s in ("
                params.extend(value)
                for _ in range(len(value)):
                    sql += "%s,"
                    values.append("%s")
                sql = sql[:-1] + ")"
            else:
                values.append(key)
                values.append("%s")
                params.append(value)
                sql += " %s = %s"

        sql = sql % tuple(values)
        # print sql
        # print params
        conn = self.borrow_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, tuple(params))
            conn.commit()
            return cursor.rowcount
        except BaseException as e:
            if not self.logger:
                self.logger.error("list %s error %s ", table, e.message)
        finally:
            cursor.close()
            self.return_conn(conn)
        return -1

    def _insert_into_table(self, table, params):
        data_values = "(" + "%s, " * (len(params)) + ")"
        data_values = data_values.replace(', )', ')')

        dbField = params.keys()
        dataTuple = tuple(params.values())
        dbField = str(tuple(dbField)).replace("'", '')
        conn = self.borrow_conn()
        cursor = conn.cursor()
        sql = """ insert into %s %s values %s """ % (
            table, dbField, data_values)

        print(sql)

        try:
            cursor.execute(sql, dataTuple)
            conn.commit()
            return True
        except BaseException as e:
            print("insert {} error {}".format(table, e.message))
        finally:
            cursor.close()
            self.return_conn(conn)
        return False

    def create_stock(self, stock):
        table = "stock"
        return self._insert_into_table(table, stock)

    def update_stock(self, filters, values):
        table = "stock"
        return self._update_table(table, filters, values)

    def query_stock(self, id):
        table = "stock"
        return self._query_table(table, table_spec[table], "id", id)


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 3306
    db = "ais"
    user = "ais"
    passwd = "ais"
    globalDb = DbUtils(host, port, db, user, passwd)
    id = "sz300761"
    s = stock_query.StockQuery(id)
    r = s.get_stock_info()
    print(r)
    globalDb.create_stock(r)
