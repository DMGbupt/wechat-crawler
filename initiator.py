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

def crawl(spiders, query, start, end, page):
    spider_logger.info("Start crawling {0} from {1} to {2}".format(query, start, end))
    process = CrawlerProcess(get_project_settings())
    process.crawl(spiders, query=query, start_time=start, end_time=end, index_pages=page)
    process.start()

if __name__ == "__main__":
    # 参数设置
    if "-t" in sys.argv: # "t" for total: 指定抓取公众号目录页的页数，1到10之间的整数（搜狗微信公众号搜索每次会返回一共10页的文章目录数据）
        # 此选项指定爬取的目录页数来实现增量爬取，只抓取最新的几页目录，减少文章的重复爬取，避免搜狗反爬
        idx = sys.argv.index("-t")
        index_pages = int(sys.argv[idx+1])
    else: # 默认10页目录全爬取
        index_pages = 10
    while True:
        # 参数设置，每轮爬取时动态设置公众号的爬取顺序
        if "-n" in sys.argv: # "n" for number: 按照各个公众号已爬文章数目递增的顺序来确定公众号的爬取顺序，确保已爬文章少的公众号能被优先爬取
            # 此选项仅会爬取在数据库中有文章记录数的公众号，所以新加入的公众号需先爬取历史数据后才能被该选项爬取到
            conn = MySQLdb.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute("""select media_id from media_info group by media_id order by count(1)""")
            # 以下版本曾使用公众号的名字作为参数传递，但是后续较繁琐，仅供参考
            # cur.execute("""select a.name from media as a right join media_info as b on a.id=b.media_id group by b.media_id order by count(1)""")
            result = cur.fetchall()
            gzh_order = [x[0] for x in result]
            cur.close()
        elif "-p" in sys.argv: # "p" for publish time: 按照各个公众号已爬文章里的最新发布时间递增顺序来确定公众号的爬取顺序，确保距离上次爬取间隔较长的公众号能被优先爬取
            # 此选项仅会爬取在数据库中有文章记录数的公众号，所以新加入的公众号需先爬取历史数据后才能被该选项爬取到
            conn = MySQLdb.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute("""select media_id from media_info group by media_id order by max(publish_time)""")
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
            if "-s" in sys.argv: # "s" for start time: 传入起始时间字符串，需按照%Y/%m/%d/%H:%M:%S格式
                idx = sys.argv.index("-s")
                start_time = datetime.strptime(sys.argv[idx+1], "%Y/%m/%d/%H:%M:%S")
            elif "-c" in sys.argv:  # "c" for continue: 从数据库读取待爬公众号距现在最近的文章发布时间的之前一天作为启动时间，达到持续更新的效果
                # 此选项适用于每轮爬取周期较短时，每个公众号积累的文章数较少，可以一次爬完。若积累文章数较多，则爬取时可能被反爬，会漏掉一些文章
                # 目前不推荐使用，所以才用"-t"参数指定爬取的目录页数来替代它的效果
                conn = MySQLdb.connect(**DB_CONFIG)
                cur = conn.cursor()
                cur.execute("""select max(publish_time) from media_info where media_id=%s""",(unicode(gzh_id),))
                lasttime = cur.fetchone()[0]
                start_time = lasttime-timedelta(days=1) # 由于数据库里文章的发布时间均是0点，为防止上次爬取当天更新的文章被忽略，需把起始时间提前一天
                cur.close()
            else:
                start_time = end_time-timedelta(days=365) # 默认起始时间，一年之前
            conn = MySQLdb.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute("""select name from media where id=%s""",(unicode(gzh_id),))
            query = cur.fetchone()[0] # 获取公众号的名字，作为搜索词
            cur.close()
            pool = Pool(processes=1) # 进程池，由于公众号的反爬限制较严，限制为单进程
            pool.apply(crawl, args=('wechat', query, start_time, end_time, index_pages))
            pool.close()
            pool.join()
