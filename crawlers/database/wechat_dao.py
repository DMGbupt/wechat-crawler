# -*- coding: utf-8 -*-

from dao import Dao
from crawlers.logs.crawler_logger import spider_logger

class WeChatDao(Dao):

    """wechatDao
    """
    _sql_load_media_id = """select id from media where {0} = %s"""
    _sql_save_wechat = """insert into media_info(title, digest, content, icon, image, publish_time, media_id, crawl_website, crawl_url)values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    def save(self, item):
        """将微信公众号存入数据库
        """
        cur = self.conn.cursor()
        try:
            cur.execute(WeChatDao._sql_load_media_id.format("name"), (unicode(item['source']),))
            item_id = cur.fetchone()[0]
            item["media_id"] = item_id
            # 准备参数
            param_item = (item['title'], item['digest'], item['content'], item['icon'], item['image_path'], item['publish_time'], item['media_id'], item['source'], item['article_addr'])
            # 插入微信公众号
            cur.execute(WeChatDao._sql_save_wechat, param_item)
            self.conn.commit()
        except Exception, e:
            spider_logger.warning("[MySQL] Flush wechat to database failed, because of {0} !".format(e))
            self.conn.rollback()
        finally:
            cur.close()

    
    _sql_load_id = """select id from media_info where {0} = %s"""
    
    def load_id(self, attribute, value, size=None):
        """选择attribute为value的行的id
        :param attribute: 属性
        :param value: 值
        :param size: 返回结果条数
        :return: select结果
        """
        cur = self.conn.cursor()
        cur.execute(self._sql_load_id.format(attribute), (unicode(value),))
        rel = cur.fetchmany(size)
        cur.close()
        return rel
