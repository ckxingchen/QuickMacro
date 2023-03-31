#!/usr/bin/python
# -*- coding:utf-8 -*-
import hashlib
import os
import time
import zipfile
from configparser import RawConfigParser, ConfigParser


def get_config_data(file_path):
    """获取ini文件数据，返回字典"""
    dictionary = {}
    config = RawConfigParser()
    config.read(file_path, encoding='utf-8')
    for section in config.sections():
        dictionary[section] = {}
        for option in config.options(section):
            dictionary[section][option] = config.get(section, option)
    return dictionary


def edit_config_data(file_path, section, key, value):
    """修改ini文件"""
    cfp = ConfigParser(comment_prefixes='/', allow_no_value=True)
    cfp.read(file_path, encoding='utf-8')
    cfp.set(section, key, value)
    cfp.write(open(file_path, 'w', encoding='utf-8'))


def make_zip(local_path, p_name):
    """打包zip"""
    zip_file = zipfile.ZipFile(p_name, 'w', zipfile.ZIP_DEFLATED)
    pre_len = len(os.path.dirname(local_path))
    for parent, dirname, filenames in os.walk(local_path):
        for filename in filenames:
            path_file = os.path.join(parent, filename)
            arc_name = path_file[pre_len:].strip(os.path.sep)
            zip_file.write(path_file, arc_name)
    zip_file.close()
    return p_name


def py_path_to_module(py_path):
    """模块重载"""
    if py_path[-3:] != '.py':
        raise Exception('不为py文件！')
    module_name = ''
    py_path = py_path.replace('.py', '').replace('\\', '/')
    file_list = py_path.split('/')
    while True:
        module_name = '.' + file_list[-1] + module_name
        del file_list[-1]
        if file_list[-1] == 'testcase':
            break
    return 'testcase' + module_name


def string_change_to_list(text):
    """字符串转列表，按照;分割"""
    return str(text).split(';')


def make_id():
    """构造id"""
    time_stamp = str(time.time()).encode("utf-8")
    time_md5 = hashlib.md5(time_stamp)
    id_str = time_md5.hexdigest()
    return id_str


def init_file_path(dir_path):
    """遍历目录下所有层级获取所有图片的路径"""
    path = {}
    value = None
    path_lists = [path_list for path_list in os.walk(dir_path)]
    for path_list in path_lists:
        for file_path in path_list:
            if isinstance(file_path, str):
                value = file_path
            elif isinstance(file_path, list):
                for file_name in file_path:
                    if '.yaml' in file_name:
                        path[file_name.split('.')[0]] = os.path.join(value, file_name)
    return path


if __name__ == "__main__":
    # config_path = r'D:\0MYITEM0\10_GitCode\auto_runner\testsuits\01gjxt_web\testcase\01登录功能模块\demo.py'
    # res = py_path_to_module(config_path)
    res = init_file_path(r'D:\01MyCode\01DemoCode\auto_worker\action')
    print(res)
