# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import time
import datetime

# Wizard modules
from wizard.core import tools
from wizard.core import user
from wizard.core import repository
from wizard.core import assets
from wizard.core import project
from wizard.core import image
from wizard.vars import ressources
from wizard.vars import assets_vars
from wizard.vars import user_vars

# Wizard gui modules
from wizard.gui import gui_server
from wizard.gui import gui_utils
from wizard.gui import comment_widget
from wizard.gui import tag_label

class asset_tracking_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(asset_tracking_widget, self).__init__(parent)

        self.last_time = 0
        self.stage_id = None
        self.stage_row = None
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
                user_row = repository.get_user_data(user_id)
                self.users_ids[user_id] = user_row['user_name']
                icon = QtGui.QIcon()
                pm = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_row['profile_picture']), 'png', 18)
                icon.addPixmap(pm)
                self.assignment_comboBox.addItem(icon, self.users_ids[user_id])

    def edit_estimation(self):
        self.estimation_widget = estimation_widget()
        if self.estimation_widget.exec_() == QtWidgets.QDialog.Accepted:
            days = self.estimation_widget.days
            assets.modify_stage_estimation(self.stage_id, days)
            gui_server.refresh_team_ui()

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(3)
        self.setLayout(self.main_layout)

        self.setup_widget = QtWidgets.QFrame()
        self.setup_widget.setObjectName('asset_tracking_event_frame')
        self.setup_layout = QtWidgets.QHBoxLayout()
        self.setup_layout.setContentsMargins(6,6,6,6)
        self.setup_layout.setSpacing(6)
        self.setup_widget.setLayout(self.setup_layout)
        self.main_layout.addWidget(self.setup_widget)

        self.assignment_comboBox = gui_utils.QComboBox()
        self.assignment_comboBox.setIconSize(QtCore.QSize(16,16))
        self.setup_layout.addWidget(self.assignment_comboBox)

        self.state_comboBox = gui_utils.QComboBox()
        self.state_comboBox.setIconSize(QtCore.QSize(16,16))
        self.state_comboBox.setFixedWidth(90)
        self.setup_layout.addWidget(self.state_comboBox)
        for state in assets_vars._asset_states_list_:
            self.state_comboBox.addItem(QtGui.QIcon(ressources._states_icons_[state]), state)

        self.priority_comboBox = gui_utils.QComboBox()
        self.priority_comboBox.setIconSize(QtCore.QSize(16,16))
        self.priority_comboBox.setFixedWidth(90)
        self.setup_layout.addWidget(self.priority_comboBox)
        for priority in assets_vars._priority_list_:
            self.priority_comboBox.addItem(QtGui.QIcon(ressources._priority_icons_list_[priority]), priority)

        self.progress_widget = QtWidgets.QFrame()
        self.progress_widget.setObjectName('asset_tracking_event_frame')
        self.progress_layout = QtWidgets.QVBoxLayout()
        self.progress_layout.setContentsMargins(6,6,6,6)
        self.progress_layout.setSpacing(6)
        self.progress_widget.setLayout(self.progress_layout)
        self.main_layout.addWidget(self.progress_widget)

        self.time_infos_widget = QtWidgets.QWidget()
        self.time_infos_widget.setObjectName('transparent_widget')
        self.time_infos_layout = QtWidgets.QVBoxLayout()
        self.time_infos_layout.setContentsMargins(0,0,0,0)
        self.time_infos_layout.setSpacing(6)
        self.time_infos_widget.setLayout(self.time_infos_layout)
        self.progress_layout.addWidget(self.time_infos_widget)

        self.time_infos_layout_1 = QtWidgets.QHBoxLayout()
        self.time_infos_layout_1.setContentsMargins(0,0,0,0)
        self.time_infos_layout_1.setSpacing(6)
        self.time_infos_layout.addLayout(self.time_infos_layout_1)

        self.work_time_icon_label = QtWidgets.QLabel()
        self.work_time_icon_label.setFixedSize(QtCore.QSize(22,22))
        self.work_time_icon_label.setPixmap(QtGui.QIcon(ressources._work_time_icon_).pixmap(22))
        self.time_infos_layout_1.addWidget(self.work_time_icon_label)

        self.work_time_label = QtWidgets.QLabel()
        self.work_time_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.time_infos_layout_1.addWidget(self.work_time_label)

        self.time_infos_layout_1.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.estimated_time_icon_label = QtWidgets.QLabel()
        self.estimated_time_icon_label.setFixedSize(QtCore.QSize(22,22))
        self.estimated_time_icon_label.setPixmap(QtGui.QIcon(ressources._estimated_time_icon_).pixmap(22))
        self.time_infos_layout_1.addWidget(self.estimated_time_icon_label)

        self.estimated_time_label = QtWidgets.QLabel()
        self.estimated_time_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.time_infos_layout_1.addWidget(self.estimated_time_label)

        self.edit_estimation_button = gui_utils.transparent_button(ressources._edit_transparent_icon_, ressources._edit_icon_)
        self.edit_estimation_button.setFixedSize(16,16)
        self.time_infos_layout_1.addWidget(self.edit_estimation_button)

        self.time_infos_layout_2 = QtWidgets.QHBoxLayout()
        self.time_infos_layout_2.setContentsMargins(0,0,0,0)
        self.time_infos_layout_2.setSpacing(6)
        self.time_infos_layout.addLayout(self.time_infos_layout_2)

        self.start_date_label = QtWidgets.QLabel()
        self.time_infos_layout_2.addWidget(self.start_date_label)

        self.date_arrow_label = QtWidgets.QLabel(">")
        self.date_arrow_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.date_arrow_label.setObjectName('gray_label')
        self.time_infos_layout_2.addWidget(self.date_arrow_label)

        self.due_date_label = QtWidgets.QLabel()
        self.time_infos_layout_2.addWidget(self.due_date_label)

        self.time_infos_layout_2.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.separation_widget_1 = QtWidgets.QWidget()
        self.separation_layout_1 = QtWidgets.QHBoxLayout()
        self.separation_layout_1.setContentsMargins(0,0,0,0)
        self.separation_layout_1.setSpacing(6)
        self.separation_widget_1.setLayout(self.separation_layout_1)
        self.main_layout.addWidget(self.separation_widget_1)

        self.note_label = QtWidgets.QLabel('Note')
        self.note_label.setObjectName("bold_label")
        self.separation_layout_1.addWidget(self.note_label)

        self.separation_layout_1.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.edit_note_button = QtWidgets.QPushButton('Edit note')
        self.edit_note_button.setMaximumHeight(24)
        self.edit_note_button.setStyleSheet('padding:3px;')
        self.separation_layout_1.addWidget(self.edit_note_button)

        self.note_content = gui_utils.minimum_height_textEdit()
        self.note_content.setReadOnly(True)
        self.note_content.setObjectName('gray_label')
        self.main_layout.addWidget(self.note_content)

        self.separation_widget_2 = QtWidgets.QWidget()
        self.separation_layout_2 = QtWidgets.QHBoxLayout()
        self.separation_layout_2.setContentsMargins(0,0,0,0)
        self.separation_layout_2.setSpacing(6)
        self.separation_widget_2.setLayout(self.separation_layout_2)
        self.main_layout.addWidget(self.separation_widget_2)

        self.asset_history_label = QtWidgets.QLabel('Asset history')
        self.asset_history_label.setObjectName("bold_label")
        self.separation_layout_2.addWidget(self.asset_history_label)

        self.separation_layout_2.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.add_comment_button = QtWidgets.QPushButton('Add comment')
        self.add_comment_button.setMaximumHeight(24)
        self.add_comment_button.setStyleSheet('padding:3px;')
        self.separation_layout_2.addWidget(self.add_comment_button)

        self.events_scrollArea = QtWidgets.QScrollArea()
        self.events_scrollArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
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
        self.events_content_layout.setSpacing(3)
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

    def change_stage(self, stage_id):
        self.stage_id = stage_id
        self.refresh()

    def refresh(self):
        #QtWidgets.QApplication.processEvents()
        start_time = time.perf_counter()
        if self.stage_id is not None:
            self.stage_row = project.get_stage_data(self.stage_id)
        else:
            self.stage_row = None
        self.refresh_tracking_events()
        self.refresh_state()
        self.refresh_priority()
        self.refresh_note()
        self.refresh_users_dic()
        self.refresh_user()
        self.refresh_time()
        self.update_refresh_time(start_time)

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.perf_counter()-start_time), 3))
        self.refresh_label.setText(f"refresh : {refresh_time}s")

    def refresh_time(self):
        if self.stage_id is not None:
            string_time = tools.convert_seconds_to_string_time(float(self.stage_row['work_time']))
            self.work_time_label.setText(string_time)
            if self.stage_row['estimated_time'] is not None:
                self.estimated_time_label.setText(f"{int(self.stage_row['estimated_time'])} days")
            start_date = datetime.datetime.fromtimestamp(float(self.stage_row['start_date'])).strftime("%d/%m/%Y")
            self.start_date_label.setText(start_date)
            due_time = float(self.stage_row['start_date'])+ int(self.stage_row['estimated_time'])*3600*24
            due_date = datetime.datetime.fromtimestamp(due_time).strftime("%d/%m/%Y")
            self.due_date_label.setText(f"{due_date}{" - " + tools.time_left_from_timestamp(due_time) if due_time > time.time() else ''}")
            if due_time > time.time():
                self.due_date_label.setStyleSheet("color:#7ca657")
            else:
                self.due_date_label.setStyleSheet("color:#d16666")

        else:
            self.work_time_label.setText('Work time')
            self.estimated_time_label.setText('Estimation time')

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
        if self.stage_id is not None:
            event_number = self.event_count_spinBox.value()
            tracking_event_rows = project.get_asset_tracking_events(self.stage_id)
            for tracking_event_row in tracking_event_rows[-event_number:]:
                project_tracking_events_ids.append(tracking_event_row['id'])
                if tracking_event_row['id'] not in self.tracking_event_ids.keys():
                    widget = tracking_event_widget(tracking_event_row)

                    if tracking_event_row['creation_time']-self.last_time > 350:
                        widget.add_time()
                    self.last_time = tracking_event_row['creation_time']

                    self.events_content_layout.addWidget(widget)
                    self.tracking_event_ids[tracking_event_row['id']] = widget

        tracking_event_ids = list(self.tracking_event_ids.keys())
        for event_id in tracking_event_ids:
            if event_id not in project_tracking_events_ids:
                self.remove_tracking_event(event_id)
        
        if self.stage_id is not None:
            self.remove_useless_events(event_number)

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
        if self.stage_row is not None:
            if self.stage_row['assignment'] is not None:
                self.assignment_comboBox.setCurrentText(self.stage_row['assignment'])
        self.apply_assignment_modification = 1

    def refresh_state(self):
        self.apply_state_modification = None
        if self.stage_row is not None:
            self.state_comboBox.setCurrentText(self.stage_row['state'])
        else:
            self.state_comboBox.setCurrentText('todo')
        self.apply_state_modification = 1

    def refresh_priority(self):
        self.apply_priority_modification = None
        if self.stage_row is not None:
            self.priority_comboBox.setCurrentText(self.stage_row['priority'])
        else:
            self.priority_comboBox.setCurrentText('normal')
        self.apply_priority_modification = 1

    def refresh_note(self):
        if self.stage_row is not None:
            if self.stage_row['note'] is None or self.stage_row['note'] == '':
                self.note_content.setText('Missing note')
                return
            self.note_content.setText(self.stage_row['note'])
        else:
            self.note_content.setText('')

    def modify_state(self, state):
        if self.stage_id is not None:
            if self.apply_state_modification:
                self.comment_widget = comment_widget.comment_widget()
                if self.comment_widget.exec_() == QtWidgets.QDialog.Accepted:
                    comment = self.comment_widget.comment
                    assets.modify_stage_state(self.stage_id, state, comment)
                    gui_server.refresh_team_ui()

    def modify_priority(self, priority):
        if self.stage_id is not None:
            if self.apply_priority_modification:
                assets.modify_stage_priority(self.stage_id, priority)
                gui_server.refresh_team_ui()

    def modify_assignment(self, user_name):
        if self.stage_id is not None:
            if self.apply_assignment_modification:
                assets.modify_stage_assignment(self.stage_id, user_name)
                gui_server.refresh_team_ui()

    def add_comment(self):
        if self.stage_id is not None:
            self.comment_widget = comment_widget.comment_widget()
            if self.comment_widget.exec_() == QtWidgets.QDialog.Accepted:
                comment = self.comment_widget.comment
                assets.add_stage_comment(self.stage_id, comment)
                gui_server.refresh_team_ui()

    def edit_note(self):
        if self.stage_id is not None:
            self.comment_widget = comment_widget.comment_widget(title='Edit note',
                                                                old_comment=self.stage_row['note'],
                                                                propose_tags=False,
                                                                button_text='Edit')
            if self.comment_widget.exec_() == QtWidgets.QDialog.Accepted:
                note = self.comment_widget.comment
                assets.edit_stage_note(self.stage_id, note)
                gui_server.refresh_team_ui()

    def change_count(self):
        self.clear_all_tracking_events()
        self.refresh_tracking_events()

    def connect_functions(self):
        self.state_comboBox.currentTextChanged.connect(self.modify_state)
        self.priority_comboBox.currentTextChanged.connect(self.modify_priority)
        self.assignment_comboBox.currentTextChanged.connect(self.modify_assignment)
        self.events_scrollBar.rangeChanged.connect(lambda: self.events_scrollBar.setValue(self.events_scrollBar.maximum()))
        self.event_count_spinBox.valueChanged.connect(self.change_count)
        self.edit_estimation_button.clicked.connect(self.edit_estimation)
        self.add_comment_button.clicked.connect(self.add_comment)
        self.edit_note_button.clicked.connect(self.edit_note)

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
        self.day_label = QtWidgets.QLabel(f"{tools.time_ago_from_timestamp(self.time_float)} - ")
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
        elif self.tracking_event_row['event_type'] == 'priority_switch':
            self.build_priority_switch_ui()
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
        self.main_layout.setContentsMargins(8,8,8,8)
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
        self.comment_label = tag_label.tag_label()
        self.comment_label.setText(self.tracking_event_row['comment'])
        #self.comment_label = QtWidgets.QLabel(self.tracking_event_row['comment'])
        #self.comment_label.setWordWrap(True)
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

        self.estimation_label = QtWidgets.QLabel(f"{self.tracking_event_row['data']} days")
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
        self.state_frame_layout.setContentsMargins(4,4,4,4)
        self.state_frame.setLayout(self.state_frame_layout)
        self.main_layout.addWidget(self.state_frame)

        color = ressources._states_colors_[self.tracking_event_row['data']]
        self.state_frame.setStyleSheet(f'background-color:{color};')
        
        self.state_label = QtWidgets.QLabel(self.tracking_event_row['data'].upper())
        self.state_label.setObjectName('bold_label')
        self.state_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.state_frame_layout.addWidget(self.state_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

    def build_priority_switch_ui(self):
        self.user_label = QtWidgets.QLabel(self.tracking_event_row['creation_user'])
        self.user_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout.addWidget(self.user_label)

        self.info_label = QtWidgets.QLabel('switched priority to')
        self.info_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.info_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.info_label)
        
        self.priority_label = QtWidgets.QLabel(self.tracking_event_row['data'].upper())
        self.priority_label.setObjectName('bold_label')
        self.priority_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout.addWidget(self.priority_label)

        self.priority_icon = QtWidgets.QLabel()
        self.priority_icon.setFixedSize(14,14)
        self.priority_icon.setPixmap(QtGui.QIcon(ressources._priority_icons_list_[self.tracking_event_row['data']]).pixmap(14))
        self.main_layout.addWidget(self.priority_icon)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

