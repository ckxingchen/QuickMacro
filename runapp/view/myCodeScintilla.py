import sys
from PyQt5 import Qsci, QtGui
from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QKeySequence
from PyQt5.QtWidgets import QApplication, QWidget


class CodeEditWidget(Qsci.QsciScintilla):
    isEditFinished = pyqtSignal(bool)

    def __init__(self, parent, lexer='yaml'):
        super().__init__(parent)
        self.text_edit_flag = False      # 是否编辑yaml标志
        self.current_text = None
        self.customConfigUI()
        self.set_syntax_lexer(lexer)

    def customConfigUI(self):
        """自定义设置UI"""
        self.setReadOnly(False)
        self.setEolMode(self.SC_EOL_LF)  # 以\n换行
        # 设置括号匹配模式
        self.setBraceMatching(QsciScintilla.StrictBraceMatch)
        # 设置 Tab 键功能
        self.setIndentationsUseTabs(True)  # 行首缩进采用Tab键，反向缩进是Shift +Tab
        self.setIndentationWidth(4)  # 行首缩进宽度为4个空格
        self.setIndentationGuides(True)  # 显示虚线垂直线的方式来指示缩进
        self.setTabIndents(True)  # 编辑器将行首第一个非空格字符推送到下一个缩进级别
        self.setAutoIndent(True)  # 插入新行时，自动缩进将光标推送到与前一个相同的缩进级别
        self.setBackspaceUnindents(True)
        self.setTabWidth(4)  # Tab 等于 4 个空格
        # 设置光标
        self.setCaretWidth(2)  # 光标宽度（以像素为单位），0表示不显示光标
        self.setCaretForegroundColor(QColor("darkCyan"))  # 光标颜色
        self.setCaretLineVisible(True)  # 是否高亮显示光标所在行
        self.setCaretLineBackgroundColor(QColor('#FFCFCF'))  # 光标所在行的底色
        # 设置行号
        self.setMarginsFont(QtGui.QFont('Arial', 10))  # 行号字体
        self.setMarginLineNumbers(0, True)  # 设置标号为0的页边显示行号
        self.setMarginWidth(0, 30)  # 行号宽度
        self.setMarkerForegroundColor(QColor("#FFFFFF"), 0)
        # 设置代码自动折叠区域
        self.setFolding(QsciScintilla.PlainFoldStyle)
        self.setMarginWidth(2, 12)
        # # 自动补全
        # self.setAutoCompletionSource(self.AcsAll)  # 自动补全。对于所有Ascii字符
        # self.setAutoCompletionCaseSensitivity(False)  # 自动补全大小写敏感
        # self.setAutoCompletionThreshold(1)  # 输入多少个字符才弹出补全提示

    def set_syntax_lexer(self, lexer):
        """设置语法类型"""
        if lexer == 'yaml':
            self.setYamlSyntax()

    def setYamlSyntax(self):
        lexer = Qsci.QsciLexerYAML()
        lexer.setDefaultFont(QtGui.QFont('Arial', 10))
        self.setLexer(lexer)  # 关键是这句

    def keyPressEvent(self, event):
        """【自定义槽函数】文本模式ctrl+s触发"""
        try:
            if event.matches(QKeySequence.Save):
                self.text_edit_flag = True
                self.isEditFinished.emit(self.text_edit_flag)
            super().keyPressEvent(event)
        except Exception as e:
            print(e)
        finally:
            self.current_text = self.text()

    def focusOutEvent(self, event):
        """【自定义槽函数】文本模式修改测试数据触发"""
        try:
            text = self.text()
            if not text:
                return
            if self.current_text != text:
                self.text_edit_flag = True
                self.isEditFinished.emit(self.text_edit_flag)
        except Exception as e:
            print(e)
        finally:
            self.current_text = self.text()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    code = CodeEditWidget(QWidget())
    yaml_path = r'D:\01MyCode\01DemoCode\pyqt5_widgets\01用户登录.yaml'
    with open(yaml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    code.setText(content)
    code.resize(400, 800)
    code.show()
    sys.exit(app.exec_())
