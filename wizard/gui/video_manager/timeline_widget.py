# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import math
import logging

# Wizard modules
from wizard.core import tools
from wizard.core import project
from wizard.core import repository
from wizard.core import assets
from wizard.core import image
from wizard.vars import ressources
from wizard.vars import assets_vars

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server

logger = logging.getLogger(__name__)

class signal_manager(QtCore.QObject):

    on_seek = pyqtSignal(int)
    on_play_pause = pyqtSignal(int)
    on_next_frame = pyqtSignal(int)
    on_prev_frame = pyqtSignal(int)
    on_bounds_change = pyqtSignal(object)
    on_video_item_move = pyqtSignal(object)
    on_video_item_moved = pyqtSignal(object)
    on_video_item_scale = pyqtSignal(object)
    on_current = pyqtSignal(object)
    current_video_name = pyqtSignal(str)
    on_video_item_in_out_modified = pyqtSignal(object)
    on_video_item_double_clicked = pyqtSignal(object)
    on_videos_dropped = pyqtSignal(list)
    on_select = pyqtSignal(list)
    on_delete = pyqtSignal(list)
    current_stage = pyqtSignal(int)
    current_variant = pyqtSignal(int)
    current_video_row = pyqtSignal(object)
    is_last = pyqtSignal(object)
    replace_videos = pyqtSignal(object)
    clear_playlist = pyqtSignal(int)

    def __init__(self, parent=None):
        super(signal_manager, self).__init__(parent)

class timeline_widget(QtWidgets.QWidget):

    on_seek = pyqtSignal(int)
    on_play_pause = pyqtSignal(int)
    on_next_frame = pyqtSignal(int)
    on_prev_frame = pyqtSignal(int)
    on_loop_toggle = pyqtSignal(int)
    on_bounds_change = pyqtSignal(list)
    on_end_requested = pyqtSignal(int)
    on_beginning_requested = pyqtSignal(int)
    on_order_changed = pyqtSignal(list)
    on_video_in_out_modified = pyqtSignal(dict)
    on_videos_dropped = pyqtSignal(list)
    on_delete = pyqtSignal(list)
    current_stage = pyqtSignal(int)
    current_variant = pyqtSignal(int)
    current_video_row = pyqtSignal(object)
    replace_videos = pyqtSignal(object)
    clear_playlist = pyqtSignal(int)

    def __init__(self, parent=None):
        super(timeline_widget, self).__init__(parent)
        self.timeline_viewport = timeline_viewport()
        self.playing_infos_widget = playing_infos_widget()
        self.videos_dic = dict()
        self.frame_range = [0,1000]
        self.bounds_range = [0,1000]
        self.fps = 24
        self.build_ui()
        self.connect_functions()
        self.set_frame(0)

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.setObjectName("main_widget")
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(1)
        self.main_layout.addWidget(self.playing_infos_widget)
        self.main_layout.addWidget(self.timeline_viewport)
        self.setLayout(self.main_layout)

    def refresh(self):
        self.timeline_viewport.refresh()

    def update_videos_dic(self, videos_dic):
        self.videos_dic = videos_dic
        self.timeline_viewport.update_videos_dic(self.videos_dic)

    def set_play_pause(self, playing):
        self.playing_infos_widget.set_play_pause(playing)

    def set_fps(self, fps=24):
        self.fps = fps
        self.timeline_viewport.set_fps(fps)
        self.playing_infos_widget.set_fps(fps)

    def set_resolution(self, resolution=[1920, 1080]):
        self.playing_infos_widget.set_resolution(resolution)

    def set_frame_range(self, frame_range):
        old_frame_range = self.frame_range
        self.frame_range = [int(frame_range[0]), int(frame_range[1])]
        self.timeline_viewport.set_frame_range(self.frame_range)
        self.playing_infos_widget.set_frame_range(self.frame_range)
        if old_frame_range == self.bounds_range:
            self.set_bounds_range(self.frame_range)
        else:
            self.update_bound_range()

    def update_bound_range(self):
        if self.bounds_range[0] < self.frame_range[0]:
            self.bounds_range[0] = int(self.frame_range[0])
        if self.bounds_range[1] > self.frame_range[1]:
            self.bounds_range[1] = int(self.frame_range[1])
        self.timeline_viewport.set_bounds_range(self.bounds_range)
        self.playing_infos_widget.set_bounds_range(self.bounds_range)
        self.on_bounds_change.emit(self.bounds_range)
        self.update()

    def replace_current_video(self, project_video_id):
        self.timeline_viewport.replace_current_video(project_video_id)

    def set_bounds_range(self, bounds_range):
        self.bounds_range = bounds_range
        self.update_bound_range()

    def bounds_changed(self, bounds_range):
        self.set_bounds_range(bounds_range)

    def set_frame(self, frame):
        self.timeline_viewport.set_frame(frame)
        self.playing_infos_widget.set_frame(frame)

    def connect_functions(self):
        self.timeline_viewport.signal_manager.on_seek.connect(self.on_seek.emit)
        self.timeline_viewport.signal_manager.on_play_pause.connect(self.on_play_pause.emit)
        self.timeline_viewport.signal_manager.on_next_frame.connect(self.on_next_frame.emit)
        self.timeline_viewport.signal_manager.on_prev_frame.connect(self.on_prev_frame.emit)
        self.timeline_viewport.signal_manager.on_bounds_change.connect(self.bounds_changed)
        self.timeline_viewport.signal_manager.on_video_item_moved.connect(self.on_order_changed.emit)
        self.timeline_viewport.signal_manager.on_video_item_in_out_modified.connect(self.on_video_in_out_modified.emit)
        self.timeline_viewport.signal_manager.current_video_name.connect(self.playing_infos_widget.update_current_video_name)
        self.timeline_viewport.signal_manager.on_videos_dropped.connect(self.on_videos_dropped.emit)
        self.timeline_viewport.signal_manager.on_delete.connect(self.on_delete.emit)
        self.timeline_viewport.signal_manager.current_stage.connect(self.current_stage.emit)
        self.timeline_viewport.signal_manager.current_variant.connect(self.current_variant.emit)
        self.timeline_viewport.signal_manager.current_video_row.connect(self.current_video_row.emit)
        self.timeline_viewport.signal_manager.current_video_row.connect(self.playing_infos_widget.update_current_video_row)
        self.timeline_viewport.signal_manager.is_last.connect(self.playing_infos_widget.update_is_last)
        self.timeline_viewport.signal_manager.replace_videos.connect(self.replace_videos.emit)
        self.timeline_viewport.signal_manager.clear_playlist.connect(self.clear_playlist.emit)

        self.playing_infos_widget.on_play_pause.connect(self.on_play_pause.emit)
        self.playing_infos_widget.on_loop_toggle.connect(self.on_loop_toggle.emit)
        self.playing_infos_widget.on_end_requested.connect(self.on_end_requested.emit)
        self.playing_infos_widget.on_beginning_requested.connect(self.on_beginning_requested.emit)
        self.playing_infos_widget.on_previous_video_requested.connect(self.timeline_viewport.jump_to_previous_video)
        self.playing_infos_widget.on_next_video_requested.connect(self.timeline_viewport.jump_to_next_video)

