# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/05/27
from copy import deepcopy
from pprint import pformat
from collections.abc import MutableMapping

from bald_spider.items import Field, ItemMeta


class Item(MutableMapping, metaclass=ItemMeta):
    FIELDS: dict

    def __init__(self):
        self._values = {}
        # print(self.FIELDS)

    def __setitem__(self, key, value):
        if key not in self.FIELDS:
            raise KeyError(f"{self.__class__.__name__} does not supported {key} ")
        self._values[key] = value

    def __getitem__(self, key):
        return self._values[key]

    def __delitem__(self, key):
        del self._values[key]

    def __getattribute__(self, key):
        fields = super().__getattribute__('FIELDS')
        if key in fields:
            raise AttributeError(f"Use [{key!r}] syntax to access {key}")
        return object.__getattribute__(self, key)

    def __getattr__(self, item):
        raise AttributeError(f"{self.__class__.__name__} does not have attribute {item}, "
                             f"please add the `{item}` field to the {self.__class__.__name__}")

    def __setattr__(self, key, value):
        if key == '_values':  # 允许_values属性正常 self._values = {}
            object.__setattr__(self, key, value)
        else:
            raise AttributeError(f"please use item[{key!r}] = {value!r}  to set value, not use item.{key!r} = {value!r} ")

    def __repr__(self):
        return pformat(dict(self))

    __str__ = __repr__

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._values)

    def to_dict(self):
        return dict(self)

    def copy(self):
        return deepcopy(self)

if __name__ == '__main__':
    class TestItem(Item):
        url = Field()
        title = Field()

    test = TestItem()
    test['url']=999
    test['title']=999
    print(test['title'])
    print(test.xxxx)


