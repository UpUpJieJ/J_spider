# encoding: utf-8
# @Author: Ji jie
# @Date  :  2025/08/25
from datetime import datetime


def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def date_delta(date1, date2):
    start = datetime.strptime(date1, '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(date2, '%Y-%m-%d %H:%M:%S')
    return (end - start).seconds
