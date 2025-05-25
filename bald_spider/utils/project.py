# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/05/11
import os.path
import sys

from bald_spider.settings.setting_manager import SettingsManager

def _get_closest(path='.'):
    path = os.path.abspath(path)
    return path

def _init_env():
    closest = _get_closest()
    if closest:
        project_dir = os.path.dirname(closest)
        sys.path.append(project_dir)

def get_settings(settings='settings'):
    _settings = SettingsManager({'1':2})
    _init_env()
    _settings.set_setting(settings)
    return _settings


def merge_settings(spider, settings):
    if hasattr(spider, "custom_settings"):
        settings.update_values(spider.custom_settings)
