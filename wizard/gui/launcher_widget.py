# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.vars import ressources
from wizard.core import project
from wizard.core import tools

# Wizard gui modules

class launcher_widget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(launcher_widget, self).__init__(parent)
        self.stage_id = None
        self.build_ui()
        self.connect_functions()
        self.fill_state_comboBox()
        self.refresh(1)

    def refresh(self, stage_id):
        self.stage_id = stage_id
        self.refresh_variants()

    def refresh_variants(self):
        self.variant_comboBox.clear()
        self.variants_dic = dict()
        variants_rows = project.get_stage_childs(self.stage_id)
        for variant_row in variants_rows:
            self.variants_dic[variant_row['name']] = variant_row['id']
            self.variant_comboBox.addItem(variant_row['name'])
        self.refresh_work_envs()

    def refresh_work_envs(self):
        self.work_env_comboBox.clear()
        self.work_envs_dic = dict()
        variant_id = self.variants_dic[self.variant_comboBox.currentText()]
        state = project.get_variant_data(variant_id, 'state')
        self.state_comboBox.setCurrentText(state)
        work_env_rows = project.get_variant_work_envs_childs(variant_id)
        for work_env_row in work_env_rows:
            self.work_envs_dic[work_env_row['name']] = work_env_row['id']
            self.work_env_comboBox.addItem(work_env_row['name'])
        self.refresh_versions()

    def refresh_versions(self):
        self.version_comboBox.clear()
        self.versions_dic = dict()
        work_env_id = self.work_envs_dic[self.work_env_comboBox.currentText()]
        version_rows = project.get_work_versions(work_env_id)
        for version_row in version_rows:
            self.versions_dic[version_row['name']] = version_row['id']
            self.version_comboBox.addItem(version_row['name'])
        self.refresh_infos()

    def refresh_infos(self):
        version_id = self.versions_dic[self.version_comboBox.currentText()]
        version_row = project.get_version_data(version_id)
        self.user_label.setText(version_row['creation_user'])
        self.comment_label.setText(version_row['comment'])
        day, hour = tools.convert_time(version_row['creation_time'])
        self.date_label.setText(f"{day} - {hour}")

    def fill_state_comboBox(self):
        self.state_comboBox.addItem('todo')
        self.state_comboBox.addItem('wip')
        self.state_comboBox.addItem('done')
        self.state_comboBox.addItem('error')

    def update_state_comboBox_style(self):
        current_state = self.state_comboBox.currentText()
        if current_state == 'todo':
            color = 'gray'
        elif current_state == 'wip':
            color = '#f79360'
        elif current_state == 'done':
            color = '#9cf277'
        elif current_state == 'error':
            color = '#f0605b'
        self.state_comboBox.setStyleSheet(f"background-color:{color};")

    def connect_functions(self):
        self.state_comboBox.currentTextChanged.connect(self.update_state_comboBox_style)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.screenshot_button = QtWidgets.QPushButton()
        self.main_layout.addWidget(self.screenshot_button)

        self.variant_widget = QtWidgets.QWidget()
        self.variant_layout = QtWidgets.QHBoxLayout()
        self.variant_layout.setContentsMargins(0,0,0,0)
        self.variant_layout.setSpacing(6)
        self.variant_widget.setLayout(self.variant_layout)
        self.main_layout.addWidget(self.variant_widget)

        self.variant_comboBox = QtWidgets.QComboBox()
        self.variant_comboBox.setItemDelegate(QtWidgets.QStyledItemDelegate())
        self.variant_layout.addWidget(self.variant_comboBox)

        self.state_comboBox = QtWidgets.QComboBox()
        self.state_comboBox.setItemDelegate(QtWidgets.QStyledItemDelegate())
        self.variant_layout.addWidget(self.state_comboBox)

        self.add_variant_button = QtWidgets.QPushButton()
        self.add_variant_button.setFixedSize(29,29)
        self.add_variant_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.add_variant_button.setIconSize(QtCore.QSize(14,14))
        self.variant_layout.addWidget(self.add_variant_button)

        self.work_env_comboBox = QtWidgets.QComboBox()
        self.work_env_comboBox.setItemDelegate(QtWidgets.QStyledItemDelegate())
        self.main_layout.addWidget(self.work_env_comboBox)

        self.version_comboBox = QtWidgets.QComboBox()
        self.version_comboBox.setItemDelegate(QtWidgets.QStyledItemDelegate())
        self.main_layout.addWidget(self.version_comboBox)

        self.spaceItem = QtWidgets.QSpacerItem(100,25,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.comment_label = QtWidgets.QLabel("Retake mdr lol prout proueozj foezifj eoifjzef")
        self.comment_label.setWordWrap(True)
        self.main_layout.addWidget(self.comment_label)

        self.version_infos_widget = QtWidgets.QWidget()
        self.version_infos_layout = QtWidgets.QHBoxLayout()
        self.version_infos_layout.setContentsMargins(0,0,0,0)
        self.version_infos_layout.setSpacing(6)
        self.version_infos_widget.setLayout(self.version_infos_layout)
        self.main_layout.addWidget(self.version_infos_widget)

        self.date_label = QtWidgets.QLabel('23/06/1995 - 23:15')
        self.date_label.setObjectName('gray_label')
        self.version_infos_layout.addWidget(self.date_label)

        self.user_label = QtWidgets.QLabel('j.smith')
        self.version_infos_layout.addWidget(self.user_label)

        self.spaceItem = QtWidgets.QSpacerItem(100,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.version_infos_layout.addSpacerItem(self.spaceItem)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(6)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.lock_button = QtWidgets.QPushButton()
        self.lock_button.setFixedSize(60,60)
        self.buttons_layout.addWidget(self.lock_button)

        self.launch_button = QtWidgets.QPushButton('Launch')
        self.launch_button.setMinimumHeight(60)
        self.launch_button.setObjectName('blue_button')
        self.buttons_layout.addWidget(self.launch_button)