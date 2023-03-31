#!/usr/bin/python
# -*- coding:utf-8 -*-
import base64
import requests
import io
from PIL import ImageGrab
import pyperclip
from common.utils import *
from common.logger import Logger
from common.path import BasePath

logger = Logger('client_base.py').getLogger()


class ClientAction(object):
    """客户端操作基类"""

    __doc__ = 'Client关键字'

    def __init__(self):
        self.client_config = BasePath().getConfig()['客户端自动化配置']
        self.duration = float(self.client_config['duration'])  # 设置鼠标移动速度；0为立即执行
        self.interval = float(self.client_config['interval'])  # 每次点击间隔时间；0为立即执行
        self.timeout = float(self.client_config['timeout'])  # 隐试等待时间
        self.confidence = float(self.client_config['confidence'])  # 设置图片识别信任度

    def mouse_down(self, posx=None, posy=None, button='left'):
        """鼠标按下"""
        import pyautogui
        pyautogui.mouseDown(posx, posy, button=button, duration=self.duration)
        logger.debug('鼠标在坐标{},{} 按下{}键'.format(posx, posy, button))

    def mouse_up(self, posx=None, posy=None, button='left'):
        """鼠标松开"""
        import pyautogui
        pyautogui.mouseUp(posx, posy, button=button, duration=self.duration)
        logger.debug('鼠标在坐标{},{} 松开{}键'.format(posx, posy, button))

    def mouse_click(self, posx=None, posy=None, clicks=1, button='left'):
        """鼠标点击方法"""
        import pyautogui
        pyautogui.click(posx, posy, clicks=clicks, button=button, duration=self.duration, interval=self.interval)
        logger.debug('鼠标在坐标{},{} 点击{}键 {}次'.format(posx, posy, button, clicks))

    def rel_mouse_click(self, rel_x=0, rel_y=0, clicks=1, button='left'):
        """相对坐标点击"""
        import pyautogui
        pyautogui.move(rel_x, rel_y)
        pyautogui.click(clicks=clicks, button=button, duration=self.duration, interval=self.interval)
        logger.debug('鼠标在相对坐标{},{} 点击{}键 {}次'.format(rel_x, rel_y, button, clicks))

    def moveto(self, posx=0, posy=0, rel=False):
        """鼠标移动方法"""
        import pyautogui
        if rel:
            pyautogui.move(posx, posy, duration=self.duration)
            logger.debug('鼠标偏移{},{}'.format(posx, posy))
        else:
            pyautogui.moveTo(posx, posy, duration=self.duration)
            logger.debug('鼠标移动到{},{}'.format(posx, posy))

    def dragto(self, posx, posy, button='left', rel=False):
        """鼠标拖拽"""
        import pyautogui
        if rel:
            pyautogui.dragRel(posx, posy, duration=self.duration)
            logger.debug('鼠标相对拖拽{},{}'.format(posx, posy))
        else:
            pyautogui.dragTo(posx, posy, duration=self.duration, button=button)
            logger.debug('鼠标拖拽{},{}'.format(posx, posy))

    @staticmethod
    def scroll(amount_to_scroll, move_x=None, move_y=None):
        """鼠标滚动"""
        import pyautogui
        pyautogui.scroll(clicks=amount_to_scroll, x=move_x, y=move_y)
        logger.debug('鼠标在{}位置滚动{}值'.format(move_x, move_y), amount_to_scroll)

    def keyboard_write(self, content):
        """键盘输入"""
        import pyautogui
        pyautogui.typewrite(content, interval=self.interval)
        logger.debug('键盘输入：{}'.format(content))

    @staticmethod
    def input_string(text, clear=False):
        """输入中文"""
        import pyautogui
        pyperclip.copy(text)
        if not clear:
            pyautogui.hotkey('ctrl', 'v')
        logger.debug('输入文本：{}'.format(text))

    @staticmethod
    def press(key):
        import pyautogui
        pyautogui.press(key)
        logger.debug("键盘按下单个按键：{}".format(key))

    @staticmethod
    def press_down(key):
        import pyautogui
        pyautogui.keyDown(key)
        logger.debug("键盘单个按键按下：{}".format(key))

    @staticmethod
    def press_up(key):
        import pyautogui
        pyautogui.keyUp(key)
        logger.debug("键盘单个按键松开：{}".format(key))

    @staticmethod
    def hotkey(keys):
        import pyautogui
        pyautogui.hotkey(*keys)
        logger.debug("键盘执行组合键：{}".format(keys))

    @staticmethod
    def always_get_position():
        import pyautogui
        while True:
            time.sleep(1)
            x, y = pyautogui.position()
            print(x, y)


