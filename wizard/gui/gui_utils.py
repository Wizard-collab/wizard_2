# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

def move_ui(widget):
    desktop = QtWidgets.QApplication.desktop()
    screenRect = desktop.screenGeometry()

    screen_minX = screenRect.topLeft().x()
    screen_minY = screenRect.topLeft().y()
    screen_maxX = screenRect.bottomRight().x()
    screen_maxY = screenRect.bottomRight().y()
    cursor_x = QtGui.QCursor.pos().x()
    cursor_y = QtGui.QCursor.pos().y()
    win_width = widget.frameSize().width()
    win_heigth = widget.frameSize().height()

    if (cursor_y - 20 - win_heigth) <= screen_minY:
        posy = cursor_y - 10
        angley = 'top'
    else:
        posy = cursor_y - win_heigth + 10
        angley = 'bottom'
    if (cursor_x + 20 + win_width) >= screen_maxX:
        posx = cursor_x - win_width + 10
        anglex = 'right'
    else:
        posx = cursor_x - 10
        anglex = 'left'

    widget.move(posx, posy)
    return f"{angley}-{anglex}"

def round_image(label, image_bytes, radius):
        label.Antialiasing = True
        label.radius = radius/2
        label.target = QtGui.QPixmap(label.size())
        label.target.fill(QtCore.Qt.transparent)
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(image_bytes, 'png')
        pixmap = pixmap.scaled(
            radius, radius, QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation)
        painter = QtGui.QPainter(label.target)
        if label.Antialiasing:
            painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
            painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
        path = QtGui.QPainterPath()
        path.addRoundedRect(
            0, 0, label.width(), label.height(), label.radius, label.radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        label.setPixmap(label.target)

def round_corners_image(label, image_bytes, size_tuple, radius):
        label.Antialiasing = True
        label.radius = radius
        label.target = QtGui.QPixmap(label.size())
        label.target.fill(QtCore.Qt.transparent)
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(image_bytes, 'png')
        pixmap = pixmap.scaled(
            size_tuple[0], size_tuple[1], QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation)
        painter = QtGui.QPainter(label.target)
        if label.Antialiasing:
            painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
            painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
        path = QtGui.QPainterPath()
        path.addRoundedRect(
            0, 0, size_tuple[0], size_tuple[1], label.radius, label.radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        label.setPixmap(label.target)

class ElidedLabel(QtWidgets.QLabel):
    _width = _text = _elided = None

    def __init__(self, text='', width=40, parent=None):
        super(ElidedLabel, self).__init__(text, parent)
        self.setMinimumWidth(width if width > 0 else 1)

    def elidedText(self):
        return self._elided or ''

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        self.drawFrame(painter)
        margin = self.margin()
        rect = self.contentsRect()
        rect.adjust(margin, margin, -margin, -margin)
        text = self.text()
        width = rect.width()
        if text != self._text or width != self._width:
            self._text = text
            self._width = width
            self._elided = self.fontMetrics().elidedText(
                text, QtCore.Qt.ElideRight, width)
        option = QtWidgets.QStyleOption()
        option.initFrom(self)
        self.style().drawItemText(
            painter, rect, self.alignment(), option.palette,
            self.isEnabled(), self._elided, self.foregroundRole())

class QProgressBar(QtWidgets.QProgressBar):
    def __init__(self, parent=None):
        super(QProgressBar, self).__init__(parent)

    def paintEvent(self, event):
        qp = QtWidgets.QStylePainter(self)
        opt = QtWidgets.QStyleOptionProgressBar()
        self.initStyleOption(opt)
        rect = self.style().subElementRect(QtWidgets.QStyle.SE_ProgressBarContents, opt, self)
        minSize = rect.height()
        grooveSize = rect.width() - minSize - 1
        valueRange = self.maximum() - self.minimum()
        offset = self.value() / valueRange * grooveSize
        newValue = (minSize + 1 + offset) / rect.width() * valueRange
        if int(newValue) != newValue:
            newValue = min(self.maximum(), newValue + 1)
        opt.progress = newValue
        qp.drawControl(QtWidgets.QStyle.CE_ProgressBar, opt)

class password_lineEdit(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(password_lineEdit, self).__init__(parent)
        self.build_ui()
        self.connect_functions()
        self.toggle_password_visibility()

    def build_ui(self):
        self.setObjectName('password_lineEdit_frame')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,10,0)

        self.setLayout(self.main_layout)

        self.password_lineEdit = QtWidgets.QLineEdit()
        self.main_layout.addWidget(self.password_lineEdit)

        self.toggle_visibility_button = QtWidgets.QPushButton()
        self.toggle_visibility_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.toggle_visibility_button.setObjectName('password_visibility_button')
        self.toggle_visibility_button.setCheckable(True)
        self.toggle_visibility_button.setFixedSize(16,16)
        self.main_layout.addWidget(self.toggle_visibility_button)

    def connect_functions(self):
        self.toggle_visibility_button.clicked.connect(self.toggle_password_visibility)

    def toggle_password_visibility(self):
        if not self.toggle_visibility_button.isChecked():
            self.password_lineEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        else:
            self.password_lineEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)

    def text(self):
        return self.password_lineEdit.text()

    def setPlaceholderText(self, placeholderText):
        self.password_lineEdit.setPlaceholderText(placeholderText)



