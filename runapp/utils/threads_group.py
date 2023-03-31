import logging
import os
from PyQt5.QtCore import QThread
from common.logger import Logger
from common.maker import ScriptRunner
from common.path import BasePath
from common.rw_yaml import read_yaml
from werkzeug.serving import run_simple
from common.rpc_server import application

logger = Logger('threads_group.py').getLogger()


class RecordScriptThread(QThread):
    """录制脚本"""

    def run(self):
        pass


class RunScriptThread(QThread):
    """本地运行线程"""

    def __init__(self, widget):
        self.widget = widget
        self.is_stop = False
        super(RunScriptThread, self).__init__()

    def run(self):
        self.is_stop = False
        for times in range(self.widget.run_times):
            for script_path in self.widget.run_script_list:
                if not os.path.exists(script_path):
                    continue
                if self.is_stop:
                    logger.info("******{},脚本运行结束******".format(os.path.basename(script_path)[:-5]))
                    break
                logger.info("******{},脚本运行开始******".format(os.path.basename(script_path)[:-5]))
                script_data = read_yaml(script_path)['step']
                ScriptRunner().step_parse(script_data)
                logger.info("******{},脚本运行结束******".format(os.path.basename(script_path)[:-5]))

    def stop(self):
        self.is_stop = True


class RunRPCThread(QThread):
    """启动RPC服务线程"""
    def __init__(self, widget):
        self.widget = widget
        super(RunRPCThread, self).__init__()

    def run(self):
        config = BasePath().getConfig()['客户端自动化配置']
        logger.info("RPC服务IP:{}".format(config['rpc_host']))
        logger.info("RPC服务端口号:{}".format(config['rpc_port']))
        run_simple(config['rpc_host'], int(config['rpc_port']), application)


class LogThread(QThread):
    """日志线程"""

    def __init__(self, widget):
        super(LogThread, self).__init__()
        self.log_ui = widget

    def run(self):
        try:
            logging.basicConfig(
                stream=self.log_ui.logSignal,
                format='%(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        except Exception as e:
            print(e)
