# -*- coding: utf-8 -*-

"""建立数据表工具
"""

import sys

import MySQLdb

from crawlers.settings import DB_CONFIG

reload(sys)
sys.setdefaultencoding('utf-8')

# 建立数据表
conn = MySQLdb.connect(**DB_CONFIG)
cur = conn.cursor()
full_sql = "create table {0}(" \
            "id int(11) NOT NULL AUTO_INCREMENT COMMENT '主键'," \
            "title VARCHAR(127) NOT NULL DEFAULT '' COMMENT '标题'," \
            "digest varchar(1022) NOT NULL COMMENT '摘要'," \
            "content mediumtext NOT NULL COMMENT '正文'," \
            "icon varchar(127) NOT NULL DEFAULT '' COMMENT '资讯图标'," \
            "image varchar(2046) NOT NULL DEFAULT '' COMMENT '附图:图片1,图片2,...'," \
            "publish_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' COMMENT '发布时间'," \
            "media_id int(11) NOT NULL COMMENT '媒体id'," \
            "crawl_website varchar(127) NOT NULL DEFAULT '' COMMENT '抓取资讯的网站'," \
            "crawl_url varchar(510) NOT NULL DEFAULT '' COMMENT '抓取资讯的网站URL'," \
            "create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间, 即爬取时间'," \
            "update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'," \
            "PRIMARY KEY (id)," \
            "KEY idx_ptime (publish_time) USING BTREE," \
            "KEY idx_media (media_id) USING BTREE" \
            ") ENGINE=InnoDB AUTO_INCREMENT=4290 DEFAULT CHARSET=utf8mb4 COMMENT='微信公众号资讯表单';"
try:
    cur.execute("drop table if exists wechat")
    cur.execute(full_sql.format("wechat"))
except Exception, e:
    print("Create table failed !")
    print(e)
else:
    print("Create table succeed !")
finally:
    cur.close()
    conn.close()