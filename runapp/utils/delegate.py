from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QFont
from PyQt5.QtWidgets import QStyledItemDelegate


class BorderItemDelegate(QStyledItemDelegate):
    """绘制外边框"""
    def __init__(self, parent, role, floor):
        super(BorderItemDelegate, self).__init__(parent)
        self.borderRole = role
        self.floor = floor

    def paint(self, painter, option, index):
        pen = None
        width = None
        data = index.data(self.borderRole)
        if data:
            if data['floor'] == self.floor:
                pen = QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        rect = QtCore.QRect(option.rect)
        if pen is not None:
            width = max(pen.width(), 1)
            option.rect.adjust(width, width, -width, -width)
        super(BorderItemDelegate, self).paint(painter, option, index)
        if pen is not None:
            painter.save()
            painter.setClipRect(rect, QtCore.Qt.ReplaceClip)
            pen.setWidth(2 * width)
            painter.setPen(pen)
            painter.setFont(QFont('SimSun', 20))
            painter.drawRect(rect)
            painter.restore()