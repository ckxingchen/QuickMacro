#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author: 李传勇
# @datatime: 2022/6/30 16:57

import os
import subprocess
from common.container import GlobalManager
from common.logger import Logger

logger = Logger('file_base.py').getLogger()


class FileOper:

    def __init__(self):
        self.gm = GlobalManager()

    def open_file(self, file_path):
        """打开文件"""
        try:
            os.startfile(file_path)
        except:
            subprocess.Popen(['xdg-open', file_path])
        logger.debug("打开文件成功：{}".format(file_path))

    def is_file_exist(self, file_path):
        """判断文件是否存在,返回bool"""
        is_exist = os.path.exists(file_path)
        logger.debug("判断文件是否存在：{}".format(is_exist))
        return is_exist


if __name__ == '__main__':
    f = FileOper()
    f.is_file_exist(r'C:\Users\Administrator\Desktop\新建文件夹\推广进度.txt')