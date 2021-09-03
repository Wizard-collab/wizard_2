# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtProperty

# Wizard modules
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_server

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

    if (cursor_y - 30 - win_heigth) <= screen_minY:
        posy = cursor_y - 15
        angley = 'top'
    else:
        posy = cursor_y - win_heigth + 15
        angley = 'bottom'
    if (cursor_x + 30 + win_width) >= screen_maxX:
        posx = cursor_x - win_width + 15
        anglex = 'right'
    else:
        posx = cursor_x - 15
        anglex = 'left'

    widget.move(posx, posy)
    return f"{angley}-{anglex}"

def move_ui_bottom_right(widget, width, height):
    cursor_x = QtGui.QCursor.pos().x()
    cursor_y = QtGui.QCursor.pos().y()
    posx = cursor_x - width + 15
    posy = cursor_y - height + 15
    widget.move(posx, posy)

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

def round_icon(icon, image_bytes, radius):
    icon.Antialiasing = True
    icon.radius = radius/2
    icon.target = QtGui.QPixmap(QtCore.QSize(radius, radius))
    icon.target.fill(QtCore.Qt.transparent)
    pixmap = QtGui.QPixmap()
    pixmap.loadFromData(image_bytes, 'png')
    pixmap = pixmap.scaled(
        radius, radius, QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation)
    painter = QtGui.QPainter(icon.target)
    if icon.Antialiasing:
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
    path = QtGui.QPainterPath()
    path.addRoundedRect(
        0, 0, radius, radius, icon.radius, icon.radius)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, pixmap)
    icon.addPixmap(icon.target, QtGui.QIcon.Normal)
    icon.addPixmap(icon.target, QtGui.QIcon.Selected)
    
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

class separator(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(separator, self).__init__(parent)
        self.setMinimumHeight(2)
        self.setMaximumHeight(2)
        self.setObjectName('separator')

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

    def clear(self):
        self.password_lineEdit.clear()

    def setPlaceholderText(self, placeholderText):
        self.password_lineEdit.setPlaceholderText(placeholderText)

class search_bar(QtWidgets.QFrame):

    textChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super(search_bar, self).__init__(parent)
        self.build_ui()
        self.connect_functions()
        self.old_text=''

    def build_ui(self):
        self.setObjectName('search_bar_frame')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(8,4,8,4)
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)
        self.search_icon_label = QtWidgets.QLabel()
        self.search_icon_label.setPixmap(QtGui.QPixmap(ressources._search_icon_).scaled(
            18, 18, QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation))
        self.main_layout.addWidget(self.search_icon_label)
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setObjectName("search_lineEdit")
        self.main_layout.addWidget(self.search_bar)
        self.clear_search_button = QtWidgets.QPushButton()
        self.clear_search_button.setFixedSize(16,16)
        self.clear_search_button.setObjectName('clear_search_button')
        self.clear_search_button.setVisible(0)
        self.main_layout.addWidget(self.clear_search_button)

    def setPlaceholderText(self, placeholderText):
        self.search_bar.setPlaceholderText(placeholderText)

    def text(self):
        return self.search_bar.text()

    def setText(self, text):
        self.search_bar.setText(text)

    def connect_functions(self):
        self.search_bar.textChanged.connect(self.textChanged.emit)
        self.search_bar.textChanged.connect(self.text_changed)
        self.clear_search_button.clicked.connect(self.search_bar.clear)

    def keyPressEvent(self, event):
        self.search_bar.keyPressEvent(event)

    def keyReleaseEvent(self, event):
        self.search_bar.keyReleaseEvent(event)

    def setFocus(self, value):
        self.search_bar.setFocus(value)

    def text_changed(self, text):
        self.update_clear_button(text)
        self.update_bg(text)

    def _set_color(self, color):
        self.setStyleSheet('#search_bar_frame{background-color:rgba(%s, %s, %s, %s);}' % (color.red() ,
                                                                                                color.green(),
                                                                                                color.blue(), 
                                                                                                color.alpha()))

    def update_bg(self, text):
        if text == '' and self.old_text!='':
            self.anim = QtCore.QPropertyAnimation(self, b"color")
            self.anim.setDuration(200)
            self.anim.setStartValue(QtGui.QColor(119, 133, 222, 255))
            self.anim.setEndValue(QtGui.QColor(44, 44, 51, 255))
            self.anim.start()
        elif text != '' and self.old_text == '':
            self.anim = QtCore.QPropertyAnimation(self, b"color")
            self.anim.setDuration(200)
            self.anim.setStartValue(QtGui.QColor(44, 44, 51, 255))
            self.anim.setEndValue(QtGui.QColor(119, 133, 222, 255))
            self.anim.start()
        self.old_text = text

    def update_clear_button(self, text):
        if text == '':
            self.clear_search_button.setVisible(False)
        else:
            self.clear_search_button.setVisible(True)

    color = pyqtProperty(QtGui.QColor, fset=_set_color)

