# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard gui modules
from wizard.gui import search_reference_widget
from wizard.gui import gui_utils

# Wizard modules
from wizard.core import assets
from wizard.vars import ressources

class references_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(references_widget, self).__init__(parent)
        self.search_reference_widget = search_reference_widget.search_reference_widget()
        self.work_env_id = None
        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.search_sc = QtWidgets.QShortcut(QtGui.QKeySequence('Tab'), self)
        self.search_sc.activated.connect(self.search_reference)

    def search_reference(self):
        self.search_reference_widget = search_reference_widget.search_reference_widget()
        self.search_reference_widget.stage_ids_signal.connect(self.create_references_from_stage_ids)
        self.search_reference_widget.show()

    def create_references_from_stage_ids(self, variant_ids):
        for variant_id in variant_ids:
            print(variant_id)
            #asset.create_reference(self.work_env_id, export_version_id)

    def change_work_env(self, work_env_id):
        self.work_env_id = work_env_id

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
