# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
import yaml
import logging

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server

# Wizard core modules
from wizard.core import application
from wizard.core import user
from wizard.core import project
from wizard.core import tools
from wizard.core import launch
from wizard.vars import ressources

logger = logging.getLogger(__name__)

class splash_screen_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(splash_screen_widget, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.WindowType.CustomizeWindowHint |  QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Splash screen")
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

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
        self.header_widget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.header_widget.setObjectName('splash_screen_header')
        self.header_widget.setStyleSheet('#splash_screen_header{border-top-left-radius:8px;border-top-right-radius:8px;}')
        #self.header_widget.setStyleSheet('#splash_screen_header{background-color:#646ca2;border-top-left-radius:8px;border-top-right-radius:8px;}')
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(20,20,20,20)
        self.header_layout.setSpacing(10)
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.wizard_icon = QtWidgets.QLabel()
        self.wizard_icon.setPixmap(QtGui.QIcon(ressources._wizard_icon_).pixmap(40))
        self.header_layout.addWidget(self.wizard_icon)

        #self.title_layout = QtWidgets.QHBoxLayout()
        #self.title_layout.setSpacing(2)
        #self.title_layout.setContentsMargins(0,0,0,0)
        #self.title_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        #self.header_layout.addLayout(self.title_layout)

        self.title_label = QtWidgets.QLabel("Wizard")
        self.title_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding)
        self.title_label.setObjectName('title_label')
        self.title_label.setStyleSheet('font-size: 38px;')
        self.header_layout.addWidget(self.title_label)

        self.header_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding))

        self.version_label = QtWidgets.QLabel()
        self.version_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding)
        self.version_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.version_label.setObjectName('')
        self.header_layout.addWidget(self.version_label)

        self.recent_scenes_layout = QtWidgets.QVBoxLayout()
        self.recent_scenes_layout.setSpacing(20)
        self.recent_scenes_layout.setContentsMargins(20,20,20,20)
        self.main_layout.addLayout(self.recent_scenes_layout)

        self.recent_scenes_label = QtWidgets.QLabel("Recent scenes")
        self.recent_scenes_label.setObjectName('title_label_2')
        self.recent_scenes_layout.addWidget(self.recent_scenes_label)

        self.no_recent_scenes_label = QtWidgets.QLabel('No recent scenes')
        self.no_recent_scenes_label.setObjectName('gray_label')
        self.recent_scenes_layout.addWidget(self.no_recent_scenes_label)
        self.no_recent_scenes_label.setVisible(0)

        self.recent_scenes_list = QtWidgets.QTreeWidget()
        self.recent_scenes_list.setObjectName('tree_as_list_widget')
        self.recent_scenes_list.setStyleSheet('#tree_as_list_widget{background-color:transparent}')
        self.recent_scenes_list.setColumnCount(3)
        self.recent_scenes_list.header().resizeSection(0, 250)
        self.recent_scenes_list.header().resizeSection(1, 250)
        self.recent_scenes_list.setIndentation(0)
        self.recent_scenes_list.setHeaderHidden(True)
        self.recent_scenes_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.recent_scenes_list.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        #self.recent_scenes_list.setFixedHeight(160)
        self.recent_scenes_layout.addWidget(self.recent_scenes_list)

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
        self.updates_scrollArea_layout.setSpacing(6)
        self.updates_scrollArea_widget.setLayout(self.updates_scrollArea_layout)

        self.updates_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.updates_scrollArea.setWidgetResizable(True)
        self.updates_scrollArea.setWidget(self.updates_scrollArea_widget)

        self.updates_layout.addWidget(self.updates_scrollArea)

        self.updates_scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding))

        self.footer_layout = QtWidgets.QHBoxLayout()
        self.footer_layout.setContentsMargins(20,20,20,20)
        self.main_layout.addLayout(self.footer_layout)

        self.footer_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.show_at_startup_checkbox = QtWidgets.QCheckBox('Show at startup')
        self.show_at_startup_checkbox.setObjectName('transparent_widget')
        self.footer_layout.addWidget(self.show_at_startup_checkbox)

    def fill_ui(self):
        self.show_at_startup_checkbox.setChecked(user.user().get_show_splash_screen())
        self.version_dic = application.get_version()
        self.version_label.setText(f"{self.version_dic['MAJOR']}.{self.version_dic['MINOR']}.{self.version_dic['PATCH']} - build {self.version_dic['builds']}")
        self.fill_whats_new()

    def refresh(self):
        self.refresh_recent_scenes()

    def refresh_recent_scenes(self):
        self.recent_scenes_list.clear()
        recent_work_env_ids = user.user().get_recent_scenes()
        recent_work_env_ids.reverse()
        if len(recent_work_env_ids) == 0:
            self.no_recent_scenes_label.setVisible(1)
            self.recent_scenes_list.setVisible(0)
            return
        self.no_recent_scenes_label.setVisible(0)
        self.recent_scenes_list.setVisible(1)
        for work_env_tuple in recent_work_env_ids:
            if not project.check_work_env_existence(work_env_tuple[0]):
                continue
            item = recent_scene_item(work_env_tuple, self.recent_scenes_list.invisibleRootItem())
        self.recent_scenes_list.setFixedHeight(self.recent_scenes_list.invisibleRootItem().childCount()*31)

    def fill_whats_new(self):
        with open(ressources._whatsnew_yaml_, 'r') as f:
            whats_new_dic = yaml.load(f, Loader=yaml.Loader)
        version_key = f"{self.version_dic['MAJOR']}.{self.version_dic['MINOR']}.{self.version_dic['PATCH']}.{self.version_dic['builds']}"
        self.updates_list = []
        self.update_areas = []
        for update in whats_new_dic.keys():
            widget = update_area(whats_new_dic[update], update, version_key)
            self.updates_scrollArea_layout.addWidget(widget)
            self.update_areas.append(widget)
            
    def connect_functions(self):
        self.show_at_startup_checkbox.stateChanged.connect(self.toggle_show_at_startup)
        self.recent_scenes_list.itemDoubleClicked.connect(self.launch_recent_work_env)

    def launch_recent_work_env(self, item):
        work_env_id = item.work_env_id
        last_work_version_id = project.get_last_work_version(work_env_id, 'id')
        launch.launch_work_version(last_work_version_id[0])
        gui_server.refresh_ui()
        self.close()

    def toggle_show_at_startup(self, state):
        user.user().set_show_splash_screen(state)

    def showEvent(self, event):
        screen = QtGui.QGuiApplication.screenAt(QtGui.QCursor().pos())
        if not screen:
            screen = QtWidgets.QGuiApplication.primaryScreen()
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

