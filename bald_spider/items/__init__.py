# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/05/27
from abc import ABCMeta


class Field(dict):
    pass

class ItemMeta(ABCMeta):
    def __new__(cls, name, bases, attrs):
        field = {}
        for k, v in attrs.items():
            if isinstance(v, Field):
                field[k] = v
        cls_instance = super().__new__(cls, name, bases, attrs)
        cls_instance.FIELDS = field
        return cls_instance