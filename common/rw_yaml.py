#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
from ruamel import yaml


def read_yaml(yaml_path):
    """读取yaml文件"""
    if not os.path.isfile(yaml_path):
        raise FileNotFoundError("文件路径不存在，请检查路径是否正确：%s" % yaml_path)
    with open(yaml_path, 'r', encoding='utf-8') as f:
        content = yaml.load(f, Loader=yaml.Loader)
    return content


def write_yaml(yaml_path, data):
    """写入yaml文件"""
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(data=data, stream=f, Dumper=yaml.RoundTripDumper, allow_unicode=True)


def get_testcase_data(yaml_path):
    """获取用例信息"""
    testcase_pool = []
    for root, dirs, files in os.walk(yaml_path, topdown=True):
        for i, j in enumerate(list(sorted([i for i in files if os.path.splitext(i)[1] == '.yaml']))):
            if j != 'conftest.yaml':
                try:
                    test_info = {}
                    testcase_name = j.replace('.yaml', '')  # 测试用例名字
                    case_path = os.path.abspath(os.path.join(root, j))
                    module_name = os.path.basename(root)
                    if 'testcase' != module_name:
                        test_info['module_name'] = module_name
                        test_info['module_path'] = root
                    test_info['yaml_name'] = testcase_name
                    test_info['yaml_path'] = case_path
                    testcase_content = read_yaml(case_path)
                    test_info['yaml_content'] = testcase_content
                    py_name = testcase_name + '.py'
                    py_case_path = os.path.join(root, py_name)
                    test_info['py_path'] = py_case_path
                    testcase_pool.append(test_info)
                except BaseException as e:
                    raise e
    return testcase_pool


def get_fixture_data(yaml_path):
    """获取用例前置后置信息"""
    fixture_pool = []
    for root, dirs, files in os.walk(yaml_path, topdown=True):
        for i, j in enumerate(list(sorted([i for i in files if os.path.splitext(i)[1] == '.yaml']))):
            if j == 'conftest.yaml':
                try:
                    fixture_info = {}
                    fixture_name = j.replace('.yaml', '')  # 测试用例名字
                    fixture_path = os.path.abspath(os.path.join(root, j))
                    fixture_info['yaml_name'] = fixture_name
                    fixture_info['yaml_path'] = fixture_path
                    fixture_content = read_yaml(fixture_path)
                    fixture_info['yaml_content'] = fixture_content
                    py_case_path = os.path.join(root, 'conftest.py')
                    fixture_info['py_path'] = py_case_path
                    fixture_pool.append(fixture_info)
                except BaseException as e:
                    raise e
    return fixture_pool


def clear_files(project_path):
    for root, dirs, files in os.walk(project_path, topdown=True):
        for i, j in enumerate(list(sorted([i for i in files if os.path.splitext(i)[1] == '.py']))):
            try:
                py_path = os.path.abspath(os.path.join(root, j))
                os.unlink(py_path)
            except BaseException as e:
                raise e


if __name__ == '__main__':
    path = r'D:\01MyCode\01DemoCode\auto_worker\action\01鼠标操作\01鼠标当前位置点击.yaml'
    res = read_yaml(path)
    print(res)
