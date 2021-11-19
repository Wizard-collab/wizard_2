# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import time

# Wizard modules
from wizard.core import tools
from wizard.core import user
from wizard.core import site
from wizard.core import assets
from wizard.core import project
from wizard.vars import ressources
from wizard.vars import assets_vars
from wizard.vars import user_vars

# Wizard gui modules
from wizard.gui import gui_server
from wizard.gui import gui_utils
from wizard.gui import estimation_widget
from wizard.gui import comment_widget

class asset_tracking_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(asset_tracking_widget, self).__init__(parent)

        self.last_time = 0
        self.variant_id = None
        self.variant_row = None
        self.users_ids = dict()
        self.tracking_event_ids = dict()

        self.apply_assignment_modification = None
        self.apply_state_modification = None

        self.build_ui()
        self.refresh_users_dic()
        self.connect_functions()

    def refresh_users_dic(self):
        users_ids = project.get_users_ids_list()
        for user_id in users_ids:
            if user_id not in self.users_ids.keys():
                self.users_ids[user_id] = site.get_user_data(user_id, 'user_name')
                self.assignment_comboBox.addItem(self.users_ids[user_id])

    def edit_estimation(self):
        self.estimation_widget = estimation_widget.estimation_widget()
        if self.estimation_widget.exec_() == QtWidgets.QDialog.Accepted:
            seconds = self.estimation_widget.hours*3600
            assets.modify_variant_estimation(self.variant_id, seconds)
            gui_server.refresh_ui()

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.setup_widget = QtWidgets.QFrame()
        self.setup_widget.setObjectName('asset_tracking_event_frame')
        self.setup_layout = QtWidgets.QHBoxLayout()
        self.setup_layout.setSpacing(6)
        self.setup_widget.setLayout(self.setup_layout)
        self.main_layout.addWidget(self.setup_widget)

        self.assignment_comboBox = gui_utils.QComboBox()
        self.setup_layout.addWidget(self.assignment_comboBox)

        self.state_comboBox = gui_utils.QComboBox()
        self.state_comboBox.setIconSize(QtCore.QSize(14,14))
        self.state_comboBox.setFixedWidth(100)
        self.setup_layout.addWidget(self.state_comboBox)
        self.state_comboBox.addItem(QtGui.QIcon(ressources._state_todo_), assets_vars._asset_state_todo_)
        self.state_comboBox.addItem(QtGui.QIcon(ressources._state_wip_), assets_vars._asset_state_wip_)
        self.state_comboBox.addItem(QtGui.QIcon(ressources._state_done_), assets_vars._asset_state_done_ )
        self.state_comboBox.addItem(QtGui.QIcon(ressources._state_error_), assets_vars._asset_state_error_)

        self.progress_widget = QtWidgets.QFrame()
        self.progress_widget.setObjectName('asset_tracking_event_frame')
        self.progress_layout = QtWidgets.QVBoxLayout()
        self.progress_layout.setSpacing(6)
        self.progress_widget.setLayout(self.progress_layout)
        self.main_layout.addWidget(self.progress_widget)

        self.time_infos_widget = QtWidgets.QWidget()
        self.time_infos_widget.setObjectName('transparent_widget')
        self.time_infos_layout = QtWidgets.QHBoxLayout()
        self.time_infos_layout.setContentsMargins(0,0,0,0)
        self.time_infos_layout.setSpacing(6)
        self.time_infos_widget.setLayout(self.time_infos_layout)
        self.progress_layout.addWidget(self.time_infos_widget)

        self.work_time_icon_label = QtWidgets.QLabel()
        self.work_time_icon_label.setFixedSize(QtCore.QSize(22,22))
        self.work_time_icon_label.setPixmap(QtGui.QIcon(ressources._work_time_icon_).pixmap(22))
        self.time_infos_layout.addWidget(self.work_time_icon_label)

        self.work_time_label = QtWidgets.QLabel()
        self.work_time_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.time_infos_layout.addWidget(self.work_time_label)

        self.time_infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.estimated_time_icon_label = QtWidgets.QLabel()
        self.estimated_time_icon_label.setFixedSize(QtCore.QSize(22,22))
        self.estimated_time_icon_label.setPixmap(QtGui.QIcon(ressources._estimated_time_icon_).pixmap(22))
        self.time_infos_layout.addWidget(self.estimated_time_icon_label)

        self.estimated_time_label = QtWidgets.QLabel()
        self.estimated_time_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.time_infos_layout.addWidget(self.estimated_time_label)

        self.edit_estimation_button = QtWidgets.QPushButton()
        self.edit_estimation_button.setObjectName('edit_button')
        self.edit_estimation_button.setFixedSize(16,16)
        self.time_infos_layout.addWidget(self.edit_estimation_button)

        self.progress_bar_widget = QtWidgets.QWidget()
        self.progress_bar_widget.setObjectName('transparent_widget')
        self.progress_bar_layout = QtWidgets.QHBoxLayout()
        self.progress_bar_layout.setContentsMargins(0,0,0,0)
        self.progress_bar_layout.setSpacing(6)
        self.progress_bar_widget.setLayout(self.progress_bar_layout)
        self.progress_layout.addWidget(self.progress_bar_widget)

        self.time_progress_bar = QtWidgets.QProgressBar()
        self.time_progress_bar.setMaximumHeight(6)
        self.progress_bar_layout.addWidget(self.time_progress_bar)

        self.percent_label = QtWidgets.QLabel()
        self.progress_bar_layout.addWidget(self.percent_label)

        self.separation_widget = QtWidgets.QWidget()
        self.separation_layout = QtWidgets.QHBoxLayout()
        self.separation_layout.setContentsMargins(0,0,0,0)
        self.separation_layout.setSpacing(6)
        self.separation_widget.setLayout(self.separation_layout)
        self.main_layout.addWidget(self.separation_widget)

        self.asset_history_label = QtWidgets.QLabel('Asset history')
        self.separation_layout.addWidget(self.asset_history_label)

        self.separation_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.add_comment_button = QtWidgets.QPushButton('Add comment')
        self.add_comment_button.setMaximumHeight(24)
        self.add_comment_button.setStyleSheet('padding:2px;')
        self.separation_layout.addWidget(self.add_comment_button)

        self.events_scrollArea = QtWidgets.QScrollArea()
        self.events_scrollBar = self.events_scrollArea.verticalScrollBar()

        self.events_scrollArea_widget = QtWidgets.QWidget()
        self.events_scrollArea_widget.setObjectName('transparent_widget')
        self.events_scrollArea_layout = QtWidgets.QVBoxLayout()
        self.events_scrollArea_layout.setContentsMargins(0,4,8,4)
        self.events_scrollArea_layout.setSpacing(0)
        self.events_scrollArea_widget.setLayout(self.events_scrollArea_layout)

        self.events_content_widget = QtWidgets.QWidget()
        self.events_content_layout = QtWidgets.QVBoxLayout()
        self.events_content_layout.setContentsMargins(0,0,0,0)
        self.events_content_layout.setSpacing(6)
        self.events_content_widget.setLayout(self.events_content_layout)
        self.events_scrollArea_layout.addWidget(self.events_content_widget)

        self.events_scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.events_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.events_scrollArea.setWidgetResizable(True)
        self.events_scrollArea.setWidget(self.events_scrollArea_widget)
        self.main_layout.addWidget(self.events_scrollArea)

        self.infos_frame = QtWidgets.QFrame()
        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(0,0,0,0)
        self.infos_frame.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_frame)

        self.refresh_label = QtWidgets.QLabel()
        self.refresh_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.refresh_label)
        
        self.infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.infos_layout.addWidget(QtWidgets.QLabel('Show'))
        self.event_count_spinBox = QtWidgets.QSpinBox()
        self.event_count_spinBox.setButtonSymbols(2)
        self.event_count_spinBox.setRange(1, 10000000)
        self.event_count_spinBox.setFixedWidth(50)
        self.infos_layout.addWidget(self.event_count_spinBox)
        self.infos_layout.addWidget(QtWidgets.QLabel('events'))

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(300,0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

    def change_variant(self, variant_id):
        self.variant_id = variant_id
        self.refresh()

    def refresh(self):
        start_time = time.time()
        if self.variant_id is not None:
            self.variant_row = project.get_variant_data(self.variant_id)
        else:
            self.variant_row = None
        self.refresh_tracking_events()
        self.refresh_state()
        self.refresh_users_dic()
        self.refresh_user()
        self.refresh_time()
        self.update_refresh_time(start_time)

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.time()-start_time), 3))
        self.refresh_label.setText(f"refresh : {refresh_time}s")

    def refresh_time(self):
        if self.variant_id is not None:
            string_time = tools.convert_seconds_to_string_time(float(self.variant_row['work_time']))
            self.work_time_label.setText(string_time)
            if self.variant_row['estimated_time'] is not None:
                self.estimated_time_label.setText(tools.convert_seconds_to_string_time(float(self.variant_row['estimated_time'])))
                percent = (float(self.variant_row['work_time'])/float(self.variant_row['estimated_time']))*100
                self.percent_label.setText(f"{str(int(percent))}%")
                if percent > 100:
                    percent = 100
                    if self.variant_row['state'] != 'done':
                        self.time_progress_bar.setStyleSheet('::chunk{background-color:#ff5d5d;}')
                else:
                    self.time_progress_bar.setStyleSheet('::chunk{background-color:#ffad4d;}')
                if self.variant_row['state'] == 'done':
                    self.time_progress_bar.setStyleSheet('::chunk{background-color:#95d859;}')
                self.time_progress_bar.setValue(percent)
            else:
                self.estimated_time_label.setText('No estimation')
                self.time_progress_bar.setValue(0)
                self.percent_label.setText("0%")
        else:
            self.work_time_label.setText('Work time')
            self.estimated_time_label.setText('Estimation time')
            self.time_progress_bar.setValue(0)
            self.percent_label.setText("0%")

    def remove_tracking_event(self, event_id):
        if event_id in self.tracking_event_ids.keys():
            self.tracking_event_ids[event_id].setVisible(False)
            self.tracking_event_ids[event_id].setParent(None)
            self.tracking_event_ids[event_id].deleteLater()
            del self.tracking_event_ids[event_id]

    def clear_all_tracking_events(self):
        tracking_event_ids = list(self.tracking_event_ids.keys())
        for event_id in tracking_event_ids:
            self.remove_tracking_event(event_id)

    def refresh_tracking_events(self):
        project_tracking_events_ids = []
        if self.variant_id is not None:
            event_number = self.event_count_spinBox.value()
            tracking_event_rows = project.get_asset_tracking_events(self.variant_id)
            for tracking_event_row in tracking_event_rows[-event_number:]:
                project_tracking_events_ids.append(tracking_event_row['id'])
                if tracking_event_row['id'] not in self.tracking_event_ids.keys():
                    widget = tracking_event_widget(tracking_event_row)

                    if tracking_event_row['creation_time']-self.last_time > 350:
                        widget.add_time()
                    self.last_time = tracking_event_row['creation_time']

                    self.events_content_layout.addWidget(widget)
                    self.tracking_event_ids[tracking_event_row['id']] = widget

            self.remove_useless_events(event_number)
        tracking_event_ids = list(self.tracking_event_ids.keys())
        for event_id in tracking_event_ids:
            if event_id not in project_tracking_events_ids:
                self.remove_tracking_event(event_id)

    def remove_useless_events(self, event_number):
        tracking_event_ids_list_to_remove = list(self.tracking_event_ids.keys())[:-event_number]
        for event_id in tracking_event_ids_list_to_remove:
            self.remove_tracking_event(event_id)
        events_ids_list = list(self.tracking_event_ids.keys())
        if events_ids_list is not None and events_ids_list != []:
            self.tracking_event_ids[events_ids_list[0]].add_time()

    def get_context(self):
        context_dic = user.user().get_context(user_vars._asset_tracking_context_)
        if context_dic is not None and context_dic != dict():
            self.event_count_spinBox.setValue(context_dic['events_count'])
        else:
            self.event_count_spinBox.setValue(5)

    def set_context(self):
        if self.isVisible():
            visible = 1
        else:
            visible = 0
        context_dic = dict()
        context_dic['events_count'] = self.event_count_spinBox.value()
        user.user().add_context(user_vars._asset_tracking_context_, context_dic)

    def refresh_user(self):
        self.apply_assignment_modification = None
        if self.variant_row is not None:
            if self.variant_row['assignment'] is not None:
                self.assignment_comboBox.setCurrentText(self.variant_row['assignment'])
        self.apply_assignment_modification = 1

    def refresh_state(self):
        self.apply_state_modification = None
        if self.variant_row is not None:
            self.state_comboBox.setCurrentText(self.variant_row['state'])
        else:
            self.state_comboBox.setCurrentText('todo')
        self.apply_state_modification = 1

    def modify_state(self, state):
        if self.variant_id is not None:
            if self.apply_state_modification:
                self.comment_widget = comment_widget.comment_widget()
                if self.comment_widget.exec_() == QtWidgets.QDialog.Accepted:
                    comment = self.comment_widget.comment
                    assets.modify_variant_state(self.variant_id, state, comment)
                    gui_server.refresh_ui()

    def modify_assignment(self, user_name):
        if self.variant_id is not None:
            if self.apply_assignment_modification:
                assets.modify_variant_assignment(self.variant_id, user_name)
                gui_server.refresh_ui()

    def add_comment(self):
        if self.variant_id is not None:
            self.comment_widget = comment_widget.comment_widget()
            if self.comment_widget.exec_() == QtWidgets.QDialog.Accepted:
                comment = self.comment_widget.comment
                assets.add_variant_comment(self.variant_id, comment)
                gui_server.refresh_ui()

    def change_count(self):
        self.clear_all_tracking_events()
        self.refresh_tracking_events()

    def connect_functions(self):
        self.state_comboBox.currentTextChanged.connect(self.modify_state)
        self.assignment_comboBox.currentTextChanged.connect(self.modify_assignment)
        self.events_scrollBar.rangeChanged.connect(lambda: self.events_scrollBar.setValue(self.events_scrollBar.maximum()))
        self.event_count_spinBox.valueChanged.connect(self.change_count)
        self.edit_estimation_button.clicked.connect(self.edit_estimation)
        self.add_comment_button.clicked.connect(self.add_comment)

