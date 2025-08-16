# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/05/27
from bald_spider.items import Field
from bald_spider import Item


class BaiduItem(Item):
    title = Field()
    price = Field()