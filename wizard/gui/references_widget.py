# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal

# Wizard gui modules
from wizard.gui import search_reference_widget
from wizard.gui import gui_utils

# Wizard modules
from wizard.core import assets
from wizard.core import project
from wizard.vars import ressources

class references_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(references_widget, self).__init__(parent)
        self.search_reference_widget = search_reference_widget.search_reference_widget()
        self.reference_infos_thread = reference_infos_thread()
        self.work_env_id = None
        self.reference_ids = dict()
        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.search_sc = QtWidgets.QShortcut(QtGui.QKeySequence('Tab'), self)
        self.search_sc.activated.connect(self.search_reference)
        self.reference_infos_thread.reference_infos_signal.connect(self.update_item_infos)

    def update_item_infos(self, infos_list):
        reference_id = infos_list[0]
        if reference_id in self.reference_ids.keys():
            self.reference_ids[reference_id].update_item_infos(infos_list)

    def search_reference(self):
        self.search_reference_widget = search_reference_widget.search_reference_widget()
        self.search_reference_widget.variant_ids_signal.connect(self.create_references_from_variant_ids)
        self.search_reference_widget.show()
        
        if self.work_env_id is not None:
            variant_row = project.get_variant_data(project.get_work_env_data(self.work_env_id, 'variant_id'))
            stage_row = project.get_stage_data(variant_row['stage_id'])
            asset_row = project.get_asset_data(stage_row['asset_id'])
            category_row = project.get_category_data(asset_row['category_id'])
            self.search_reference_widget.search_asset(f"{category_row['name']}:{asset_row['name']}")

    def create_references_from_variant_ids(self, variant_ids):
        if self.work_env_id is not None:
            for variant_id in variant_ids:
                assets.create_references_from_variant_id(self.work_env_id, variant_id)

    def change_work_env(self, work_env_id):
        self.reference_ids = dict()
        self.list_view.clear()
        self.work_env_id = work_env_id
        self.refresh()

    def refresh(self):
        if self.isVisible():
            if self.work_env_id is not None:
                reference_rows = project.get_references(self.work_env_id)
                if reference_rows is not None:
                    for reference_row in reference_rows:
                        if reference_row['id'] not in self.reference_ids.keys():
                            reference_item = custom_reference_tree_item(reference_row, self.list_view.invisibleRootItem())
                            self.reference_ids[reference_row['id']] = reference_item
                    self.reference_infos_thread.update_references_rows(reference_rows)

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
        self.list_view.setColumnCount(5)
        self.list_view.setIndentation(20)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setHeaderLabels(['Stage', 'Namespace', 'Variant', 'Exported asset', 'Export version'])
        self.list_view.header().resizeSection(3, 150)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
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

class custom_reference_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, reference_row, parent=None):
        super(custom_reference_tree_item, self).__init__(parent)
        self.reference_row = reference_row
        self.fill_ui()

    def fill_ui(self):
        self.setText(1, self.reference_row['namespace'])
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(1, bold_font)
        self.setFont(4, bold_font)
        self.setIcon(0, QtGui.QIcon(ressources._stage_icons_dic_[self.reference_row['stage']]))

    def update_item_infos(self, infos_list):
        self.setText(2, infos_list[1])
        self.setText(3, infos_list[2])
        self.setText(4, infos_list[3])
        if infos_list[4]:
            self.setForeground(4, QtGui.QBrush(QtGui.QColor('#9ce87b')))
        else:
            self.setForeground(4, QtGui.QBrush(QtGui.QColor('#f79360')))

class reference_infos_thread(QtCore.QThread):

    reference_infos_signal = pyqtSignal(list)

    def __init__(self, parent=None):
        super(reference_infos_thread, self).__init__(parent)
        self.reference_rows = None
        self.running = True

    def run(self):
        if self.reference_rows is not None:
            for reference_row in self.reference_rows:
                export_version_row = project.get_export_version_data(reference_row['export_version_id'])
                export_row = project.get_export_data(export_version_row['export_id'])
                variant_row = project.get_variant_data(export_row['variant_id'])
                last_export_version_id = project.get_last_export_version(export_row['id'], 'id')

                if last_export_version_id[0] != reference_row['export_version_id']:
                    up_to_date = 0
                else:
                    up_to_date = 1

                self.reference_infos_signal.emit([reference_row['id'], variant_row['name'], export_row['name'], export_version_row['name'], up_to_date])

    def update_references_rows(self, reference_rows):
        self.running = False
        self.reference_rows = reference_rows
        self.running = True
        self.start()