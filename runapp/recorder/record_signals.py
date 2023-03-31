import re
import time
from PyQt5.QtCore import QObject, pyqtSignal
from pynput import mouse, keyboard
from runapp.recorder.globals import record_data

# pynput is not supported in pyautogui
rename_dict = {'cmd': 'win', 'shift_r': 'shiftright', 'alt_r': 'altright', 'ctrl_r': 'ctrlright',
               'caps_lock': 'capslock', 'num_lock': 'numlock',
               'page_up': 'pageup', 'page_down': 'pagedown', 'print_screen': 'printscreen'}

num_dict = {96: 0, 97: 1, 98: 2, 99: 3, 100: 4, 101: 5, 102: 6, 103: 7, 104: 8, 105: 9}


class RecordSignal(QObject):
    event_signal = pyqtSignal(dict)

    @staticmethod
    def current_ts():
        return int(time.time() * 1000)

    def get_delay(self, method):
        delay = self.current_ts() - record_data['latest_time']
        # 录制鼠标轨迹的精度，数值越小越精准，但同时可能产生大量的冗余
        if method == 'moveto':
            if delay < record_data['mouse_interval_ms']:
                return -1

        if record_data['latest_time'] < 0:
            delay = 0
        record_data['latest_time'] = self.current_ts()
        return delay

    def get_mouse_event(self, action, method, desc, params):
        delay = self.get_delay(method)
        if delay < 0:
            return None
        else:
            return {
                'delay': {
                    'action': 'TimeAction',
                    'method': 'time_sleep',
                    'desc': '思考时间：{}'.format(str(delay/1000)),
                    'params': {'second': delay/1000}
                },
                'action': {
                    'action': action,
                    'method': method,
                    'desc': desc,
                    'params': params
                }
            }

    def get_keyboard_event(self, action, method, desc, params):
        key = params['key']
        delay = self.get_delay(method)
        if delay < 0:
            return None
        else:
            try:
                keycode = key.value.vk
                key_name = rename_dict.get(key.name, key.name)
            except AttributeError:
                keycode = key.vk
                key_name = key.char
            if key_name is None:
                key_name = str(num_dict[keycode])
            if re.match('^([0-9])$', key_name) and keycode is None:
                key_name = 'num{}'.format(key_name)
            params['key'] = key_name
            event = {
                'delay': {
                    'action': 'TimeAction',
                    'method': 'time_sleep',
                    'desc': '思考时间：{}s'.format(str(delay/1000)),
                    'params': {'second': delay/1000}
                },
                'action': {
                    'action': action,
                    'method': method,
                    'desc': desc + key_name,
                    'params': params
                }
            }
            return event

    def on_move(self, x, y):
        action = "TemplateClientAction"
        method = "moveto"
        desc = "鼠标指定位置移动({}, {})".format(x, y)
        params = {"posx": x, "posy": y, "rel": False}
        event = self.get_mouse_event(action, method, desc, params)
        if event:
            if (record_data['is_recording']) and (not record_data['pause_record']):
                self.event_signal.emit(event)

    def on_click(self, x, y, button, pressed):
        action = "TemplateClientAction"
        method = 'mouse_down' if pressed else 'mouse_up'
        if pressed:
            desc = "鼠标指定位置({}, {})按下{}".format(x, y, button.name)
        else:
            desc = "鼠标指定位置({}, {})抬起{}".format(x, y, button.name)
        params = {"posx": x, "posy": y, "button": button.name}
        event = self.get_mouse_event(action, method, desc, params)
        if event:
            if (record_data['is_recording']) and (not record_data['pause_record']):
                self.event_signal.emit(event)

    def on_scroll(self, x, y, dx, dy):
        action = "TemplateClientAction"
        method = "scroll"
        if dy < 0:
            desc = "鼠标滑轮向下滚动"
        else:
            desc = "鼠标滑轮向上滚动"
        params = {"amount_to_scroll": dy}
        event = self.get_mouse_event(action, method, desc, params)
        if event:
            if (record_data['is_recording']) and (not record_data['pause_record']):
                self.event_signal.emit(event)

    def on_press(self, key):
        action = "TemplateClientAction"
        method = "press_down"
        desc = "键盘单个按键按下"
        params = {"key": key}
        event = self.get_keyboard_event(action, method, desc, params)
        if event:
            if (event['action']['params'].get('key') in ['f1', 'f2', 'f3']) or \
                    (record_data['is_recording']) and (not record_data['pause_record']):
                self.event_signal.emit(event)

    def on_release(self, key):
        action = "TemplateClientAction"
        method = "press_up"
        desc = "键盘单个按键松开"
        params = {"key": key}
        event = self.get_keyboard_event(action, method, desc, params)
        if event:
            if (event['action']['params'].get('key') in ['f1', 'f2', 'f3']) or \
                    (record_data['is_recording']) and (not record_data['pause_record']):
                self.event_signal.emit(event)

    def setup_hook(self, commandline=False):
        listener = {}
        if not commandline:
            mouse_listener = mouse.Listener(
                on_move=self.on_move,
                on_scroll=self.on_scroll,
                on_click=self.on_click
            )
            mouse_listener.start()
            listener["mouse"] = mouse_listener
        keyboard_listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        keyboard_listener.start()
        listener["keyboard"] = keyboard_listener
        return listener


class NewScriptSignal(QObject):
    new_signal = pyqtSignal()


NewScript = NewScriptSignal()
