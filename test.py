import sys
from PyQt6 import QtWidgets, QtMultimedia, QtMultimediaWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal
import uuid
import ffmpeg
import os
os.environ['PATH'] += os.pathsep + "W:/SCRIPT/ffmpeg/bin"

def get_video_length(video_path):
    probe = ffmpeg.probe(video_path)
    duration = round(float(probe['format']['duration'])*1000)
    return duration

def get_video_fps(video_path):
    probe = ffmpeg.probe(video_path)
    video_stream = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
    frame_rate = video_stream['r_frame_rate']
    if '/' in frame_rate:
        numerator, denominator = map(int, frame_rate.split('/'))
        fps = numerator / denominator
    else:
        fps = float(frame_rate)
    return fps

class infos_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.build_ui()
        self.setObjectName('video_info_widget')
        self.setStyleSheet("#video_info_widget{background-color:transparent;}")

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        self.content_widget = QtWidgets.QWidget()
        self.content_widget.setObjectName('video_info_widget_content')
        self.content_widget.setStyleSheet("#video_info_widget_content{background-color:rgba(10,10,20,100);}")
        self.content_layout = QtWidgets.QHBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_widget)

        self.frame_label = QtWidgets.QLabel('')
        self.frame_label.setFixedWidth(50)
        self.content_layout.addWidget(self.frame_label)

        self.time_label = QtWidgets.QLabel('')
        self.time_label.setFixedWidth(50)
        self.content_layout.addWidget(self.time_label)

        self.fps_label = QtWidgets.QLabel('')
        self.fps_label.setFixedWidth(50)
        self.content_layout.addWidget(self.fps_label)

        self.content_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.current_video_label = QtWidgets.QLabel('')
        self.content_layout.addWidget(self.current_video_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding))

    def set_frame(self, frame):
        self.frame_label.setText(f"F{frame}")

    def set_time(self, position):
        self.time_label.setText(f"{round(position/1000, 2)}s")

    def set_fps(self, fps):
        self.fps_label.setText(f"{fps} Fps")

    def set_current_video(self, video):
        self.current_video_label.setText(f"{video}")

class video_output(QtWidgets.QWidget):
    def __init__(self, media_player, parent=None):
        super().__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        self.video_item = QtMultimediaWidgets.QGraphicsVideoItem()
        self.view = QtWidgets.QGraphicsView()
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.setBackgroundBrush(QtGui.QColor("black"))
        self.view.setScene(self.scene)
        self.scene.addItem(self.video_item)

        self.media_player = media_player
        self.media_player.setVideoOutput(self.video_item)

        self.main_layout.addWidget(self.view)

    def resizeEvent(self, event):
        rect = QtCore.QRectF(self.view.contentsRect())
        self.scene.setSceneRect(rect)
        self.video_item.setSize(rect.size())

class video_player(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.media_player = QtMultimedia.QMediaPlayer()
        self.video_output = video_output(self.media_player)
        self.timeline_widget = timeline_widget()

        self.videos_dic = dict()
        self.is_video_loaded = False
        self.next_index = 0
        self.frame = 0

        self.build_ui()
        self.connect_functions()

    def resizeEvent(self, event):
        self.infos_widget.resize(self.video_surface.size())
        super().resizeEvent(event)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.video_surface = QtWidgets.QWidget()
        self.video_surface.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.video_surface_layout = QtWidgets.QVBoxLayout()
        self.video_surface_layout.setContentsMargins(0,0,0,0)
        self.video_surface.setLayout(self.video_surface_layout)
        self.main_layout.addWidget(self.video_surface)
        self.video_surface_layout.addWidget(self.video_output)

        self.infos_widget = infos_widget(self.video_surface)

        self.play_button = QtWidgets.QPushButton('Play')
        self.main_layout.addWidget(self.play_button)

        self.main_layout.addWidget(self.timeline_widget)

    def connect_functions(self):
        self.play_button.clicked.connect(self.toggle_play_pause)
        self.media_player.positionChanged.connect(self.position_changed)
        self.timeline_widget.seek.connect(self.seek)

    def seek(self, frame):
        if self.media_player.duration() == 0:
            return
        fps = self.videos_dic[list(self.videos_dic.keys())[self.next_index-1]]["fps"]
        time = int(frame*fps)
        self.media_player.setPosition(time)

    def add_video(self, video):
        video_id = uuid.uuid4()
        self.videos_dic[video_id] = dict()
        self.videos_dic[video_id]["path"] = video
        self.videos_dic[video_id]["duration"] = get_video_length(video)
        self.videos_dic[video_id]["fps"] = get_video_fps(video)
        self.videos_dic[video_id]["total_frames"] = round(self.videos_dic[video_id]["duration"] / self.videos_dic[video_id]["fps"])

    def toggle_play_pause(self):
        if self.media_player.playbackState() == QtMultimedia.QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            if not self.is_video_loaded:
                self.load_next()
            self.media_player.play()

    def load_next(self):
        video_to_play = self.videos_dic[list(self.videos_dic.keys())[self.next_index]]["path"]
        fps = self.videos_dic[list(self.videos_dic.keys())[self.next_index]]["fps"]
        duration = self.videos_dic[list(self.videos_dic.keys())[self.next_index]]["duration"]
        total_frames = int(duration / fps)
        self.media_player.setSource(QtCore.QUrl.fromLocalFile(video_to_play))
        self.timeline_widget.set_range(0, total_frames)
        self.infos_widget.set_fps(fps)
        self.infos_widget.set_current_video(video_to_play)
        self.next_index += 1
        if self.next_index >= len(list(self.videos_dic.keys())):
            self.next_index = 0
        self.is_video_loaded = True

    def position_changed(self, position):
        if position >= self.media_player.duration():
            self.load_next()
            self.media_player.play()
        if self.media_player.duration() == 0:
            return
        fps = self.videos_dic[list(self.videos_dic.keys())[self.next_index-1]]["fps"]
        duration = self.videos_dic[list(self.videos_dic.keys())[self.next_index-1]]["duration"]
        total_frames = self.videos_dic[list(self.videos_dic.keys())[self.next_index-1]]["total_frames"]
        frame = int(position / fps)
        if frame == self.frame:
            return
        self.frame = frame
        self.timeline_widget.set_frame(frame)
        self.infos_widget.set_frame(frame)
        self.infos_widget.set_time(position)

class timeline_widget(QtWidgets.QWidget):

    seek = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.ignore_seek = False
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)

        self.slider = QtWidgets.QSlider()
        self.slider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)

        self.main_layout.addWidget(self.slider)

    def connect_functions(self):
        self.slider.valueChanged.connect(self.send_seek)

    def send_seek(self, value):
        if self.ignore_seek:
            return
        self.seek.emit(value)

    def set_frame(self, frame):
        self.ignore_seek = True
        self.slider.setValue(frame)
        self.ignore_seek = False

    def set_range(self, start, end):
        self.slider.setMinimum(start)
        self.slider.setMaximum(end)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    player = video_player()
    player.show()
    player.add_video("W:/SCRIPT/video_player/test_4.mp4")
    player.add_video("W:/SCRIPT/video_player/test_7.mp4")
    sys.exit(app.exec())
