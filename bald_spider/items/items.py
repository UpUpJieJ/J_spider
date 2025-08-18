# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/05/27
from copy import deepcopy
from pprint import pformat
from collections.abc import MutableMapping

from bald_spider.exceptions import ItemInitError
from bald_spider.items import Field, ItemMeta


class Item(MutableMapping, metaclass=ItemMeta):
    FIELDS: dict

    # 可接受字典传参
    def __init__(self, *args, **kwargs):
        self._values = {}
        if args:
            raise ItemInitError(f'{self.__class__.__name__} does not support positional arguments. '
                                f'Use keyword arguments instead.')
        if kwargs:
            for key, value in kwargs.items():
                self[key] = value

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
            raise AttributeError(f"Use [{key!r}] syntax to access {key}, not dot notation")
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            raise AttributeError(f"{self.__class__.__name__} does not have attribute {key}")

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

    test = TestItem(url='https://www.baidu.com', title='百度一下')
    test['url']=999
    test['title']=999
    print(test['title'])
    print(test.xxx)


