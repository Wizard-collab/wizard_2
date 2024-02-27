# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.core import project
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils


class current_asset_viewer(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(current_asset_viewer, self).__init__(parent)
        self.setObjectName('dark_widget')
        self.arrow_pixmap = gui_utils.QIcon_from_svg(ressources._right_icon_, '#505061').pixmap(20)
        self.build_ui()

    def refresh(self, instance_type, instance_id):
        if instance_id is None or instance_id == 0:
            self.info_label.setText("Nothing selected")
            self.infos_widget.setVisible(1)
            self.viewer_widget.setVisible(0)
            return
        self.viewer_widget.setVisible(1)
        self.infos_widget.setVisible(0)

        if instance_type == 'work_env':
            work_env_row = project.get_work_env_data(instance_id)
            variant_id = work_env_row['variant_id']
            self.work_env_label.setPixmap(QtGui.QIcon(ressources._softwares_icons_dic_[work_env_row['name']]).pixmap(12))
            self.work_env_label.setVisible(1)
            self.arrow_4.setVisible(1)
            if not variant_id:
                return
            variant_row = project.get_variant_data(variant_id)
            self.variant_label.setText(variant_row['name'])
            stage_row = project.get_stage_data(variant_row['stage_id'])

        elif instance_type == 'stage':
            self.work_env_label.setVisible(0)
            self.arrow_4.setVisible(0)
            self.variant_label.setVisible(0)
            self.arrow_3.setVisible(0)
            stage_row = project.get_stage_data(instance_id)

        else:
            variant_id = instance_id
            self.work_env_label.setVisible(0)
            self.arrow_4.setVisible(0)
            variant_row = project.get_variant_data(variant_id)
            if not variant_row:
                return
            self.variant_label.setText(variant_row['name'])
            stage_row = project.get_stage_data(variant_row['stage_id'])
            
        if not stage_row:
            return
        asset_row = project.get_asset_data(stage_row['asset_id'])
        if not asset_row:
            return
        category_row = project.get_category_data(asset_row['category_id'])
        if not category_row:
            return
        self.category_label.setText(category_row['name'])
        self.asset_label.setText(asset_row['name'])
        self.stage_label.setText(stage_row['name'])

    def set_contents_margins(self, *arg, **args):
        self.main_layout.setContentsMargins(*arg, **args)

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(8,8,8,8)
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)

        self.infos_widget = QtWidgets.QFrame()
        self.infos_widget.setObjectName('round_frame')
        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(6,2,6,2)
        self.infos_layout.setSpacing(2)
        self.infos_widget.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_widget)
        self.infos_widget.setVisible(0)

        self.info_label = QtWidgets.QLabel()
        self.infos_layout.addWidget(self.info_label)
        self.info_label.setObjectName('bold_label')

        self.viewer_widget = QtWidgets.QFrame()
        self.viewer_widget.setObjectName('round_frame')
        self.viewer_layout = QtWidgets.QHBoxLayout()
        self.viewer_layout.setContentsMargins(6,2,6,2)
        self.viewer_layout.setSpacing(2)
        self.viewer_widget.setLayout(self.viewer_layout)
        self.main_layout.addWidget(self.viewer_widget)

        self.category_label = QtWidgets.QLabel('')
        self.category_label.setObjectName('bold_label')
        self.viewer_layout.addWidget(self.category_label)

        self.arrow_1 = QtWidgets.QLabel()
        self.arrow_1.setPixmap(self.arrow_pixmap)
        self.viewer_layout.addWidget(self.arrow_1)

        self.asset_label = QtWidgets.QLabel('')
        self.asset_label.setObjectName('bold_label')
        self.viewer_layout.addWidget(self.asset_label)

        self.arrow_2 = QtWidgets.QLabel()
        self.arrow_2.setPixmap(self.arrow_pixmap)
        self.viewer_layout.addWidget(self.arrow_2)

        self.stage_label = QtWidgets.QLabel('')
        self.stage_label.setObjectName('bold_label')
        self.viewer_layout.addWidget(self.stage_label)

        self.arrow_3 = QtWidgets.QLabel()
        self.arrow_3.setPixmap(self.arrow_pixmap)
        self.viewer_layout.addWidget(self.arrow_3)

        self.variant_label = QtWidgets.QLabel('')
        self.variant_label.setObjectName('bold_label')
        self.viewer_layout.addWidget(self.variant_label)

        self.arrow_4 = QtWidgets.QLabel()
        self.arrow_4.setPixmap(self.arrow_pixmap)
        self.viewer_layout.addWidget(self.arrow_4)

        self.work_env_label = QtWidgets.QLabel('')
        self.work_env_label.setObjectName('bold_label')
        self.viewer_layout.addWidget(self.work_env_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
