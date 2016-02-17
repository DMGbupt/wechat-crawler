# -*- coding: utf-8 -*-

"""爬虫启动脚本
   约定在整个工程内使用统一的时间格式：%Y/%m/%d/%H:%M:%S以方便传递时间，例如2015/8/13/16:00:00
"""

import sys
import time
import MySQLdb
import random
from datetime import datetime, timedelta
from multiprocessing import Pool
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawlers.settings import DB_CONFIG
from crawlers.logs.crawler_logger import spider_logger
from crawlers.topics.wechat import WECHAT_LIST

def crawl(spiders, query, start, end, mode):
    spider_logger.info("Start crawling {0} from {1} to {2}".format(query, start, end))
    process = CrawlerProcess(get_project_settings())
    process.crawl(spiders, query=query, start_time=start, end_time=end, crawl_mode=mode)
    process.start()

if __name__ == "__main__":
    # 时间
    start_time = None
    crawl_mode = None
    if "-s" in sys.argv: # 传入start_time
        idx = sys.argv.index("-s")
        start_time = datetime.strptime(sys.argv[idx+1], "%Y/%m/%d/%H:%M:%S")
    if "-c" in sys.argv:  # 从数据库读取距现在最近的爬取时间作为启动时间
        # 此选项用于宕机重启，目前的做法不能保证宕机前最后一次爬取完成，会漏掉一部分新闻
        conn = MySQLdb.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("select max(create_time) from media_info")
        start_time = cur.fetchone()[0]
    if "-o" in sys.argv: # 按照各个公众号已爬文章数目递增的顺序来确定公众号的爬取顺序，确保已爬文章少的公众号能被优先爬取
        conn = MySQLdb.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("select media_id from media_info group by media_id order by count(1)")
        result = cur.fetchall()
        search_order = [x[0] for x in result]
    if "-m" in sys.argv: # 爬取模式
        idx = sys.argv.index("-m")
        crawl_mode =sys.argv[idx+1]

    while True:
        end_time = datetime.now()  # 默认截止时间：爬虫启动时
        if not start_time:
            start_time = datetime.now()-timedelta(days=100) # 默认开始时间，100天以前
        if not search_order:
            search_order = range(1,51)
            random.shuffle(search_order) # 默认随机排列待抓取公众号
        if not crawl_mode:
            crawl_mode = 1 # 默认全量抓取
        for ind in search_order:
            pool = Pool(processes=1) # 进程池，由于公众号的反爬限制较严，限制为单进程
            pool.apply(crawl, args=('wechat', WECHAT_LIST[ind-1], start_time, end_time, crawl_mode))
            pool.close()
            pool.join()
