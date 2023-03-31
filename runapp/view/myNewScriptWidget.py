import os
import sys
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QColor, QCursor
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog, QTreeWidgetItem, QTreeWidget, \
    QAbstractItemView, QMessageBox, QMenu, QAction
from common.path import BasePath
from common.rw_yaml import write_yaml, read_yaml
from runapp.recorder.globals import record_data
from runapp.recorder.record_signals import NewScript
from runapp.ui.ui_newScriptWidget import Ui_newScriptWidget
from runapp.utils.delegate import BorderItemDelegate
from runapp.utils.params_desc import label_root_desc, label_params_desc
from runapp.utils.utils import get_directory_tree, text_input_change, file_operate
from runapp.view.message_box import QMyInputDialog, QMyMessageBox
from runapp.view.myRecordScriptWidget import QmyRecordScriptWidget


class QmyNewScriptWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)  # 调用父类的构造函数，创建QWidget窗体
        self.ui = Ui_newScriptWidget()  # 创建UI对象
        self.ui.setupUi(self)  # 构造UI
        self.customConfigUI()
        self.setupActionWidgetItem()
        self.temp_item = None
        self.ord_text = []              # 文本模式旧内容
        self.new_text = []              # 文本模式新内容
        self.step_list = []             # 视图模式步骤列表
        self.cur_step = {}              # 视图模式当前步骤
        self.copy_flag = None

    def customConfigUI(self):
        """自定义组件设置"""
        self.ui.actionTreeWidget.headerItem().setText(0, "注：可拖拽到右侧视图模式！")
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.viewTreeWidget.headerItem().setText(0, "注：请先新建或打开一个脚本文件！")
        self.ui.viewTreeWidget.setColumnWidth(0, 300)
        self.ui.viewTreeWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 初始化不能进行编辑
        # 拖拽设置
        self.ui.actionTreeWidget.setDragEnabled(True)
        self.ui.actionTreeWidget.setAcceptDrops(True)
        self.ui.actionTreeWidget.setDragDropOverwriteMode(True)
        self.ui.actionTreeWidget.setDragDropMode(QTreeWidget.DragOnly)
        self.ui.viewTreeWidget.setDragEnabled(True)
        self.ui.viewTreeWidget.setAcceptDrops(True)
        self.ui.viewTreeWidget.setDragDropMode(QTreeWidget.DragDrop)
        # 信号和事件关联
        self.ui.viewTreeWidget.dragEnterEvent = self.dragEnterEvent
        self.ui.viewTreeWidget.dropEvent = self.dropEvent
        self.ui.actionTreeWidget.itemDoubleClicked.connect(self.actionDoubleClicked)  # 绑定事件
        self.ui.scriptPlainTextEdit.isEditFinished.connect(self.on_scriptPlainTextEdit_isEditFinished)
        # 使用自绘组件
        delegate = BorderItemDelegate(self.ui.viewTreeWidget, Qt.UserRole, "param")
        self.ui.viewTreeWidget.setItemDelegate(delegate)
        # 右键菜单
        self.ui.viewTreeWidget.setContextMenuPolicy(Qt.CustomContextMenu)  # 打开右键菜单的策略
        self.ui.viewTreeWidget.customContextMenuRequested.connect(self.setupTreeWidgetItemMenu)  # 绑定事件

    def __init_file_tree_item(self, children, item):
        """文件树展示"""
        for file in children:
            tree_widget = self.__file_tree_display(file, item)
            if file.get('children'):
                self.__init_file_tree_item(file['children'], tree_widget)  # 递归

    @staticmethod
    def __file_tree_display(tree_dict, item):
        """文件树显示规则"""
        if os.path.isdir(tree_dict['href']):
            tree_widget = QTreeWidgetItem(item)
            tree_widget.setText(0, tree_dict['name'])
            tree_widget.setIcon(0, QIcon(os.path.join(BasePath.IMAGES_ICON_DIR, '文件夹.png')))
            tree_widget.setToolTip(0, tree_dict['name'])
            tree_widget.setExpanded(True)  # 默认展开一级文本
            tree_widget.setData(0, Qt.UserRole, {"name": tree_dict['name'], "href": tree_dict['href']})
            return tree_widget
        else:
            if tree_dict['name'].split('.')[1] == 'yaml':
                tree_widget = QTreeWidgetItem(item)
                tree_widget.setText(0, tree_dict['name'].split('.')[0])
                tree_widget.setIcon(0, QIcon(os.path.join(BasePath.IMAGES_ICON_DIR, 'YAML.png')))
                tree_widget.setToolTip(0, tree_dict['name'])
                tree_widget.setData(0, Qt.UserRole, {"name": tree_dict['name'], "href": tree_dict['href']})
                return tree_widget

    def setupActionWidgetItem(self):
        """【自定义组件】基础关键字TreeWidgetItem"""
        self.ui.actionTreeWidget.clear()
        file_tree = get_directory_tree(BasePath.ACTION_KEYWORD).get('children')
        for base_file in file_tree:
            base_floor = self.__file_tree_display(base_file, self.ui.actionTreeWidget)
            if base_file.get('children'):
                self.__init_file_tree_item(base_file['children'], base_floor)

    def make_header_floor_item(self, step_type: str) -> QTreeWidgetItem:
        """构造第一层item"""
        header_floor = QTreeWidgetItem(self.ui.viewTreeWidget)
        desc = label_root_desc(step_type)
        header_floor.setExpanded(True)  # 默认展开一级文本
        header_floor.setText(0, desc)
        header_floor.setData(0, Qt.UserRole, {"type": step_type, "floor": "header"})
        return header_floor

    @staticmethod
    def make_desc_floor_item(step_type: str, f2_value: dict) -> QTreeWidgetItem:
        """构造第二层item"""
        desc_floor = QTreeWidgetItem()
        desc_floor.setText(0, f2_value['desc'])
        # 美化
        if step_type == "step":
            desc_floor.setForeground(0, QColor(0, 0, 255))
            if f2_value.get('business'):
                desc_floor.setIcon(0, QIcon(os.path.join(BasePath.IMAGES_ICON_DIR, 'case_business.png')))
            else:
                desc_floor.setIcon(0, QIcon(os.path.join(BasePath.IMAGES_ICON_DIR, 'case_step.png')))
        elif step_type == "business":
            desc_floor.setForeground(0, QColor(0, 0, 255))
            desc_floor.setIcon(0, QIcon(os.path.join(BasePath.IMAGES_ICON_DIR, 'case_config.png')))
        desc_floor.setFlags(
            Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable |
            Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        )
        desc_floor.setData(0, Qt.UserRole, {"type": step_type, "floor": "desc",
                                            "key": "desc", "value": f2_value['desc']})
        return desc_floor

    @staticmethod
    def make_param_floor_item(step_type: str, f2_value: dict, f3_key: str, f3_value: str) -> QTreeWidgetItem:
        """构造第三层item"""
        param_floor = QTreeWidgetItem()
        if f2_value.get('business') and step_type == 'step':
            if f3_key == 'output':
                desc = '业务关键字出参(使用;分割多个);' + f3_key
            else:
                desc = '业务关键字入参;' + f3_key
        else:
            desc = label_params_desc(f3_key, step_type, f2_value.get('action'))
        param_floor.setText(0, desc)
        param_floor.setText(1, str(f3_value))
        param_floor.setForeground(1, QColor(0, 0, 255))
        param_floor.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)
        param_floor.setData(0, Qt.UserRole, {"type": step_type, "floor": "param",
                                             "key": f3_key, "value": str(f3_value)})
        param_floor.setData(1, Qt.UserRole, {"type": step_type, "floor": "param"})
        return param_floor

    def setupScriptTreeWidgetItem(self):
        """【自定义组件】测试用例TreeWidgetItem"""
        self.ui.viewTreeWidget.blockSignals(True)  # 进入阻塞模式
        self.ui.viewTreeWidget.clear()
        if not record_data['script_path']:
            return
        self.ui.viewTreeWidget.headerItem().setText(0, "步骤")
        self.ui.viewTreeWidget.headerItem().setText(1, "参数值")
        current_file_data = read_yaml(record_data['script_path'])
        try:
            if 'action' in record_data['script_path']:
                desc_floor = self.make_desc_floor_item('step', current_file_data[0])
                self.ui.viewTreeWidget.addTopLevelItem(desc_floor)
                if current_file_data[0].get('params'):
                    for f2_key, f2_value in current_file_data[0]['params'].items():
                        param_floor = self.make_param_floor_item('step', current_file_data[0], f2_key, f2_value)
                        desc_floor.addChild(param_floor)
            else:
                for f1_key, f1_value in current_file_data.items():
                    # 构造第一层TreeWidgetItem
                    header_floor = self.make_header_floor_item(f1_key)
                    self.ui.viewTreeWidget.addTopLevelItem(header_floor)
                    if not f1_value:
                        continue
                    for index, f2_value in enumerate(f1_value):
                        # 构造第二层TreeWidgetItem
                        desc_floor = self.make_desc_floor_item(f1_key, f2_value)
                        header_floor.addChild(desc_floor)
                        if f2_value.get('params'):
                            for f3_key, f3_value in f2_value['params'].items():
                                # 构造第三层TreeWidgetItem
                                param_floor = self.make_param_floor_item(f1_key, f2_value, f3_key, f3_value)
                                desc_floor.addChild(param_floor)
        except Exception as e:
            print(e)
        finally:
            self.ui.viewTreeWidget.blockSignals(False)  # 退出阻塞模式

    def setupScriptPlainTextEdit(self):
        """初始化文本内容"""
        try:
            self.ui.viewTreeWidget.blockSignals(True)  # 进入阻塞模式
            self.ui.scriptPlainTextEdit.setReadOnly(False)
            if not record_data['script_path']:
                return
            with open(record_data['script_path'], 'r', encoding='utf-8') as f:
                content = f.read()
            self.ui.scriptPlainTextEdit.setText(content)
        except Exception as e:
            print(e)
        finally:
            self.ui.viewTreeWidget.blockSignals(False)  # 退出阻塞模式

    def actionDoubleClicked(self, item, column):
        """测试用例双击"""
        if item is None or column is None:
            return
        item_data = item.data(0, Qt.UserRole)
        if os.path.isfile(item_data['href']):
            record_data['script_path'] = item_data['href']
            self.setupScriptTreeWidgetItem()
            self.setupScriptPlainTextEdit()
            if 'action' in record_data['script_path']:
                self.ui.scriptPlainTextEdit.setReadOnly(True)

    @pyqtSlot(bool)
    def on_addScriptButton_clicked(self):
        """单击新建脚本按钮-槽函数"""
        try:
            name, ok = QMyInputDialog(self).inputDialogText("新建脚本", "请输入要新建的脚本名：")
            if name and ok:
                script_path = os.path.join(BasePath.HAND_SCRIPT_DIR, name + '.yaml')
                write_yaml(script_path, BasePath.SCRIPT_TEMPLATE)
                record_data['script_path'] = script_path
                NewScript.new_signal.emit()
                self.ui.editLabel.setText("正在编辑：" + record_data['script_path'])
                self.setupScriptTreeWidgetItem()
                self.setupScriptPlainTextEdit()
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("新建", "新建脚本未知错误！\n错误:{}".format(e))

    @pyqtSlot(bool)
    def on_openScriptButton_clicked(self):
        """单击打开脚本按钮-槽函数"""
        try:
            folder_path = QFileDialog.getOpenFileNames(self, '打开脚本', BasePath.SCRIPT_DIR, "脚本文件(*.yaml)")
            if folder_path[0]:
                record_data['script_path'] = folder_path[0][0]
                self.ui.editLabel.setText("正在编辑：" + record_data['script_path'])
                self.setupScriptTreeWidgetItem()
                self.setupScriptPlainTextEdit()
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("打开", "打开脚本未知错误！\n错误:{}".format(e))

    @pyqtSlot(bool)
    def on_deleteScriptButton_clicked(self):
        """单击删除按钮-槽函数"""
        try:
            if not record_data['script_path']:
                QMyMessageBox(self).msgBoxCritical("删除", "当前未打开任何脚本，无法删除！")
                return
            if 'action' in record_data['script_path']:
                QMyMessageBox(self).msgBoxCritical("删除", "当前未打开任何脚本，无法删除！")
                return
            reply = QMyMessageBox(self).msgBoxQuestion('删除', '是否删除当前正在编辑的脚本？')
            if reply == QMessageBox.Yes:
                file_operate("delete", record_data['script_path'])
                record_data['script_path'] = None
                self.ui.editLabel.setText("正在编辑：")
                self.ui.viewTreeWidget.setColumnCount(1)
                self.ui.viewTreeWidget.headerItem().setText(0, "注：请先新建或打开一个脚本文件！")
                self.setupScriptTreeWidgetItem()
                self.setupScriptPlainTextEdit()
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("删除", "删除脚本未知错误！\n错误:{}".format(e))

    @pyqtSlot(bool)
    def on_recordScriptButton_clicked(self):
        """单击录制按钮-槽函数"""
        try:
            # 录制页面
            record_dialog = QmyRecordScriptWidget(self)
            record_dialog.setAttribute(Qt.WA_DeleteOnClose)
            record_dialog.setWindowFlag(Qt.Window, True)
            record_dialog.show()
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("录制", "录制脚本未知错误！\n错误:{}".format(e))

    def on_viewTreeWidget_itemClicked(self, item, column):
        """【自定义槽函数】测试用例单击事件"""
        try:
            self.ui.viewTreeWidget.blockSignals(True)  # 进入阻塞模式
            if item is None or column is None:
                return
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
        except Exception as e:
            print(e)
        finally:
            self.ui.viewTreeWidget.blockSignals(False)  # 退出阻塞模式

    def on_viewTreeWidget_itemDoubleClicked(self, item, column):
        """【自定义槽函数】测试用例双击事件"""
        try:
            self.ui.viewTreeWidget.blockSignals(True)  # 进入阻塞模式
            if item is None or column is None:
                return
            item_data = item.data(0, Qt.UserRole)
            if not item_data:
                return
            if 'action' in record_data['script_path']:
                item.setFlags(Qt.ItemIsEnabled)
            else:
                if item_data['floor'] == 'param' and column == 1:
                    self.ui.viewTreeWidget.editItem(item, column)  # 设为可编辑
                elif item_data['type'] in ['step', 'business']:
                    if item_data['floor'] == 'desc' and column == 0:
                        self.ui.viewTreeWidget.editItem(item, column)  # 设为可编辑
        except Exception as e:
            print(e)
        finally:
            self.ui.viewTreeWidget.blockSignals(False)  # 退出阻塞模式

    def on_viewTreeWidget_itemChanged(self, item, column):
        """【自定义槽函数】修改测试数据触发"""
        try:
            self.ui.viewTreeWidget.blockSignals(True)  # 进入阻塞模式
            if item is None or column is None:
                return
            current_file_data = read_yaml(record_data['script_path'])
            item_data = item.data(0, Qt.UserRole)
            if not item_data or not current_file_data:
                return
            item_text = text_input_change(item.text(column))
            if item_data['floor'] == 'param' and column == 1:
                cur_index = self.get_child_index(item.parent())  # 获取当前节点索引
                item_data['value'] = item_text
                item.setData(0, Qt.UserRole, item_data)
                current_file_data[item_data['type']][cur_index]['params'][item_data['key']] = item_text
                write_yaml(record_data['script_path'], current_file_data)
            elif item_data['floor'] == 'desc' and column == 0:
                if item_data['type'] in ['step', 'business']:
                    cur_index = self.get_child_index(item)  # 获取当前节点索引
                    item_data['value'] = item_text
                    item.setData(0, Qt.UserRole, item_data)
                    current_file_data[item_data['type']][cur_index][item_data['key']] = item_text
                    write_yaml(record_data['script_path'], current_file_data)
        except Exception as e:
            print(e)
        finally:
            self.setupScriptPlainTextEdit()
            self.ui.viewTreeWidget.blockSignals(False)  # 退出阻塞模式

    def on_scriptPlainTextEdit_isEditFinished(self, is_edit):
        """【自定义槽函数】文本模式修改测试数据触发"""
        try:
            if not is_edit:
                return
            with open(record_data['script_path'], 'r', encoding='utf-8') as f:
                self.ord_text = f.read()
            self.new_text = self.ui.scriptPlainTextEdit.text()
            with open(record_data['script_path'], 'w', encoding='utf-8') as f:
                f.write(self.new_text)
            read_yaml(record_data['script_path'])
        except Exception as e:
            with open(record_data['script_path'], 'w', encoding='utf-8') as f:
                f.writelines(self.ord_text)
            QMyMessageBox(self).msgBoxCritical("文本编辑", "yaml格式错误,请重新编辑！\n错误:{}".format(e))
        finally:
            self.setupScriptTreeWidgetItem()
            self.setupScriptPlainTextEdit()

    def dragEnterEvent(self, event) -> None:
        """拖动开始时Event"""
        try:
            source_widget: object = event.source()
            if source_widget == self.ui.viewTreeWidget:  # 判断拖入来源是否为测试用例
                item = self.ui.viewTreeWidget.currentItem()
                item_data = item.data(0, Qt.UserRole)
                if (item_data['type'] == 'step') and (item_data['floor'] == 'desc'):  # 判断是否是步骤和检查点
                    event.accept()  # 是的话就允许拖拽开始
                else:
                    event.ignore()
            elif source_widget == self.ui.actionTreeWidget:
                item = self.ui.actionTreeWidget.currentItem()
                item_data = item.data(0, Qt.UserRole)
                if item_data and record_data['script_path']:
                    event.accept()
                else:
                    event.ignore()
            else:
                event.ignore()
        except Exception as e:
            print(e)

    def dropEvent(self, event) -> None:
        """释放鼠标时Event"""
        try:
            source_widget = event.source()
            current_file_data = read_yaml(record_data['script_path'])  # 获取脚本数据
            cur_item = source_widget.currentItem()  # 当前移动的节点
            cur_index = self.get_child_index(cur_item)
            pos_item = self.ui.viewTreeWidget.itemAt(event.pos())  # 目标落下的节点
            if not pos_item:
                count = self.ui.viewTreeWidget.topLevelItem(1).childCount()
                if count > 0:
                    pos_item = self.ui.viewTreeWidget.topLevelItem(1).child(count - 1)
                else:
                    pos_item = self.ui.viewTreeWidget.topLevelItem(1)
            cur_data = cur_item.data(0, Qt.UserRole)
            pos_data = pos_item.data(0, Qt.UserRole)
            pos_index = self.get_child_index(pos_item)
            if 'action' in record_data['script_path']:
                self.ui.viewTreeWidget.setDragEnabled(False)
            else:
                if not current_file_data.get(pos_data['type']):
                    current_file_data['step'] = []
                step_list = current_file_data.get(pos_data['type'])  # 目标处的步骤列表
                if source_widget == self.ui.viewTreeWidget:  # 内部拖拽
                    if pos_data['type'] == 'step':
                        self.temp_item = cur_item.clone()
                        cur_action = step_list[cur_index]  # 当前移动的关键字
                        del step_list[cur_index]  # 删除yaml数据
                        self.parent_take_child(cur_item, cur_index)  # 删除树形结构
                        if pos_data['floor'] == 'header':
                            step_list.insert(0, cur_action)
                            self.parent_insert_child(pos_item, 0, self.temp_item)  # 插入树形结构
                        elif pos_data['floor'] == 'desc':
                            if pos_index < cur_index:
                                step_list.insert(pos_index + 1, cur_action)
                                self.parent_insert_child(pos_item, pos_index + 1, self.temp_item)  # 插入树形结构
                            else:
                                step_list.insert(pos_index, cur_action)
                                self.parent_insert_child(pos_item, pos_index, self.temp_item)  # 插入树形结构
                        write_yaml(record_data['script_path'], current_file_data)
                        self.setupScriptPlainTextEdit()
                        event.accept()
                    else:
                        event.ignore()
                elif source_widget == self.ui.actionTreeWidget:  # 来源与基础关键字拖拽
                    if pos_data['type'] == 'step':
                        cur_action = read_yaml(cur_data['href'])[0]
                        self.temp_item = self.make_new_step_item(pos_data['type'], cur_action)
                        if pos_data['floor'] == 'header':
                            step_list.insert(0, cur_action)
                            self.parent_insert_child(pos_item, 0, self.temp_item)  # 插入树形结构
                        elif pos_data['floor'] == 'desc':
                            step_list.insert(pos_index + 1, cur_action)
                            self.parent_insert_child(pos_item, pos_index + 1, self.temp_item)  # 插入树形结构
                        write_yaml(record_data['script_path'], current_file_data)
                        self.setupScriptPlainTextEdit()
                        event.accept()
                else:
                    event.ignore()
        except Exception as e:
            print(e)

    def setupTreeWidgetItemMenu(self, pos):
        """右键菜单界面"""
        if 'action' in record_data['script_path']:
            return
        cur_item = self.ui.viewTreeWidget.currentItem()
        at_item = self.ui.viewTreeWidget.itemAt(pos)
        if cur_item is not None and at_item is not None:  # 判断菜单是否为空
            item_data = at_item.data(0, Qt.UserRole)
            if item_data['type'] == 'step' and item_data['floor'] == 'desc':
                right_menu = QMenu()
                right_menu.addAction('复制')
                right_menu.addAction('剪切')
                right_menu.addAction('粘贴')
                right_menu.addAction('删除')
                right_menu.addAction('上移')
                right_menu.addAction('下移')
                right_menu.triggered[QAction].connect(self.on_treeWidgetItem_menu)  # 右键点击清空之后执行的操作
                right_menu.exec_(QCursor.pos())  # 执行之后菜单可以显示

    def on_treeWidgetItem_menu(self, action):
        """右键事件行为"""
        try:
            self.ui.viewTreeWidget.blockSignals(True)  # 进入阻塞模式
            command = action.text()
            cur_item = self.ui.viewTreeWidget.currentItem()
            cur_data = cur_item.data(0, Qt.UserRole)
            cur_index = self.get_child_index(cur_item)  # 获取当前节点索引
            current_file_data = read_yaml(record_data['script_path'])
            self.step_list = current_file_data[cur_data['type']]  # 当前处的步骤列表
            if command == "复制":
                self.temp_item = cur_item.clone()
                self.cur_step = self.step_list[cur_index]  # 当前移动的关键字
                self.copy_flag = True
            elif command == "剪切":
                self.temp_item = cur_item
                self.cur_step = self.step_list[cur_index]  # 当前移动的关键字
                self.copy_flag = False
            elif command == "粘贴":
                if self.copy_flag:
                    self.step_list.insert(cur_index + 1, self.cur_step)
                    write_yaml(record_data['script_path'], current_file_data)
                    self.parent_insert_child(cur_item, cur_index + 1, self.temp_item)  # 插入树形结构
                    self.setupScriptPlainTextEdit()
                else:
                    temp_index = self.get_child_index(self.temp_item)
                    del self.step_list[temp_index]
                    self.step_list.insert(cur_index + 1, self.cur_step)
                    write_yaml(record_data['script_path'], current_file_data)
                    self.temp_item.parent().removeChild(self.temp_item)
                    if temp_index > cur_index:
                        self.parent_insert_child(cur_item, cur_index + 1, self.temp_item)  # 插入树形结构
                    else:
                        self.parent_insert_child(cur_item, cur_index, self.temp_item)  # 插入树形结构
                    self.setupScriptPlainTextEdit()
            elif command == "删除":
                del self.step_list[cur_index]
                write_yaml(record_data['script_path'], current_file_data)
                self.parent_take_child(cur_item, cur_index)  # 删除树形结构
                self.setupScriptPlainTextEdit()
            elif command == "上移":
                self.temp_item = cur_item.clone()
                self.cur_step = self.step_list[cur_index]  # 当前移动的关键字
                if cur_index != 0:
                    self.step_list.insert(cur_index - 1, self.cur_step)
                    del self.step_list[cur_index + 1]
                    write_yaml(record_data['script_path'], current_file_data)
                    self.parent_insert_child(cur_item, cur_index - 1, self.temp_item)  # 插入树形结构
                    self.parent_take_child(cur_item, cur_index + 1)  # 删除树形结构
                    self.setupScriptPlainTextEdit()
            elif command == "下移":
                self.temp_item = cur_item.clone()
                self.cur_step = self.step_list[cur_index]  # 当前移动的关键字
                if cur_index != len(self.step_list) - 1:
                    self.step_list.insert(cur_index + 2, self.cur_step)
                    del self.step_list[cur_index]
                    write_yaml(record_data['script_path'], current_file_data)
                    self.parent_insert_child(cur_item, cur_index + 2, self.temp_item)  # 插入树形结构
                    self.parent_take_child(cur_item, cur_index)  # 删除树形结构
                    self.setupScriptPlainTextEdit()
        except Exception as e:
            QMyMessageBox(self).msgBoxCritical("右键菜单", "右键菜单未知错误！\n错误:{}".format(e))
        finally:
            self.ui.viewTreeWidget.blockSignals(False)  # 退出阻塞模式

    def get_child_index(self, cur_item: QTreeWidgetItem) -> int:
        """获取当前节点的所在父级的索引"""
        parent_item = cur_item.parent()
        if parent_item:
            return parent_item.indexOfChild(cur_item)
        else:
            return self.ui.viewTreeWidget.indexOfTopLevelItem(cur_item)

    def parent_insert_child(self, cur_item, index, add_item) -> None:
        """为父级节点插入字节的item"""
        cur_data = cur_item.data(0, Qt.UserRole)
        if cur_data['type'] == 'step' and cur_data['floor'] == 'header':
            return cur_item.insertChild(index, add_item)
        parent_item = cur_item.parent()
        if parent_item:
            return parent_item.insertChild(index, add_item)
        else:
            return self.ui.viewTreeWidget.insertTopLevelItem(index, add_item)

    def parent_take_child(self, cur_item, index) -> None:
        """为父级节点删除字节的item"""
        parent_item = cur_item.parent()
        if parent_item:
            parent_item.takeChild(index)
        else:
            self.ui.viewTreeWidget.takeTopLevelItem(index)

    def make_new_step_item(self, step_type, source_content) -> QTreeWidgetItem:
        """构造新的步骤节点"""
        new_item = self.make_desc_floor_item(step_type, source_content)
        if source_content.get('params'):
            for f3_key, f3_value in source_content['params'].items():
                # 构造第三层TreeWidgetItem
                param_floor = self.make_param_floor_item(step_type, source_content, f3_key, f3_value)
                new_item.addChild(param_floor)
        return new_item


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWidget = QmyNewScriptWidget()
    myWidget.show()
    sys.exit(app.exec_())
