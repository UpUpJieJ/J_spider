# encoding: utf-8
# @Author: Ji jie
# @Date  :  2024/07/14
class TransformTypeError(TypeError):
    pass


class OutputTypeError(Exception):
    pass


class SpiderTypeError(TypeError):
    pass


class ItemInitError(Exception):
    pass


class DecodeError(Exception):
    pass


class MiddlewareInitError(Exception):
    pass


class InvalidOutputError(Exception):
    pass


class RequestMethodError(Exception):
    pass


class IgnoreRequest(Exception):
    def __init__(self, message=None):
        self.message = message
        super(IgnoreRequest, self).__init__(self.message)