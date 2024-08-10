# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal
import colorsys

# Wizard gui modules
from wizard.gui import gui_utils

class color_picker(QtWidgets.QWidget):

    validate_signal = pyqtSignal(str)
    color_signal = pyqtSignal(str)

    def __init__(self, color='#798fe8', parent=None):
        super(color_picker, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.ToolTip)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.build_ui()
        self.connect_functions()

        self.set_color(color)

    def showEvent(self, event):
        gui_utils.move_ui(self)
        event.accept()

    def set_color(self, hex):
        h, s, v = self.hex_to_hsv(hex)
        self.set_HSV(h, s, v)

    def set_HSV(self, h, s, v):
        self.hue_selector.move(0, int((100 - h) * 1.85))
        self.color_view.setStyleSheet(f"border-radius: 5px;background-color: qlineargradient(x1:1, x2:0, stop:0 hsl({h}%,100%,50%), stop:1 #fff);")
        self.selector.move(int(s * 2 - 6), int((200 - v * 2) - 6))

    def hex_to_hsv(self, hex):
        hex = hex.replace('#', '')
        if len(hex) < 6: hex += "0"*(6-len(hex))
        elif len(hex) > 6: hex = hex[0:6]
        r,g,b = tuple(int(hex[i:i+2], 16) for i in (0,2,4))
        h,s,v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        return (h * 100, s * 100, v * 100)

    def leaveEvent(self, event):
        h, s, v = self.get_color()
        self.validate_signal.emit(self.hsv_to_hex(h, s, v))
        self.close()

    def connect_functions(self):
        self.hue.mouseMoveEvent = self.moveHueSelector
        self.black_overlay.mouseMoveEvent = self.moveSVSelector
        self.black_overlay.mousePressEvent = self.moveSVSelector

    def moveSVSelector(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            pos = event.pos()
            if pos.x() < 0: pos.setX(0)
            if pos.y() < 0: pos.setY(0)
            if pos.x() > 200: pos.setX(200)
            if pos.y() > 200: pos.setY(200)
            self.selector.move(pos - QtCore.QPoint(6,6))
            self.hsvChanged()

    def moveHueSelector(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            pos = event.pos().y()
            if pos < 0: pos = 0
            if pos > 185: pos = 185
            self.hue_selector.move(QtCore.QPoint(0,pos))
            self.hsvChanged()

    def hsv_to_hex(self, h, s, v):
        r,g,b = colorsys.hsv_to_rgb(h / 100.0, s / 100.0, v / 100.0)
        hex = '#%02x%02x%02x' % (int(r*255),int(g*255),int(b*255))
        return hex

    def hsvChanged(self):
        h, s, v = self.get_color()
        self.color_signal.emit(self.hsv_to_hex(h,s,v))
        self.color_view.setStyleSheet(f"border-radius: 5px;background-color: qlineargradient(x1:1, x2:0, stop:0 hsl({h}%,100%,50%), stop:1 #fff);")

    def get_color(self):
        h,s,v = (100 - self.hue_selector.y() / 1.85, (self.selector.x() + 6) / 2.0, (194 - self.selector.y()) / 2.0)
        return h, s, v

    def build_ui(self):
        self.main_widget_layout = QtWidgets.QHBoxLayout()
        self.main_widget_layout.setContentsMargins(12, 12, 12, 12)
        self.setLayout(self.main_widget_layout)

        self.main_widget = QtWidgets.QFrame()
        self.main_widget.setMaximumWidth(300)
        self.main_widget.setObjectName('black_round_frame')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setSpacing(6)
        self.main_widget.setLayout(self.main_layout)
        self.main_widget_layout.addWidget(self.main_widget)

        self.color_view = QtWidgets.QFrame(self)
        self.color_view.setMinimumSize(QtCore.QSize(200, 200))
        self.color_view.setMaximumSize(QtCore.QSize(200, 200))
        self.color_view.setStyleSheet("/* ALL CHANGES HERE WILL BE OVERWRITTEN */;\n"
        "background-color: qlineargradient(x1:1, x2:0, stop:0 hsl(0%,100%,50%), stop:1 rgba(255, 255, 255, 255));border-radius:6px;\n"
        "\n"
        "")
        self.color_view.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.color_view.setFrameShadow(QtWidgets.QFrame.Raised)
        self.color_view.setObjectName("color_view")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.color_view)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.black_overlay = QtWidgets.QFrame(self.color_view)
        self.black_overlay.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0, 0, 0, 0), stop:1 rgba(0, 0, 0, 255));;border-radius:4px;\n"
        "\n"
        "\n"
        "")
        self.black_overlay.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.black_overlay.setFrameShadow(QtWidgets.QFrame.Raised)
        self.black_overlay.setObjectName("black_overlay")
        self.selector = QtWidgets.QFrame(self.black_overlay)
        self.selector.setGeometry(QtCore.QRect(194, 20, 12, 12))
        self.selector.setMinimumSize(QtCore.QSize(12, 12))
        self.selector.setMaximumSize(QtCore.QSize(12, 12))
        self.selector.setStyleSheet("background-color:none;\n"
        "border: 2px solid white;\n"
        "border-radius: 6px;")
        self.selector.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.selector.setFrameShadow(QtWidgets.QFrame.Raised)
        self.selector.setObjectName("selector")
        self.verticalLayout_2.addWidget(self.black_overlay)
        self.main_layout.addWidget(self.color_view)
        self.frame_2 = QtWidgets.QFrame(self)
        self.frame_2.setObjectName('transparent_widget')
        self.frame_2.setMinimumSize(QtCore.QSize(12, 0))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.hue_bg = QtWidgets.QFrame(self.frame_2)
        self.hue_bg.setGeometry(QtCore.QRect(0, 0, 12, 200))
        self.hue_bg.setMinimumSize(QtCore.QSize(12, 200))
        self.hue_bg.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 rgba(255, 0, 0, 255), stop:0.166 rgba(255, 255, 0, 255), stop:0.333 rgba(0, 255, 0, 255), stop:0.5 rgba(0, 255, 255, 255), stop:0.666 rgba(0, 0, 255, 255), stop:0.833 rgba(255, 0, 255, 255), stop:1 rgba(255, 0, 0, 255));\n"
        "border-radius: 6px;")
        self.hue_bg.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.hue_bg.setFrameShadow(QtWidgets.QFrame.Raised)
        #self.hue_bg.setObjectName("hue_bg")
        self.hue_selector = QtWidgets.QLabel(self.frame_2)
        self.hue_selector.setGeometry(QtCore.QRect(0, 185, 0, 12))
        self.hue_selector.setMinimumSize(QtCore.QSize(12, 0))
        self.hue_selector.setStyleSheet("background-color: none;\n"
        "border: 2px solid white;\n"
        "border-radius: 6px;")
        self.hue_selector.setText("")
        self.hue_selector.setObjectName("hue_selector")
        self.hue = QtWidgets.QFrame(self.frame_2)
        self.hue.setGeometry(QtCore.QRect(0, 0, 12, 200))
        self.hue.setMinimumSize(QtCore.QSize(12, 200))
        self.hue.setStyleSheet("background-color: none;")
        self.hue.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.hue.setFrameShadow(QtWidgets.QFrame.Raised)
        self.hue.setObjectName("hue")
        self.main_layout.addWidget(self.frame_2)