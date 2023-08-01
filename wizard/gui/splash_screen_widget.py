# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import yaml
import logging

# Wizard modules
from wizard.vars import ressources
from wizard.core import application
from wizard.core import user

logger = logging.getLogger(__name__)

class splash_screen_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(splash_screen_widget, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint |  QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Splash screen")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.build_ui()
        self.fill_ui()
        self.connect_functions()

    def build_ui(self):
        self.resize(700,700)
        self.setObjectName('transparent_widget')
        self.widget_layout = QtWidgets.QVBoxLayout()
        self.widget_layout.setContentsMargins(18,18,18,18)
        self.setLayout(self.widget_layout)

        self.main_frame = QtWidgets.QFrame()
        self.main_frame.setObjectName('dark_round_frame')
        self.main_frame.setStyleSheet("#dark_round_frame{background: qlineargradient(spread:pad, x1:1 y1:0, x2:1 y2:1, stop:0 #141418, stop:1 #1d1d23);border-top-left-radius:8px;border-top-right-radius:8px;}")

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(70)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 80))
        self.shadow.setXOffset(2)
        self.shadow.setYOffset(2)
        self.main_frame.setGraphicsEffect(self.shadow)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.main_frame.setLayout(self.main_layout)
        self.widget_layout.addWidget(self.main_frame)

        self.header_widget = QtWidgets.QWidget()
        self.header_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.header_widget.setObjectName('transparent_widget')
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(20,20,20,20)
        self.header_layout.setSpacing(20)
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.wizard_icon = QtWidgets.QLabel()
        self.wizard_icon.setPixmap(QtGui.QIcon(ressources._wizard_icon_).pixmap(50))
        self.header_layout.addWidget(self.wizard_icon)

        self.title_layout = QtWidgets.QVBoxLayout()
        self.title_layout.setSpacing(2)
        self.title_layout.setContentsMargins(0,0,0,0)
        self.header_layout.addLayout(self.title_layout)

        self.title_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.title_label = QtWidgets.QLabel("Wizard")
        self.title_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.title_label.setObjectName('title_label')
        self.title_layout.addWidget(self.title_label)

        self.version_label = QtWidgets.QLabel()
        self.version_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.version_label.setObjectName('title_label_gray')
        self.title_layout.addWidget(self.version_label)

        self.title_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.header_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.recent_scenes_layout = QtWidgets.QVBoxLayout()
        self.recent_scenes_layout.setSpacing(20)
        self.recent_scenes_layout.setContentsMargins(20,0,20,20)
        self.main_layout.addLayout(self.recent_scenes_layout)

        self.recent_scenes_label = QtWidgets.QLabel("Recent scenes")
        self.recent_scenes_label.setObjectName('title_label_2')
        self.recent_scenes_layout.addWidget(self.recent_scenes_label)

        self.updates_layout = QtWidgets.QVBoxLayout()
        self.updates_layout.setContentsMargins(20,0,20,20)
        self.updates_layout.setSpacing(20)
        self.main_layout.addLayout(self.updates_layout)

        self.updates_label = QtWidgets.QLabel("Last updates")
        self.updates_label.setObjectName('title_label_2')
        self.updates_layout.addWidget(self.updates_label)

        self.updates_scrollArea = QtWidgets.QScrollArea()
        self.updates_scrollArea.setObjectName('transparent_widget')

        self.updates_scrollArea_widget = QtWidgets.QWidget()
        self.updates_scrollArea_widget.setObjectName('transparent_widget')
        self.updates_scrollArea_layout = QtWidgets.QVBoxLayout()
        self.updates_scrollArea_layout.setContentsMargins(0,0,0,0)
        self.updates_scrollArea_layout.setSpacing(1)
        self.updates_scrollArea_widget.setLayout(self.updates_scrollArea_layout)

        self.updates_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.updates_scrollArea.setWidgetResizable(True)
        self.updates_scrollArea.setWidget(self.updates_scrollArea_widget)

        self.updates_layout.addWidget(self.updates_scrollArea)

        self.updates_scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        #self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.footer_layout = QtWidgets.QHBoxLayout()
        self.footer_layout.setContentsMargins(20,20,20,20)
        self.main_layout.addLayout(self.footer_layout)

        self.footer_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.show_at_startup_checkbox = QtWidgets.QCheckBox('Show at startup')
        self.show_at_startup_checkbox.setObjectName('transparent_widget')
        self.footer_layout.addWidget(self.show_at_startup_checkbox)

    def fill_ui(self):
        self.show_at_startup_checkbox.setChecked(user.user().get_show_splash_screen())

        self.version_dic = application.get_version()
        self.version_label.setText(f"{self.version_dic['MAJOR']}.{self.version_dic['MINOR']}.{self.version_dic['PATCH']} - build {self.version_dic['builds']}")
        self.fill_whats_new()

    def fill_whats_new(self):

        with open(ressources._whatsnew_yaml_, 'r') as f:
            whats_new_dic = yaml.load(f, Loader=yaml.Loader)

        version_key = f"{self.version_dic['MAJOR']}.{self.version_dic['MINOR']}.{self.version_dic['PATCH']}"
        self.updates_list = []
        if version_key in whats_new_dic.keys():
            for update_tuple in whats_new_dic[version_key]['update_list']:
                widget = update_frame(update_tuple[0], update_tuple[1])
                self.updates_list.append(widget)
                self.updates_scrollArea_layout.insertWidget(0,widget)

        #with open(ressources._whatsnew_yaml_, 'r') as f:
        #    html_data = f.read()

        #self.textedit.insertHtml(html_data)

    def connect_functions(self):
        self.show_at_startup_checkbox.stateChanged.connect(self.toggle_show_at_startup)

    def toggle_show_at_startup(self, state):
        user.user().set_show_splash_screen(state)

    def showEvent(self, event):
        screen = QtGui.QGuiApplication.screenAt(QtGui.QCursor().pos())
        if not screen:
            screen = QtWidgets.QApplication.desktop()
        screenRect = screen.availableGeometry()
        screen_maxX = screenRect.bottomRight().x()
        screen_maxY = screenRect.bottomRight().y()
        self.move(int((screenRect.x()+screen_maxX-self.width())/2), int((screenRect.y()+screen_maxY-self.height())/2))
        self.setFocus()

    def toggle(self):
        if self.isVisible():
            if not self.isActiveWindow():
                self.show()
                self.raise_()
            else:
                self.hide()
        else:
            self.show()
            self.raise_()

    def focusOutEvent(self,event):
        if not self.focusWidget().isAncestorOf(self):
            self.setFocus()
            return
        self.close()

class update_frame(QtWidgets.QFrame):
    def __init__(self, update_type, update, parent=None):
        super(update_frame, self).__init__(parent)

        self.update_type = update_type
        self.update = update

        self.setObjectName('transparent_widget')
        self.setStyleSheet('#transparent_widget{border-top:1px solid rgba(255,255,255,6)}')
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.build_ui()
        self.fill_ui()

    def fill_ui(self):
        self.update_type_label.setText(self.update_type)
        if self.update_type == 'new':
            color = '#96ca69'
        elif self.update_type == 'debug':
            color = '#f79360'
        #self.update_type_label.setStyleSheet(f"color:{color}")
        self.update_label.setText(self.update)

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,6,6,6)
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)

        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(0,0,0,0)
        self.main_layout.addLayout(self.header_layout)

        self.update_type_label = QtWidgets.QLabel()
        self.update_type_label.setFixedWidth(60)
        self.update_type_label.setAlignment(QtCore.Qt.AlignTop)
        self.update_type_label.setObjectName('gray_label')
        self.header_layout.addWidget(self.update_type_label)

        self.update_label = QtWidgets.QLabel()
        self.update_label.setAlignment(QtCore.Qt.AlignLeft)
        self.main_layout.addWidget(self.update_label)