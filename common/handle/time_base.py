#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author: 李传勇
# @datatime: 2022/10/20 9:40
import time

from common.container import GlobalManager
from common.logger import Logger

logger = Logger('file_base.py').getLogger()


class TimeAction(object):

    def __init__(self):
        self.gm = GlobalManager()

    def time_sleep(self, second):
        """停止时间"""
        time.sleep(second)
        logger.debug("等待：{}秒".format(second))

