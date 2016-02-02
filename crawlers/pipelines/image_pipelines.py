# -*- coding: utf-8 -*-

"""图片持久化处理方法
"""

import re
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from crawlers.logs.crawler_logger import spider_logger

class ArticleImagesPipeline(ImagesPipeline):
    """ download image
    """
    def get_media_requests(self, item, info):
        if 'image_urls' in item:
            urls = []
            for image_url in item['image_urls']:
                urls.append(image_url.strip())
            item['image_urls'] = urls
            for image_url in item['image_urls']:
                yield Request(image_url)

    def item_completed(self, results, item, info):
        # 标记并重定向已下载对应图片的<img>标签
        if 'image_urls' in item:
            content = item['content']
            item['images'] = [image for ok, image in results if ok]  # 取下载成功的图片
            image_path = ''
            for image in item['images']:
                url = re.sub("\?", "\?", image['url'])
                # <img!>为一个标记标签，不会被误删
                content = re.sub("<img[^<>]*?src=\"{0}\"[^<>]*?>".format(url),
                                 "<img!>", content)
                image_path = image_path + "media/" + image['path'] + ','
            if len(image_path) > 0:
                image_path = image_path[0:-1]
            item['image_path'] = image_path
            # 删除其他的<img>标签
            content = re.sub("<img[^!]*?>", "", content)
            # 换位标记位“>”
            content = re.sub("<img!", "<img", content)
            item['content'] = content
            # 下载失败的图片输出日志
            for error in [errors for ok, errors in results if not ok]:
                spider_logger.warning("Download image failed: {0}".format(error.getErrorMessage()))
        return item

class IconPipeline(ImagesPipeline):
    """ download icon
    """
    def get_media_requests(self, item, info):
        if 'icon' in item:
            yield Request(item['icon'])

    def item_completed(self, results, item, info):
        # 重定向已下载icon路径
        if 'icon' in item:
            image_path = [image['path'] for ok, image in results if ok]  # 取下载成功的图片
            if not image_path:
                for error in [errors for ok, errors in results if not ok]:
                    spider_logger.warning("Download icon failed: {0}".format(error.getErrorMessage()))
                return item
            item['icon'] = "media/" + image_path[0]
            return item
