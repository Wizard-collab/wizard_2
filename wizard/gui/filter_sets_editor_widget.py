# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal
import logging

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server

# Wizard core modules
from wizard.core import user
from wizard.core import project
from wizard.core import repository
from wizard.vars import ressources
from wizard.vars import assets_vars

logger = logging.getLogger(__name__)


class filter_sets_editor_widget(QtWidgets.QWidget):
    def __init__(self, context, parent=None):
        super(filter_sets_editor_widget, self).__init__(parent)
        self.context = context

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Filter sets editor - {self.context}")

        self.build_ui()
        self.connect_functions()

    def showEvent(self, event):
        self.fill_filter_set_content_ui()
        self.refresh_filter_sets()

    def connect_functions(self):
        self.domain_add_button.clicked.connect(self.add_domain)
        self.category_add_button.clicked.connect(self.add_category)
        self.stage_add_button.clicked.connect(self.add_stage)
        self.state_add_button.clicked.connect(self.add_state)
        self.assignment_add_button.clicked.connect(self.add_assignment)
        self.priority_add_button.clicked.connect(self.add_priority)
        self.domain_exclude_button.clicked.connect(self.exclude_domain)
        self.category_exclude_button.clicked.connect(self.exclude_category)
        self.stage_exclude_button.clicked.connect(self.exclude_stage)
        self.state_exclude_button.clicked.connect(self.exclude_state)
        self.assignment_exclude_button.clicked.connect(self.exclude_assignment)
        self.priority_exclude_button.clicked.connect(self.exclude_priority)
        self.save_button.clicked.connect(self.apply)
        self.filter_sets_add_button.clicked.connect(self.add_filter_set)
        self.delete_filter_set_button.clicked.connect(
            self.delete_selected_filter_set)
        self.filter_sets_list.itemSelectionChanged.connect(
            self.refresh_filters)

    def build_ui(self):
        self.setObjectName('main_widget')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(1)
        self.setLayout(self.main_layout)

        self.second_widget = QtWidgets.QWidget()
        self.second_widget.setFixedWidth(300)
        self.second_layout = QtWidgets.QVBoxLayout()
        self.second_widget.setLayout(self.second_layout)
        self.main_layout.addWidget(self.second_widget)

        self.filter_sets_title_label = QtWidgets.QLabel("Your filter sets")
        self.filter_sets_title_label.setObjectName('title_label_2')
        self.second_layout.addWidget(self.filter_sets_title_label)

        self.filter_sets_header = QtWidgets.QHBoxLayout()
        self.filter_sets_header.setContentsMargins(0, 0, 0, 0)
        self.second_layout.addLayout(self.filter_sets_header)
        self.filter_set_name_lineEdit = QtWidgets.QLineEdit()
        self.filter_set_name_lineEdit.setPlaceholderText('New filter set')
        self.filter_sets_header.addWidget(self.filter_set_name_lineEdit)
        self.filter_sets_add_button = QtWidgets.QPushButton()
        self.filter_sets_add_button.setFixedSize(22, 22)
        self.filter_sets_add_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.filter_sets_header.addWidget(self.filter_sets_add_button)
        self.delete_filter_set_button = QtWidgets.QPushButton()
        self.delete_filter_set_button.setFixedSize(22, 22)
        self.delete_filter_set_button.setIcon(
            QtGui.QIcon(ressources._archive_icon_))
        self.filter_sets_header.addWidget(self.delete_filter_set_button)

        self.filter_sets_list = QtWidgets.QListWidget()
        self.second_layout.addWidget(self.filter_sets_list)

        self.third_widget = QtWidgets.QWidget()
        self.third_layout = QtWidgets.QVBoxLayout()
        self.third_widget.setLayout(self.third_layout)
        self.main_layout.addWidget(self.third_widget)

        self.title_label = QtWidgets.QLabel("Choose your filters")
        self.title_label.setObjectName('title_label_2')
        self.third_layout.addWidget(self.title_label)
        self.description_label = QtWidgets.QLabel(
            "Click on + to filter via the selected item. Click on - to exclude the selected item.")
        self.description_label.setObjectName('gray_label')
        self.third_layout.addWidget(self.description_label)

        self.third_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 25, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed))

        self.combobox_layout = QtWidgets.QGridLayout()
        self.combobox_layout.setSpacing(4)
        self.combobox_layout.setContentsMargins(0, 0, 0, 0)
        self.third_layout.addLayout(self.combobox_layout)

        self.domain_label = QtWidgets.QLabel('Domains')
        self.domain_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.domain_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.domain_comboBox = gui_utils.QComboBox()
        self.domain_add_button = QtWidgets.QPushButton()
        self.domain_add_button.setFixedSize(30, 30)
        self.domain_add_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.domain_exclude_button = QtWidgets.QPushButton()
        self.domain_exclude_button.setFixedSize(30, 30)
        self.domain_exclude_button.setIcon(
            QtGui.QIcon(ressources._remove_icon_))
        self.combobox_layout.addWidget(self.domain_label, 0, 0)
        self.combobox_layout.addWidget(self.domain_comboBox, 0, 1)
        self.combobox_layout.addWidget(self.domain_add_button, 0, 2)
        self.combobox_layout.addWidget(self.domain_exclude_button, 0, 3)

        self.category_label = QtWidgets.QLabel('Categories')
        self.category_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.category_comboBox = gui_utils.QComboBox()
        self.category_add_button = QtWidgets.QPushButton()
        self.category_add_button.setFixedSize(30, 30)
        self.category_add_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.category_exclude_button = QtWidgets.QPushButton()
        self.category_exclude_button.setFixedSize(30, 30)
        self.category_exclude_button.setIcon(
            QtGui.QIcon(ressources._remove_icon_))
        self.combobox_layout.addWidget(self.category_label, 1, 0)
        self.combobox_layout.addWidget(self.category_comboBox, 1, 1)
        self.combobox_layout.addWidget(self.category_add_button, 1, 2)
        self.combobox_layout.addWidget(self.category_exclude_button, 1, 3)

        self.stage_label = QtWidgets.QLabel('Stages')
        self.stage_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.stage_comboBox = gui_utils.QComboBox()
        self.stage_add_button = QtWidgets.QPushButton()
        self.stage_add_button.setFixedSize(30, 30)
        self.stage_add_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.stage_exclude_button = QtWidgets.QPushButton()
        self.stage_exclude_button.setFixedSize(30, 30)
        self.stage_exclude_button.setIcon(
            QtGui.QIcon(ressources._remove_icon_))
        self.combobox_layout.addWidget(self.stage_label, 2, 0)
        self.combobox_layout.addWidget(self.stage_comboBox, 2, 1)
        self.combobox_layout.addWidget(self.stage_add_button, 2, 2)
        self.combobox_layout.addWidget(self.stage_exclude_button, 2, 3)

        self.combobox_layout.addItem(QtWidgets.QSpacerItem(
            50, 0, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed), 0, 4)
        self.combobox_layout.addItem(QtWidgets.QSpacerItem(
            50, 0, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed), 1, 4)
        self.combobox_layout.addItem(QtWidgets.QSpacerItem(
            50, 0, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed), 2, 4)
        self.combobox_layout.addItem(QtWidgets.QSpacerItem(
            50, 0, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed), 3, 4)

        self.state_label = QtWidgets.QLabel('State')
        self.state_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.state_comboBox = gui_utils.QComboBox()
        self.state_add_button = QtWidgets.QPushButton()
        self.state_add_button.setFixedSize(30, 30)
        self.state_add_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.state_exclude_button = QtWidgets.QPushButton()
        self.state_exclude_button.setFixedSize(30, 30)
        self.state_exclude_button.setIcon(
            QtGui.QIcon(ressources._remove_icon_))
        self.combobox_layout.addWidget(self.state_label, 0, 5)
        self.combobox_layout.addWidget(self.state_comboBox, 0, 6)
        self.combobox_layout.addWidget(self.state_add_button, 0, 7)
        self.combobox_layout.addWidget(self.state_exclude_button, 0, 8)

        self.assignment_label = QtWidgets.QLabel('Assignment')
        self.assignment_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.assignment_comboBox = gui_utils.QComboBox()
        self.assignment_add_button = QtWidgets.QPushButton()
        self.assignment_add_button.setFixedSize(30, 30)
        self.assignment_add_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.assignment_exclude_button = QtWidgets.QPushButton()
        self.assignment_exclude_button.setFixedSize(30, 30)
        self.assignment_exclude_button.setIcon(
            QtGui.QIcon(ressources._remove_icon_))
        self.combobox_layout.addWidget(self.assignment_label, 1, 5)
        self.combobox_layout.addWidget(self.assignment_comboBox, 1, 6)
        self.combobox_layout.addWidget(self.assignment_add_button, 1, 7)
        self.combobox_layout.addWidget(self.assignment_exclude_button, 1, 8)

        self.priority_label = QtWidgets.QLabel('Priority')
        self.priority_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.priority_comboBox = gui_utils.QComboBox()
        self.priority_add_button = QtWidgets.QPushButton()
        self.priority_add_button.setFixedSize(30, 30)
        self.priority_add_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.priority_exclude_button = QtWidgets.QPushButton()
        self.priority_exclude_button.setFixedSize(30, 30)
        self.priority_exclude_button.setIcon(
            QtGui.QIcon(ressources._remove_icon_))
        self.combobox_layout.addWidget(self.priority_label, 2, 5)
        self.combobox_layout.addWidget(self.priority_comboBox, 2, 6)
        self.combobox_layout.addWidget(self.priority_add_button, 2, 7)
        self.combobox_layout.addWidget(self.priority_exclude_button, 2, 8)

        self.third_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 25, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed))

        self.title_label_2 = QtWidgets.QLabel("Your filters")
        self.title_label_2.setObjectName('title_label_2')
        self.third_layout.addWidget(self.title_label_2)
        self.description_label_2 = QtWidgets.QLabel(
            "Click on x to delete a filter.")
        self.description_label_2.setObjectName('gray_label')
        self.third_layout.addWidget(self.description_label_2)

        self.third_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 25, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed))

        self.filters_list = QtWidgets.QListWidget()
        self.filters_list.setSpacing(10)
        self.filters_list.setContentsMargins(0, 0, 0, 0)
        self.filters_list.setStyleSheet(
            "QListWidget:item{padding:0px;}QListWidget:item:hover{background-color:transparent;}")
        self.filters_list.setObjectName('transparent_widget')
        self.filters_list.setViewMode(QtWidgets.QListView.ViewMode.IconMode)
        self.filters_list.setMovement(QtWidgets.QListView.Movement.Static)
        self.filters_list.setResizeMode(QtWidgets.QListView.ResizeMode.Adjust)
        self.filters_list.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.third_layout.addWidget(self.filters_list)

        self.third_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 25, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed))

        self.save_button = QtWidgets.QPushButton('Save')
        self.save_button.setObjectName('blue_button')
        self.third_layout.addWidget(self.save_button)

    def remove_filter(self, data):
        for i in range(self.filters_list.count()):
            item = self.filters_list.item(i)
            widget = self.filters_list.itemWidget(item)
            item_data = widget.data
            if data == item_data:
                widget.setVisible(False)
                widget.setParent(None)
                widget.deleteLater()
                self.filters_list.takeItem(i)
                del item
                break

    def add_item(self, data):
        for i in range(self.filters_list.count()):
            item_data = self.filters_list.itemWidget(
                self.filters_list.item(i)).data
            if data == item_data:
                return
        item = QtWidgets.QListWidgetItem()
        text = data.split(':')[-1]
        widget = filter_item(data, text)
        widget.remove_filter_signal.connect(self.remove_filter)
        self.filters_list.addItem(item)
        self.filters_list.setItemWidget(item, widget)
        item.setSizeHint(widget.sizeHint())

    def add_domain(self, domain):
        self.add_item(f"domain:{self.domain_comboBox.currentText()}")

    def add_category(self, category):
        self.add_item(f"category:{self.category_comboBox.currentText()}")

    def add_stage(self, stage):
        self.add_item(f"stage:{self.stage_comboBox.currentText()}")

    def add_state(self, data):
        self.add_item(f"data:{self.state_comboBox.currentText()}")

    def add_assignment(self, data):
        self.add_item(f"data:{self.assignment_comboBox.currentText()}")

    def add_priority(self, data):
        self.add_item(f"data:{self.priority_comboBox.currentText()}")

    def exclude_domain(self, domain):
        self.add_item(f"!domain:{self.domain_comboBox.currentText()}")

    def exclude_category(self, category):
        self.add_item(f"!category:{self.category_comboBox.currentText()}")

    def exclude_stage(self, stage):
        self.add_item(f"!stage:{self.stage_comboBox.currentText()}")

    def exclude_state(self, data):
        self.add_item(f"!data:{self.state_comboBox.currentText()}")

    def exclude_assignment(self, data):
        self.add_item(f"!data:{self.assignment_comboBox.currentText()}")

    def exclude_priority(self, data):
        self.add_item(f"!data:{self.priority_comboBox.currentText()}")

    def add_filter_set(self):
        filter_set_name = self.filter_set_name_lineEdit.text()
        if user.user().add_filter_set(self.context, filter_set_name, dict()):
            self.filter_set_name_lineEdit.clear()
            self.refresh_filter_sets()
            gui_server.refresh_ui()

    def delete_selected_filter_set(self):
        selected_items = self.filter_sets_list.selectedItems()
        for selected_item in selected_items:
            user.user().delete_filter_set(self.context, selected_item.text())
        self.refresh_filter_sets()
        gui_server.refresh_ui()

    def refresh_filter_sets(self):
        filter_sets_dic = user.user().get_filters_sets(self.context)
        all_filter_sets = self.get_all_filter_sets()
        user_filter_sets = []
        for filter_set in filter_sets_dic.keys():
            user_filter_sets.append(filter_set)
            if filter_set in all_filter_sets:
                continue
            self.filter_sets_list.addItem(filter_set)
        for filter_set in all_filter_sets:
            if filter_set not in user_filter_sets:
                self.remove_filter_set(filter_set)

    def remove_filter_set(self, text):
        for i in range(self.filter_sets_list.count()):
            item = self.filter_sets_list.item(i)
            if item.text() == text:
                self.filter_sets_list.takeItem(i)
                del item
                break

    def get_all_filter_sets(self):
        filter_sets = []
        for item_index in range(self.filter_sets_list.count()):
            item_text = self.filter_sets_list.item(item_index).text()
            filter_sets.append(item_text)
        return filter_sets

    def fill_filter_set_content_ui(self):
        for domain_row in project.get_domains():
            if domain_row['name'] == 'library':
                continue
            self.domain_comboBox.addItem(domain_row['name'])
            for category_row in project.get_domain_childs(domain_row['id']):
                self.category_comboBox.addItem(category_row['name'])
        for stage in assets_vars._assets_stages_list_ + assets_vars._sequences_stages_list_:
            self.stage_comboBox.addItem(stage)
        for state in assets_vars._asset_states_list_:
            self.state_comboBox.addItem(state)
        for priority in assets_vars._priority_list_:
            self.priority_comboBox.addItem(priority)
        for user_id in project.get_users_ids_list():
            user_name = repository.get_user_data(user_id, 'user_name')
            self.assignment_comboBox.addItem(user_name)

    def get_selected_filter_set(self):
        selected_filter_set = self.filter_sets_list.selectedItems()
        if selected_filter_set is None:
            return
        if selected_filter_set == []:
            return
        selected_filter_set = selected_filter_set[0].text()
        return selected_filter_set

    def refresh_filters(self):
        self.filters_list.clear()
        selected_filter_set = self.get_selected_filter_set()
        if selected_filter_set is None:
            return
        filters_dic = user.user().get_filter_set(self.context, selected_filter_set)
        if filters_dic == dict():
            return
        for key in filters_dic['include'].keys():
            for data in filters_dic['include'][key]:
                self.add_item(f"{key}:{data}")
        for key in filters_dic['exclude'].keys():
            for data in filters_dic['exclude'][key]:
                self.add_item(f"!{key}:{data}")

    def apply(self):
        filter_dic = dict()
        filter_dic['include'] = dict()
        filter_dic['exclude'] = dict()
        for item_index in range(self.filters_list.count()):
            item = self.filters_list.item(item_index)
            widget = self.filters_list.itemWidget(item)
            item_text = widget.data
            key = item_text.split(':')[0]
            data = item_text.split(':')[-1]

            if key.startswith('!'):
                dic = filter_dic['exclude']
                key = key.replace('!', '')
            else:
                dic = filter_dic['include']

            if key not in dic.keys():
                dic[key] = []
            if data not in dic[key]:
                dic[key].append(data)
        selected_filter_set = self.get_selected_filter_set()
        if selected_filter_set is None:
            return
        user.user().edit_filter_set(self.context, selected_filter_set, filter_dic)
        gui_server.refresh_ui()


