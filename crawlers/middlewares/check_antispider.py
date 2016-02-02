# -*- coding: utf-8 -*-

"""antispider
"""
from crawlers.logs.crawler_logger import spider_logger
from scrapy.exceptions import CloseSpider


class  CheckAntispider(object):

    def process_response(request, response, spider):
    	if "antispider" in response.url:
    		spider_logger.error("recieve verification code in %s" % response.url) 
    		raise CloseSpider('antispider')
        return response
