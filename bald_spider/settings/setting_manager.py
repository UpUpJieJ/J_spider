# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/05/11
from importlib import import_module
from collections.abc import MutableMapping
from bald_spider.settings import default_settings


class SettingsManager(MutableMapping):
    def __init__(self,values=None):
        self.attributes={}
        self.set_setting(default_settings)
        self.update_values(values)
    def __getitem__(self, item):
        if item not in self:
            return None
        return self.attributes[item]

    def __contains__(self, item):
        return item in self.attributes

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key):
        del self.attributes[key]

    def __iter__(self):
        return iter(self.attributes)

    def __len__(self):
        return len(self.attributes)

    def set(self, key, value):
        self.attributes[key] = value

    def get(self, key, default=None):
        return self[key] if key in self else default

    def getint(self, key, default=0):
        return int(self.get(key, default))

    def getfloat(self, key, default=0.0):
        return float(self.get(key, default))

    def getbool(self, key, default=False): # noqa
        # 兼容 字符串‘True’ 或数字1/0
        got = self.get(key, default)
        try:
            return bool(int(got))
        except ValueError:
            if got in ('True', 'true', 'TRUE'):
                return True
            elif got in ('False', 'false', 'FALSE'):
                return False
            raise ValueError(f'{got} is not a valid boolean value, must be (0 or 1),  (true or false), (True or False)')

    def getlist(self, key, default=None):
        value = self.get(key, default or [])
        if isinstance(value, str):
            return value.split(',')
        return value

    def set_setting(self, module):
        if isinstance(module, str):
            module = import_module(module)
        for key in dir(module):
            if key.isupper():
                self.set(key, getattr(module, key))

    def __str__(self):
        return f'<Settings values: {self.attributes}>'

    __repr__ = __str__

    def update_values(self,values):
        if values is not None:
            for key,value in values.items():
                self.set(key,value)


if __name__ == '__main__':
    settings = SettingsManager()
    settings['abc'] = 666
    print(settings.items())
