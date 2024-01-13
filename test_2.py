import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QScrollBar
import os
import time

os.environ["PATH"] = os.path.dirname(__file__) + os.pathsep + os.environ["PATH"]
import mpv

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.dont_update_scroll = False
        
        self.scrollbar = QScrollBar()

        self.playlist = []  # List to store video files
        self.current_video_index = 0

        layout = QVBoxLayout()
        layout.addWidget(self.scrollbar)

        self.widget=QWidget(self)
        layout.addWidget(self.widget)

        self.player = mpv.MPV(wid=str(int(self.widget.winId())))

        # Buttons for controlling playlist
        self.prev_button = QPushButton('Previous', self)
        self.prev_button.clicked.connect(self.play_previous)
        layout.addWidget(self.prev_button)

        self.play_pause_button = QPushButton('Play', self)
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        layout.addWidget(self.play_pause_button)

        self.next_button = QPushButton('Next', self)
        self.next_button.clicked.connect(self.play_next)
        layout.addWidget(self.next_button)

        self.setLayout(layout)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Video Player')

        self.scrollbar.setMaximum(100)
        self.scrollbar.sliderMoved.connect(self.update_video_position)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_scrollbar)
        self.timer.start(20)  # Update every 200 milliseconds

        # Signal for video end
        self.player.observe_property('eof-reached', self.check_end_of_video)
        
        # Signal for video start
        #self.player.observe_property('time-pos', self.check_video_start)

        # Flag to track whether the next video is preloaded

    def update_scrollbar(self):
        if self.dont_update_scroll:
            return
        duration = self.player.duration
        if not duration:
            return
        if duration > 0:
            current_position = self.player.time_pos / duration * 100
            self.scrollbar.setValue(int(current_position))

    def update_video_position(self, value):
        if not self.player.pause:
            self.player.command('cycle', 'pause')  # Resume playback
        self.dont_update_scroll = True
        self.player.command('seek', value, 'absolute-percent')

    def play_video(self, file_path):
        self.player.play(file_path)

    def load_videos(self, paths):
        for path in paths:
            self.player.command('loadfile', path, 'append')

    def play_previous(self):
        self.current_video_index = (self.current_video_index - 1) % len(self.playlist)
        self.play_video(self.playlist[self.current_video_index])

    def play_next(self):
        self.current_video_index = (self.current_video_index + 1) % len(self.playlist)
        self.play_video(self.playlist[self.current_video_index])

    def toggle_play_pause(self):
        if self.player.pause:
            self.dont_update_scroll = False
            self.player.command('cycle', 'pause')  # Resume playback
            self.play_pause_button.setText('Pause')
        else:
            self.player.command('cycle', 'pause')  # Pause playback
            self.play_pause_button.setText('Play')

    def check_end_of_video(self, _, eof_reached):
        if eof_reached:
            self.play_next()

    def check_video_start(self, _, time_pos):
        # Check if the next video needs to be preloaded
        if not self.player.pause and self.preloaded_next_video:
            self.preloaded_next_video = False
            self.play_next()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    
    # Prompt user to select multiple videos
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.ExistingFiles)
    if file_dialog.exec_() == QFileDialog.Accepted:
        player.playlist = file_dialog.selectedFiles()
        player.load_videos(file_dialog.selectedFiles())
        time.sleep(2)
        player.play_video(player.playlist[player.current_video_index])

    player.show()
    sys.exit(app.exec_())
