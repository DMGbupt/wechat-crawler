# -*- coding: utf-8 -*-

"""去重模块
"""

from crawlers.items import WeChat
from crawlers.database.wechat_dao import WeChatDao
from crawlers.logs.crawler_logger import spider_logger
from scrapy.exceptions import DropItem

class DuplicateRemoval(object):

    """去重
    """

    def process_item(self, item, spider):
        """去重流程控制
        """

        # 微信去重
        if isinstance(item, WeChat):
            if self.is_duplicate_wechat(item):
                return DropItem("Duplicate news found: %s" % item['article_addr'])
            else:
                return item

    def is_duplicate_wechat(self, news):
        """微信去重
        :param news: 待判断的新闻
        :return: True/False，是否已被保存在数据库中
        """
        db = WeChatDao()
        # 数据库中已包含有相同标题的数据,相同URL时标题也一定相同
        if len(db.load_id("crawl_url", news['article_addr'])) > 0:
            spider_logger.warning("There is a record with the same url of news {0} in the database!"
                                  .format(news['article_addr']))
            return True
        db.close()
        return False
