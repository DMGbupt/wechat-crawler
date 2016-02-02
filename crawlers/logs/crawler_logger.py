# -*- coding: utf-8 -*-

"""日志模块，使用python原生的logging模块，允许设置5个log等级，支持多线程。但是多进程可能会写冲突，后续可考虑加锁
   目前为每一个爬虫进程引入一个spider_logger，生成两个日志，详见注释
   引入：from crawler_logger import spider_logger
   使用：spider_logger.INFO("log level INFO")
"""

import logging
import logging.handlers
import datetime
import os
from crawlers.settings import LOG_DIR


class SpiderLogger(object):

    def __init__(self, logger="Spider"):
        """需指定保存日志的文件路径LOG_DIR，logger名字全局继承（默认Spider），
           存储每小时的爬虫记录和每天的错误日志
        """

        # 创建logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)
        log_path = LOG_DIR+"/%s" % datetime.datetime.now().strftime("%Y-%m")
        if not os.path.exists(log_path):
            os.makedirs(log_path)

        # 创建一个日志handler，按小时写入日志文件
        file_behavior = logging.handlers.TimedRotatingFileHandler(
            log_path+"/SpiderBehavior-%s.log" % datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'H', 1, 0)
        file_behavior.setLevel(logging.INFO)

        # 创建一个错误报告handler，按日写入日志文件
        file_daily = logging.handlers.TimedRotatingFileHandler(
            log_path+"/ErrorReport-%s.log" % datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), 'D', 1, 0)
        file_daily.setLevel(logging.ERROR)

        # 定义handler的输出格式formatter，可采用以下格式：
        # %(asctime)s       年-月-日 时-分-秒,毫秒
        # %(filename)s      文件名，不含目录
        # %(pathname)s      目录名，完整路径
        # %(funcName)s      函数名
        # %(levelname)s     级别名
        # %(lineno)d        行号
        # %(module)s        模块名
        # %(message)s       消息体
        # %(name)s          日志模块名
        # %(process)d       进程id
        # %(processName)s   进程名
        # %(thread)d        线程id
        # %(threadName)s    线程名
        formatter = logging.Formatter(
            '%(levelname)s - %(processName)s - %(module)s - %(asctime)s - %(message)s')

        file_behavior.setFormatter(formatter)
        file_daily.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(file_behavior)
        self.logger.addHandler(file_daily)

    def getLog(self):
        return self.logger

spider_logger = SpiderLogger().getLog()
