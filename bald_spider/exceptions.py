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


class NotConfigured(Exception):
    pass


class ExtensionInitError(Exception):
    pass


class ReceiverTypeError(TypeError):
    pass


class PipelineInitError(TypeError):
    pass


class ItemDiscard(Exception):
    def __init__(self, message=None):
        self.message = message
        super(ItemDiscard, self).__init__(self.message)