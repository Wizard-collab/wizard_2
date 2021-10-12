# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import json
import time
import os

# Wizard modules
from wizard.core import launch
from wizard.core import assets
from wizard.core import project
from wizard.core import tools
from wizard.core import subtasks_library
from wizard.vars import ressources
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server
from wizard.gui import confirm_widget
from wizard.gui import menu_widget
from wizard.gui import create_ticket_widget
from wizard.gui import manual_export_widget
from wizard.gui import drop_files_widget
from wizard.gui import comment_widget

class exports_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(exports_widget, self).__init__(parent)

        self.search_thread = search_thread()

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

        self.variant_id = None
        self.export_ids = dict()
        self.export_versions_ids = dict()
        self.check_existence_thread = check_existence_thread()
        self.build_ui()
        self.connect_functions()
        self.show_info_mode("Select or create a stage\nin the project tree !", ressources._select_stage_info_image_)

    def dragEnterEvent(self, event):
        self.drop_widget.setVisible(1)
        event.accept()

    def dragLeaveEvent(self, event):
        self.drop_widget.setVisible(0)
        event.accept()

    def dropEvent(self, event):
        self.drop_widget.setVisible(0)
        data = event.mimeData()
        urls = data.urls()
        files = []
        for url in urls:
            if url and url.scheme() == 'file':
                path = str(url.path())[1:]
                files.append(path)
        if len(files) != 0:
            self.merge_files(files)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.info_widget = gui_utils.info_widget()
        self.info_widget.setVisible(0)
        self.main_layout.addWidget(self.info_widget)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setAnimated(1)
        self.list_view.setExpandsOnDoubleClick(0)
        self.list_view.setObjectName('tree_as_list_widget')
        self.list_view.setColumnCount(7)
        self.list_view.setIndentation(20)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setHeaderLabels(['Export name', 'Version', 'User', 'Date', 'Comment', 'From', 'Infos'])
        self.list_view.header().resizeSection(0, 250)
        self.list_view.header().resizeSection(3, 150)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_view_scrollBar = self.list_view.verticalScrollBar()
        self.main_layout.addWidget(self.list_view)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_widget.setObjectName('dark_widget')
        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(8,8,8,0)
        self.infos_layout.setSpacing(4)
        self.infos_widget.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_widget)

        self.infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.versions_count_label = QtWidgets.QLabel()
        self.versions_count_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.versions_count_label)

        self.selection_count_label = QtWidgets.QLabel()
        self.infos_layout.addWidget(self.selection_count_label)

        self.refresh_label = QtWidgets.QLabel()
        self.refresh_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.refresh_label)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_widget.setObjectName('dark_widget')
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(8,8,8,8)
        self.buttons_layout.setSpacing(4)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
        
        self.search_bar = gui_utils.search_bar()
        gui_utils.application_tooltip(self.search_bar, "Search for a specific version")
        self.search_bar.setPlaceholderText('"0023", "user:j.smith", "comment:retake eye", "from:houdini"')
        self.buttons_layout.addWidget(self.search_bar)

        self.manual_publish_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.manual_publish_button, "Manually add a file")
        self.manual_publish_button.setFixedSize(35,35)
        self.manual_publish_button.setIconSize(QtCore.QSize(30,30))
        self.manual_publish_button.setIcon(QtGui.QIcon(ressources._tool_manually_publish_))
        self.buttons_layout.addWidget(self.manual_publish_button)

        self.batch_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.batch_button, "Batch export")
        self.batch_button.setFixedSize(35,35)
        self.batch_button.setIconSize(QtCore.QSize(30,30))
        self.batch_button.setIcon(QtGui.QIcon(ressources._tool_batch_publish_))
        self.buttons_layout.addWidget(self.batch_button)

        self.launch_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.launch_button, "Launch related work version")
        self.launch_button.setFixedSize(35,35)
        self.launch_button.setIconSize(QtCore.QSize(30,30))
        self.launch_button.setIcon(QtGui.QIcon(ressources._tool_launch_))
        self.buttons_layout.addWidget(self.launch_button)

        self.folder_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.folder_button, "Open export folder")
        self.folder_button.setFixedSize(35,35)
        self.folder_button.setIconSize(QtCore.QSize(30,30))
        self.folder_button.setIcon(QtGui.QIcon(ressources._tool_folder_))
        self.buttons_layout.addWidget(self.folder_button)

        self.ticket_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.ticket_button, "Open a ticket")
        self.ticket_button.setFixedSize(35,35)
        self.ticket_button.setIconSize(QtCore.QSize(30,30))
        self.ticket_button.setIcon(QtGui.QIcon(ressources._tool_ticket_))
        self.buttons_layout.addWidget(self.ticket_button)

        self.archive_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.archive_button, "Archive selection")
        self.archive_button.setFixedSize(35,35)
        self.archive_button.setIconSize(QtCore.QSize(30,30))
        self.archive_button.setIcon(QtGui.QIcon(ressources._tool_archive_))
        self.buttons_layout.addWidget(self.archive_button)

        self.drop_widget = drop_files_widget.drop_widget(self)
        self.drop_widget.setText('Merge file as new export version')
        self.drop_widget.setVisible(0)

    def check_if_export_is_referenced(self, export_version_row):
        string = None
        if len(project.get_references_by_export_version(export_version_row['id'], 'id'))!=0:
            export_row = project.get_export_data(export_version_row['export_id'])
            variant_row = project.get_variant_data(export_version_row['variant_id'])
            stage_row = project.get_stage_data(export_version_row['stage_id'])
            asset_row = project.get_asset_data(stage_row['asset_id'])
            string = f"{asset_row['name']}/{stage_row['name']}/{variant_row['name']}/{export_row['name']}/{export_version_row['name']}"
        return string

    def archive(self):
        selection = self.list_view.selectedItems()
        if selection is not None:
            if selection != []:

                # Check if exports are referenced somewhere
                referenced_items = []
                for item in selection:
                    if item.type == 'export_version':
                        string = self.check_if_export_is_referenced(item.export_version_row)
                        if string is not None and string not in referenced_items:
                            referenced_items.append(string)
                    elif item.type == 'export':
                        childs_ids = project.get_export_versions(item.export_row['id'], 'id')
                        for export_version_id in childs_ids:
                            export_version_row = project.get_export_version_data(export_version_id)
                            string = self.check_if_export_is_referenced(export_version_row)
                            if string is not None and string not in referenced_items:
                                referenced_items.append(string)

                self.confirm_widget = confirm_widget.confirm_widget('Do you want to continue ?', parent=self)
                if len(referenced_items)!=0:
                    message = 'The following export versions are referenced in some scenes,\ndo you REALLY want to continue ?\n\n-'
                    message += ('\n-').join(referenced_items)
                    self.confirm_widget.set_important_message(message)
                    self.confirm_widget.set_security_sentence('I understand the risks')

                if self.confirm_widget.exec_() == QtWidgets.QDialog.Accepted:

                    export_ids = []
                    export_version_ids = []

                    for item in selection:
                        if item.type == 'export_version':
                            export_version_ids.append(item.export_version_row['id'])
                        elif item.type == 'export':
                            export_ids.append(item.export_row['id'])

                    if len(export_ids) > 0:
                        subtasks_library.archive_exports(export_ids)
                    if len(export_version_ids) > 0:
                        subtasks_library.archive_export_versions(export_version_ids)


    def open_folder(self):
        if self.variant_id is not None:
            folder = assets.get_variant_export_path(self.variant_id)
            selection = self.list_view.selectedItems()
            if selection is not None:
                if len(selection)==1:
                    if selection[0].type == 'export_version':
                        files = json.loads(selection[0].export_version_row['files'])
                        if files != [] and files != None:
                            file = files[0]
                            folder = os.path.dirname(file)
                    elif selection[0].type == 'export':
                        export_id = selection[0].export_row['id']
                        folder = assets.get_export_path(export_id)
            if os.path.isdir(folder):
                os.startfile(folder)
            else:
                logger.warning(f"{folder} not found")

    def open_ticket(self):
        selection = self.list_view.selectedItems()
        if selection is not None:
            if len(selection) == 1:
                export_version_id = selection[0].export_version_row['id']
                self.create_ticket_widget = create_ticket_widget.create_ticket_widget(export_version_id)
                self.create_ticket_widget.show()
            else:
                logger.warning('Please select one version to open a ticket')

    def update_search(self):
        search_data = self.search_bar.text()
        if search_data != '':
            self.hide_all()
            search_column = 'name'
            if ':' in search_data:
                if search_data.split(':')[0] == 'comment':
                    search_column = 'comment'
                    search_data = search_data.split(':')[-1]
                elif search_data.split(':')[0] == 'user':
                    search_column = 'creation_user'
                    search_data = search_data.split(':')[-1]
                elif search_data.split(':')[0] == 'from':
                    search_column = 'software'
                    search_data = search_data.split(':')[-1]
            self.search_thread.update_search(self.variant_id, search_data, search_column)
        else:
            self.show_all()

    def hide_all(self):
        for export_id in self.export_ids.keys():
            self.export_ids[export_id].setHidden(1)
        for export_version_id in self.export_versions_ids.keys():
            self.export_versions_ids[export_version_id].setHidden(1)

    def show_all(self):
        for export_id in self.export_ids.keys():
            self.export_ids[export_id].setHidden(0)
        for export_version_id in self.export_versions_ids.keys():
            self.export_versions_ids[export_version_id].setHidden(0)

    def add_search_version(self, export_version_id):
        if export_version_id in self.export_versions_ids.keys():
            export_id = self.export_versions_ids[export_version_id].export_version_row['export_id']
            if export_id in self.export_ids.keys():
                self.export_ids[export_id].setHidden(0)
            self.export_versions_ids[export_version_id].setHidden(0)

    def connect_functions(self):
        self.list_view_scrollBar.rangeChanged.connect(lambda: self.list_view_scrollBar.setValue(self.list_view_scrollBar.maximum()))
        self.list_view.customContextMenuRequested.connect(self.context_menu_requested)
        self.list_view.itemDoubleClicked.connect(self.open_folder)
        self.list_view.itemSelectionChanged.connect(self.refresh_infos)

        self.check_existence_thread.missing_file_signal.connect(self.missing_file)
        self.check_existence_thread.not_missing_file_signal.connect(self.not_missing_file)

        self.search_bar.textChanged.connect(self.update_search)
        self.search_thread.id_signal.connect(self.add_search_version)

        self.archive_button.clicked.connect(self.archive)
        self.manual_publish_button.clicked.connect(lambda:self.merge_files())
        self.folder_button.clicked.connect(self.open_folder)
        self.launch_button.clicked.connect(self.launch_work_version)
        self.ticket_button.clicked.connect(self.open_ticket)

    def refresh_infos(self):
        self.versions_count_label.setText(f"{len(self.export_ids)} exports / {len(self.export_versions_ids)} export versions -")
        selection = self.list_view.selectedItems()
        if selection is not None:
            number = len(selection)
        else:
            number = 0
        self.selection_count_label.setText(f"{number} selected")

    def refresh(self):
        start_time = time.time()
        if self.isVisible():
            if self.variant_id is not None:
                self.setAcceptDrops(True)
                stage_id = project.get_variant_data(self.variant_id, 'stage_id')
                stage_name = project.get_stage_data(stage_id, 'name')
                stage_icon = QtGui.QIcon(self.icons_dic[stage_name])
                exports_rows = project.get_variant_export_childs(self.variant_id)
                project_export_id = []
                if exports_rows is not None:
                    if exports_rows != []:
                        self.hide_info_mode()
                        for export_row in exports_rows:
                            project_export_id.append(export_row['id'])
                            if export_row['id'] not in self.export_ids.keys():
                                export_item = custom_export_tree_item(export_row, stage_icon, self.list_view.invisibleRootItem())
                                export_item.setExpanded(1)
                                self.export_ids[export_row['id']] = export_item
                    else:
                        self.show_info_mode("No exports, create exports\nwithin softwares !", ressources._empty_info_image_)

                    project_export_versions_id = []
                    export_versions_rows = project.get_export_versions_by_variant(self.variant_id)
                    if export_versions_rows is not None:
                        if export_versions_rows != []:
                            for export_version_row in export_versions_rows:
                                project_export_versions_id.append(export_version_row['id'])
                                if export_version_row['id'] not in self.export_versions_ids.keys():
                                    if export_version_row['export_id'] in self.export_ids.keys():
                                        export_version_item = custom_export_version_tree_item(export_version_row, self.export_ids[export_version_row['export_id']])
                                    self.export_versions_ids[export_version_row['id']] = export_version_item
                                else:
                                    self.export_versions_ids[export_version_row['id']].refresh(export_version_row)
                            self.check_existence_thread.update_versions_rows(export_versions_rows)


                    export_list_ids = list(self.export_ids.keys())
                    for export_id in export_list_ids:
                        if export_id not in project_export_id:
                            self.remove_export(export_id)
                    export_version_list_ids = list(self.export_versions_ids.keys())
                    for export_version_id in export_version_list_ids:
                        if export_version_id not in project_export_versions_id:
                            self.remove_export_version(export_version_id)
                else:
                    self.show_info_mode("No exports, create exports\nwithin softwares !", ressources._empty_info_image_)

            else:
                self.show_info_mode("Select or create a stage\nin the project tree !", ressources._select_stage_info_image_)
                self.setAcceptDrops(False)
        self.refresh_infos()
        self.update_refresh_time(start_time)

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.time()-start_time), 3))
        self.refresh_label.setText(f"- refresh : {refresh_time}s")

    def missing_file(self, tuple_signal):
        export_version_id = tuple_signal[0]
        number = tuple_signal[-1]
        if export_version_id in self.export_versions_ids.keys():
            self.export_versions_ids[export_version_id].set_missing(number)

    def not_missing_file(self, tuple_signal):
        export_version_id = tuple_signal[0]
        number = tuple_signal[-1]
        if export_version_id in self.export_versions_ids.keys():
            self.export_versions_ids[export_version_id].set_not_missing(number)

    def remove_export_version(self, export_version_id):
        if export_version_id in self.export_versions_ids.keys():
            item = self.export_versions_ids[export_version_id]
            try:
                item.parent().removeChild(item)
            except RuntimeError:
                pass
            del self.export_versions_ids[export_version_id]

    def remove_export(self, export_id):
        if export_id in self.export_ids.keys():
            item = self.export_ids[export_id]
            self.list_view.invisibleRootItem().removeChild(item)
            del self.export_ids[export_id]

    def context_menu_requested(self):
        selection = self.list_view.selectedItems()
        self.menu_widget = menu_widget.menu_widget(self)
        folder_action = self.menu_widget.add_action(f'Open folder', ressources._tool_folder_)
        batch_action = self.menu_widget.add_action(f'Batch export', ressources._tool_batch_publish_)
        manual_action = self.menu_widget.add_action(f'Manually add a file', ressources._tool_manually_publish_)
        archive_action = None
        ticket_action = None
        if len(selection)>=1:
            archive_action = self.menu_widget.add_action(f'Archive version(s)', ressources._tool_archive_)
            comment_action = self.menu_widget.add_action('Modify comment', ressources._tool_comment_)
        launch_action = None
        if len(selection)==1:
            launch_action = self.menu_widget.add_action(f'Launch related work version', ressources._tool_launch_)
            ticket_action = self.menu_widget.add_action(f'Open a ticket', ressources._tool_ticket_)
        if self.menu_widget.exec_() == QtWidgets.QDialog.Accepted:
            if self.menu_widget.function_name is not None:
                if self.menu_widget.function_name == folder_action:
                    self.open_folder()
                elif self.menu_widget.function_name == archive_action:
                    self.archive()
                elif self.menu_widget.function_name == launch_action:
                    self.launch_work_version()
                elif self.menu_widget.function_name == ticket_action:
                    self.open_ticket()
                elif self.menu_widget.function_name == manual_action:
                    self.merge_files()
                elif self.menu_widget.function_name == comment_action:
                    self.modify_comment()

    def modify_comment(self):
        selection = self.list_view.selectedItems()
        if selection is not None:
            if len(selection) > 0:
                self.comment_widget = comment_widget.comment_widget()
                if self.comment_widget.exec_() == QtWidgets.QDialog.Accepted:
                    comment = self.comment_widget.comment
                    for item in selection:
                        project.modify_export_version_comment(item.export_version_row['id'], comment)
                    gui_server.refresh_ui()

    def launch_work_version(self):
        selection = self.list_view.selectedItems()
        if selection is not None:
            if len(selection) == 1:
                item = selection[0]
                if item.type == 'export_version':
                    work_version_id = item.export_version_row['work_version_id']
                    if work_version_id is not None:
                        launch.launch_work_version(work_version_id)

    def merge_files(self, files=[]):
        if self.variant_id is not None:
            self.manual_export_widget = manual_export_widget.manual_export_widget()
            self.manual_export_widget.add_files(files)

            variant_row = project.get_variant_data(self.variant_id)
            stage_row = project.get_stage_data(variant_row['stage_id'])
            asset_row = project.get_asset_data(stage_row['asset_id'])

            self.manual_export_widget.set_export_name(f"{asset_row['name']}_{stage_row['name']}_{variant_row['name']}")

            if self.manual_export_widget.exec_() == QtWidgets.QDialog.Accepted:
                files = self.manual_export_widget.files
                export_name = self.manual_export_widget.export_name
                comment = self.manual_export_widget.comment
                if assets.merge_file_as_export_version(export_name, files, self.variant_id, comment):
                    gui_server.refresh_ui()

    def focus_export_version(self, export_version_id):
        if export_version_id in self.export_versions_ids.keys():
            item = self.export_versions_ids[export_version_id]
            item.parent().setExpanded(1)
            self.list_view.scrollToItem(item)
            self.list_view.setCurrentItem(item)

    def show_info_mode(self, text, image):
        self.list_view.setVisible(0)
        self.info_widget.setVisible(1)
        self.info_widget.setText(text)
        self.info_widget.setImage(image)

    def hide_info_mode(self):
        self.info_widget.setVisible(0)
        self.list_view.setVisible(1)

    def change_variant(self, variant_id):
        self.check_existence_thread.running = False
        self.export_ids = dict()
        self.export_versions_ids = dict()
        self.list_view.clear()
        self.variant_id = variant_id
        self.refresh()
        
