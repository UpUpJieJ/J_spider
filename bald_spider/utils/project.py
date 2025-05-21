# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/05/11
from bald_spider.settings.setting_manager import SettingsManager

def get_settings(settings='settings'):
    _settings = SettingsManager()
    _settings.set_setting(settings)
    return _settings