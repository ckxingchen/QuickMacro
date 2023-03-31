#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import sys
from configparser import RawConfigParser

if hasattr(sys, 'frozen'):
    Path = lambda p: os.path.abspath(os.path.join(os.path.dirname(sys.executable), p))
else:
    Path = lambda p: os.path.abspath(os.path.join(os.path.dirname(__file__), p))


class BasePath(object):
    """公共路径类"""
    SCRIPT_TEMPLATE = {
        "business": [
            {
                "business": "None",
                "desc": "请填写业务功能描述",
                "params": {
                    "input": "None",
                    "output": "None"
                }
            }
        ],
        "step": []
    }

    PROJECT_ROOT = Path('../')  # 根目录
    ACTION_KEYWORD = os.path.join(PROJECT_ROOT, 'action')
    DRIVER_DIR = os.path.join(PROJECT_ROOT, 'driver')
    LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
    THEME_FILE = os.path.join(DRIVER_DIR, 'QCandyUi', 'candyUi', 'theme.json')
    IMAGES_ICON_DIR = os.path.join(PROJECT_ROOT, "images", "icon")
    SCREENSHOT_DIR = os.path.join(PROJECT_ROOT, "images", "screenshot")
    SCRIPT_DIR = os.path.join(PROJECT_ROOT, "scripts")
    HAND_SCRIPT_DIR = os.path.join(SCRIPT_DIR, "手写脚本")
    RECORD_SCRIPT_DIR = os.path.join(SCRIPT_DIR, "录制脚本")
    CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.ini")
    LIB_DIR = os.path.join(SCRIPT_DIR, "lib")
    PET_IMG_DIR = os.path.join(PROJECT_ROOT, "images", "pet")
    ICON_PICTURE = os.path.join(IMAGES_ICON_DIR, 'logo.png')

    def getConfig(self):
        """获取当前项目配置"""
        dictionary = {}
        config = RawConfigParser()
        config.read(self.CONFIG_PATH, encoding='utf-8')
        for section in config.sections():
            dictionary[section] = {}
            for option in config.options(section):
                dictionary[section][option] = config.get(section, option)
        return dictionary


if __name__ == '__main__':
    p = BasePath()
    res = p.getConfig()
    print(res)
