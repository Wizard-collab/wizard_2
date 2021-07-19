# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

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
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.info_widget = gui_utils.info_widget()
        self.info_widget.setVisible(0)
        self.main_layout.addWidget(self.info_widget)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setObjectName('tree_as_list_widget')
        self.list_view.setColumnCount(5)
        self.list_view.setIndentation(20)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setHeaderLabels(['Export name', 'Version', 'User', 'Date', 'Comment'])
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.list_view_scrollBar = self.list_view.verticalScrollBar()
        self.main_layout.addWidget(self.list_view)

    def connect_functions(self):
        self.list_view_scrollBar.rangeChanged.connect(lambda: self.list_view_scrollBar.setValue(self.list_view_scrollBar.maximum()))

    def refresh(self):
        if self.isVisible():
            if self.variant_id is not None:
                print('loool')
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
                                self.export_ids[export_row['id']] = export_item
                    export_versions_rows = project.get_export_versions_by_variant(self.variant_id)
                    if export_versions_rows is not None:
                        if export_versions_rows != []:
                            for export_version_row in export_versions_rows:
                                if export_version_row['id'] not in self.export_versions_ids.keys():
                                    if export_version_row['export_id'] in self.export_ids.keys():
                                        export_version_item = custom_export_version_tree_item(export_version_row, self.export_ids[export_version_row['export_id']])
                                    self.export_versions_ids[export_version_row['id']] = export_version_item
            else:
                self.show_info_mode("Select or create a stage\nin the project tree !", ressources._select_stage_info_image_)


    def show_info_mode(self, text, image):
        self.info_widget.setVisible(1)
        self.info_widget.setText(text)
        self.info_widget.setImage(image)
        self.list_view.setVisible(0)

    def hide_info_mode(self):
        self.info_widget.setVisible(0)
        self.list_view.setVisible(1)

    def change_variant(self, variant_id):
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