# -*- coding: utf-8 -*-

# Scrapy settings for crawlers project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'skyystock'
SPIDER_MODULES = ['crawlers.spiders']
DATA_BASE = "/home/plustock/data/crawler"

# 下载器中间件
DOWNLOADER_MIDDLEWARES = {
    'crawlers.middlewares.random_useragent.RandomUserAgent': 100,
    #'crawlers.middlewares.click_interval.ClickInterval': 110,
    #'crawlers.middlewares.check_antispider.CheckAntispider': 200,
    #'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': None,
    }

# 持久化组件
ITEM_PIPELINES = {
    'crawlers.pipelines.duplicate_removal.DuplicateRemoval': 100,
    'crawlers.pipelines.image_pipelines.ArticleImagesPipeline': 200,
    'crawlers.pipelines.image_pipelines.IconPipeline': 210,
    'crawlers.pipelines.wechat_pipelines.WeChatPipeline': 500,
    }

# 代理配置：当PROXY_SPIDERS列表中爬虫，发出符合PROXY_URL中任一正则表达式的请求时，会使用代理完成请求

# 爬取速度控制
DOWNLOAD_DELAY =20 # 下载延迟
DOWNLOAD_TIMEOUT = 120  # 下载超时，单位秒
# 自动限速：开启
AUTOTHROTTLE_ENABLED = True
CONCURRENT_REQUESTS = 1
AUTOTHROTTLE_START_DELAY = 20
AUTOTHROTTLE_MAX_DELAY = 120
CONCURRENT_REQUESTS_PER_IP = 1
#CONCURRENT_REQUESTS_PER_DOMAIN = 4
#COOKIES_DEBUG = True
# 图片
IMAGES_EXPIRES = 10
IMAGES_STORE = DATA_BASE+"/images/media"

# 日志
LOG_DIR = DATA_BASE+"/logs"
# LOG_FILE = LOG_DIR+"/log.log"
# LOG_LEVEL = "INFO"

# 数据库连接信息
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'passwd': '1qaz2wsx',
    'db': 'goblin',
    'charset': 'utf8'
    }

# 索引路径
INDEX_DIR = DATA_BASE+"/index_storage"

# 自定义词典路径
DICT = "./crawlers/topics/dict.txt"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#  USER_AGENT = 'crawlers (+http://www.yourdomain.com)'