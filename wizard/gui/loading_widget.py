# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.core import image
from wizard.core import repository
from wizard.core import environment
from wizard.core import application
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils

class loading_widget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(loading_widget, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Loading - {environment.get_project_name()}")

        self.build_ui()
        self.fill_ui()

    def showEvent(self, event):
        desktop = QtWidgets.QApplication.desktop()
        screenRect = desktop.screenGeometry()
        screen_maxX = screenRect.bottomRight().x()
        screen_maxY = screenRect.bottomRight().y()
        self.move((screen_maxX-self.width())/2, (screen_maxY-self.height())/2)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(18,18,18,18)
        self.setLayout(self.main_layout)

        self.main_frame = QtWidgets.QFrame()

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(18)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 180))
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.main_frame.setGraphicsEffect(self.shadow)

        self.main_frame.setObjectName('loading_widget_frame')
        self.frame_layout = QtWidgets.QVBoxLayout()
        self.frame_layout.setContentsMargins(0,0,0,0)
        self.frame_layout.setSpacing(6)
        self.main_frame.setLayout(self.frame_layout)
        self.main_layout.addWidget(self.main_frame)

        self.image_label = QtWidgets.QLabel()
        #self.image_label.setFixedSize(400,226)
        self.frame_layout.addWidget(self.image_label)

        self.content_widget = QtWidgets.QWidget()
        self.content_widget.setObjectName('transparent_widget')
        self.content_layout = QtWidgets.QHBoxLayout()
        self.content_layout.setContentsMargins(12,12,12,12)
        self.content_layout.setSpacing(4)
        self.content_widget.setLayout(self.content_layout)
        self.frame_layout.addWidget(self.content_widget)

        self.wizard_logo = QtWidgets.QLabel()
        self.wizard_logo.setPixmap(QtGui.QIcon(ressources._wizard_ico_).pixmap(40))
        self.content_layout.addWidget(self.wizard_logo)

        self.datas_widget = QtWidgets.QWidget()
        self.datas_widget.setObjectName('transparent_widget')
        self.datas_layout = QtWidgets.QVBoxLayout()
        self.datas_layout.setContentsMargins(8,0,0,0)
        self.datas_layout.setSpacing(4)
        self.datas_widget.setLayout(self.datas_layout)
        self.content_layout.addWidget(self.datas_widget)

        self.datas_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.user_label = QtWidgets.QLabel()
        self.user_label.setObjectName('gray_label')
        self.datas_layout.addWidget(self.user_label)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(0,0,0,0)
        self.infos_widget.setLayout(self.infos_layout)
        self.datas_layout.addWidget(self.infos_widget)

        self.info_label = QtWidgets.QLabel()
        self.info_label.setObjectName('bold_label')
        self.infos_layout.addWidget(self.info_label)

        self.infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.version_label = QtWidgets.QLabel()
        self.infos_layout.addWidget(self.version_label)

        self.build_label = QtWidgets.QLabel()
        self.build_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.build_label)

    def fill_ui(self):
        self.user_label.setText(environment.get_user())
        self.info_label.setText(f'Loading {environment.get_project_name()}...')
        version_dic = application.get_version()
        self.version_label.setText(f"version {version_dic['MAJOR']}.{version_dic['MINOR']}.{version_dic['PATCH']}")
        self.build_label.setText(f"- build {version_dic['builds']}")

        project_row = repository.get_project_row_by_name(environment.get_project_name())
        project_image = image.convert_str_data_to_image_bytes(project_row['project_image'])
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(project_image)
        icon = QtGui.QIcon(pixmap)
        pm = gui_utils.round_corners_image_button(project_image, (350,197), 0)
        self.image_label.setPixmap(pm)