class TemplateClientAction(ClientAction):

    def __init__(self):
        super(TemplateClientAction, self).__init__()
        self.grayscale = bool(self.client_config['grayscale'])

    @staticmethod
    def _init_file_path(pic_path):
        """遍历目录下所有层级获取所有图片的路径"""
        path = {}
        value = None
        path_lists = [path_list for path_list in os.walk(pic_path)]
        for path_list in path_lists:
            for file_path in path_list:
                if isinstance(file_path, str):
                    value = file_path
                elif isinstance(file_path, list):
                    for file_name in file_path:
                        path[file_name.split('.')[0]] = os.path.join(value, file_name)
        return path

    def _is_file_exist(self, el):
        """检查json中读取的图片名称获取全路径后是否存在"""
        pic_path = os.path.join(BasePath.PROJECT_ROOT, 'picture')
        abs_path = self._init_file_path(pic_path).get(el)
        if not abs_path:
            raise FileNotFoundError('el:{} 不存在检查文件名或检查配置文件test_project！'.format(el))
        return abs_path

    @staticmethod
    def _error_record(name, method):
        import pyautogui
        pyautogui.screenshot(os.path.join(BasePath.SCREENSHOT_DIR, name + '.png'))
        logger.error('类型：{},查找图片 {} 位置, 当前屏幕无此内容，已截图'.format(method, name))
        raise pyautogui.ImageNotFoundException

    def isexist(self, el, timeout=None):
        """检查图片是否呈现在当前屏幕"""
        import pyautogui
        pic_path = self._is_file_exist(el)
        if not timeout:
            timeout = self.timeout
        coordinates = pyautogui.locateOnScreen(pic_path, minSearchTime=timeout,
                                               confidence=self.confidence, grayscale=True)
        if coordinates:
            logger.debug('查找对象{}存在'.format(el.split('.')[0]))
            return pyautogui.center(coordinates)
        logger.debug('查找对象{}不存在'.format(el.split('.')[0]))
        return None

    def is_pic_exist(self, el, timeout=3):
        """判断图片是否存在,返回bool类型"""
        res = self.isexist(el, timeout)
        if res:
            return True
        else:
            return False

    def click_picture(self, el, clicks=1, button='left', isclick=True):
        """点击图片方法"""
        import pyautogui
        pos_x_y = self.isexist(el)
        if not pos_x_y:
            self._error_record(el, "click_picture")
        pyautogui.moveTo(*pos_x_y)
        if isclick:
            pyautogui.click(*pos_x_y, duration=self.duration, interval=self.interval, clicks=clicks, button=button)
        logger.debug('移动到图片 {} 位置{}, 点击:{} 成功'.format(el, isclick, pos_x_y))

    def rel_picture_click(self, el, rel_x=0, rel_y=0, clicks=1, button='left', isclick=True):
        """图像的相对位置点击"""
        import pyautogui
        pos_x_y = self.isexist(el)
        if not pos_x_y:
            self._error_record(el, "rel_picture_click")
        pyautogui.moveTo(*pos_x_y, duration=self.duration)  # 移动到 (100,100)
        pyautogui.move(rel_x, rel_y, duration=self.duration)  # 从当前位置右移100像素
        if isclick:
            pyautogui.click(clicks=clicks, button=button, duration=self.duration)
        logger.debug('查找图片{}, 位置{}, 偏移{},点击{}, 成功'.format(el, pos_x_y, (rel_x, rel_y), isclick))


