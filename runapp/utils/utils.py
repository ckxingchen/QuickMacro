import os
import ast
import re
import shutil
import time
from PyQt5.QtWidgets import QTreeWidgetItem


def text_input_change(text: str):
    """文本输入转换"""
    try:
        return ast.literal_eval(text)
    except ValueError:
        return text
    except Exception:
        return text


def get_directory_tree(folder: str) -> dict:
    """遍历本地目录返回字典树"""
    dir_tree = {'children': []}
    if os.path.isfile(folder):
        return {'name': os.path.basename(folder), 'href': os.path.abspath(folder)}
    else:
        dir_tree['name'] = os.path.basename(folder)
        dir_tree['href'] = folder
        for item in os.listdir(folder):
            dir_tree['children'].append(get_directory_tree(os.path.join(folder, item)))
        return dir_tree


def get_tree_widget_data_list(node: QTreeWidgetItem) -> list:
    """ 得到当前节点选中的所有分支， 返回一个 list """
    temp_list = []
    # 此处看下方注释 1
    for item in node.takeChildren():
        temp_list.append(item.data(0, 1))
        # 判断是否还有子分支
        if item.childCount():
            temp_list.extend(get_tree_widget_data_list(item))
        node.addChild(item)
    return temp_list


def file_operate(command, file_path, new_path=None):
    """文件操作"""
    if os.path.isdir(file_path):
        if command == 'copy':
            shutil.copytree(file_path, new_path)
        elif command == 'cut':
            shutil.copytree(file_path, new_path)
            shutil.rmtree(file_path)
        elif command == 'delete':
            shutil.rmtree(file_path)
        elif command == 'rename':
            shutil.move(file_path, new_path)
    else:
        if command == 'copy':
            shutil.copy(file_path, new_path)
        elif command == 'cut':
            shutil.move(file_path, new_path)
        elif command == 'delete':
            os.unlink(file_path)
        elif command == 'rename':
            shutil.move(file_path, new_path)


def kill_port_process(port):
    # 根据端口号杀死进程
    try:
        ret = os.popen("netstat -nao|findstr " + str(port))
        str_list = ret.read()

        if not str_list:
            print('端口未使用')
            return
        # 只关闭处于LISTENING的端口
        if 'TCP' in str_list:
            ret_list = str_list.replace(' ', '')
            ret_list = re.split('\n', ret_list)
            listening_list = [rl.split('LISTENING') for rl in ret_list]
            process_pids = [ll[1] for ll in listening_list if len(ll) >= 2]
            process_pid_set = set(process_pids)
            for process_pid in process_pid_set:
                os.popen('taskkill /pid ' + str(process_pid) + ' /F')
                print(port, '端口已被释放')
                time.sleep(1)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    path = r'D:\01MyCode\01DemoCode\AutoTestFramework_kw\TestSuits\01gjxt_web\TestCase'
    res = get_directory_tree(path)
    print(res)