class filter_item(QtWidgets.QFrame):

    remove_filter_signal = pyqtSignal(str)

    def __init__(self, data, text, parent=None):
        super(filter_item, self).__init__(parent)
        self.data = data
        self.text = text
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.setObjectName('round_frame')
        self.setFixedHeight(30)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(11, 3, 11, 3)
        self.main_layout.setSpacing(20)
        self.setLayout(self.main_layout)

        if self.data.startswith("!"):
            bg_color = '#d16666'
        else:
            bg_color = '#7ca657'

        self.setStyleSheet(
            "#round_frame{background-color:%s;border-radius:14px;}" % bg_color)

        self.label = QtWidgets.QLabel(self.text)
        self.label.setObjectName('bold_label')
        self.label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.main_layout.addWidget(self.label)

        self.delete_filter_button = gui_utils.transparent_button(
            ressources._close_tranparent_icon_, ressources._close_icon_)
        self.delete_filter_button.setFixedSize(12, 12)
        self.delete_filter_button.setIconSize(QtCore.QSize(12, 12))
        self.main_layout.addWidget(self.delete_filter_button)

    def connect_functions(self):
        self.delete_filter_button.clicked.connect(self.remove_filter)

    def remove_filter(self):
        self.remove_filter_signal.emit(self.data)
