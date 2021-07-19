# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import json
import os

# Wizard modules
from wizard.core import project
from wizard.core import tools
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils

class exports_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(exports_widget, self).__init__(parent)

        self.icons_dic = dict()
        self.icons_dic['modeling'] = QtGui.QIcon(ressources._modeling_icon_small_)
        self.icons_dic['rigging'] = QtGui.QIcon(ressources._rigging_icon_small_)
        self.icons_dic['grooming'] = QtGui.QIcon(ressources._grooming_icon_small_)
        self.icons_dic['texturing'] = QtGui.QIcon(ressources._texturing_icon_small_)
        self.icons_dic['shading'] = QtGui.QIcon(ressources._shading_icon_small_)
        self.icons_dic['layout'] = QtGui.QIcon(ressources._layout_icon_small_)
        self.icons_dic['animation'] = QtGui.QIcon(ressources._animation_icon_small_)
        self.icons_dic['cfx'] = QtGui.QIcon(ressources._cfx_icon_small_)
        self.icons_dic['fx'] = QtGui.QIcon(ressources._fx_icon_small_)
        self.icons_dic['lighting'] = QtGui.QIcon(ressources._lighting_icon_small_)
        self.icons_dic['camera'] = QtGui.QIcon(ressources._camera_icon_small_)
        self.icons_dic['compositing'] = QtGui.QIcon(ressources._compositing_icon_small_)

        self.export_ids = dict()
        self.export_versions_ids = dict()
        self.check_existence_thread = check_existence_thread()
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.info_widget = gui_utils.info_widget()
        self.info_widget.setVisible(0)
        self.main_layout.addWidget(self.info_widget)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setObjectName('tree_as_list_widget')
        self.list_view.setColumnCount(6)
        self.list_view.setIndentation(20)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setHeaderLabels(['Export name', 'Version', 'User', 'Date', 'Comment', 'Infos'])
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.list_view_scrollBar = self.list_view.verticalScrollBar()
        self.main_layout.addWidget(self.list_view)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_widget.setObjectName('dark_widget')
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(8,8,8,0)
        self.buttons_layout.setSpacing(4)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
        
        self.search_bar = gui_utils.search_bar()
        gui_utils.application_tooltip(self.search_bar, "Search for a specific version")
        self.search_bar.setPlaceholderText('"0023", "user:j.smith", "comment:retake eye"')
        self.buttons_layout.addWidget(self.search_bar)

        self.manual_publish_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.manual_publish_button, "Publish a file manually")
        self.manual_publish_button.setFixedSize(35,35)
        self.manual_publish_button.setIconSize(QtCore.QSize(30,30))
        self.manual_publish_button.setIcon(QtGui.QIcon(ressources._tool_manually_publish_))
        self.buttons_layout.addWidget(self.manual_publish_button)

        self.batch_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.batch_button, "Batch publish")
        self.batch_button.setFixedSize(35,35)
        self.batch_button.setIconSize(QtCore.QSize(30,30))
        self.batch_button.setIcon(QtGui.QIcon(ressources._tool_batch_publish_))
        self.buttons_layout.addWidget(self.batch_button)

        self.folder_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.folder_button, "Open export folder")
        self.folder_button.setFixedSize(35,35)
        self.folder_button.setIconSize(QtCore.QSize(30,30))
        self.folder_button.setIcon(QtGui.QIcon(ressources._tool_folder_))
        self.buttons_layout.addWidget(self.folder_button)

        self.archive_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.archive_button, "Archive selection")
        self.archive_button.setFixedSize(35,35)
        self.archive_button.setIconSize(QtCore.QSize(30,30))
        self.archive_button.setIcon(QtGui.QIcon(ressources._tool_archive_))
        self.buttons_layout.addWidget(self.archive_button)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_widget.setObjectName('dark_widget')
        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(8,8,8,8)
        self.infos_layout.setSpacing(4)
        self.infos_widget.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_widget)

        self.infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.versions_count_label = QtWidgets.QLabel()
        self.versions_count_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.versions_count_label)

        self.selection_count_label = QtWidgets.QLabel()
        self.infos_layout.addWidget(self.selection_count_label)

    def connect_functions(self):
        self.list_view_scrollBar.rangeChanged.connect(lambda: self.list_view_scrollBar.setValue(self.list_view_scrollBar.maximum()))

        self.check_existence_thread.missing_file_signal.connect(self.missing_file)
        self.check_existence_thread.not_missing_file_signal.connect(self.not_missing_file)

    def refresh(self):
        if self.isVisible():
            print(self.variant_id)
            if self.variant_id is not None:
                self.show_info_mode("No exports, create exports\nwithin softwares !", ressources._empty_info_image_)
                stage_id = project.get_variant_data(self.variant_id, 'stage_id')
                stage_name = project.get_stage_data(stage_id, 'name')
                stage_icon = QtGui.QIcon(self.icons_dic[stage_name])
                exports_rows = project.get_variant_export_childs(self.variant_id)
                if exports_rows is not None:
                    if exports_rows != []:
                        self.hide_info_mode()
                        for export_row in exports_rows:
                            if export_row['id'] not in self.export_ids.keys():
                                export_item = custom_export_tree_item(export_row, stage_icon, self.list_view.invisibleRootItem())
                                export_item.setExpanded(1)
                                self.export_ids[export_row['id']] = export_item
                    export_versions_rows = project.get_export_versions_by_variant(self.variant_id)
                    if export_versions_rows is not None:
                        if export_versions_rows != []:
                            for export_version_row in export_versions_rows:
                                if export_version_row['id'] not in self.export_versions_ids.keys():
                                    if export_version_row['export_id'] in self.export_ids.keys():
                                        export_version_item = custom_export_version_tree_item(export_version_row, self.export_ids[export_version_row['export_id']])
                                    self.export_versions_ids[export_version_row['id']] = export_version_item
                            self.check_existence_thread.update_versions_rows(export_versions_rows)
            else:
                self.show_info_mode("Select or create a stage\nin the project tree !", ressources._select_stage_info_image_)

    def missing_file(self, export_version_id):
        if export_version_id in self.export_versions_ids.keys():
            self.export_versions_ids[export_version_id].set_missing()

    def not_missing_file(self, export_version_id):
        if export_version_id in self.export_versions_ids.keys():
            self.export_versions_ids[export_version_id].set_not_missing()

    def show_info_mode(self, text, image):
        self.list_view.setVisible(0)
        self.info_widget.setVisible(1)
        self.info_widget.setText(text)
        self.info_widget.setImage(image)

    def hide_info_mode(self):
        self.list_view.setVisible(1)
        self.info_widget.setVisible(0)

    def change_variant(self, variant_id):
        self.check_existence_thread.running = False
        self.export_ids = dict()
        self.export_versions_ids = dict()
        self.list_view.clear()
        self.variant_id = variant_id
        self.refresh()
        self.info_widget.pop()
        
