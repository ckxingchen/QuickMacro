#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import re
import uuid
from json import JSONDecodeError
import importlib
import types
from common.client.client_base import TemplateClientAction, Yolov5ClientAction, OcrClientAction
from common.handle.var_base import VariableAction
from common.handle.file_base import FileOper
from common.handle.time_base import TimeAction
from common.container import GlobalManager
from common.logger import Logger
from common.path import BasePath

logger = Logger('maker.py').getLogger()

INIT_ACTION_MAPS = {
    "TemplateClientAction": TemplateClientAction,
    "Yolov5ClientAction": Yolov5ClientAction,
    "OcrClientAction": OcrClientAction,
    "VariableAction": VariableAction,
    "FileOper": FileOper,
    "TimeAction": TimeAction
}


class ScriptRunner(object):

    def __init__(self):
        self.gm = GlobalManager()

    def step_parse(self, step_data, **kwargs) -> None:
        """步骤转换器，解析全部用例步骤并执行函数

        :param step_data: 所有的行为步骤列表
        :return: 关键字执行结果
        """
        try:
            if step_data:
                result_list = ["result"]
                # 合并业务关键字
                res = None
                if isinstance(step_data, list):
                    for step in step_data:
                        if 'action' in step.keys():
                            res = self.__action_step_parse(step, result_list, **kwargs)
                        elif 'function' in step.keys():
                            res = self.__function_step_parse(step, **kwargs)
                        if res:
                            self.__result_parse(res, step, result_list)
                elif isinstance(step_data, dict):
                    res = self.__business_step_parse(step_data, result_list, **kwargs)
                return res
        except Exception as e:
            logger.error("步骤运行失败：{}".format(e))
            raise e

    def __vars_substitute(self, params):
        """变量替换

        :param params: 步骤中的params参数
        :return: 替换后的步骤中的params参数
        """
        for key, value in params.items():
            if '${' in str(value):
                change_value = re.findall(r'\${(.*?)}', str(value))
                logger.debug('需要动态替换的变量为：{}'.format(change_value))
                for i, v in enumerate(change_value):
                    if isinstance(self.gm.get_value(v), str):
                        params[key] = str(params[key]).replace('${%s}' % v, self.gm.get_value(v))
                    else:
                        params[key] = eval(str(params[key]).replace('${%s}' % v, str(self.gm.get_value(v))))
                    logger.debug('动态变量{}替换成功：{}'.format(change_value[i], self.gm.get_value(v)))
        return params

    def __action_step_parse(self, step: dict, result_list: list, **kwargs):
        res = None
        if step["action"] in INIT_ACTION_MAPS.keys():
            method_name = step["method"]
            instance = INIT_ACTION_MAPS[step["action"]]()
            if hasattr(instance, method_name):
                if step.get('params'):
                    kw_params = self.__vars_substitute(step["params"])
                    if kwargs:
                        for out_key, out_value in kwargs.items():
                            self.gm.set_value(out_key, out_value)
                            kw_params[out_key] = out_value
                    params = self.separate_params(kw_params, result_list)
                    res = getattr(instance, method_name)(**params)
                    logger.debug('函数{}执行成功,参数：{}'.format(method_name, params))
                    logger.info("【步骤】:{},执行成功！".format(step['desc']))
                else:
                    res = getattr(instance, method_name)()
                    logger.debug('函数{}执行成功！'.format(method_name))
                    logger.info("【步骤】:{},执行成功！".format(step['desc']))
            else:
                logger.error("基础关键字未找到或未实现：{}".format(method_name))
                raise Exception("基础关键字未找到或未实现：{}".format(method_name))
        else:
            logger.error("基础关键字未找到或未实现：{}".format(step["action"]))
        return res

    def __function_step_parse(self, step: dict, **kwargs):
        res = None
        if step.get('function') == 'python':
            lib_path = os.path.join(BasePath.LIB_DIR)
            if os.path.exists(lib_path):
                sys.path.append(lib_path)
                is_function_exist = None
                func_dict = self.import_module(step['params']['py_name'].split('.')[0])
                for k, v in func_dict.items():
                    if k == step['params']['func_name']:
                        is_function_exist = True
                        if step['params'].get('kwargs'):
                            params = self.__vars_substitute(step["params"]["kwargs"])
                            if kwargs:
                                for out_key, out_value in kwargs.items():
                                    self.gm.set_value(out_key, out_value)
                                    params[out_key] = out_value
                            res = v(**params)
                            logger.debug('自定义函数{}执行成功,参数：{}'.format(step['params']['func_name'], params))
                            logger.info("【步骤】:{},执行成功！".format(step['desc']))
                        else:
                            res = v()
                            logger.debug('自定义函数{}执行成功！'.format(step['params']['func_name']))
                            logger.info("【步骤】:{},执行成功！".format(step['desc']))
                if not is_function_exist:
                    logger.error("自定义关键字未找到或未实现：{}".format(step['params']['func_name']))
                    raise Exception("自定义关键字未找到或未实现：{}".format(step['params']['func_name']))
            else:
                logger.error("未找到目录：{}".format(lib_path))
        else:
            logger.error("方法未找到或未实现：{}".format(step["function"]))
        return res

    def __business_step_parse(self, step: dict, result_list: list, **kwargs):
        """解析yaml用例中business步骤

        :param step: 业务关键字步骤
        :param result_list: 返回结果保存
        :return: 关键字执行结果
        """
        res = None
        if kwargs:
            for out_key, out_value in kwargs.items():
                self.gm.set_value(out_key, out_value)
        for child_step in step['step']:
            if child_step.get('action'):
                res = self.__action_step_parse(child_step, result_list)
            elif child_step.get('function'):
                res = self.__function_step_parse(child_step)
            if res:
                self.__result_parse(res, child_step, result_list)
        return res

    def __result_parse(self, res, step: dict, result_list: list):
        """解析yaml步骤中的result返回并存入全局变量管理器

        :param res: 步骤返回结果
        :param step: 关键字步骤
        :param result_list: 返回结果保存
        :return: None
        """
        for result in result_list:
            if step.get('params'):
                if step['params'].get(result):
                    if result == 'result_text':
                        save_value = res.text
                    elif result == 'result_json':
                        try:
                            save_value = res.json()
                        except JSONDecodeError:
                            save_value = None
                    elif result == 'result_code':
                        save_value = str(res.status_code)
                    else:
                        save_value = res
                    self.gm.set_value(step['params'][result], save_value)
                    logger.debug('变量{}存储完成：{}'.format(step['params'][result], save_value))

    @staticmethod
    def separate_params(params: dict, result_list: list):
        """分割参数与返回"""
        func_param = {}
        for k, v in params.items():
            if k not in result_list:
                func_param[k] = v
        return func_param

    @staticmethod
    def is_function(tup):
        """判断(name, object)是否为方法，返回bool"""
        name, item = tup
        return isinstance(item, types.FunctionType)

    @staticmethod
    def import_module(module):
        """解析模块中的方法"""
        imported = importlib.import_module(module)
        imported_function = filter(ScriptRunner.is_function, vars(imported).items())
        return dict(imported_function)

    @staticmethod
    def generate_uuid():
        """生成随机uuid"""
        uuid_data = str(uuid.uuid4())
        logger.debug('自动生成测试用例ID:{}'.format(uuid_data))
        return uuid_data


if __name__ == '__main__':
    pass
