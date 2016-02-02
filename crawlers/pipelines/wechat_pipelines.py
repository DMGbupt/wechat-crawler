# -*- coding: utf-8 -*-

"""微信公众号持久化类
"""

from crawlers.items import WeChat
from crawlers.database.wechat_dao import WeChatDao
from crawlers.logs.crawler_logger import spider_logger

class WeChatPipeline(object):
    """微信公众号持久化类
    """

    def __init__(self):
        self.db = WeChatDao()

    def process_item(self, item, spider):
        """缓存WeChat
        """
        if not isinstance(item, WeChat):
            return item
        # 检查必要属性
        for attr in ('crawl_time', 'title', 'website', 'publish_time', 'content','icon'):
            if not item[attr]:
                spider_logger.warning("[wechat_pipeline] Item of {0} lack {1}".format(item['url'], attr))
                return
        # 填充非必要属性
        for attr in ('digest', 'author', 'source', 'keyword', 'target_topic'):
            if attr not in item:
                item[attr] = None
        # 拼接target_topic,keyword,author
        for attr in ('target_topic', 'keyword', 'author'):
            if item[attr]:
                item[attr] = "".join(topic+"&" for topic in item[attr])

        # 保存
        self.db.save(item)

    def close_spider(self, spider):
        self.db.close()