# -*- coding: utf-8 -*-

"""Data Access Object
"""

import MySQLdb

from crawlers.settings import DB_CONFIG


def get_connection():
    """获得数据库连接
    :return:数据库连接
    """
    return MySQLdb.connect(**DB_CONFIG)


class Dao(object):
    """Dao的基类
    """
    def __init__(self):
        self.conn = get_connection()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        self.close()
