def label_root_desc(key: str) -> str:
    """测试用例第一层参数描述

    :param key: 参数名称
    :return: QTreeWidgetItem参数的text文本
    """
    if key == 'step':
        label_text = '测试步骤(请将操作拖拽到此处)'
    elif key == 'business':
        label_text = '业务参数配置(非必填)'
    else:
        label_text = '参数描述未定义'
    return label_text


def label_params_desc(key: str, root: str, action: str = None) -> str:
    """测试用例第三层参数描述params

    :param key: 参数名称
    :param root: 根参数名称
    :param action: 关键字行为类
    :return: QTreeWidgetItem参数的text文本
    """
    if root == 'step':
        label_text = HandlerActionParamsDesc().get_label_text(action)(key)
    elif root == 'business':
        label_text = _handler_business_desc(key)
    else:
        label_text = '参数描述未定义'
    return label_text


def _handler_business_desc(key):
    if key == 'path':
        label_text = '业务关键字相对路径；path'
    elif key == 'input':
        label_text = '业务关键字入参；input'
    elif key == 'output':
        label_text = '业务关键字出参；output'
    else:
        label_text = '参数描述未定义'
    return label_text


class HandlerActionParamsDesc:

    def __init__(self):
        self.action_maps = {
            "TemplateClientAction": self.client_action_params_desc,
            "Yolov5ClientAction": self.client_action_params_desc,
            "OcrClientAction": self.client_action_params_desc,
            "VariableAction": self.variable_action_params_desc,
            "FileOper": self.file_action_params_desc,
            "TimeAction": self.time_action_params_desc,
            "other": self.others_params_desc
        }

    @staticmethod
    def client_action_params_desc(key):
        if key == 'el':
            label_text = '图片名称(不带后缀)；el'
        elif key == 'clicks':
            label_text = '鼠标点击次数；clicks'
        elif key == 'button':
            label_text = '鼠标点击按钮(left/right)；button'
        elif key == 'isclick':
            label_text = '是否点击(true/false)；isclick'
        elif key == 'rel_x':
            label_text = '相对位置横向偏移距离(右正左负)；rel_x'
        elif key == 'rel_y':
            label_text = '相对位置纵向偏移距离(下正上负)；rel_y'
        elif key == 'posx':
            label_text = '绝对位置横坐标；posx'
        elif key == 'posy':
            label_text = '绝对位置纵坐标；posy'
        elif key == 'rel':
            label_text = '是否相对偏移(true/false)；rel'
        elif key == 'amount_to_scroll':
            label_text = '鼠标滑轮滚动距离；amount_to_scroll'
        elif key == 'move_x':
            label_text = '鼠标滑轮滚动X坐标；move_x'
        elif key == 'move_y':
            label_text = '鼠标滑轮滚动Y坐标；move_y'
        elif key == 'content':
            label_text = '键盘输入文本内容(非中文)；content'
        elif key == 'text':
            label_text = '键盘输入文本内容(可中文)；text'
        elif key == 'clear':
            label_text = '是否清空粘贴板(true/false)；clear'
        elif key == 'key':
            label_text = '键盘单个按键按下按钮名；key'
        elif key == 'keys':
            label_text = '键盘组合键列表；keys'
        elif key == 'searchTime':
            label_text = '超时时间；searchTime'
        elif key == 'weight':
            label_text = '权重文件名(不带后缀)；weight'
        elif key == 'timeout':
            label_text = '超时时间；timeout'
        elif key == 'timeout':
            label_text = '超时时间；timeout'
        elif key == 'el_list':
            label_text = '图片识别列表；el_list'
        elif key == 'left_top':
            label_text = '左顶点x,y坐标(list)；left_top'
        elif key == 'right_down':
            label_text = '右下角x,y坐标(list)；right_down'
        elif key == 'el_index':
            label_text = '图片索引；el_index'
        elif key == 'result':
            label_text = '关键字返回结果；result'
        else:
            label_text = '参数描述未定义'
        return label_text

    @staticmethod
    def variable_action_params_desc(key):
        if key == 'name':
            label_text = '变量名；name'
        elif key == 'value':
            label_text = '变量值；value'
        elif key == 'result':
            label_text = '关键字返回结果；result'
        else:
            label_text = '参数描述未定义'
        return label_text

    @staticmethod
    def file_action_params_desc(key):
        if key == 'file_path':
            label_text = '文件路径；file_path'
        elif key == 'result':
            label_text = '关键字返回结果；result'
        else:
            label_text = '参数描述未定义'
        return label_text

    @staticmethod
    def time_action_params_desc(key):
        if key == 'second':
            label_text = '秒数；second'
        elif key == 'result':
            label_text = '关键字返回结果；result'
        else:
            label_text = '参数描述未定义'
        return label_text

    @staticmethod
    def others_params_desc(key):
        if key == 'py_name':
            label_text = 'py文件名称；py_name'
        elif key == 'func_name':
            label_text = '函数名称；func_name'
        elif key == 'kwargs':
            label_text = '函数传参(字典类型)；kwargs'
        elif key == 'input':
            label_text = '业务关键字入参；input'
        elif key == 'output':
            label_text = '业务关键字出参；output'
        elif key == 'result':
            label_text = '关键字运行结果保存；result'
        else:
            label_text = '参数描述未定义'
        return label_text

    def get_label_text(self, action):
        if action:
            return self.action_maps[action]
        else:
            return self.action_maps['other']
