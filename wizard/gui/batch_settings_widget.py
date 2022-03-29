# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import logging

# Wizard modules
from wizard.core import assets
from wizard.vars import assets_vars
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils

logger = logging.getLogger(__name__)

class batch_settings_widget(QtWidgets.QDialog):
    def __init__(self, work_env_id, stage_to_export, parent=None):
        super(batch_settings_widget, self).__init__()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Batch settings")

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.ToolTip)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.stages_relations_dic = dict()
        self.stages_relations_dic['animation'] = ['rigging']
        self.stages_relations_dic['camera'] = ['camrig']
        self.stages_relations_dic['cfx'] = ['rigging', 'grooming']

        self.stages_with_frange = assets_vars._sequences_stages_list_
        if assets_vars._layout_ in self.stages_with_frange:
            self.stages_with_frange.remove(assets_vars._layout_)

        self.work_env_id = work_env_id
        self.stage_to_export = stage_to_export

        self.build_ui()
        self.get_frames()
        self.fill_ui()
        self.connect_functions()
        self.refresh()

    def showEvent(self, event):
        gui_utils.move_ui(self)

    def apply(self):
        self.frange = [self.inrollframe_spinBox.value(), self.outrollframe_spinBox.value()]
        self.refresh_assets = self.refresh_assets_checkbox.isChecked()
        self.nspace_list = self.get_selected_nspaces()
        if (len(self.nspace_list) > 0) and self.need_nspace_list:
            self.accept()
        elif not self.need_nspace_list:
            self.accept()
        else:
            logger.warning('Please select assets to export')

    def get_selected_nspaces(self):
        selected_nspaces = []
        for item in self.assets_list.selectedItems():
            selected_nspaces.append(item.text())
        return selected_nspaces

    def get_frames(self):
        asset_row = assets.get_asset_data_from_work_env_id(self.work_env_id)
        self.preroll = asset_row['preroll']
        self.postroll = asset_row['postroll']

    def connect_functions(self):
        self.inframe_spinBox.valueChanged.connect(self.refresh)
        self.outframe_spinBox.valueChanged.connect(self.refresh)
        self.rolls_checkbox.stateChanged.connect(self.refresh)
        self.batch_button.clicked.connect(self.apply)
        self.reject_button.clicked.connect(self.reject)

    def fill_ui(self):
        if self.stage_to_export in self.stages_relations_dic:
            self.need_nspace_list=True
            stages_list = self.stages_relations_dic[self.stage_to_export]
            references = []
            all_references = assets.get_references_files(self.work_env_id)
            for stage in all_references.keys():
                if stage in stages_list:
                    for reference_row in all_references[stage]:
                        item = QtWidgets.QListWidgetItem(QtGui.QIcon(ressources._stage_icons_dic_[stage]),
                                                                    reference_row['namespace'])
                        self.assets_list.addItem(item)
        else:
            self.need_nspace_list=False
            self.nspace_list_widget.setVisible(False)

        asset_row = assets.get_asset_data_from_work_env_id(self.work_env_id)
        self.inframe_spinBox.setValue(asset_row['inframe'])
        self.outframe_spinBox.setValue(asset_row['outframe'])

        if self.stage_to_export not in self.stages_with_frange:
            self.range_setup_widget.setVisible(False)

    def refresh(self):
        inrollframe = self.inframe_spinBox.value()
        outrollframe = self.outframe_spinBox.value()
        if self.rolls_checkbox.isChecked():
            inrollframe = inrollframe-self.preroll
            outrollframe = outrollframe-self.postroll
        self.inrollframe_spinBox.setValue(inrollframe)
        self.outrollframe_spinBox.setValue(outrollframe)

    def build_ui(self):
        self.setMinimumWidth(400)
        self.main_widget_layout = QtWidgets.QHBoxLayout()
        self.main_widget_layout.setContentsMargins(12, 12, 12, 12)
        self.setLayout(self.main_widget_layout)

        self.main_widget = QtWidgets.QFrame()
        self.main_widget.setObjectName('round_frame')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(12)
        self.main_widget.setLayout(self.main_layout)
        self.main_widget_layout.addWidget(self.main_widget)

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(12)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 190))
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.main_widget.setGraphicsEffect(self.shadow)
        
        self.refresh_assets_checkbox = QtWidgets.QCheckBox('Refresh assets in scene')
        self.refresh_assets_checkbox.setObjectName('transparent_widget')
        self.main_layout.addWidget(self.refresh_assets_checkbox)

        self.range_setup_widget = QtWidgets.QWidget()
        self.range_setup_widget.setObjectName('transparent_widget')
        self.range_setup_layout = QtWidgets.QVBoxLayout()
        self.range_setup_layout.setContentsMargins(0,0,0,0)
        self.range_setup_layout.setSpacing(8)
        self.range_setup_widget.setLayout(self.range_setup_layout)
        self.main_layout.addWidget(self.range_setup_widget)


        self.frame_range_label = QtWidgets.QLabel('Frame range')
        self.frame_range_label.setObjectName('gray_label')
        self.range_setup_layout.addWidget(self.frame_range_label)

        self.rolls_checkbox = QtWidgets.QCheckBox('Export with prerolls and postrolls')
        self.rolls_checkbox.setObjectName('transparent_widget')
        self.range_setup_layout.addWidget(self.rolls_checkbox)
        self.range_widget = QtWidgets.QWidget()
        self.range_widget.setObjectName('transparent_widget')
        self.range_layout = QtWidgets.QHBoxLayout()
        self.range_layout.setContentsMargins(0,0,0,0)
        self.range_layout.setSpacing(8)
        self.range_widget.setLayout(self.range_layout)
        self.range_setup_layout.addWidget(self.range_widget)

        self.inrollframe_spinBox = QtWidgets.QSpinBox()
        self.inrollframe_spinBox.setEnabled(False)
        self.inrollframe_spinBox.setObjectName('gray_label')
        self.inrollframe_spinBox.setRange(-1000000, 1000000)
        self.inrollframe_spinBox.setButtonSymbols(2)
        self.range_layout.addWidget(self.inrollframe_spinBox)

        self.inframe_spinBox = QtWidgets.QSpinBox()
        self.inframe_spinBox.setRange(-1000000, 1000000)
        self.inframe_spinBox.setButtonSymbols(2)
        self.range_layout.addWidget(self.inframe_spinBox)

        self.outframe_spinBox = QtWidgets.QSpinBox()
        self.outframe_spinBox.setRange(-1000000, 1000000)
        self.outframe_spinBox.setButtonSymbols(2)
        self.range_layout.addWidget(self.outframe_spinBox)

        self.outrollframe_spinBox = QtWidgets.QSpinBox()
        self.outrollframe_spinBox.setEnabled(False)
        self.outrollframe_spinBox.setObjectName('gray_label')
        self.outrollframe_spinBox.setRange(-1000000, 1000000)
        self.outrollframe_spinBox.setButtonSymbols(2)
        self.range_layout.addWidget(self.outrollframe_spinBox)

        self.nspace_list_widget = QtWidgets.QWidget()
        self.nspace_list_widget.setObjectName('transparent_widget')
        self.nspace_list_layout = QtWidgets.QVBoxLayout()
        self.nspace_list_layout.setContentsMargins(0,0,0,0)
        self.nspace_list_layout.setSpacing(8)
        self.nspace_list_widget.setLayout(self.nspace_list_layout)
        self.main_layout.addWidget(self.nspace_list_widget)

        self.infos_label = QtWidgets.QLabel('Select the assets to export')
        self.infos_label.setObjectName('gray_label')
        self.nspace_list_layout.addWidget(self.infos_label)

        self.assets_list = QtWidgets.QListWidget()
        self.assets_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.nspace_list_layout.addWidget(self.assets_list)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_widget.setObjectName('transparent_widget')
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(4)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.reject_button = QtWidgets.QPushButton('Cancel')
        self.reject_button.setDefault(False)
        self.reject_button.setAutoDefault(False)
        self.buttons_layout.addWidget(self.reject_button)

        self.batch_button = QtWidgets.QPushButton('Batch')
        self.batch_button.setObjectName('blue_button')
        self.batch_button.setDefault(True)
        self.batch_button.setAutoDefault(True)
        self.buttons_layout.addWidget(self.batch_button)
