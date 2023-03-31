#!/usr/bin/python
# -*- coding:utf-8 -*-
class GlobalManager(object):
    """模块间共享变量"""
    global_dict = {}
    _instance = False

    def set_value(self, name, value):
        self.global_dict[name] = value

    def get_value(self, name):
        try:
            return self.global_dict[name]
        except KeyError as e:
            print("获取的变量名称：{}不存在！！！".format(name))
            return None

    def get_driver(self):
        try:
            return self.global_dict['driver']
        except KeyError as e:
            return None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance


if __name__ == "__main__":
    g = GlobalManager()
    res = g.get_value('driver')
    print(res)
