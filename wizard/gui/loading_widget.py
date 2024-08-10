# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
import time
import logging

# Wizard modules
from wizard.core import image
from wizard.core import repository
from wizard.core import environment
from wizard.core import application
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import logging_widget

class loading_widget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(loading_widget, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.WindowType.CustomizeWindowHint |  QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Loading - {environment.get_project_name()}")

        self.fixed_width = 600
        self.fixed_height = 337

        self.build_ui()
        self.fill_ui()

    def showEvent(self, event):
        screen = QtGui.QGuiApplication.screenAt(QtGui.QCursor().pos())
        if not screen:
            screen = QtWidgets.QGuiApplication.primaryScreen()
        screenRect = screen.availableGeometry()
        screen_maxX = screenRect.bottomRight().x()
        screen_maxY = screenRect.bottomRight().y()
        self.move(int((screenRect.x()+screen_maxX-self.width())/2), int((screenRect.y()+screen_maxY-self.height())/2))
        event.accept()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(18,18,18,18)
        self.setLayout(self.main_layout)

        self.main_frame = QtWidgets.QFrame()
        self.main_frame.setObjectName('transparent_widget')

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(70)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 80))
        self.shadow.setXOffset(2)
        self.shadow.setYOffset(2)
        self.main_frame.setGraphicsEffect(self.shadow)

        #self.main_frame.setObjectName('loading_widget_frame')
        self.frame_layout = QtWidgets.QVBoxLayout()
        self.frame_layout.setContentsMargins(0,0,0,0)
        self.frame_layout.setSpacing(6)
        self.main_frame.setLayout(self.frame_layout)
        self.main_layout.addWidget(self.main_frame)

        self.image_label = QtWidgets.QLabel()
        self.frame_layout.addWidget(self.image_label)

        self.overlap_widget = QtWidgets.QWidget(self.main_frame)
        self.overlap_widget.setFixedSize(self.fixed_width, self.fixed_height)
        self.overlap_widget.setObjectName('transparent_widget')
        self.overlap_content_layout = QtWidgets.QVBoxLayout()
        self.overlap_content_layout.setContentsMargins(0,0,0,0)
        self.overlap_widget.setLayout(self.overlap_content_layout)
        
        self.overlap_content_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding))

        self.content_widget = QtWidgets.QWidget()
        self.content_widget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.content_widget.setObjectName('content_widget')
        self.content_widget.setStyleSheet("#content_widget{background: qlineargradient(spread:pad, x1:1 y1:0, x2:1 y2:1, stop:0 rgba(0, 0, 0, 0), stop:1 #24242b);border-bottom-left-radius:8px;border-bottom-right-radius:8px}")

        self.content_layout = QtWidgets.QHBoxLayout()
        self.content_layout.setContentsMargins(12,52,12,12)
        self.content_layout.setSpacing(4)
        self.content_widget.setLayout(self.content_layout)
        self.overlap_content_layout.addWidget(self.content_widget)

        self.wizard_logo = QtWidgets.QLabel()
        self.wizard_logo.setPixmap(QtGui.QIcon(ressources._wizard_ico_).pixmap(50))
        self.content_layout.addWidget(self.wizard_logo)

        self.datas_widget = QtWidgets.QWidget()
        self.datas_widget.setObjectName('transparent_widget')
        self.datas_layout = QtWidgets.QVBoxLayout()
        self.datas_layout.setContentsMargins(8,0,0,0)
        self.datas_layout.setSpacing(4)
        self.datas_widget.setLayout(self.datas_layout)
        self.content_layout.addWidget(self.datas_widget)

        self.datas_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding))

        self.project_and_user_layout = QtWidgets.QHBoxLayout()
        self.project_and_user_layout.setSpacing(10)
        self.project_and_user_layout.setContentsMargins(0,0,0,0)
        self.datas_layout.addLayout(self.project_and_user_layout)

        self.project_name_label = QtWidgets.QLabel()
        self.project_name_label.setObjectName("title_label")
        self.project_and_user_layout.addWidget(self.project_name_label)

        self.project_and_user_layout.addWidget(QtWidgets.QLabel('-'))

        self.user_label = QtWidgets.QLabel()
        self.project_and_user_layout.addWidget(self.user_label)

        self.project_and_user_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.infos_widget = QtWidgets.QWidget()
        self.infos_widget.setObjectName('transparent_widget')
        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(0,0,0,0)
        self.infos_widget.setLayout(self.infos_layout)
        self.datas_layout.addWidget(self.infos_widget)

        self.info_label = logging_label()
        self.info_label.setObjectName('bold_label')
        self.infos_layout.addWidget(self.info_label)

        self.infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.version_label = QtWidgets.QLabel()
        self.infos_layout.addWidget(self.version_label)

        self.build_label = QtWidgets.QLabel()
        #self.build_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.build_label)

    def fill_ui(self):
        self.project_name_label.setText(environment.get_project_name().capitalize())
        self.user_label.setText(environment.get_user())
        #self.info_label.setText(f'Loading {environment.get_project_name()}...')
        version_dic = application.get_version()
        self.version_label.setText(f"version {version_dic['MAJOR']}.{version_dic['MINOR']}.{version_dic['PATCH']}")
        self.build_label.setText(f"- build {version_dic['builds']}")

        project_row = repository.get_project_row_by_name(environment.get_project_name())
        project_image = image.convert_str_data_to_image_bytes(project_row['project_image'])
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(project_image)
        icon = QtGui.QIcon(pixmap)
        pm = gui_utils.round_corners_image_button(project_image, (self.fixed_width, self.fixed_height), 8)
        self.image_label.setPixmap(pm)

class logging_label(QtWidgets.QLabel):
    def __init__(self, long_formatter=False, parent=None):
        super(logging_label, self).__init__(parent)

        self.custom_handler = logging_widget.custom_handler(long_formatter, self)
        root_logger = logging.getLogger()
        root_logger.addHandler(self.custom_handler)

        self.connect_functions()

    def handle_record(self, record_tuple):
        level = record_tuple[0]
        record_msg = record_tuple[1]
        if record_msg != '\r\n' and record_msg != '\r' and record_msg != '\n':
            record_msg = record_msg.replace('\n', ' ')
            record_msg = record_msg.replace('\r', ' ')
            self.setText(record_msg)
            QtWidgets.QApplication.processEvents()

    def connect_functions(self):
        self.custom_handler.log_record.connect(self.handle_record)