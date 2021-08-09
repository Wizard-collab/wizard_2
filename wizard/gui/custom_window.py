# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal

# Wizard modules
from wizard.vars import ressources

class custom_widget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(custom_widget, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(12)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 180))
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.setGraphicsEffect(self.shadow)

        self.build_main_ui()

    def add_title(self, title):
        self.header.add_title(title)

    def setCentralWidget(self, widget):
        self.main_container_layout.addWidget(widget)

    def add_header_widget(self, widget):
        self.header.add_header_widget(widget)

    def build_main_ui(self):
        self.setObjectName('transparent_widget')
        self.setStyleSheet('#transparent_widget{background:none;}')
        self.handle_layout = QtWidgets.QHBoxLayout()
        self.handle_layout.setContentsMargins(0,0,0,0)
        self.handle_layout.setSpacing(0)
        self.setLayout(self.handle_layout)

        self.left_resize_widget = QtWidgets.QWidget()
        self.left_resize_widget.setObjectName('transparent_widget')
        self.left_resize_layout = QtWidgets.QVBoxLayout()
        self.left_resize_layout.setContentsMargins(0,0,0,0)
        self.left_resize_layout.setSpacing(0)
        self.left_resize_widget.setLayout(self.left_resize_layout)
        self.handle_layout.addWidget(self.left_resize_widget)

        self.top_left_frame = resize_frame()
        self.top_left_frame.setObjectName('transparent_widget')
        self.top_left_frame.setCursor(QtGui.QCursor(QtCore.Qt.SizeFDiagCursor))
        self.top_left_frame.mouse_press.connect(self.start_top_left_resize)
        self.top_left_frame.setFixedSize(12, 12)
        self.left_resize_layout.addWidget(self.top_left_frame)

        self.left_frame = resize_frame()
        self.left_frame.setObjectName('transparent_widget')
        self.left_frame.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
        self.left_frame.mouse_press.connect(self.start_left_resize)
        self.left_frame.setFixedWidth(12)
        self.left_resize_layout.addWidget(self.left_frame)

        self.bottom_left_frame = resize_frame()
        self.bottom_left_frame.setObjectName('transparent_widget')
        self.bottom_left_frame.setCursor(QtGui.QCursor(QtCore.Qt.SizeBDiagCursor))
        self.bottom_left_frame.mouse_press.connect(self.start_bottom_left_resize)
        self.bottom_left_frame.setFixedSize(12, 12)
        self.left_resize_layout.addWidget(self.bottom_left_frame)

        self.central_resize_widget = QtWidgets.QWidget()
        self.central_resize_widget.setObjectName('transparent_widget')
        self.central_resize_layout = QtWidgets.QVBoxLayout()
        self.central_resize_layout.setContentsMargins(0,0,0,0)
        self.central_resize_layout.setSpacing(0)
        self.central_resize_widget.setLayout(self.central_resize_layout)
        self.handle_layout.addWidget(self.central_resize_widget)

        self.top_frame = resize_frame()
        self.top_frame.setObjectName('transparent_widget')
        self.top_frame.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))
        self.top_frame.mouse_press.connect(self.start_top_resize)
        self.top_frame.setFixedHeight(12)
        self.central_resize_layout.addWidget(self.top_frame)

        self.content_widget = QtWidgets.QWidget()
        self.content_widget.setObjectName('custom_content_widget')
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_layout.setContentsMargins(1,1,1,1)
        self.content_layout.setSpacing(2)
        self.content_widget.setLayout(self.content_layout)
        self.central_resize_layout.addWidget(self.content_widget)

        self.header = header()
        self.header.start_move.connect(self.start_move)
        self.header.toggle_size.connect(self.toggle_size)
        self.header.minimize.connect(self.minimize)
        self.content_layout.addWidget(self.header)

        self.main_container_widget = QtWidgets.QWidget()
        self.main_container_widget.setObjectName('dark_widget')
        self.main_container_layout = QtWidgets.QVBoxLayout()
        self.main_container_layout.setContentsMargins(0,0,0,0)
        self.main_container_layout.setSpacing(0)
        self.main_container_widget.setLayout(self.main_container_layout)
        self.content_layout.addWidget(self.main_container_widget)

        self.bottom_frame = resize_frame()
        self.bottom_frame.setObjectName('transparent_widget')
        self.bottom_frame.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))
        self.bottom_frame.mouse_press.connect(self.start_bottom_resize)
        self.bottom_frame.setFixedHeight(12)
        self.central_resize_layout.addWidget(self.bottom_frame)

        self.right_resize_widget = QtWidgets.QWidget()
        self.right_resize_widget.setObjectName('transparent_widget')
        self.right_resize_layout = QtWidgets.QVBoxLayout()
        self.right_resize_layout.setContentsMargins(0,0,0,0)
        self.right_resize_layout.setSpacing(0)
        self.right_resize_widget.setLayout(self.right_resize_layout)
        self.handle_layout.addWidget(self.right_resize_widget)        

        self.top_right_frame = resize_frame()
        self.top_right_frame.setObjectName('transparent_widget')
        self.top_right_frame.setCursor(QtGui.QCursor(QtCore.Qt.SizeBDiagCursor))
        self.top_right_frame.mouse_press.connect(self.start_top_right_resize)
        self.top_right_frame.setFixedSize(12, 12)
        self.right_resize_layout.addWidget(self.top_right_frame)

        self.right_frame = resize_frame()
        self.right_frame.setObjectName('transparent_widget')
        self.right_frame.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
        self.right_frame.mouse_press.connect(self.start_right_resize)
        self.right_frame.setFixedWidth(12)
        self.right_resize_layout.addWidget(self.right_frame)

        self.bottom_right_frame = resize_frame()
        self.bottom_right_frame.setObjectName('transparent_widget')
        self.bottom_right_frame.setCursor(QtGui.QCursor(QtCore.Qt.SizeFDiagCursor))
        self.bottom_right_frame.mouse_press.connect(self.start_bottom_right_resize)
        self.bottom_right_frame.setFixedSize(12, 12)
        self.right_resize_layout.addWidget(self.bottom_right_frame)

    def start_top_left_resize(self):
        self.windowHandle().startSystemResize(QtCore.Qt.LeftEdge | QtCore.Qt.TopEdge)

    def start_left_resize(self):
        self.windowHandle().startSystemResize(QtCore.Qt.LeftEdge)

    def start_bottom_left_resize(self):
        self.windowHandle().startSystemResize(QtCore.Qt.LeftEdge | QtCore.Qt.BottomEdge)

    def start_top_resize(self):
        self.windowHandle().startSystemResize(QtCore.Qt.TopEdge)

    def start_bottom_resize(self):
        self.windowHandle().startSystemResize(QtCore.Qt.BottomEdge)

    def start_top_right_resize(self):
        self.windowHandle().startSystemResize(QtCore.Qt.RightEdge | QtCore.Qt.TopEdge)

    def start_right_resize(self):
        self.windowHandle().startSystemResize(QtCore.Qt.RightEdge)

    def start_bottom_right_resize(self):
        self.windowHandle().startSystemResize(QtCore.Qt.RightEdge | QtCore.Qt.BottomEdge)

    def start_move(self):
        self.windowHandle().startSystemMove()

    def minimize(self):
        self.showMinimized()

    def resizeEvent(self, event):
        window = self.windowHandle()
        if window is not None:
            if window.windowState() == QtCore.Qt.WindowMaximized:
                self.right_resize_widget.setVisible(1)
                self.left_resize_widget.setVisible(1)
                self.bottom_frame.setVisible(1)
                self.top_frame.setVisible(1)

    def toggle_size(self):
        window = self.windowHandle()
        state = window.windowState()
        if state == QtCore.Qt.WindowNoState:
            window.setWindowStates(QtCore.Qt.WindowMaximized)
            self.right_resize_widget.setVisible(0)
            self.left_resize_widget.setVisible(0)
            self.bottom_frame.setVisible(0)
            self.top_frame.setVisible(0)
        else:
            window.setWindowStates(QtCore.Qt.WindowNoState)
            self.right_resize_widget.setVisible(1)
            self.left_resize_widget.setVisible(1)
            self.bottom_frame.setVisible(1)
            self.top_frame.setVisible(1)

