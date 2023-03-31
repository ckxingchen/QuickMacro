from QCandyUi.CandyWindow import *
from common.path import BasePath


def set_my_theme(widget, theme):
    """设置主题"""
    theme_file = BasePath.THEME_FILE
    if os.path.isfile(theme_file):
        path = theme_file
    else:
        path = (os.path.split(__file__)[0] + '\\' + theme_file).replace('\\', '/')
    theme_dict = json.load(open(path))
    # theme.json的theme的优先级比setTheme中的theme的优先级高
    config_theme = theme_dict.get('theme')
    if config_theme is None or config_theme == '' or theme_dict.get(config_theme) is None:
        color_dict = theme_dict.get(theme)
    else:
        color_dict = theme_dict.get(config_theme)
    if color_dict is None:
        qss = simple_qss.getDefaultQss()
    else:
        qss = simple_qss.getQss(color_dict['fontLight'], color_dict['fontDark'], color_dict['normal'],
                                color_dict['light'], color_dict['deep'], color_dict['disLight'],
                                color_dict['disDark'], theme)
    widget.setStyleSheet(qss)
