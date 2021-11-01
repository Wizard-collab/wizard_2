# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.core import project
from wizard.core import assets
from wizard.core import site
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import drop_files_widget
from wizard.gui import gui_server

class create_ticket_widget(QtWidgets.QDialog):
    def __init__(self, export_version_id, parent=None):
        super(create_ticket_widget, self).__init__()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Create ticket")

        self.export_version_id = export_version_id
        self.build_ui()
        self.fill_ui()
        self.connect_functions()

    def submit(self):
        title = self.title_lineEdit.text()
        destination_user = self.destination_comboBox.currentText()
        if destination_user == 'everybody':
            destination_user = None
        content = self.content_textEdit.toPlainText()
        files = self.drop_files_widget.files()
        if assets.create_ticket(title, content, self.export_version_id, destination_user, files):
            gui_server.refresh_ui()
            self.close()

    def connect_functions(self):
        self.submit_button.clicked.connect(self.submit)
        self.quit_button.clicked.connect(self.close)

    def fill_ui(self):
        self.destination_comboBox.addItem('everybody')
        for user_id in project.get_users_ids_list():
            user_name = site.get_user_data(user_id, 'user_name')
            self.destination_comboBox.addItem(user_name)
        export_version_row = project.get_export_version_data(self.export_version_id)
        export_row = project.get_export_data(export_version_row['export_id'])
        variant_row = project.get_variant_data(export_row['variant_id'])
        stage_row = project.get_stage_data(variant_row['stage_id'])
        asset_row = project.get_asset_data(stage_row['asset_id'])
        category_row = project.get_category_data(asset_row['category_id'])
        info = f"This ticket is about "
        info += f"{category_row['name']} |"
        info += f"{asset_row['name']} |"
        info += f"{stage_row['name']} |"
        info += f"{variant_row['name']} |"
        info += f"{export_row['name']} |"
        info += f"{export_version_row['name']}"
        self.infos_label.setText(info)

    def build_ui(self):
        self.resize(350, 500)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.infos_label = QtWidgets.QLabel()
        self.infos_label.setWordWrap(True)
        self.infos_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.infos_label)

        self.header_widget = QtWidgets.QWidget()
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(0,0,0,0)
        self.header_layout.setSpacing(6)
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.title_lineEdit = QtWidgets.QLineEdit()
        self.title_lineEdit.setPlaceholderText('Ticket title')
        self.header_layout.addWidget(self.title_lineEdit)

        self.destination_comboBox = QtWidgets.QComboBox()
        self.destination_comboBox.setItemDelegate(QtWidgets.QStyledItemDelegate())
        self.header_layout.addWidget(self.destination_comboBox)

        self.content_textEdit = QtWidgets.QTextEdit()
        self.content_textEdit.setPlaceholderText('Your message here')
        self.main_layout.addWidget(self.content_textEdit)

        self.drop_files_widget = drop_files_widget.drop_files_widget()
        self.main_layout.addWidget(self.drop_files_widget)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(6)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.spaceItem = QtWidgets.QSpacerItem(100,0,QtWidgets.QSizePolicy.Expanding,
                                                    QtWidgets.QSizePolicy.Fixed)
        self.buttons_layout.addSpacerItem(self.spaceItem)

        self.quit_button = QtWidgets.QPushButton('Cancel')
        self.buttons_layout.addWidget(self.quit_button)
        self.submit_button = QtWidgets.QPushButton('Submit')
        self.submit_button.setObjectName('blue_button')
        self.buttons_layout.addWidget(self.submit_button)