from jsonrpc import Dispatcher
from common.maker import ScriptRunner
from common.path import BasePath
from common.rw_yaml import read_yaml
from common.utils import init_file_path


def create_action_cls():
    cls_name = type('ActionMeta', (), {})
    action_path_dict = init_file_path(BasePath.ACTION_KEYWORD)
    for action_name, action_path in action_path_dict.items():
        action_data = read_yaml(action_path)
        func = '''def {}(self, **kwargs):\n    res=ScriptRunner().step_parse({}, **kwargs)\n    return res'''.format(
            'fun_' + action_name, action_data)
        exec(func)
        exec_func = eval('fun_' + action_name)
        setattr(cls_name, 'fun_' + action_name, exec_func)
    return cls_name


def create_script_cls():
    cls_name = type('ScriptMeta', (), {})
    script_path_dict = init_file_path(BasePath.SCRIPT_DIR)
    for script_name, script_path in script_path_dict.items():
        script_data = read_yaml(script_path)
        func = '''def {}(self, **kwargs):\n    res=ScriptRunner().step_parse({}, **kwargs)\n    return res'''.format(
            'fun_' + script_name, script_data)
        exec(func)
        exec_func = eval('fun_' + script_name)
        setattr(cls_name, 'fun_' + script_name, exec_func)
    return cls_name


class CusDispatcher(Dispatcher):
    """自定义注册器"""

    def __init__(self):
        self.maps = {
            "action": create_action_cls(),
            "scripts": create_script_cls(),
        }
        super(CusDispatcher, self).__init__(self.maps)

    def build_method_map(self, prototype, prefix=''):
        """重写方法，支持maps格式注册"""
        for class_desc, class_name in prototype.items():
            class_obj = class_name()
            prototype_class = dict((method, getattr(class_obj, method))
                                   for method in dir(class_obj)
                                   if not method.startswith('_'))
            for attr, method in prototype_class.items():
                if callable(method):
                    self[class_desc + '.' + attr.replace('fun_', '')] = method