class time_widget(QtWidgets.QWidget):
    def __init__(self, time_float, parent = None):
        super(time_widget, self).__init__(parent)
        self.time_float = time_float
        self.build_ui()

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(4,4,4,4)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)
        day, hour = tools.convert_time(self.time_float)
        self.day_label = QtWidgets.QLabel(f"{day} - ")
        self.day_label.setObjectName('gray_label')
        self.hour_label = QtWidgets.QLabel(hour)
        self.hour_label.setObjectName('bold_label')
        current_day, current_hour = tools.convert_time(time.time())
        if current_day != day:
            self.main_layout.addWidget(self.day_label)
        self.main_layout.addWidget(self.hour_label)
        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

class tracking_event_widget(QtWidgets.QFrame):
    def __init__(self, tracking_event_row, parent=None):
        super(tracking_event_widget, self).__init__(parent)

        self.time_widget = None
        self.tracking_event_row = tracking_event_row

        self.build_ui()

        if self.tracking_event_row['event_type'] == 'state_switch':
            self.build_state_switch_ui()
        elif self.tracking_event_row['event_type'] == 'assignment':
            self.build_assignment_ui()
        elif self.tracking_event_row['event_type'] == 'work_session':
            self.build_work_session_ui()
        elif self.tracking_event_row['event_type'] == 'estimation':
            self.build_estimation_ui()
        elif self.tracking_event_row['event_type'] == 'comment':
            self.build_comment_event_ui()

        if self.tracking_event_row['comment'] is not None and self.tracking_event_row['comment'] != '':
            self.build_comment_ui()

    def add_time(self):
        if self.time_widget == None:
            self.time_widget = time_widget(self.tracking_event_row['creation_time'])
            self.overall_layout.insertWidget(0, self.time_widget)

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.setObjectName('transparent_widget')
        self.overall_layout = QtWidgets.QVBoxLayout()
        self.overall_layout.setContentsMargins(0,0,0,0)
        self.overall_layout.setSpacing(6)
        self.setLayout(self.overall_layout)

        self.overall_widget = QtWidgets.QWidget()
        self.overall_widget.setObjectName('asset_tracking_event_bg_frame')
        self.widget_layout = QtWidgets.QVBoxLayout()
        self.widget_layout.setContentsMargins(0,0,0,0)
        self.widget_layout.setSpacing(0)
        self.overall_widget.setLayout(self.widget_layout)
        self.overall_layout.addWidget(self.overall_widget)

        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setObjectName('asset_tracking_event_frame')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setSpacing(6)
        self.main_widget.setLayout(self.main_layout)
        self.widget_layout.addWidget(self.main_widget)

    def build_comment_ui(self):
        self.comment_widget = QtWidgets.QWidget()
        self.comment_widget.setObjectName('transparent_widget')
        self.comment_layout = QtWidgets.QHBoxLayout()
        self.comment_layout.setSpacing(6)
        self.comment_widget.setLayout(self.comment_layout)
        self.widget_layout.addWidget(self.comment_widget)
        self.comment_label = QtWidgets.QLabel(self.tracking_event_row['comment'])
        self.comment_label.setWordWrap(True)
        self.comment_layout.addWidget(self.comment_label)

    def build_comment_event_ui(self):
        self.user_label = QtWidgets.QLabel(self.tracking_event_row['creation_user'])
        self.user_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout.addWidget(self.user_label)

        self.info_label = QtWidgets.QLabel('added a comment')
        self.info_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.info_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.info_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

    def build_estimation_ui(self):
        self.user_label = QtWidgets.QLabel(self.tracking_event_row['creation_user'])
        self.user_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout.addWidget(self.user_label)

        self.info_label = QtWidgets.QLabel('estimated task at')
        self.info_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.info_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.info_label)

        string_time = tools.convert_seconds_to_string_time(float(self.tracking_event_row['data']))

        self.estimation_label = QtWidgets.QLabel(string_time)
        self.estimation_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout.addWidget(self.estimation_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

    def build_work_session_ui(self):
        self.user_label = QtWidgets.QLabel(self.tracking_event_row['creation_user'])
        self.user_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout.addWidget(self.user_label)

        self.info_label = QtWidgets.QLabel('worked')
        self.info_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.info_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.info_label)

        string_time = tools.convert_seconds_to_string_time(float(self.tracking_event_row['data']))

        self.work_time_label = QtWidgets.QLabel(string_time)
        self.work_time_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout.addWidget(self.work_time_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

    def build_assignment_ui(self):
        self.user_label = QtWidgets.QLabel(self.tracking_event_row['creation_user'])
        self.user_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout.addWidget(self.user_label)

        self.info_label = QtWidgets.QLabel('assigned task to')
        self.info_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.info_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.info_label)

        self.assignment_label = QtWidgets.QLabel(self.tracking_event_row['data'])
        self.assignment_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout.addWidget(self.assignment_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

    def build_state_switch_ui(self):
        self.user_label = QtWidgets.QLabel(self.tracking_event_row['creation_user'])
        self.user_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout.addWidget(self.user_label)

        self.info_label = QtWidgets.QLabel('switched state to')
        self.info_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.info_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.info_label)

        self.state_frame = QtWidgets.QFrame()
        self.state_frame.setObjectName('asset_tracking_event_frame')
        self.state_frame.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.state_frame_layout = QtWidgets.QHBoxLayout()
        self.state_frame_layout.setContentsMargins(8,8,8,8)
        self.state_frame.setLayout(self.state_frame_layout)
        self.main_layout.addWidget(self.state_frame)

        if self.tracking_event_row['data'] == 'todo':
            color = '#8a8a8a'
        elif self.tracking_event_row['data'] == 'wip':
            color = '#ffad4d'
        elif self.tracking_event_row['data'] == 'done':
            color = '#95d859'
        elif self.tracking_event_row['data'] == 'error':
            color = '#ff5d5d'
        self.state_frame.setStyleSheet(f'background-color:{color};')
        
        self.state_label = QtWidgets.QLabel(self.tracking_event_row['data'].upper())
        self.state_label.setObjectName('bold_label')
        self.state_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.state_frame_layout.addWidget(self.state_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