class Yolov5ClientAction(ClientAction):

    def __init__(self):
        super(Yolov5ClientAction, self).__init__()
        self.ai_server = self.client_config['ai_server']
        self.ai_device = self.client_config['ai_device']

    @staticmethod
    def _current_screen_base64():
        """图片转base64格式"""
        try:
            buffer = io.BytesIO()
            img = ImageGrab.grab()
            img.save(buffer, format='PNG')
            img.close()
            img_bytes = base64.b64encode(buffer.getvalue())
            img_base64 = 'Data:image/png;base64,%s' % img_bytes.decode()
            return img_base64
        except Exception as e:
            logger.error("截取当前屏幕图片并转base64失败：{}".format(e))

    @staticmethod
    def _get_bbox_center(bbox):
        """获取按钮坐标"""
        x = int(bbox[0] + (bbox[2] - bbox[0]) / 2)
        y = int(bbox[1] + (bbox[3] - bbox[1]) / 2)
        return x, y

    def yolov5_serve_post(self, weight, timeout=None):
        """获取识别结果"""
        el_list = None
        start = time.time()
        if not timeout:
            timeout = self.timeout
        try:
            while True:
                pic_base64 = self._current_screen_base64()
                header = {
                    'Content-Type': 'application/json'
                }
                body = {
                    "image": pic_base64,
                    "weights": weight,
                    "device": self.ai_device
                }
                res = requests.post(url=self.ai_server, headers=header, json=body)
                if (res.status_code == 200) and (res.json()['results']):
                    el_list = res.json()['results']
                    logger.debug("访问yolov5服务获取图像识别结果成功：{}".format(el_list))
                    break
                if time.time() - start > timeout:
                    logger.debug("访问yolov5服务获取图像识别结果为空且超时！")
                    break
            return el_list
        except Exception as e:
            logger.error("访问yolov5服务获取图像识别结果失败：{}".format(e))

    def yolov5_is_el_exist(self, el, el_list, el_index=0):
        """判断元素是否存在"""
        el_pos_list = []
        for i in el_list:
            if i['name'] == el:
                if float(i['conf']) >= self.confidence:
                    el_pos_list.append(self._get_bbox_center(i['bbox']))
        if el_pos_list:
            el_pos = el_pos_list[el_index]
            logger.debug("元素存在：{},元素坐标：{}".format(el, el_pos))
            return el_pos
        else:
            logger.debug("元素不存在：{}".format(el))
            return None

    def yolov5_is_pic_exist(self, el, el_list, el_index=0):
        """判断图片是否存在，返回bool"""
        res = self.yolov5_is_el_exist(el, el_list, el_index=el_index)
        if res:
            return True
        else:
            return False

    def yolov5_click_picture(self, el, el_list, clicks=1, button='left', isclick=True, el_index=0):
        """点击图片方法"""
        import pyautogui
        pos_x_y = self.yolov5_is_el_exist(el, el_list, int(el_index))
        if not pos_x_y:
            current_screen = ImageGrab.grab()
            current_screen.save("error_{}.png".format(el))
        pyautogui.moveTo(*pos_x_y)
        if isclick:
            pyautogui.click(*pos_x_y, duration=self.duration, interval=self.interval, clicks=clicks, button=button)
        logger.debug('移动到图片 {} 位置{}, 点击:{} 成功'.format(el, isclick, pos_x_y))

    def yolov5_rel_picture_click(self, el, el_list, rel_x=0, rel_y=0, clicks=1, button='left', isclick=True,
                                 el_index=0):
        """图像的相对位置点击"""
        import pyautogui
        pos_x_y = self.yolov5_is_el_exist(el, el_list, el_index)
        if not pos_x_y:
            current_screen = ImageGrab.grab()
            current_screen.save("error_{}.png".format(el))
        pyautogui.moveTo(*pos_x_y, duration=self.duration)  # 移动到 (100,100)
        pyautogui.move(rel_x, rel_y, duration=self.duration)  # 从当前位置右移100像素
        if isclick:
            pyautogui.click(clicks=clicks, button=button, duration=self.duration)
        logger.debug('查找图片{}, 位置{}, 偏移{},点击{}, 成功'.format(el, pos_x_y, (rel_x, rel_y), isclick))


class OcrClientAction(ClientAction):

    def __init__(self):
        super(OcrClientAction, self).__init__()
        self.ocr_url = self.client_config['ocr_url']

    def ocr_from_server(self, left_top: list, right_down: list):
        try:
            import pyautogui
            try:
                ip = self.client_config['ocr_url']
                logger.debug("指定的OCR服务地址为：{}".format(ip))
            except:
                ip = 'http://172.168.124.200:18200/dias/ocr'
                logger.debug("默认的OCR服务地址为：{}".format(ip))
            else:
                ocr_pic_path = os.path.join(BasePath.SCREENSHOT_DIR, 'ocr_pic_temp.png')
                are = tuple(left_top + right_down)
                pyautogui.screenshot(ocr_pic_path, are)
                logger.debug("图像文件路径为：{}".format(ocr_pic_path))
                if os.path.exists(ocr_pic_path):
                    with open(ocr_pic_path, "rb") as f:
                        img = f.read()
                        img_base64 = str(base64.b64encode(img), encoding="utf-8")
                    headers = {
                        'Content-Type': 'application/json'
                    }
                    jsons = {
                        "mode": "imgstream",
                        "language": "chinese",
                        # 图片base64
                        "imgstring": img_base64
                    }
                    re = requests.post(url=ip, headers=headers, json=jsons)
                else:
                    logger.debug('步骤：{%s}，失败原因：%s' % (ocr_pic_path, "图片不存在"))
                    raise ValueError('图片不存在')
                logger.debug("图像识别结果为：{}".format(re.json()))
                return re.json()
        except BaseException as e:
            logger.error('步骤：{%s}，失败原因：%s' % e)


if __name__ == '__main__':
    gui = Yolov5ClientAction()
    gui.hotkey(['win', 'm'])
