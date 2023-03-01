# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import logging

# Wizard modules
from wizard.core import assets
from wizard.core import project
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server

logger = logging.getLogger(__name__)

class destination_manager(QtWidgets.QWidget):
    def __init__(self, export_id, parent=None):
        super(destination_manager, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Destination manager")

        self.references_ids = dict()
        self.export_id = export_id
        self.fill_thread = fill_thread(self)
        self.build_ui()
        self.connect_functions()
        self.refresh()

    def build_ui(self):
        self.setMinimumSize(QtCore.QSize(900,500))
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.header = QtWidgets.QWidget()
        self.header.setObjectName('transparent_widget')
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setSpacing(6)
        self.header.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header)

        self.header_label = QtWidgets.QLabel()
        self.header_layout.addWidget(self.header_label)

        self.content_widget = QtWidgets.QWidget()
        self.content_widget.setObjectName('dark_widget')
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_layout.setSpacing(6)
        self.content_widget.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_widget)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_view.setObjectName('tree_as_list_widget')
        self.list_view.setColumnCount(4)
        self.list_view.setHeaderLabels(['Destination', 'Reference namespace', 'Referenced version', 'Auto update'])
        self.list_view.header().resizeSection(0, 450)
        self.list_view.header().resizeSection(1, 200)
        self.list_view.setIndentation(0)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.content_layout.addWidget(self.list_view)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_widget.setObjectName('transparent_widget')
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(6)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.content_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.remove_selection_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.remove_selection_button, "Remove selected references")
        self.remove_selection_button.setFixedSize(35,35)
        self.remove_selection_button.setIconSize(QtCore.QSize(25,25))
        self.remove_selection_button.setIcon(QtGui.QIcon(ressources._tool_archive_))
        self.buttons_layout.addWidget(self.remove_selection_button)

        self.update_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.update_button, "Update selected references")
        self.update_button.setFixedSize(35,35)
        self.update_button.setIconSize(QtCore.QSize(25,25))
        self.update_button.setIcon(QtGui.QIcon(ressources._tool_update_))
        self.buttons_layout.addWidget(self.update_button)     

    def connect_functions(self):
        self.fill_thread.data_signal.connect(self.update_reference)
        self.remove_selection_button.clicked.connect(self.remove_selection)
        self.update_button.clicked.connect(self.update_selection)

    def refresh(self):
        self.header_label.setText(assets.instance_to_string(('export', self.export_id)))
        reference_rows = project.get_references_by_export(self.export_id)
        project_references_id = []
        for reference_row in reference_rows:
            project_references_id.append(reference_row['id'])
            if reference_row['id'] not in self.references_ids.keys():
                target_item = custom_target_item(reference_row, self.list_view.invisibleRootItem())
                self.references_ids[reference_row['id']] = target_item
        references_list_ids = list(self.references_ids.keys())
        for reference_id in references_list_ids:
            if reference_id not in project_references_id:
                self.remove_reference_item(reference_id)

        self.fill_thread.update_reference_rows(self.export_id, reference_rows)

    def remove_reference_item(self, reference_id):
        if reference_id in self.references_ids.keys():
            item = self.references_ids[reference_id]
            self.list_view.invisibleRootItem().removeChild(item)
            del self.references_ids[reference_id]

    def remove_selection(self):
        selected_items = self.list_view.selectedItems()
        for selected_item in selected_items:
            project.remove_reference(selected_item.reference_row['id'])
        gui_server.refresh_team_ui()

    def update_selection(self):
        selected_items = self.list_view.selectedItems()
        for selected_item in selected_items:
            reference_id = selected_item.reference_row['id']
            assets.set_reference_last_version(reference_id)
        gui_server.refresh_team_ui()

    def update_reference(self, data_tuple):
        if data_tuple[0]['id'] in self.references_ids.keys():
            self.references_ids[data_tuple[0]['id']].update(data_tuple)