class resize_frame(QtWidgets.QFrame):

    mouse_press = pyqtSignal(int)

    def __init__(self, parent=None):
        super(resize_frame, self).__init__(parent)

    def mousePressEvent(self, event):
        self.mouse_press.emit(1)

    def mouseEnterEvent(self, event):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.SizeVerCursor)

    def mouseLeaveEvent(self, event):
        QtWidgets.QApplication.restoreOverrideCursor()

class header(QtWidgets.QFrame):

    start_move = pyqtSignal(int)
    minimize = pyqtSignal(int)
    toggle_size = pyqtSignal(int)
    quit = pyqtSignal(int)

    def __init__(self, parent=None):
        super(header, self).__init__(parent)
        self.parent = parent
        self.setMinimumHeight(40)
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.setObjectName('custom_title_bar')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.title_label = QtWidgets.QLabel('')
        self.title_label.setVisible(0)
        self.title_label.setObjectName('window_title_label')
        self.main_layout.addWidget(self.title_label)

        self.custom_widgets_container = QtWidgets.QWidget()
        self.custom_widgets_container.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.custom_widgets_container.setObjectName('transparent_widget')
        self.custom_widgets_layout = QtWidgets.QHBoxLayout()
        self.custom_widgets_layout.setContentsMargins(0,0,0,0)
        self.custom_widgets_layout.setSpacing(0)
        self.custom_widgets_container.setLayout(self.custom_widgets_layout)
        self.main_layout.addWidget(self.custom_widgets_container)

        self.decoration_content = QtWidgets.QWidget()
        self.decoration_content.setObjectName('transparent_widget')
        self.decoration_content_layout = QtWidgets.QVBoxLayout()
        self.decoration_content_layout.setContentsMargins(0,0,0,0)
        self.decoration_content_layout.setSpacing(0)
        self.decoration_content.setLayout(self.decoration_content_layout)
        self.main_layout.addWidget(self.decoration_content)

        self.decoration_widget = QtWidgets.QWidget()
        self.decoration_widget.setObjectName('transparent_widget')
        self.decoration_layout = QtWidgets.QHBoxLayout()
        self.decoration_layout.setContentsMargins(6,6,6,6)
        self.decoration_layout.setSpacing(6)
        self.decoration_widget.setLayout(self.decoration_layout)
        self.decoration_content_layout.addWidget(self.decoration_widget)

        self.decoration_content_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.minimize_button = QtWidgets.QPushButton()
        self.minimize_button.setIcon(QtGui.QIcon(ressources._minimize_decoration_))
        self.minimize_button.setIconSize(QtCore.QSize(12,12))
        self.minimize_button.setObjectName('window_decoration_button')
        self.minimize_button.setFixedSize(16, 16)
        self.decoration_layout.addWidget(self.minimize_button)

        self.resize_button = QtWidgets.QPushButton()
        self.resize_button.setIcon(QtGui.QIcon(ressources._resize_decoration_))
        self.resize_button.setIconSize(QtCore.QSize(12,12))
        self.resize_button.setObjectName('window_decoration_button')
        self.resize_button.setFixedSize(16, 16)
        self.decoration_layout.addWidget(self.resize_button)

        self.quit_button = QtWidgets.QPushButton()
        self.quit_button.setIcon(QtGui.QIcon(ressources._quit_decoration_))
        self.quit_button.setIconSize(QtCore.QSize(12,12))
        self.quit_button.setObjectName('window_decoration_button')
        self.quit_button.setFixedSize(16, 16)
        self.decoration_layout.addWidget(self.quit_button)

    def mousePressEvent(self, event):
        self.start_move.emit(1)

    def mouseDoubleClickEvent(self, event):
        self.toggle_size.emit(1)

    def connect_functions(self):
        self.minimize_button.clicked.connect(self.minimize.emit)
        self.resize_button.clicked.connect(self.toggle_size.emit)
        self.quit_button.clicked.connect(self.quit.emit)

    def add_header_widget(self, widget):
        self.custom_widgets_layout.addWidget(widget)

    def add_title(self, title):
        self.title_label.setVisible(1)
        self.title_label.setText(title)

class custom_dialog(QtWidgets.QDialog, custom_widget):
    def __init__(self, parent=None):
        super(custom_dialog, self).__init__()
        self.header.quit.connect(self.reject)
        self.header.minimize_button.setVisible(0)
        self.header.resize_button.setVisible(0)

    def toggle_size(self):
        pass

class custom_window(custom_widget):
    def __init__(self, parent=None):
        super(custom_window, self).__init__()
        self.header.quit.connect(self.close)
