#!/usr/bin/python
# -*- coding:utf-8 -*-
import logging
import time
import os
from common.path import BasePath


config = BasePath().getConfig()
if not config:
    config = {
        "formatter": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "level": "INFO",
        "stream_handler_level": "DEBUG",
        "file_handler_level": "DEBUG"
    }
else:
    config = config['日志打印配置']
rq = time.strftime('%Y%m%d_%H', time.localtime()) + '.log'


class Logger(object):

    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(config['level'])
        self.streamHandler = logging.StreamHandler()
        self.fileHandler = logging.FileHandler(os.path.join(BasePath.LOGS_DIR, rq), 'a', encoding='utf-8')
        self.formatter = logging.Formatter(config['formatter'])
        self.streamHandler.setLevel(config['stream_handler_level'])
        self.fileHandler.setLevel(config['file_handler_level'])
        self.fileHandler.setFormatter(self.formatter)
        self.streamHandler.setFormatter(self.formatter)
        self.logger.addHandler(self.streamHandler)
        self.logger.addHandler(self.fileHandler)

    def getLogger(self):
        return self.logger