class custom_target_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, reference_row, parent=None):
        super(custom_target_item, self).__init__(parent)
        self.reference_row = reference_row
        self.fill_ui()
        self.connect_functions()

    def connect_functions(self):
        self.version_widget.button_clicked.connect(self.version_modification_requested)
        self.auto_update_checkbox.stateChanged.connect(self.modify_auto_update)

    def fill_ui(self):
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(0, bold_font)
        self.version_widget = editable_data_widget(bold=True)
        self.treeWidget().setItemWidget(self, 2, self.version_widget)
        self.auto_update_checkbox = QtWidgets.QCheckBox()
        self.auto_update_checkbox.setStyleSheet('background-color:transparent;')
        self.treeWidget().setItemWidget(self, 3, self.auto_update_checkbox)

    def update(self, data_tuple):
        self.reference_row = data_tuple[0]
        self.setText(0, data_tuple[1])
        self.setText(1, self.reference_row['namespace'])
        self.version_widget.setText(data_tuple[2])
        if data_tuple[3]:
            self.version_widget.setColor('#9ce87b')
        else:
            self.version_widget.setColor('#f79360')
        self.set_auto_update(self.reference_row['auto_update'])

    def set_auto_update(self, auto_update):
        self.apply_auto_update_change = False
        self.auto_update_checkbox.setChecked(auto_update)
        if auto_update:
            self.version_widget.hide_button()
        else:
            self.version_widget.unhide_button()
        self.apply_auto_update_change = True

    def modify_auto_update(self, auto_update):
        if self.apply_auto_update_change:
            project.modify_reference_auto_update(self.reference_row['id'], auto_update)
            gui_server.refresh_team_ui()

    def version_modification_requested(self, point):
        versions_list = project.get_export_versions(self.reference_row['export_id'])
        if versions_list is not None and versions_list != []:
            menu = gui_utils.QMenu()
            for version in versions_list:
                if len(version['comment']) > 20:
                    comment = version['comment'][-20:] + '...'
                else:
                    comment = version['comment']
                action = menu.addAction(f"{version['name']} - {comment}")
                action.id = version['id']
            action = menu.exec_(QtGui.QCursor().pos())
            if action is not None:
                self.modify_version(action.id)

    def modify_version(self, export_version_id):
        project.update_reference(self.reference_row['id'], export_version_id)
        gui_server.refresh_team_ui()

class fill_thread(QtCore.QThread):

    data_signal = pyqtSignal(tuple)

    def __init__(self, parent = None):
        super(fill_thread, self).__init__(parent)
        self.export_id = None
        self.references_rows = []
        self.running = False

    def update_reference_rows(self, export_id, reference_rows):
        self.references_rows = reference_rows
        self.export_id = export_id
        self.running = True
        self.start()

    def run(self):
        if self.running:
            default_export_version_id = project.get_default_export_version(self.export_id, 'id')
            for reference_row in self.references_rows:
                work_env_string = assets.instance_to_string(('work_env', reference_row['work_env_id']))
                export_version_row = project.get_export_version_data(reference_row['export_version_id'])
                if default_export_version_id != export_version_row['id']:
                    up_to_date = 0
                else:
                    up_to_date = 1

                self.data_signal.emit((reference_row, work_env_string, export_version_row['name'], up_to_date))

class editable_data_widget(QtWidgets.QFrame):

    button_clicked = pyqtSignal(int)

    def __init__(self, parent=None, bold=False):
        super(editable_data_widget, self).__init__(parent)
        self.bold=bold
        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.main_button.clicked.connect(self.button_clicked.emit)

    def build_ui(self):
        self.setObjectName('reference_edit_widget')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(8,4,4,4)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.label)
        if self.bold:
            bold_font=QtGui.QFont()
            bold_font.setBold(True)
            self.label.setFont(bold_font)

        self.main_button = QtWidgets.QPushButton()
        self.main_button.setObjectName('dropdown_button')
        self.main_button.setFixedSize(QtCore.QSize(14,14))
        self.main_layout.addWidget(self.main_button)

    def hide_button(self):
        self.main_button.setVisible(0)

    def unhide_button(self):
        self.main_button.setVisible(1)

    def setText(self, text):
        self.label.setText(text)

    def setColor(self, color):
        self.setStyleSheet(f'color:{color}')