class playing_infos_widget(QtWidgets.QWidget):

    on_play_pause = pyqtSignal(int)
    on_loop_toggle = pyqtSignal(int)
    on_end_requested = pyqtSignal(int)
    on_beginning_requested = pyqtSignal(int)
    on_previous_video_requested = pyqtSignal(int)
    on_next_video_requested = pyqtSignal(int)

    def __init__(self, parent=None):
        super(playing_infos_widget, self).__init__(parent)
        self.frame_range = [0,1000]
        self.fps = 24
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(1)
        self.setLayout(self.main_layout)

        self.video_infos_widget = QtWidgets.QWidget()
        self.video_infos_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.video_infos_layout = QtWidgets.QHBoxLayout()
        self.video_infos_layout.setContentsMargins(6,6,6,6)
        self.video_infos_widget.setLayout(self.video_infos_layout)
        self.main_layout.addWidget(self.video_infos_widget)

        self.video_name_label = QtWidgets.QLabel('')
        self.video_name_label.setObjectName('bold_label')
        self.video_infos_layout.addWidget(self.video_name_label)

        self.video_version_label = QtWidgets.QLabel()
        self.video_infos_layout.addWidget(self.video_version_label)

        self.video_user_label = QtWidgets.QLabel()
        self.video_user_label.setObjectName('gray_label')
        self.video_infos_layout.addWidget(self.video_user_label)

        self.video_date_label = QtWidgets.QLabel()
        self.video_date_label.setObjectName('gray_label')
        self.video_infos_layout.addWidget(self.video_date_label)

        self.video_infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.content_1_layout = QtWidgets.QHBoxLayout()
        self.content_1_layout.setContentsMargins(6,6,6,6)
        self.main_layout.addLayout(self.content_1_layout)

        self.beginning_button = gui_utils.transparent_button(ressources._player_beginning_icon_, ressources._player_beginning_icon_hover_)
        self.beginning_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.beginning_button.setFixedSize(QtCore.QSize(20,20))
        self.content_1_layout.addWidget(self.beginning_button)

        self.previous_button = gui_utils.transparent_button(ressources._player_previous_icon_, ressources._player_previous_icon_hover_)
        self.previous_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.previous_button.setFixedSize(QtCore.QSize(20,20))
        self.content_1_layout.addWidget(self.previous_button)

        self.play_pause_button = gui_utils.transparent_button(ressources._player_play_icon_, ressources._player_play_icon_hover_)
        self.play_pause_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.play_pause_button.setFixedSize(QtCore.QSize(20,20))
        self.content_1_layout.addWidget(self.play_pause_button)

        self.next_button = gui_utils.transparent_button(ressources._player_next_icon_, ressources._player_next_icon_hover_)
        self.next_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.next_button.setFixedSize(QtCore.QSize(20,20))
        self.content_1_layout.addWidget(self.next_button)

        self.end_button = gui_utils.transparent_button(ressources._player_end_icon_, ressources._player_end_icon_hover_)
        self.end_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.end_button.setFixedSize(QtCore.QSize(20,20))
        self.content_1_layout.addWidget(self.end_button)

        self.loop_button = gui_utils.transparent_button(ressources._player_loop_icon_,
                                                        ressources._player_loop_icon_hover_,
                                                        checked_icon=ressources._player_loop_icon_checked_)
        self.loop_button.setCheckable(True)
        self.loop_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.loop_button.setFixedSize(QtCore.QSize(20,20))
        self.content_1_layout.addWidget(self.loop_button)

        self.content_1_layout.addSpacerItem(QtWidgets.QSpacerItem(12,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        self.time_label = QtWidgets.QLabel('00:00:00:00')
        self.content_1_layout.addWidget(self.time_label)

        self.total_time_label = QtWidgets.QLabel('| 00:00:00:00')
        self.total_time_label.setObjectName('gray_label')
        self.content_1_layout.addWidget(self.total_time_label)

        self.content_1_layout.addSpacerItem(QtWidgets.QSpacerItem(12,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        self.fps_label = QtWidgets.QLabel()
        self.content_1_layout.addWidget(self.fps_label)

        self.content_1_layout.addSpacerItem(QtWidgets.QSpacerItem(12,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        self.resolution_label = QtWidgets.QLabel()
        self.content_1_layout.addWidget(self.resolution_label)

        self.content_1_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

    def connect_functions(self):
        self.play_pause_button.clicked.connect(self.on_play_pause.emit)
        self.loop_button.toggled.connect(self.on_loop_toggle.emit)
        self.end_button.clicked.connect(self.on_end_requested.emit)
        self.beginning_button.clicked.connect(self.on_beginning_requested.emit)
        self.previous_button.clicked.connect(self.on_previous_video_requested.emit)
        self.next_button.clicked.connect(self.on_next_video_requested.emit)

    def set_play_pause(self, playing):
        if playing:
            self.play_pause_button.icon = ressources._player_pause_icon_
            self.play_pause_button.hover_icon = ressources._player_pause_icon_hover_
            self.play_pause_button.update_icon()
        else:
            self.play_pause_button.icon = ressources._player_play_icon_
            self.play_pause_button.hover_icon = ressources._player_play_icon_hover_
            self.play_pause_button.update_icon()

    def set_frame_range(self, frame_range):
        self.frame_range = frame_range
        total_time = (frame_range[1]-frame_range[0]+1)/self.fps
        hours, minutes, seconds, miliseconds = tools.convert_seconds_with_miliseconds(total_time)
        self.total_time_label.setText(f"| {str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}:{str(miliseconds).zfill(2)}")

    def set_bounds_range(self, bounds_range):
        self.bounds_range = bounds_range

    def set_frame(self, frame):
        time_s = frame/self.fps
        hours, minutes, seconds, miliseconds = tools.convert_seconds_with_miliseconds(time_s)
        self.time_label.setText(f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}:{str(miliseconds).zfill(2)}")

    def set_fps(self, fps):
        self.fps = fps
        self.fps_label.setText(f"{fps} fps")

    def set_resolution(self, resolution):
        self.resolution_label.setText(f"{resolution[0]}x{resolution[1]}")

    def update_current_video_name(self, video_name):
        self.video_name_label.setText(video_name)

    def update_current_video_row(self, video_row):
        if video_row is None:
            self.video_version_label.setText('')
            self.video_user_label.setText('')
            self.video_date_label.setText('')
            return
        self.video_version_label.setText(video_row['name'])
        self.video_user_label.setText(video_row['creation_user'])
        self.video_date_label.setText(tools.time_ago_from_timestamp(video_row['creation_time']))

    def update_is_last(self, is_last):
        if is_last:
            self.video_version_label.setStyleSheet("color:#b3f07d")
        else:
            self.video_version_label.setStyleSheet("color:#ffae4f")

class timeline_viewport(QtWidgets.QGraphicsView):

    def __init__(self):
        super(timeline_viewport, self).__init__()
        self.setAcceptDrops(True)
        self.setFixedHeight(80)
        self.timeline_scene = timeline_scene()
        self.signal_manager = signal_manager()
        self.setScene(self.timeline_scene)
        self.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.pan = False
        self.move_cursor = False
        self.last_mouse_pos = None
        self.frame_width = 2
        self.frame_range = [0,1000]
        self.videos_dic = dict()
        self.moving_items = []

        self.fps = 24

        empty_item = custom_graphic_item()
        self.timeline_scene.addItem(empty_item)
        self.cursor_item = cursor_item()
        self.timeline_scene.addItem(self.cursor_item)
        self.in_bound_item = bound_item()
        self.in_bound_item.set_type('in')
        self.timeline_scene.addItem(self.in_bound_item)
        self.out_bound_item = bound_item()
        self.out_bound_item.set_type('out')
        self.timeline_scene.addItem(self.out_bound_item)
        self.insert_item = insert_item()
        self.timeline_scene.addItem(self.insert_item)
        self.insert_item.setVisible(False)

        self.last_video_id = None

        self.init_users_images()

        self.connect_functions()

    def init_users_images(self):
        self.users_images_dic = dict()
        for user_row in repository.get_users_list():
            user_image =  user_row['profile_picture']
            pixmap = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_image), 'png', 20, 8)
            self.users_images_dic[user_row['user_name']] = pixmap

    def dragEnterEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        pass

    def dropEvent(self, event):
        data = event.mimeData()
        urls = data.urls()

        paths = []
        for url in urls:
            if url and url.scheme() == 'file':
                path = str(url.path())[1:]
                paths.append(path)
        self.signal_manager.on_videos_dropped.emit(paths)

    def update_selection(self, video_items):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if not modifiers & QtCore.Qt.ShiftModifier:
            self.deselect_all()
        for video_item in video_items:
            video_item.set_selected(True)
        self.selection_changed()

    def get_selected_items(self):
        selected_items = []
        for video_id in self.videos_dic.keys():
            if self.videos_dic[video_id].selected:
                selected_items.append(self.videos_dic[video_id])
        return selected_items

    def selection_changed(self):
        self.update()

    def deselect_all(self):
        for video_id in self.videos_dic.keys():
            self.videos_dic[video_id].set_selected(False)
        self.update()

    def jump_to_previous_video(self):
        videos_list = list(self.videos_dic.keys())
        for video_id in videos_list:
            index = videos_list.index(video_id)
            if self.videos_dic[video_id].is_current():
                destination_index = index - 1
                break
        if destination_index < 0:
            destination_index = len(videos_list) - 1
        video_id = videos_list[destination_index]
        while self.videos_dic[video_id].start_frame > self.bounds_range[-1]:
            destination_index -= 1
            video_id = videos_list[destination_index]
            if self.videos_dic[video_id].start_frame < self.bounds_range[0]:
                destination_index = len(videos_list) - 1
                video_id = videos_list[destination_index]
        self.signal_manager.on_seek.emit(self.videos_dic[video_id].start_frame)

    def jump_to_next_video(self):
        videos_list = list(self.videos_dic.keys())
        for video_id in videos_list:
            index = videos_list.index(video_id)
            if self.videos_dic[video_id].is_current():
                destination_index = index + 1
                break
        if destination_index > len(videos_list) - 1:
            destination_index = 0
        video_id = videos_list[destination_index]
        while self.videos_dic[video_id].start_frame < self.bounds_range[0]:
            destination_index += 1
            video_id = videos_list[destination_index]
            if self.videos_dic[video_id].start_frame > self.bounds_range[-1]:
                destination_index = 0
                video_id = videos_list[destination_index]
        self.signal_manager.on_seek.emit(self.videos_dic[video_id].start_frame)

    def connect_functions(self):
        self.cursor_item.signal_manager.on_seek.connect(self.signal_manager.on_seek.emit)
        self.in_bound_item.signal_manager.on_bounds_change.connect(self.bounds_changed)
        self.out_bound_item.signal_manager.on_bounds_change.connect(self.bounds_changed)

    def update_videos_dic(self, videos_dic):
        for video_id in videos_dic.keys():
            if video_id not in self.videos_dic.keys():
                self.videos_dic[video_id] = video_item(videos_dic[video_id]['name'], video_id, videos_dic[video_id]['frames_count'], self.users_images_dic)
                self.timeline_scene.addItem(self.videos_dic[video_id])
                self.videos_dic[video_id].signal_manager.on_video_item_moved.connect(self.video_items_moved)
                self.videos_dic[video_id].signal_manager.on_video_item_move.connect(self.video_item_is_moving)
                self.videos_dic[video_id].signal_manager.on_video_item_in_out_modified.connect(self.video_item_in_out_modified)
                self.videos_dic[video_id].signal_manager.on_video_item_double_clicked.connect(self.video_item_double_clicked)
                self.videos_dic[video_id].signal_manager.on_video_item_double_clicked.connect(self.video_item_double_clicked)
                self.videos_dic[video_id].signal_manager.on_select.connect(self.update_selection)
                self.videos_dic[video_id].signal_manager.on_current.connect(self.current_playing_item)
            self.videos_dic[video_id].set_frame_width(self.frame_width)
            self.videos_dic[video_id].set_frames_count(videos_dic[video_id]['frames_count'])
            self.videos_dic[video_id].set_in_frame((videos_dic[video_id]['inpoint']))
            self.videos_dic[video_id].set_out_frame((videos_dic[video_id]['outpoint']))
            self.videos_dic[video_id].set_thumbnail(videos_dic[video_id]['thumbnail'])
            self.videos_dic[video_id].set_loaded(videos_dic[video_id]['proxy'])
            self.videos_dic[video_id].name = videos_dic[video_id]['name']
            self.videos_dic[video_id].project_video_id = videos_dic[video_id]['project_video_id']
        existing_video_ids = list(self.videos_dic.keys())
        for video_id in existing_video_ids:
            if video_id not in videos_dic.keys():
                self.remove_video(video_id)
        self.videos_dic = dict(sorted(self.videos_dic.items(), key=lambda x: list(videos_dic.keys()).index(x[0])))
        self.reorganise_items()
        self.refresh()

    def refresh(self):
        stage_rows = project.get_all_stages()
        stages = dict()
        for stage_row in stage_rows:
            stages[stage_row['id']] = stage_row
        variant_rows = project.get_all_variants()
        variants = dict()
        for variant_row in variant_rows:
            variants[variant_row['id']] = variant_row
        video_rows = project.get_all_videos()
        videos = dict()
        variant_videos = dict()
        for video_row in video_rows:
            videos[video_row['id']] = video_row
            if video_row['variant_id'] not in variant_videos.keys():
                variant_videos[video_row['variant_id']] = video_row['id']
            if video_row['id'] > variant_videos[video_row['variant_id']]:
                variant_videos[video_row['variant_id']] = video_row['id']

        for video_id in self.videos_dic.keys():
            video_item = self.videos_dic[video_id]
            if video_item.project_video_id:
                video_row = videos[video_item.project_video_id]
                video_item.set_video_row(video_row)
                variant_row = variants[video_row['variant_id']]
                video_item.set_variant_row(variant_row)
                stage_row = stages[variant_row['stage_id']]
                video_item.set_stage_row(stage_row)
                last_variant_video_id = variant_videos[video_row['variant_id']]
                video_item.set_is_last(video_row['id'] == last_variant_video_id)
            if video_item.is_current():
                self.current_playing_item(video_item, force=True)
        self.update()

    def show_context_menu(self):
        selection = self.get_selected_items()
        menu = gui_utils.QMenu(self)
        
        update_selection_action = None
        remove_selection_action = None

        if len(selection) > 0:
            update_selection_action = menu.addAction(QtGui.QIcon(ressources._tool_update_), 'Update selected')
            remove_selection_action = menu.addAction(QtGui.QIcon(ressources._tool_archive_), 'Remove selected')

        update_all_action = menu.addAction(QtGui.QIcon(ressources._tool_update_), 'Update all')
        clear_playlist_action = menu.addAction(QtGui.QIcon(ressources._tool_archive_), 'Clear playlist')

        states_submenu = menu.addMenu("State ")
        states_actions = dict()

        for state in assets_vars._asset_states_list_:
            states_actions[state] = states_submenu.addAction(QtGui.QIcon(ressources._states_icons_[state]), state)
        assignments_submenu = menu.addMenu("Assignment ")
        assignments_actions = dict()
        users_ids = project.get_users_ids_list()
        for user_id in users_ids:
            user_row = repository.get_user_data(user_id)
            icon = QtGui.QIcon()
            pm = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_row['profile_picture']), 'png', 24)
            icon.addPixmap(pm)
            assignments_actions[user_id] = assignments_submenu.addAction(icon, user_row['user_name'])
        priorities_submenu = menu.addMenu("Priority ")
        priorities_actions = dict()
        for priority in assets_vars._priority_list_:
            priorities_actions[priority] = priorities_submenu.addAction(QtGui.QIcon(ressources._priority_icons_list_[priority]), priority)

        action = menu.exec_(QtGui.QCursor().pos())
        if action is not None:
            if action in states_actions.values():
                self.modify_state_on_selected(action.text())
            elif action in assignments_actions.values():
                self.modify_assignment_on_selected(action.text())
            elif action in priorities_actions.values():
                self.modify_priority_on_selected(action.text())
            elif action == update_selection_action:
                self.update_selected_items_versions()
            elif action == remove_selection_action:
                self.delete_selection()
            elif action == update_all_action:
                self.update_all()
            elif action == clear_playlist_action:
                self.clear_playlist()

    def update_selected_items_versions(self):
        selected_items = self.get_selected_items()
        video_ids = []
        for item in selected_items:
            video_ids.append(item.video_id)
        self.update_videos_version(video_ids)

    def update_all(self):
        video_ids = []
        for video_id in self.videos_dic.keys():
            video_ids.append(video_id)
        self.update_videos_version(video_ids)

    def clear_playlist(self):
        self.signal_manager.clear_playlist.emit(1)

    def update_videos_version(self, video_ids):
        tuples_list = []
        for video_id in video_ids:
            variant_id = self.videos_dic[video_id].video_row['variant_id']
            last_video_row = project.get_videos(variant_id)
            if not last_video_row:
                continue
            last_video_row = last_video_row[-1]
            tuples_list.append((video_id, last_video_row['file_path'], last_video_row['id']))
        self.signal_manager.replace_videos.emit(tuples_list)

    def modify_state_on_selected(self, state):
        selected_items = self.get_selected_items()
        for item in selected_items:
            stage_id = item.stage_row['id']
            if item.stage_row['state'] == state:
                continue
            assets.modify_stage_state(stage_id, state)
        gui_server.refresh_team_ui()

    def modify_assignment_on_selected(self, user_name):
        selected_items = self.get_selected_items()
        for item in selected_items:
            stage_id = item.stage_row['id']
            if item.stage_row['assignment'] == user_name:
                continue
            assets.modify_stage_assignment(stage_id, user_name)
        gui_server.refresh_team_ui()

    def modify_priority_on_selected(self, priority):
        selected_items = self.get_selected_items()
        for item in selected_items:
            stage_id = item.stage_row['id']
            if item.stage_row['priority'] == priority:
                continue
            assets.modify_stage_priority(stage_id, priority)
        gui_server.refresh_team_ui()

    def current_playing_item(self, item, force=False):
        if item.stage_row:
            self.signal_manager.current_video_name.emit(item.variant_row['string'])
            video_id = item.video_row['id']
        else:
            self.signal_manager.current_video_name.emit(item.video_name)
            video_id = None
            return
        if self.last_video_id != video_id or force:
            self.signal_manager.is_last.emit(item.is_last)
            self.signal_manager.current_stage.emit(item.stage_row['id'])
            self.signal_manager.current_variant.emit(item.variant_row['id'])
            self.signal_manager.current_video_row.emit(item.video_row)
            self.last_video_id = video_id

    def get_current_video_id(self):
        for video_id in self.videos_dic.keys():
            if self.videos_dic[video_id].is_current():
                return video_id
        return None

    def replace_current_video(self, project_video_id):
        current_video_id = self.get_current_video_id()
        if not current_video_id:
            logger.error("No current video found")
            return
        video_path = project.get_video_data(project_video_id, 'file_path')
        self.signal_manager.replace_videos.emit([(current_video_id, video_path, project_video_id)])

    def remove_video(self, video_id):
        if video_id in self.videos_dic.keys():
            self.timeline_scene.removeItem(self.videos_dic[video_id])
            del self.videos_dic[video_id]

    def reorganise_items(self):
        start_frame = 0
        for video_id in self.videos_dic.keys():
            if self.videos_dic[video_id] in self.moving_items:
                continue
            self.videos_dic[video_id].set_start_frame(start_frame)
            self.videos_dic[video_id].update()
            start_frame += self.videos_dic[video_id].get_frames_count()

    def video_item_double_clicked(self, video_item):
        in_bound = video_item.start_frame
        out_bound = video_item.start_frame + video_item.get_frames_count() - 1
        self.signal_manager.on_bounds_change.emit([in_bound, out_bound])
        self.signal_manager.on_seek.emit(in_bound)

    def video_items_moved(self):
        self.insert_item.setVisible(False)
        start_frames = []
        ordered_ids = []
        for video_id in self.videos_dic.keys():
            if self.videos_dic[video_id] in self.moving_items:
                continue
            start_frames.append(self.videos_dic[video_id].start_frame)
            ordered_ids.append(video_id)
        start_frames.append(self.videos_dic[video_id].start_frame+self.videos_dic[video_id].get_frames_count())
        cursor_pos = self.mapToScene(self.mapFromGlobal(QtGui.QCursor().pos()))
        closest_frame = min(start_frames, key=lambda x: abs(x - int(cursor_pos.x()/self.frame_width)))
        selected_items = self.get_selected_items()
        moved_videos_ids = []
        for video_item in selected_items:
            moved_videos_ids.append(video_item.video_id)
            video_item.stop_moving()
        new_index = start_frames.index(closest_frame)
        for video_id in reversed(moved_videos_ids):
            ordered_ids.insert(new_index, video_id)
        self.moving_items = []
        self.videos_dic = dict(sorted(self.videos_dic.items(), key=lambda x: ordered_ids.index(x[0])))
        self.reorganise_items()
        self.signal_manager.on_video_item_moved.emit(ordered_ids)

    def video_item_is_moving(self, delta):
        selected_items = self.get_selected_items()
        self.moving_items = selected_items
        self.reorganise_items()
        posx = selected_items[0].pos().x()
        for video_item in self.get_selected_items():
            video_item.setPos(posx, 50)
            posx += video_item.get_frames_count() * self.frame_width
            video_item.move_item(delta)
        start_frames = []
        for video_id in self.videos_dic.keys():
            if self.videos_dic[video_id] in self.moving_items:
                continue
            start_frames.append(self.videos_dic[video_id].start_frame)
        start_frames.append(self.videos_dic[video_id].start_frame+self.videos_dic[video_id].get_frames_count())
        cursor_pos = self.mapToScene(self.mapFromGlobal(QtGui.QCursor().pos()))
        closest_frame = min(start_frames, key=lambda x: abs(x - int(cursor_pos.x()/self.frame_width)))
        self.insert_item.setVisible(True)
        self.insert_item.setPos(closest_frame*self.frame_width, self.insert_item.pos().y())

    def video_item_in_out_modified(self, video_item):
        self.reorganise_items()
        inpoint = video_item.in_frame
        outpoint = video_item.out_frame
        video_id = video_item.video_id
        modification_dic = dict()
        modification_dic['id'] = video_id
        modification_dic['inpoint'] = inpoint
        modification_dic['outpoint'] = outpoint
        self.signal_manager.on_video_item_in_out_modified.emit(modification_dic)

    def bounds_changed(self):
        in_frame = self.in_bound_item.get_frame()
        out_frame = self.out_bound_item.get_frame()
        bounds_range = [in_frame, out_frame]
        self.signal_manager.on_bounds_change.emit(bounds_range)

    def set_fps(self, fps):
        self.fps = fps
        self.timeline_scene.set_fps(fps)

    def set_frame_range(self, frame_range):
        self.frame_range = frame_range
        self.timeline_scene.set_frame_range(frame_range)
        self.cursor_item.set_frame_range(frame_range)
        self.in_bound_item.set_frame_range(frame_range)
        self.out_bound_item.set_frame_range(frame_range)

    def set_bounds_range(self, bounds_range):
        self.bounds_range = bounds_range
        self.timeline_scene.set_bounds_range(self.bounds_range)
        self.in_bound_item.set_bounds_range(self.bounds_range)
        self.out_bound_item.set_bounds_range(self.bounds_range)
        self.in_bound_item.set_frame(self.bounds_range[0])
        self.out_bound_item.set_frame(self.bounds_range[1])
        self.cursor_item.set_bounds_range(self.bounds_range)

    def set_frame_width(self, frame_width=2):
        self.frame_width = frame_width
        self.timeline_scene.set_frame_width(frame_width)
        self.cursor_item.set_frame_width(frame_width)
        self.in_bound_item.set_frame_width(frame_width)
        self.out_bound_item.set_frame_width(frame_width)
        for video_id in self.videos_dic.keys():
            self.videos_dic[video_id].set_frame_width(frame_width)

    def showEvent(self, event):
        self.init_scene()
        self.update()

    def init_scene(self):
        self.move_scene_center_to_left(force = True)
        self.cursor_item.set_frame(0)

    def set_frame(self, frame):
        self.cursor_item.set_frame(frame)
        for video_id in self.videos_dic.keys():
            self.videos_dic[video_id].set_frame(frame)
        self.update()

    def move_scene_center_to_left(self, force=False):
        delta_x = self.mapToScene(QtCore.QPoint(0,0)).x() + 20
        if (delta_x >= 0) and not force:
            return
        self.update_scene_rect(self.sceneRect().translated(-delta_x, 0))

    def resizeEvent(self, event):
        self.move_scene_center_to_left()

    def update_scene_rect(self, rect):
        self.setSceneRect(rect)
        self.update()

    def delete_selection(self):
        selected_items = self.get_selected_items()
        selected_ids = []
        for selected_item in selected_items:
            selected_ids.append(selected_item.video_id)
        self.signal_manager.on_delete.emit(selected_ids)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == QtCore.Qt.Key_Space:
            self.signal_manager.on_play_pause.emit(1)
        if event.key() == QtCore.Qt.Key_Left:
            self.signal_manager.on_prev_frame.emit(1)
        if event.key() == QtCore.Qt.Key_Right:
            self.signal_manager.on_next_frame.emit(1)
        if event.key() == QtCore.Qt.Key_Delete:
            self.delete_selection()

    def mousePressEvent(self, event):
        self.move_cursor = None
        super().mousePressEvent(event)
        if event.button() == QtCore.Qt.MiddleButton:
            self.pan = True
            self.last_mouse_pos = event.pos()

        if event.button() == QtCore.Qt.LeftButton:
            if self.timeline_scene.is_in_cursor_zone(self.mapToScene(event.pos())):
                self.cursor_item.move_item(self.mapToScene(event.pos()).x())
                self.move_cursor = True

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == QtCore.Qt.MiddleButton:
            self.pan = False
        if event.button() == QtCore.Qt.LeftButton:
            self.move_cursor = None
            self.move_video_item = None
        elif event.button() == QtCore.Qt.RightButton:
            self.show_context_menu()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.pan:
            delta = event.pos() - self.last_mouse_pos
            self.last_mouse_pos = event.pos()
            dx = -delta.x()
            point = self.mapToScene(QtCore.QPoint(0,0))
            self.update_scene_rect(self.sceneRect().translated(dx, 0))
            self.move_scene_center_to_left()
        if self.move_cursor:
            self.cursor_item.move_item(self.mapToScene(event.pos()).x())

    def wheelEvent(self, event):
        if event.modifiers() & QtCore.Qt.ShiftModifier:
            self.zoom_frame_width(event)

    def zoom_frame_width(self, event):
        delta = event.angleDelta().y() / 100
        if delta > 0:
            frame_width = self.frame_width*delta
        else:
            frame_width = self.frame_width/-delta
        frame_width = min(max(frame_width, 0.1), 30)
        mouse_view_pos = event.pos()
        mouse_scene_pos = self.mapToScene(mouse_view_pos).x() / self.frame_width
        self.set_frame_width(frame_width)
        new_mouse_scene_pos = self.mapToScene(mouse_view_pos).x() / self.frame_width
        diff = (new_mouse_scene_pos - mouse_scene_pos) * self.frame_width
        self.update_scene_rect(QtCore.QRectF(self.sceneRect().x() - diff,
                                        self.sceneRect().y(),
                                        self.sceneRect().width(),
                                        self.sceneRect().height()))
        self.move_scene_center_to_left()


class timeline_scene(QtWidgets.QGraphicsScene):
    def __init__(self):
        super(timeline_scene, self).__init__()
        self.frame_width = 2
        self.fps = 24
        self.frame_range = [0,1000]
        self.bounds_range = [0,1000]
        self.cache_scene_painting()

    def cache_scene_painting(self):
        self.color1 = QtGui.QColor(0,0,10,60)
        self.color2 = QtGui.QColor(245,245,255,10)

    def set_frame_width(self, frame_width):
        self.frame_width = frame_width
        self.update()

    def set_fps(self, fps=24):
        self.fps = fps

    def set_frame_range(self, frame_range):
        self.frame_range = frame_range
        self.update()

    def set_bounds_range(self, bounds_range):
        self.bounds_range = bounds_range
        self.update()

    def is_in_cursor_zone(self, pos):
        cursor_zone_rect = QtCore.QRectF(self.sceneRect().left(),10,self.sceneRect().width(),20)
        return cursor_zone_rect.contains(pos)

    def drawBackground(self, painter, rect):
        painter.fillRect(rect, self.color1)

        bounds_zone = QtCore.QRectF(rect.left(),0,rect.width(),10)
        painter.fillRect(bounds_zone, QtGui.QColor(0,0,10,10))

        bounds_rect = QtCore.QRectF(self.bounds_range[0]*self.frame_width,2,(self.bounds_range[1]-self.bounds_range[0])*self.frame_width,6)
        painter.fillRect(bounds_rect, QtGui.QColor(245,245,255,20))

        time_rect = QtCore.QRectF(rect.left(),10,rect.width(),20)
        painter.fillRect(time_rect, QtGui.QColor(0,0,10,10))

        frame_range_rect = QtCore.QRectF(self.frame_range[0]*self.frame_width,10,(self.frame_range[1]-self.frame_range[0]+1)*self.frame_width,20)
        painter.fillRect(frame_range_rect, QtGui.QColor(245,245,255,10))

        in_rect = QtCore.QRectF((self.frame_range[0]*self.frame_width),10,1,20)
        painter.fillRect(in_rect, QtGui.QColor(100,100,110,150))

        out_rect = QtCore.QRectF((self.frame_range[1]+1)*self.frame_width,10,1,20)
        painter.fillRect(out_rect, QtGui.QColor(100,100,110,150))

        start_x = 0
        end_x = int(rect.right() // self.frame_width)

        # Adjust frames display
        step = int(self.fps)
        if self.frame_width >= 4:
            step = int(self.fps/2)
        if self.frame_width >= 10:
            step = int(self.fps/4)
        if self.frame_width >= 15:
            step = int(self.fps/6)
        if self.frame_width >= 20:
            step = 1
        if self.frame_width <= 1:
            step = self.fps*2
        if self.frame_width <= 0.5:
            step = self.fps*6
        if self.frame_width <= 0.2:
            step = self.fps*8
        if self.frame_width <= 0.15:
            step = self.fps*12
        if self.frame_width <= 0.1:
            step = self.fps*18
        
        for x in range(start_x, end_x + 1, step):
            x_pos = int(x * self.frame_width)
            rect = QtCore.QRectF(x_pos-25+int(self.frame_width/2), 10, 50, 20)
            pen = QtGui.QPen(QtGui.QColor(255,255,255,int(255*0.2)), 1, QtCore.Qt.SolidLine)
            painter.setPen(pen)
            painter.drawText(rect, QtCore.Qt.AlignCenter | QtCore.Qt.AlignHCenter, str(x))
            pen = QtGui.QPen(QtGui.QColor(255,255,255,int(255*0.05)), 1, QtCore.Qt.SolidLine)
            painter.setPen(pen)
            painter.drawLine(x_pos, 30, x_pos, 80)

class custom_graphic_item(QtWidgets.QGraphicsItem):
    def __init__(self):
        super(custom_graphic_item, self).__init__()

        self.selected = False
        self.x = 0
        self.y = 0
        self.width = 1
        self.height = 1

    def set_selected(self, selection):
        self.selected = selection

    def toggle_selection(self):
        self.selected = 1-self.selected

    def setRect(self, x, y , width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def set_size(self, width, height):
        self.prepareGeometryChange()
        self.width = width
        self.height = height
        self.update()

    def setVisible(self, visible):
        if not visible:
            self.selected = False
        super().setVisible(visible)

    def boundingRect(self):
        return QtCore.QRectF(self.x, self.y, self.width, self.height)

    def paint(self, painter, option, widget):
        color = QtGui.QColor('transparent')
        pen = QtGui.QPen(QtGui.QColor('transparent'), 1, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(color)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(self.x, self.y, self.width, self.height)

class insert_item(custom_graphic_item):
    def __init__(self):
        super(insert_item, self).__init__()
        self.height = 50
        self.width = 2 
        self.setPos(self.pos().x(), 30)

    def paint(self, painter, option, widget):
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255,255,int(255*0.85))))
        painter.drawRoundedRect(option.rect, 1, 1)

class video_item(custom_graphic_item):
    def __init__(self, video_name, video_id, frames_count, users_images_dic):
        super(video_item, self).__init__()
        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.video_name = video_name
        self.thumbnail_path = None
        self.thumbnail_pixmap = None
        self.video_id = video_id
        self.start_crop_in = None
        self.start_crop_out = None
        self.start_move_pos = False
        self.frames_count = frames_count
        self.in_frame = 0
        self.out_frame = 1
        self.signal_manager = signal_manager()
        self.height = 50
        self.width = 0
        self.frame_width = 2
        self.loaded = False
        self.moved = False
        self.in_or_out_modified = False
        self.margin = 1
        self.frame = 0
        self.start_frame = 0
        self.video_frame_range = [0,1]
        self.scale_handle_width = 8
        self.hover_in_frame_handle = False
        self.hover_out_frame_handle = False
        self.setPos(self.pos().x(), 30)
        self.video_row = None
        self.variant_row = None
        self.stage_row = None
        self.is_last = True

        self.widget = video_item_widget(users_images_dic)
        self.widget.set_video_name(self.video_name)
        self.proxy_widget = QtWidgets.QGraphicsProxyWidget(self)
        self.proxy_widget.setWidget(self.widget)

    def set_is_last(self, is_last):
        self.is_last = is_last
        self.widget.set_is_last(is_last)

    def set_video_row(self, video_row):
        self.video_row = video_row

    def set_variant_row(self, variant_row):
        self.widget.set_video_name(variant_row['string'])
        self.variant_row = variant_row

    def set_stage_row(self, stage_row):
        self.widget.set_stage_row(stage_row)
        self.stage_row = stage_row

    def mousePressEvent(self, event):
        self.moved = False
        self.start_crop_in = None
        self.start_crop_out = None
        self.start_move_pos = False
        self.in_or_out_modified = False

        if event.button() == QtCore.Qt.LeftButton:
            if self.width < 20:
                self.start_move_pos = event.pos()
                return
            if event.pos().x() < self.scale_handle_width:
                self.start_crop_in = self.in_frame
                return
            if event.pos().x() > self.width - self.scale_handle_width:
                self.start_crop_out = event.pos()
                return
            self.start_move_pos = event.pos()
        if (not self.selected and event.button() == QtCore.Qt.LeftButton)\
                or (not self.selected and event.button() == QtCore.Qt.RightButton):
            self.signal_manager.on_select.emit([self])

    def mouseReleaseEvent(self, event):
        self.start_move_pos = None
        self.setZValue(1)

        if event.button() == QtCore.Qt.LeftButton:
            if self.moved:
                self.signal_manager.on_video_item_moved.emit(self)
            else:
                self.signal_manager.on_select.emit([self])
            if self.in_or_out_modified:
                self.signal_manager.on_video_item_in_out_modified.emit(self)
            self.start_crop_in = None
            self.start_crop_out = None
            self.update()

    def get_pos(self):
        return int(self.pos().x())

    def move_item(self, delta):
        self.setZValue(500)
        self.moveBy(delta, 0)
        self.moved = True

    def stop_moving(self):
        self.start_move_pos = None
        self.moved=False
        self.setPos(self.pos().x(), 30)
        self.setZValue(1)

    def mouseMoveEvent(self, event):
        if self.start_move_pos:
            delta = (event.pos().x() - self.start_move_pos.x())
            self.signal_manager.on_video_item_move.emit(delta)
        if self.start_crop_in is not None:
            self.setZValue(500)
            abs_frame = int(self.mapToScene(event.pos()).x()/self.frame_width)
            in_frame = int((abs_frame+(self.start_crop_in)) - self.start_frame)
            in_frame = min(max(0, in_frame), self.out_frame-1)
            self.setPos(int((in_frame-self.start_crop_in+self.start_frame)*self.frame_width), self.pos().y())
            self.set_in_frame(in_frame)
            self.in_or_out_modified = True
            self.signal_manager.on_select.emit([self])

        if self.start_crop_out:
            self.setZValue(500)
            abs_frame = self.mapToScene(event.pos()).x()/self.frame_width
            self.set_out_frame(int((abs_frame+self.in_frame) - self.start_frame))
            self.in_or_out_modified = True
            self.signal_manager.on_select.emit([self])

    def hoverLeaveEvent(self, event):
        self.hover_in_frame_handle = False
        self.hover_out_frame_handle = False
        self.update()

    def hoverMoveEvent(self, event):
        if self.width < 20:
            self.hover_in_frame_handle = False
            self.hover_out_frame_handle = False
            self.update()
            return
        if event.pos().x() < self.scale_handle_width:
            self.hover_in_frame_handle = True
        else:
            self.hover_in_frame_handle = False
        if event.pos().x() > self.width - self.scale_handle_width:
            self.hover_out_frame_handle = True
        else:
            self.hover_out_frame_handle = False
        self.update()

    def mouseDoubleClickEvent(self, event):
        self.signal_manager.on_video_item_double_clicked.emit(self)

    def contains(self, pos):
        return self.boundingRect().contains(self.mapFromScene(pos))

    def is_current(self):
        return self.frame in range(int(self.start_frame), int(self.start_frame+(self.out_frame-self.in_frame)))

    def set_frame(self, frame):
        self.frame = frame
        if self.is_current():
            self.signal_manager.on_current.emit(self)

    def set_in_frame(self, in_frame):
        self.in_frame = min(max(0, in_frame), self.out_frame-1)
        self.update_video_frame_range()
        self.update_width()

    def set_out_frame(self, out_frame):
        self.out_frame = max(self.in_frame+1, min(self.frames_count, out_frame))
        self.update_video_frame_range()
        self.update_width()

    def set_thumbnail(self, thumbnail_path):
        self.widget.set_thumbnail(thumbnail_path)

    def set_loaded(self, loaded):
        self.loaded = loaded
        self.update()

    def set_start_frame(self, start_frame):
        self.start_frame = int(start_frame)
        self.update_video_frame_range()
        self.update_pos()
        self.update()

    def update_video_frame_range(self):
        self.video_frame_range = [int(self.start_frame), int(self.out_frame-self.in_frame)]

    def set_frame_width(self, frame_width):
        self.frame_width = frame_width
        self.update_width()
        self.update_pos()

    def set_frames_count(self, frames_count):
        self.frames_count = frames_count

    def update_width(self):
        self.prepareGeometryChange()
        self.width = int(self.out_frame-self.in_frame)*self.frame_width
        self.scene().update()

    def get_frames_count(self):
        return int(self.out_frame-self.in_frame)

    def set_frame_range(self, frame_range):
        self.frame_range = frame_range

    def update_pos(self):
        self.setPos((self.start_frame*self.frame_width), self.pos().y())
        self.update()
        self.scene().update()

    def paint(self, painter, option, widget):
        # Set up background color
        bg_color = QtGui.QColor(100,100,110,190)
        if not self.loaded:
            bg_color.setAlpha(70)
        if self.is_current() and self.loaded:
            bg_color.setAlpha(255)
        # Paint cropping effect
        pen = QtGui.QPen(QtGui.QColor(255,255,255,int(255*0.45)), 1, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        if self.start_crop_in is not None or self.start_crop_out is not None:
            shadow_rect = QtCore.QRectF(self.x-(self.in_frame*self.frame_width),
                                self.y+self.margin*4,
                                self.frames_count*self.frame_width,
                                self.height-self.margin*8)
            brush = QtGui.QBrush(QtGui.QColor(30,30,40,100))
            painter.setBrush(brush)
            painter.drawRoundedRect(shadow_rect, 2,2)
            bg_color.setAlpha(255)
        # Paint background
        brush = QtGui.QBrush(bg_color)
        painter.setBrush(brush)
        if not self.selected:
            pen = QtGui.QPen(QtGui.QColor(255,255,255,0), 1, QtCore.Qt.SolidLine)
        else:
            pen = QtGui.QPen(QtGui.QColor(255,255,255,int(255*0.85)), 1, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        bg_rect = QtCore.QRect(int(self.x),
                            int(self.y+self.margin*4),
                            int(self.width-self.margin),
                            int(self.height-self.margin*8))
        painter.drawRoundedRect(bg_rect, 2,2)
        # Draw crop handles
        pen = QtGui.QPen(QtGui.QColor(255,255,255,0), 1, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        if self.hover_in_frame_handle:
            handle_rect = QtCore.QRectF(bg_rect.x(),
                                        bg_rect.y(),
                                        int(self.scale_handle_width/2),
                                        bg_rect.height())
            brush = QtGui.QBrush(QtGui.QColor(255,255,255,int(255*0.85)))
            painter.setBrush(brush)
            painter.drawRoundedRect(handle_rect,
                                    int(self.scale_handle_width/4),
                                    int(self.scale_handle_width/4))
        if self.hover_out_frame_handle:
            handle_rect = QtCore.QRectF(bg_rect.width()-int(self.scale_handle_width/2),
                                        bg_rect.y(),
                                        int(self.scale_handle_width/2),
                                        bg_rect.height())
            brush = QtGui.QBrush(QtGui.QColor(255,255,255,int(255*0.85)))
            painter.setBrush(brush)
            painter.drawRoundedRect(handle_rect, int(self.scale_handle_width/4), int(self.scale_handle_width/4))
        self.widget.set_size(int(self.width), int(self.height))

class video_item_widget(QtWidgets.QWidget):
    def __init__(self, users_images_dic, parent=None):
        super(video_item_widget, self).__init__(parent)
        self.setObjectName('transparent_widget')
        self.users_images_dic = users_images_dic
        self.build_ui()

    def set_video_name(self, video_name):
        self.video_name_label.setText(video_name)

    def set_size(self, width, height):
        self.resize(int(width), int(height))

    def set_is_last(self, is_last):
        if is_last:
            self.thumbnail_label.setStyleSheet("")
        else:
            self.thumbnail_label.setStyleSheet("border:2px solid #f79360;border-radius:2px;")

    def set_stage_row(self, stage_row):
        self.state_label.setText(stage_row['state'])
        self.state_label.setStyleSheet("background-color:%s; padding:2px; border-radius:2px"%ressources._states_colors_[stage_row['state']])
        self.assignment_label.setPixmap(self.users_images_dic[stage_row['assignment']])
        self.priority_label.setPixmap(QtGui.QIcon(ressources._priority_icons_list_[stage_row['priority']]).pixmap(20))

    def set_thumbnail(self, thumbnail_path):
        thumbnail_pixmap = QtGui.QIcon(thumbnail_path).pixmap(120)
        #height = self.height()-16
        #width = int(thumbnail_pixmap.width() * (height / thumbnail_pixmap.height()))
        #thumbnail_pixmap = thumbnail_pixmap.scaled(width, height)
        self.thumbnail_label.setPixmap(thumbnail_pixmap)

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(3,6,3,6)
        self.main_layout.setSpacing(3)
        self.setLayout(self.main_layout)

        self.thumbnail_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.thumbnail_label)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_widget.setObjectName('transparent_widget')
        self.infos_layout = QtWidgets.QVBoxLayout()
        self.infos_layout.setContentsMargins(0,0,0,0)
        self.infos_layout.setSpacing(2)
        self.infos_widget.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_widget)

        self.video_name_label = QtWidgets.QLabel()
        self.video_name_label.setObjectName('bold_label')
        self.infos_layout.addWidget(self.video_name_label)

        self.tracking_layout = QtWidgets.QHBoxLayout()
        self.tracking_layout.setContentsMargins(0,0,0,0)
        self.tracking_layout.setSpacing(2)
        self.infos_layout.addLayout(self.tracking_layout)

        self.assignment_label = QtWidgets.QLabel()
        self.tracking_layout.addWidget(self.assignment_label)

        self.state_label = QtWidgets.QLabel()
        self.state_label.setObjectName('bold_label')
        self.tracking_layout.addWidget(self.state_label)

        self.priority_label = QtWidgets.QLabel()
        self.tracking_layout.addWidget(self.priority_label)

        self.tracking_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

class cursor_item(custom_graphic_item):
    def __init__(self):
        super(cursor_item, self).__init__()
        self.signal_manager = signal_manager()
        self.height = 70
        self.width = 40
        self.frame_width = 2
        self.frame = 0
        self.start_move_pos = None
        self.frame_range = [0,1000]
        self.bounds_range = [0,1000]
        self.setZValue(1000)
        self.setPos(self.pos().x(), 10)

    def set_frame(self, frame):
        self.frame = int(frame)
        self.update_pos()
        self.update()

    def set_frame_range(self, frame_range):
        self.frame_range = frame_range

    def set_bounds_range(self, bounds_range):
        self.bounds_range = bounds_range
        if self.frame < self.bounds_range[0]:
            self.set_frame(self.bounds_range[0])
            self.signal_manager.on_seek.emit(self.frame)
        if self.frame > self.bounds_range[1]:
            self.set_frame(self.bounds_range[1])
            self.signal_manager.on_seek.emit(self.frame)

    def update_pos(self):
        self.setPos((self.frame*self.frame_width)- int(self.width/2) + int(self.frame_width/2), self.pos().y())

    def update_frame(self):
        self.frame = int((self.pos().x() + self.width/2 - int(self.frame_width/2))/self.frame_width)
        self.update()

    def set_frame_width(self, frame_width):
        self.frame_width = frame_width
        self.update_pos()

    def get_pos(self):
        return int(self.pos().x() + self.width/2 + int(self.frame_width/2))

    def get_frame_from_pos(self, pos_x):
        return int(pos_x/self.frame_width)

    def move_item(self, pos_x):
        frame = self.get_frame_from_pos(pos_x)
        if frame > (self.bounds_range[1]):
            self.set_frame(self.bounds_range[1])
        elif frame < self.bounds_range[0]:
            self.set_frame(self.bounds_range[0])
        else:
            self.set_frame(frame)
            self.update_frame()
        self.signal_manager.on_seek.emit(self.frame)

    def paint(self, painter, option, widget):
        pen = QtGui.QPen(QtGui.QColor(255,100,100,200), max(self.frame_width, 2), QtCore.Qt.SolidLine)
        painter.setPen(pen)
        painter.drawLine(self.x+int(self.width/2), 20, self.x+int(self.width/2), self.height)
        frame_rect = QtCore.QRectF(self.x, 0, self.width, 20)
        pen = QtGui.QPen(QtGui.QColor(255,255,255,0), 1, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(QtGui.QColor(255,100,100,255))
        painter.setBrush(brush)
        painter.setPen(pen)
        painter.drawRoundedRect(frame_rect, 4, 4)
        pen = QtGui.QPen(QtGui.QColor(255,255,255,int(255*0.85)), 1, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        font = QtGui.QFont()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(frame_rect, QtCore.Qt.AlignCenter | QtCore.Qt.AlignHCenter, str(self.frame))

class bound_item(custom_graphic_item):
    def __init__(self):
        super(bound_item, self).__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setZValue(999)
        self.signal_manager = signal_manager()
        self.height = 8
        self.width = 8
        self.frame_width = 2
        self.frame = 0
        self.type = 'in'
        self.start_move_pos = None
        self.frame_range = [0,1000]
        self.bounds_range = [0,1000]
        self.setPos(self.pos().x(), 1)

    def set_type(self, bound_type):
        self.type = bound_type

    def set_frame(self, frame):
        self.frame = int(frame)
        self.update_pos()

    def get_frame(self):
        return self.frame

    def set_frame_range(self, frame_range):
        self.frame_range = frame_range

    def set_bounds_range(self, bounds_range):
        self.bounds_range = bounds_range

    def update_pos(self):
        self.setPos((self.frame)*self.frame_width - int(self.width/2) + int(self.frame_width/2), self.pos().y())

    def update_frame(self):
        self.frame = int((self.pos().x() + self.width/2 - int(self.frame_width/2))/self.frame_width)
        self.update()

    def set_frame_width(self, frame_width):
        self.frame_width = frame_width
        if self.frame_width >= 8:
            self.width = self.frame_width
        else:
            self.width = 8
        self.update_pos()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.start_move_pos = event.pos()

    def mouseReleaseEvent(self, event):
        self.start_move_pos = None

    def get_pos(self):
        return int(self.pos().x() + self.width/2 + int(self.frame_width/2))

    def mouseMoveEvent(self, event):
        if not self.start_move_pos:
            return
        delta = int((event.pos().x() - self.start_move_pos.x())/self.frame_width)*self.frame_width
        if self.type == 'in':
            if self.get_pos() + delta >= (self.bounds_range[1])*self.frame_width:
                self.set_frame(self.bounds_range[1]-1)
                self.signal_manager.on_bounds_change.emit(1)
                return

        if self.type == 'out':
            if self.get_pos() + delta <= (self.bounds_range[0]+1)*self.frame_width:
                self.set_frame(self.bounds_range[0]+1)
                self.signal_manager.on_bounds_change.emit(1)
                return

        if self.get_pos() + delta > (self.frame_range[1])*self.frame_width:
            self.set_frame(self.frame_range[1])
            self.signal_manager.on_bounds_change.emit(1)
            return

        if self.get_pos() + delta < self.frame_range[0]*self.frame_width:
            self.set_frame(self.frame_range[0])
            self.signal_manager.on_bounds_change.emit(1)
            return

        self.moveBy(delta, 0)
        self.update_frame()
        self.signal_manager.on_bounds_change.emit(1)

    def paint(self, painter, option, widget):
        brush = QtGui.QBrush(QtGui.QColor(255,100,100,255))
        pen = QtGui.QPen(QtGui.QColor(255,255,255,0), 1, QtCore.Qt.SolidLine)
        painter.setBrush(brush)
        painter.setPen(pen)
        painter.drawRoundedRect(QtCore.QRectF(0,0, self.width, self.height), 4, 4)
