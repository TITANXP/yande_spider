from scrapy import cmdline
from scrapy.utils.project import get_project_settings

setting = get_project_settings()
cmdline.execute(['scrapy', 'crawl', setting['RUN_SPIDER']])