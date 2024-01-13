import sys
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import os
os.environ["PATH"] = os.path.dirname(__file__) + os.pathsep + os.environ["PATH"]
import mpv
import subprocess
import tempfile
from wizard.core.video_player import ffmpeg_utils
from wizard.gui import app_utils

class VideoPlayer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.apply_seek = True

        self.container = QtWidgets.QWidget(self)
        self.container.setAttribute(QtCore.Qt.WA_DontCreateNativeAncestors)
        self.container.setAttribute(QtCore.Qt.WA_NativeWindow)
        self.player = mpv.MPV(wid=str(int(self.container.winId())))
        self.frame = 1

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.container)

        self.frame_label = QtWidgets.QLabel('', self)
        self.frame_label.move(100,100)
        self.frame_label.setMinimumWidth(1000)
        self.frame_label.setStyleSheet('color:red')
        #layout.addWidget(self.frame_label)

        self.pause_button = QtWidgets.QPushButton('Pause')
        self.pause_button.clicked.connect(self.play_pause_toggle)
        layout.addWidget(self.pause_button)

        self.next_button = QtWidgets.QPushButton('next frame')
        self.next_button.clicked.connect(self.next_frame)
        layout.addWidget(self.next_button)

        self.previous_button = QtWidgets.QPushButton('prev frame')
        self.previous_button.clicked.connect(self.previous_frame)
        layout.addWidget(self.previous_button)

        self.seek_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.seek_slider.setMinimum(0)
        self.seek_slider.setMaximum(1000)
        self.seek_slider.setValue(0)
        self.seek_slider.sliderMoved.connect(self.update_video_position)
        layout.addWidget(self.seek_slider)

        self.setLayout(layout)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Video Player')

        # Timer to update the current percent label
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_current_percent)
        self.timer.start(10)  # Update every 100 milliseconds

    def play_video(self, video_path):
        self.player.play(video_path)

    def update_current_percent(self):
        duration = self.player.duration
        if not duration:
            return
        if duration > 0:
            total_frames = duration*30
            current_position = self.player.time_pos / duration
            frame = round(current_position*total_frames)
            if frame == self.frame:
                return
            self.frame = frame
            self.frame_label.setText(f"frame : {self.frame}")
            self.apply_seek = False
            self.seek_slider.setValue(int(current_position*1000))
            self.apply_seek = True

    def play_pause_toggle(self):
        self.player.command('cycle', 'pause')

    def seek(self, frame):
        frame = 47
        t = (1/30)*frame
        self.player.seek(t, reference="absolute", precision="exact")

    def update_video_position(self, value):
        if not self.apply_seek:
            return
        duration = self.player.duration
        t =  duration * (value/1000)
        self.player.seek(t, reference="absolute", precision="exact")

    def next_frame(self):
        t = (1/30)
        self.player.seek(t, reference="relative", precision="exact")

    def previous_frame(self):
        t = -(1/30)
        self.player.seek(t, reference="relative", precision="exact")

if __name__ == '__main__':
    import locale
    locale.setlocale(locale.LC_NUMERIC, 'C')
    app = app_utils.get_app()
    player = VideoPlayer()
    temp_dir = 'temp'
    videos = ["video_1.mp4",
                "video_2.mp4",
                "video_3.mp4",
                "video_4.mp4",
                "video_5.mp4"]

    ffmpeg_utils.create_proxys(temp_dir, videos, 30)
    output_video_file = ffmpeg_utils.concatenate_videos(temp_dir, videos, 30)

    player.play_video(output_video_file)

    player.show()
    sys.exit(app.exec_())