class update_area(QtWidgets.QFrame):
    def __init__(self, update_dic, update, current_version_key, parent=None):
        super(update_area, self).__init__(parent)
        self.setObjectName('round_frame')
        self.setStyleSheet("#round_frame{background-color:rgba(255,255,255,5)}")
        self.update = update
        self.current_version_key = current_version_key
        self.update_dic = update_dic
        self.updates_list = []
        self.build_ui()
        self.fill_ui()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(10,10,10,10)
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)

        self.version_label = QtWidgets.QLabel()
        self.version_label.setObjectName('title_label')
        self.main_layout.addWidget(self.version_label)

        self.date_label = QtWidgets.QLabel()
        self.date_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.date_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,12, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.updates_layout = QtWidgets.QVBoxLayout()
        self.updates_layout.setContentsMargins(0,0,0,0)
        self.main_layout.addLayout(self.updates_layout)

    def fill_ui(self):
        day, hour = tools.convert_time(self.update_dic['time'])
        self.date_label.setText(f"{day} ( {tools.time_ago_from_timestamp(self.update_dic['time'])} )")
        if self.update != 'last':
            self.version_label.setText(self.update)
        else:
            self.version_label.setText(self.current_version_key)

        for update_tuple in self.update_dic['update_list']:
            widget = update_frame(update_tuple[0], update_tuple[1])
            self.updates_list.append(widget)
            self.updates_layout.insertWidget(0,widget)

class update_frame(QtWidgets.QFrame):
    def __init__(self, update_type, update, parent=None):
        super(update_frame, self).__init__(parent)

        self.update_type = update_type
        self.update = update

        self.setObjectName('transparent_widget')
        self.setStyleSheet('#transparent_widget{border-top:1px solid rgba(255,255,255,6)}')
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.build_ui()
        self.fill_ui()

    def fill_ui(self):
        self.update_type_label.setText(self.update_type)
        self.update_label.setText(self.update)

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,6,6,6)
        self.main_layout.setSpacing(2)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed))
        self.setLayout(self.main_layout)

        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(0,0,0,0)
        self.main_layout.addLayout(self.header_layout)

        self.update_type_label = QtWidgets.QLabel()
        self.update_type_label.setFixedWidth(60)
        self.update_type_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.update_type_label.setObjectName('gray_label')
        self.header_layout.addWidget(self.update_type_label)

        self.update_label = QtWidgets.QLabel()
        self.update_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addWidget(self.update_label)

class recent_scene_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, work_env_tuple, parent = None):
        super(recent_scene_item, self).__init__(parent)
        self.work_env_id = work_env_tuple[0]
        self.timestamp = work_env_tuple[1]
        self.fill_ui()

    def fill_ui(self):
        work_env_row = project.get_work_env_data(self.work_env_id)
        variant_row = project.get_variant_data(work_env_row['variant_id'])
        stage_row = project.get_stage_data(variant_row['stage_id'])
        asset_row = project.get_asset_data(stage_row['asset_id'])
        category_row = project.get_category_data(asset_row['category_id'])
        icon = gui_utils.QIcon_from_svg(ressources._stage_icons_dic_[stage_row['name']], 'gray')
        software_icon = gui_utils.QIcon_from_svg(ressources._softwares_icons_dic_[work_env_row['name']], 'gray')
        name = f"{category_row['name']} / {asset_row['name']} - {variant_row['name']}"
        self.setIcon(0, icon)
        self.setText(0, name)
        self.setIcon(1, software_icon)
        self.setText(1, work_env_row['name'])
        self.setText(2, tools.time_ago_from_timestamp(self.timestamp))
        self.setForeground(2, QtGui.QColor('gray'))