class RoundProgress(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(RoundProgress, self).__init__(parent)
        self.chunck_color = '#7785de'
        self.bg_color = '#24242b'
        self.angle=90
        self.drawAngle=self.angle
        self.lineWidth=18
        self.timeLine=QtCore.QTimeLine(2000,self)
        self.timeLine.frameChanged.connect(self.updateTimeline)
 
    def setValue(self, percent):
        #self.drawAngle = percent*3.6
        #self.update()

        self.angle=percent*3.6
        self.timeLine.setFrameRange(self.drawAngle,self.angle)
        self.timeLine.start()

    def updateTimeline(self,frame):
        self.drawAngle=frame
        self.update()

    def setChunckColor(self, color):
        self.chunck_color = color

    def paintEvent(self,event):
        the_rect=QtCore.QRectF(0,0,self.width(),self.height())
        if the_rect.isNull():
            return
        painter=QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing|QtGui.QPainter.SmoothPixmapTransform,on=True)
        painter.setViewport(self.width(),0,-self.width(),self.height())
        the_path=QtGui.QPainterPath()
        the_path.addEllipse(the_rect.adjusted(1,1,-1,-1))
        the_path.addEllipse(the_rect.adjusted(
            1+self.lineWidth,1+self.lineWidth,-1-self.lineWidth,-1-self.lineWidth))
        painter.fillPath(the_path,QtGui.QColor(6,79,103))
        the_gradient=QtGui.QConicalGradient(the_rect.center(),90)
        the_angle=self.drawAngle/360
        the_gradient.setColorAt(0,QtGui.QColor(self.chunck_color))
        the_gradient.setColorAt(the_angle,QtGui.QColor(self.chunck_color))
        if the_angle+0.001<1:
            the_gradient.setColorAt(the_angle+0.001,QtGui.QColor(self.bg_color))
        painter.fillPath(the_path,the_gradient)


def enterEvent(self, event=None):
    gui_server.tooltip(self.application_tooltip)
    self.legacy_enterEvent(event)

def leaveEvent(self, event=None):
    gui_server.tooltip('Tooltips')
    self.legacy_leaveEvent(event)

def application_tooltip(widget, custom_tooltip):
    widget.legacy_enterEvent = widget.enterEvent
    widget.application_tooltip = custom_tooltip
    widget.enterEvent = lambda self: enterEvent(widget)
    widget.legacy_leaveEvent = widget.leaveEvent
    widget.leaveEvent = lambda self: leaveEvent(widget)

def modify_application_tooltip(widget, custom_tooltip):
    widget.application_tooltip = custom_tooltip

def add_menu_to_menu_bar(menu_bar, title, icon=None):
    if icon is not None:
        menu = menu_bar.addMenu(icon, title)
    else:
        menu = menu_bar.addMenu(title)
    menu.setWindowFlags(QtCore.Qt.Popup | QtCore.Qt.FramelessWindowHint | QtCore.Qt.NoDropShadowWindowHint)
    menu.setAttribute(QtCore.Qt.WA_TranslucentBackground)
    return menu

class info_widget(QtWidgets.QFrame):
    def __init__(self, parent=None, transparent = None):
        super(info_widget, self).__init__(parent)
        self.transparent = transparent
        self.build_ui()

    def build_ui(self):
        self.setObjectName('dark_widget')
        if self.transparent:
            self.setObjectName('transparent_widget')
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.main_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(self.main_layout)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.image = QtWidgets.QLabel()
        self.image.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.image)
        self.text = QtWidgets.QLabel()
        self.text.setAlignment(QtCore.Qt.AlignCenter)
        self.text.setObjectName('title_label_gray')
        self.main_layout.addWidget(self.text)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

    def setImage(self, image):
        self.image.setPixmap(QtGui.QPixmap(image).scaled(
            150, 150, QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation))

    def setText(self, text):
        self.text.setText(text)