class estimation_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(estimation_widget, self).__init__(parent)
        self.hours = 6
        self.build_ui()
        self.connect_functions()
        
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def showEvent(self, event):
        corner = gui_utils.move_ui(self)

    def connect_functions(self):
        self.close_pushButton.clicked.connect(self.reject)
        self.enter_sc = QtWidgets.QShortcut(QtGui.QKeySequence('Return'), self)
        self.enter_sc.activated.connect(self.apply)

    def apply(self):
        self.days = self.days_spinBox.value()
        self.accept()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(8,8,8,8)
        self.setLayout(self.main_layout)
        self.main_frame = QtWidgets.QFrame()
        self.main_frame.setObjectName('instance_creation_frame')
        self.frame_layout = QtWidgets.QHBoxLayout()
        self.frame_layout.setSpacing(6)
        self.main_frame.setLayout(self.frame_layout)
        self.main_layout.addWidget(self.main_frame)

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(70)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 80))
        self.shadow.setXOffset(2)
        self.shadow.setYOffset(2)
        self.main_frame.setGraphicsEffect(self.shadow)

        self.days_spinBox = QtWidgets.QSpinBox()
        self.days_spinBox.setRange(1, 200)
        self.days_spinBox.setValue(6)
        self.days_spinBox.setButtonSymbols(2)
        self.frame_layout.addWidget(self.days_spinBox)

        self.days_label = QtWidgets.QLabel('days')
        self.frame_layout.addWidget(self.days_label)

        self.close_frame = QtWidgets.QFrame()
        self.close_layout = QtWidgets.QHBoxLayout()
        self.close_layout.setContentsMargins(2,2,2,2)
        self.close_layout.setSpacing(2)
        self.close_frame.setLayout(self.close_layout)
        self.close_pushButton = gui_utils.transparent_button(ressources._close_tranparent_icon_, ressources._close_icon_)
        self.close_pushButton.setFixedSize(16,16)
        self.close_pushButton.setIconSize(QtCore.QSize(12,12))
        self.close_layout.addWidget(self.close_pushButton)
        self.frame_layout.addWidget(self.close_frame)