class custom_export_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, export_row, stage_icon, parent=None):
        super(custom_export_tree_item, self).__init__(parent)
        self.export_row = export_row
        self.stage_icon = stage_icon
        self.fill_ui()

    def fill_ui(self):
        self.setText(0, self.export_row['name'])
        self.setIcon(0, self.stage_icon)
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(0, bold_font)
        self.setText(2, self.export_row['creation_user'])
        day, hour = tools.convert_time(self.export_row['creation_time'])
        self.setText(3, f"{day} - {hour}")
        self.setForeground(3, QtGui.QBrush(QtGui.QColor('gray')))

class custom_export_version_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, export_version_row, parent=None):
        super(custom_export_version_tree_item, self).__init__(parent)
        self.export_version_row = export_version_row
        self.fill_ui()

    def fill_ui(self):
        self.setText(1, self.export_version_row['name'])
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(1, bold_font)
        self.setText(2, self.export_version_row['creation_user'])
        day, hour = tools.convert_time(self.export_version_row['creation_time'])
        self.setText(3, f"{day} - {hour}")
        self.setForeground(3, QtGui.QBrush(QtGui.QColor('gray')))
        self.setText(4, self.export_version_row['comment'])
        self.setText(5, 'ok')

    def set_missing(self):
        self.setText(5, 'missing files')
        self.setForeground(5, QtGui.QBrush(QtGui.QColor('#f79360')))

    def set_not_missing(self):
        self.setText(5, 'ok')
        self.setForeground(5, QtGui.QBrush(QtGui.QColor('white')))

class check_existence_thread(QtCore.QThread):

    missing_file_signal = pyqtSignal(int)
    not_missing_file_signal = pyqtSignal(int)

    def __init__(self, parent=None):
        super(check_existence_thread, self).__init__(parent)
        self.export_versions_rows = None
        self.running = True

    def run(self):
        if self.export_versions_rows is not None:
            for export_version_row in self.export_versions_rows:
                files_list = json.loads(export_version_row['files'])
                missing_file = 0
                for file in files_list:
                    if not os.path.isfile(file):
                        missing_file = 1
                        break
                    if not self.running:
                        break

                if missing_file:
                    self.missing_file_signal.emit(export_version_row['id'])
                else:
                    self.not_missing_file_signal.emit(export_version_row['id'])
                if not self.running:
                    break

    def update_versions_rows(self, export_versions_rows):
        self.running = False
        self.export_versions_rows = export_versions_rows
        self.running = True
        self.start()