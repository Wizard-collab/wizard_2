import sys
from PyQt6 import QtWidgets, QtMultimedia, QtMultimediaWidgets, QtCore
from PyQt6.QtCore import pyqtSignal
import uuid

class video_player(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(350, 100, 700, 500)

        self.media_player = QtMultimedia.QMediaPlayer()
        self.video_widget = QtMultimediaWidgets.QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        self.timeline_widget = timeline_widget()

        self.videos_dic = dict()
        self.is_video_loaded = False
        self.current_index = 0

        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.play_button = QtWidgets.QPushButton('Play')

        self.main_layout.addWidget(self.video_widget)
        self.main_layout.addWidget(self.play_button)
        self.main_layout.addWidget(self.timeline_widget)

    def connect_functions(self):
        self.play_button.clicked.connect(self.toggle_play_pause)
        self.media_player.positionChanged.connect(self.position_changed)
        self.timeline_widget.seek.connect(self.seek)

    def seek(self, progress):
        if self.media_player.duration() == 0:
            return
        time = int(self.media_player.duration() * progress/100)
        self.media_player.setPosition(time)

    def add_video(self, video):
        video_id = uuid.uuid4()
        self.videos_dic[video_id] = video

    def toggle_play_pause(self):
        if self.media_player.playbackState() == QtMultimedia.QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            if not self.is_video_loaded:
                self.load_next()
            self.media_player.play()

    def load_next(self):
        video_to_play = self.videos_dic[list(self.videos_dic.keys())[self.current_index]]
        self.media_player.setSource(QtCore.QUrl.fromLocalFile(video_to_play))
        self.current_index += 1
        if self.current_index >= len(list(self.videos_dic.keys())):
            self.current_index = 0
        self.is_video_loaded = True

    def position_changed(self, position):
        if position >= self.media_player.duration():
            self.load_next()
            self.media_player.play()
        if self.media_player.duration() == 0:
            return
        progress = int(position/self.media_player.duration()*100)
        self.timeline_widget.update_position(progress)

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

    def update_position(self, progress):
        self.ignore_seek = True
        self.slider.setValue(progress)
        self.ignore_seek = False

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    player = video_player()
    player.show()
    player.add_video("W:/SCRIPT/video_player/test.mp4")
    player.add_video("W:/SCRIPT/video_player/test_3.mp4")
    sys.exit(app.exec())
