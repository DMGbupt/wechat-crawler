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

def crawl(spiders, query, start, end, mode):
    spider_logger.info("Start crawling {0} from {1} to {2}".format(query, start, end))
    process = CrawlerProcess(get_project_settings())
    process.crawl(spiders, query=query, start_time=start, end_time=end, crawl_mode=mode)
    process.start()

if __name__ == "__main__":
    # 静态参数设置
    if "-m" in sys.argv: # 爬取模式
        idx = sys.argv.index("-m")
        crawl_mode = int(sys.argv[idx+1])
    else:
        crawl_mode = 1 # 默认全量抓取
    while True:
        # 动态设置公众号爬取顺序
        if "-o" in sys.argv: # 按照各个公众号已爬文章数目递增的顺序来确定公众号的爬取顺序，确保已爬文章少的公众号能被优先爬取
            # 此选项仅会爬取在数据库中有文章记录数的公众号，所以新加入的公众号需先爬取历史数据后才能被该选项爬取到
            conn = MySQLdb.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute("""select media_id from media_info group by media_id order by count(1)""")
            # 以下版本使用公众号的名字作为参数传递，后来发现有点繁琐，改用公众号的序号
            # cur.execute("""select a.name from media as a right join media_info as b on a.id=b.media_id group by b.media_id order by count(1)""")
            result = cur.fetchall()
            gzh_order = [x[0] for x in result]
            cur.close()
        else: # 默认随机爬取所有的公众号
            conn = MySQLdb.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute("""select id from media""")
            result = cur.fetchall()
            gzh_order = [x[0] for x in result]
            random.shuffle(gzh_order) # 打乱公众号排列顺序来随机爬取
            cur.close()
        for gzh_id in gzh_order:
            # 设置各个公众号的爬取起止时间
            end_time = datetime.now()  # 默认截止时间：爬虫启动时
            if "-s" in sys.argv: # 传入start_time
                idx = sys.argv.index("-s")
                start_time = datetime.strptime(sys.argv[idx+1], "%Y/%m/%d/%H:%M:%S")
            elif "-c" in sys.argv:  # 从数据库读取待爬公众号距现在最近的文章发布时间的之前一天作为启动时间，达到增量更新的效果
                # 此选项适用于每轮爬取周期较短时，每个公众号积累的文章数较少，可以一次爬完。若积累文章数较多，则爬取时可能被反爬，会漏掉一些文章
                # 目前不推荐使用，所以才用爬取模式crawl_mode来替代它的效果
                conn = MySQLdb.connect(**DB_CONFIG)
                cur = conn.cursor()
                cur.execute("""select max(publish_time) from media_info where media_id=%s""",(unicode(gzh_id),))
                lasttime = cur.fetchone()[0]
                start_time = lasttime-timedelta(days=1) # 由于数据库里文章的发布时间均是0点，为防止上次爬取当天更新的文章被忽略，需把起始时间提前一天
                cur.close()
            else:
                start_time = end_time-timedelta(days=365) # 默认开始时间，一年之前
            conn = MySQLdb.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute("""select name from media where id=%s""",(unicode(gzh_id),))
            query = cur.fetchone()[0]
            cur.close()
            pool = Pool(processes=1) # 进程池，由于公众号的反爬限制较严，限制为单进程
            pool.apply(crawl, args=('wechat', query, start_time, end_time, crawl_mode))
            pool.close()
            pool.join()