class custom_export_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, export_row, stage_icon, parent=None):
        super(custom_export_tree_item, self).__init__(parent)
        self.export_row = export_row
        self.stage_icon = stage_icon
        self.type = 'export'
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
        self.type = 'export_version'
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
        if self.export_version_row['software'] is not None:
            self.setIcon(5, QtGui.QIcon(ressources._sofwares_icons_dic_[self.export_version_row['software']]))
        else:
            self.setIcon(5, QtGui.QIcon(ressources._manual_export_))
        self.setText(6, 'ok')

    def refresh(self, export_version_row):
        self.export_version_row = export_version_row
        self.fill_ui()

    def set_missing(self, number):
        self.setText(6, f'missing {number} files')
        self.setForeground(6, QtGui.QBrush(QtGui.QColor('#f79360')))

    def set_not_missing(self, number):
        self.setText(6, f'{number} files')
        self.setForeground(6, QtGui.QBrush(QtGui.QColor('#9ce87b')))

class check_existence_thread(QtCore.QThread):

    missing_file_signal = pyqtSignal(tuple)
    not_missing_file_signal = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super(check_existence_thread, self).__init__(parent)
        self.export_versions_rows = None
        self.running = True

    def run(self):
        if self.export_versions_rows is not None:
            for export_version_row in self.export_versions_rows:
                files_list = json.loads(export_version_row['files'])
                missing_files = 0
                for file in files_list:
                    if not os.path.isfile(file):
                        missing_files += 1
                    if not self.running:
                        break

                if missing_files:
                    self.missing_file_signal.emit((export_version_row['id'], missing_files))
                else:
                    self.not_missing_file_signal.emit((export_version_row['id'], len(files_list)))
                if not self.running:
                    break

    def update_versions_rows(self, export_versions_rows):
        self.running = False
        self.export_versions_rows = export_versions_rows
        self.running = True
        self.start()

class search_thread(QtCore.QThread):

    id_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = True

    def update_search(self, variant_id, search_data, search_column):
        self.running = False
        self.variant_id = variant_id
        self.search_data = search_data
        self.search_column = search_column
        self.running = True
        self.start()

    def run(self):
        versions_ids = project.search_export_version(self.search_data, 
                                                self.variant_id, 
                                                column_to_search=self.search_column,
                                                column='id')
        for version_id in versions_ids:
            if not self.running:
                break
            self.id_signal.emit(version_id)
