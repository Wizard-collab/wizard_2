# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import sys
try:
    from PyQt6 import QtWidgets, QtCore, QtGui
except ModuleNotFoundError:
    from PySide2 import QtWidgets, QtCore, QtGui
import logging

# Wizard modules
import wizard_communicate

logger = logging.getLogger(__name__)

dialog_accepted = QtWidgets.QDialog.DialogCode.Accepted

if not QtWidgets.QApplication.instance():
    app = QtWidgets.QApplication(sys.argv)

class video_settings_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(video_settings_widget, self).__init__(parent)

        self.setWindowTitle("Wizard - Video settings")

        self.icons_dic = dict()
        self.icons_dic['camera'] = "icons/camera.png"
        self.icons_dic['camrig'] = "icons/camera_rig.png"

        self.build_ui()
        self.get_frames()
        self.fill_ui()
        self.connect_functions()
        self.refresh()
        self.cam_list_changed()

    def apply(self):
        self.frange = [self.inrollframe_spinBox.value(), self.outrollframe_spinBox.value()]
        self.nspace_list = self.get_selected_nspaces()
        self.accept()

    def get_selected_nspaces(self):
        selected_nspaces = []
        for item in self.assets_list.selectedItems():
            selected_nspaces.append(item.text())
        return selected_nspaces

    def get_frames(self):
        frame_range = wizard_communicate.get_frame_range(int(os.environ['wizard_work_env_id']))
        self.preroll = frame_range[0]
        self.postroll = frame_range[3]

    def connect_functions(self):
        self.inframe_spinBox.valueChanged.connect(self.refresh)
        self.outframe_spinBox.valueChanged.connect(self.refresh)
        self.rolls_checkbox.stateChanged.connect(self.refresh)
        self.video_button.clicked.connect(self.apply)
        self.reject_button.clicked.connect(self.reject)
        self.assets_list.itemSelectionChanged.connect(self.cam_list_changed)

    def cam_list_changed(self):
        selected_nspaces = self.get_selected_nspaces()
        if len(selected_nspaces) == 0:
            text = "Warning, if you don't select at least one camera, the video will be created with the default camera, you may want to select a camera."
        elif len(selected_nspaces) > 1:
            text = "Warning, if you select multiple cameras, wizard will create a video for each selected camera."
        else:
            text = ''
        self.warning_label.setText(text)

    def fill_ui(self):
        frame_range = wizard_communicate.get_frame_range(int(os.environ['wizard_work_env_id']))
        self.inframe_spinBox.setValue(frame_range[1])
        self.outframe_spinBox.setValue(frame_range[2])
        references = []
        all_references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
        for stage in all_references.keys():
            if stage in ['camrig', 'camera']:
                for reference_row in all_references[stage]:
                    item = QtWidgets.QListWidgetItem(QtGui.QIcon(self.icons_dic[stage]), reference_row['namespace'])
                    self.assets_list.addItem(item)

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
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(12)
        self.setLayout(self.main_layout)

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
        self.inrollframe_spinBox.setButtonSymbols(QtWidgets.QSpinBox.ButtonSymbols.NoButtons)
        self.range_layout.addWidget(self.inrollframe_spinBox)

        self.inframe_spinBox = QtWidgets.QSpinBox()
        self.inframe_spinBox.setRange(-1000000, 1000000)
        self.inframe_spinBox.setButtonSymbols(QtWidgets.QSpinBox.ButtonSymbols.NoButtons)
        self.range_layout.addWidget(self.inframe_spinBox)

        self.outframe_spinBox = QtWidgets.QSpinBox()
        self.outframe_spinBox.setRange(-1000000, 1000000)
        self.outframe_spinBox.setButtonSymbols(QtWidgets.QSpinBox.ButtonSymbols.NoButtons)
        self.range_layout.addWidget(self.outframe_spinBox)

        self.outrollframe_spinBox = QtWidgets.QSpinBox()
        self.outrollframe_spinBox.setEnabled(False)
        self.outrollframe_spinBox.setObjectName('gray_label')
        self.outrollframe_spinBox.setRange(-1000000, 1000000)
        self.outrollframe_spinBox.setButtonSymbols(QtWidgets.QSpinBox.ButtonSymbols.NoButtons)
        self.range_layout.addWidget(self.outrollframe_spinBox)

        self.nspace_list_widget = QtWidgets.QWidget()
        self.nspace_list_widget.setObjectName('transparent_widget')
        self.nspace_list_layout = QtWidgets.QVBoxLayout()
        self.nspace_list_layout.setContentsMargins(0,0,0,0)
        self.nspace_list_layout.setSpacing(8)
        self.nspace_list_widget.setLayout(self.nspace_list_layout)
        self.main_layout.addWidget(self.nspace_list_widget)

        self.infos_label = QtWidgets.QLabel('Select the camera(s)')
        self.infos_label.setObjectName('gray_label')
        self.nspace_list_layout.addWidget(self.infos_label)

        self.assets_list = QtWidgets.QListWidget()
        self.assets_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.nspace_list_layout.addWidget(self.assets_list)

        self.warning_label = QtWidgets.QLabel('')
        self.warning_label.setWordWrap(True)
        self.warning_label.setStyleSheet('color:#ffad4d;')
        self.nspace_list_layout.addWidget(self.warning_label)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_widget.setObjectName('transparent_widget')
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(4)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.reject_button = QtWidgets.QPushButton('Cancel')
        self.reject_button.setDefault(False)
        self.reject_button.setAutoDefault(False)
        self.buttons_layout.addWidget(self.reject_button)

        self.video_button = QtWidgets.QPushButton('Create video')
        self.video_button.setObjectName('blue_button')
        self.video_button.setDefault(True)
        self.video_button.setAutoDefault(True)
        self.buttons_layout.addWidget(self.video_button)
