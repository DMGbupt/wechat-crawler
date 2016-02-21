爬虫使用说明：
1、数据库配置：
	crawlers/setting.py中须要修改数据库连接信息DB_CONFIG
	crawlers/utils/create_db： 自动建表脚本，需手动执行，可不使用
2、启动爬虫
	I.在项目目录下输入： scrapy crawl crawler_name ，其中crawler_name为crawlers/spiders中各爬虫文件的文件名
	II.运行启动脚本initiator.py，可配置参数有：
		(1)公众号爬取顺序的参数：
			"-n"参数，根据各个公众号已爬取文章数量，按递增顺序爬取公众号，优先爬取文章记录较少的公众号；
			"-p"参数，根据各个公众号已爬取文章里距离现在最近的发布时间，按递增顺序爬取公众号，优先爬取最新文章发布时间距离现在较远的公众号；
			无参数时，默认随机爬取全部公众号。
		(2)爬取起始时间参数：
			"-s"参数，传入开始爬取的时间，时间须按照"2015/8/13/16:00:00"格式；
			"-c"参数，从数据库读取距现在最近的爬取时间作为启动时间；
			无参数时，默认起始时间为一年之前。
		(3)爬取目录页数参数：
			"-t"参数，传入公众号要爬取的目录页数；
			无参数时，默认爬取全部10页目录。
3、关于正文部分(content)的说明:
	正文部分放在一个<div></div>标签内，其中
	使用<p></p>和<br>标签分段，保留<table>及相关标签用于记录表格的格式信息，保留<img>标签用于记录图片信息，删除了其他标签
	清除了所有标签的属性以及css样式等内容
	<img>标签仅保留了src属性，属性值为本地下载的图片相对于存储图片的目录的位置
4、索引模块：
	使用crawlers/index/indexer.py中Indexer的get方法获取索引的writer和searcher。
	新闻和博客的索引是分开的
	索引不支持多进程/线程写，可多进程/线程读

其他：
1、文件结构：
	crawlers/database：dao类
	crawlers/index: 索引读写模块
    crawlers/pipelines: 各种pipeline
    crawlers/spiders: 各网站的爬虫
    crawlers/topics: 公众号爬虫使用的查询词
    crawlers/utils: 附加工具脚本
    crawlers/index_spider.py: 爬虫的基类，定义了从搜狗微信公众号搜索页面（weixin.sogou.com）为入口爬取网页的流程
    crawlers/items.py: 爬取的各种item
    crawlers/setting.py 爬虫设置
    doc: 爬虫的数据库设计文档和测试文档
    initiator.py:爬虫启动脚本
2、过滤和去重
	crawlers.pipelines/filter是过滤模块，已实现的具体去重规则请参看注释
	crawlers/pipelines/duplicate_removal是去重模块，已实现的具体去重规则请参看注释
3、正文处理
	crawlers/utils/html_formatter.py是正文处理方法