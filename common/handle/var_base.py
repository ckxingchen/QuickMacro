#!/usr/bin/python
# -*- coding:utf-8 -*-
from common.container import GlobalManager
from common.logger import Logger

logger = Logger('var_base.py').getLogger()


class VariableAction(object):

    def __init__(self):
        self.gm = GlobalManager()

    def set_variable(self, name, value):
        """设置变量"""
        self.gm.set_value(name, value)
        logger.debug("设置局部变量{}的值为：{}".format(name, value))

    def print_variable(self, name):
        """打印变量"""
        print(name)
        logger.debug("打印变量的值为：{}".format(name))

    def colloct_variable(self, name, value):
        self.gm.set_value(name, value)
        logger.debug("设置局部变量{}的值为：{}".format(name, value))
        return self.gm.get_value(name)
