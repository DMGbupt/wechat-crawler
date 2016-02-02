# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Base(scrapy.Item):

    """需抽取的基本信息
    """

    # 主键：数据库自动生成
    id = scrapy.Field()
    # 必须属性
    crawl_time = scrapy.Field()  # 爬取时间：datatime类型
    url = scrapy.Field()
    title = scrapy.Field()
    website = scrapy.Field()
    publish_time = scrapy.Field()  # 发布时间：datatime类型
    content = scrapy.Field()
    # snapshot = scrapy.Field() 暂不考虑
    # 非必要属性
    digest = scrapy.Field()  # 爬取时可不填写


class News(Base):

    """新闻
    """

    # 可选属性
    author = scrapy.Field()  # 列表：本新闻的记者、编辑等
    source = scrapy.Field()
    keyword = scrapy.Field()  # 列表：本新闻的关键字
    target_topic = scrapy.Field()  # 列表：本新闻相关的发布主题
    # 图片相关
    image_urls = scrapy.Field()  # 列表：本新闻相关的图片链接
    images = scrapy.Field()  # 图片列表，每张图片包含path和url属性


class Blog(Base):

    """博客
    """

    # 可选属性
    author = scrapy.Field()  # 博主
    source = scrapy.Field()
    keyword = scrapy.Field()  # 列表：本博客的关键字
    target_topic = scrapy.Field()  # 列表：本博客相关的发布主题
    # 图片相关
    image_urls = scrapy.Field()  # 列表：本博客相关的图片链接
    images = scrapy.Field()  # 图片列表，每张图片包含path和url属性


class YanBao(Base):

    """研报
    """

    # 可选属性
    author = scrapy.Field()
    source = scrapy.Field()
    keyword = scrapy.Field()  # 列表：本研报的关键字
    target_topic = scrapy.Field()  # 列表：本研报相关的发布主题


class Notice(Base):

    """公告
    """

    # 可选属性
    author = scrapy.Field()
    source = scrapy.Field()
    keyword = scrapy.Field()  # 列表：本公告的关键字
    target_topic = scrapy.Field()  # 列表：本公告相关的发布主题


class WeChat(Base):

    """微信
    """

    # 可选属性
    author = scrapy.Field()
    keyword = scrapy.Field()  # 列表：本公告的关键字
    target_topic = scrapy.Field()  # 列表：本公告相关的发布主题
    source = scrapy.Field()
    media_id = scrapy.Field()  # 媒体的公众号id
    #  图片相关
    image_urls = scrapy.Field()  # 列表：本公告相关的图片链接
    images = scrapy.Field()
    icon = scrapy.Field()
    image_path = scrapy.Field()
    article_addr = scrapy.Field()
