import cv2
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import sys
import traceback
import time
import logging

logger = logging.getLogger(__name__)

class VideoPlayer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.infos_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.infos_label)

        self.video_widget = QtWidgets.QWidget()
        self.video_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.video_widget.setStyleSheet("background-color:black;")
        self.video_label = QtWidgets.QLabel(self.video_widget)
        self.video_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.video_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.main_layout.addWidget(self.video_widget)

        self.fps_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.fps_label)

        self.play_button = QtWidgets.QPushButton("Play")
        self.main_layout.addWidget(self.play_button)

        self.video_stream = video_stream()
        self.connect_functions()

    def resizeEvent(self, event):
        self.video_label.resize(self.video_widget.size())

    def connect_functions(self):
        self.video_stream.pixmap_signal.connect(self.show_frame)
        self.video_stream.buffered_signal.connect(self.infos_label.setText)
        self.video_stream.fps_signal.connect(self.update_fps)
        self.play_button.clicked.connect(self.play)

    def load_video(self, video_path):
        logger.critical(video_path)
        self.video_stream.open_video(video_path)

    def show_frame(self, pixmap):
        pixmap = pixmap.scaled(self.video_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.video_label.setPixmap(pixmap)
        self.video_stream.set_frame_displayed()

    def update_fps(self, fps):
        self.fps_label.setText(f"FPS:{round(fps, 1)}")

    def play(self):
        self.video_stream.play()

class buffer_thread(QtCore.QThread):

    pixmap_signal = pyqtSignal(object)

    def __init__(self, video_path, parent=None):
        super(buffer_thread, self).__init__(parent)
        self.cap = cv2.VideoCapture()
        self.running = False
        self.video_path = video_path
        self.load_video()

    def get_fps(self):
        return self.cap.get(cv2.CAP_PROP_FPS)

    def get_total_frame_number(self):
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def load_video(self):
        self.cap.open(self.video_path)

        if not self.cap.isOpened():
            logger.critical(f"Error: Could not open video {video_path}.")
            return

        self.running = True
        self.start()

    def run(self):
        try:
            while self.running:
                self.buffer_frame()
        except:
            logger.critical(str(traceback.format_exc()))

    def buffer_frame(self):
        ret, frame = self.cap.read()
        # Check if the video has ended
        if not ret:
            #self.set_frame(0)
            self.running = False
            return

        # Resize the frame while maintaining aspect ratio
        frame = resize_frame(frame, max_width=1920, max_height=1080)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the OpenCV frame to a Qt image
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QtGui.QImage(frame_rgb.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)

        # Convert the Qt image to a QPixmap
        pixmap = QtGui.QPixmap.fromImage(q_image)

        # Set the QPixmap on the QLabel
        self.pixmap_signal.emit((self.video_path, pixmap))

def resize_frame(frame, max_width, max_height):
    height, width = frame.shape[:2]

    # Calculate new dimensions while maintaining aspect ratio
    ratio = min(max_width / width, max_height / height)
    new_width = int(width * ratio)
    new_height = int(height * ratio)

    # Resize the frame
    resized_frame = cv2.resize(frame, (new_width, new_height))

    return resized_frame

class video_stream(QtCore.QThread):

    pixmap_signal = pyqtSignal(object)
    buffered_signal = pyqtSignal(object)
    fps_signal = pyqtSignal(float)
    
    def __init__(self, parent=None):
        super(video_stream, self).__init__(parent)
        self.videos = dict()

    def open_video(self, video_path):
        self.videos[video_path] = dict()
        self.videos[video_path]['pixmaps'] = []
        self.videos[video_path]['buffer_thread'] = buffer_thread(video_path)
        self.videos[video_path]['fps'] = self.videos[video_path]['buffer_thread'].get_fps()
        self.videos[video_path]['total_frame_number'] = self.videos[video_path]['buffer_thread'].get_total_frame_number()
        self.videos[video_path]['buffer_thread'].pixmap_signal.connect(self.add_frame_to_buffer)
        self.videos[video_path]['buffer_thread'].start()
        logger.critical(video_path)
        logger.critical(self.videos[video_path]['fps'])
        logger.critical(self.videos[video_path]['total_frame_number'])
        logger.critical(self.videos[video_path]['total_frame_number']/self.videos[video_path]['fps'])

    def add_frame_to_buffer(self, data_tuple):
        video_path = data_tuple[0]
        pixmap = data_tuple[1]
        self.videos[video_path]['pixmaps'].append(pixmap)
        self.buffered_signal.emit(f"{video_path} : {len(self.videos[video_path]['pixmaps'])}")

    def play(self):
        print('play')
        self.start()

    def set_frame_displayed(self):
        self.frame_displayed = True

    def run(self):
        try:
            while True:
                for video in self.videos.keys():
                    target_frame_time = 1 / self.videos[video]['fps']
                    start_time = time.monotonic()
                    f_time = start_time
                    for pixmap in self.videos[video]['pixmaps']:

                        elapsed_time = time.monotonic() - f_time
                        f_time += target_frame_time

                        time_to_wait = max(0, target_frame_time - elapsed_time)
                        current_fps = 1 / (elapsed_time + time_to_wait) if (elapsed_time + time_to_wait) > 0 else 0
                        self.fps_signal.emit(current_fps)
                        
                        if target_frame_time - elapsed_time < 0:
                            continue
                        
                        time_to_wait = max(0, target_frame_time - elapsed_time)
                        time.sleep(time_to_wait)
                        
                        self.frame_displayed = False
                        self.pixmap_signal.emit(pixmap)

                        while not self.frame_displayed:
                            pass

                    total_time = time.monotonic() - start_time
                    logger.critical(f"Total time: {total_time}")
        except:
            logger.critical(str(traceback.format_exc()))
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    player.load_video('video_1.mp4')  # Replace with your video file path
    #player.load_video('video_2.mp4')  # Replace with your video file path
    #player.load_video('video_3.mp4')  # Replace with your video file path
    #player.load_video('video_4.mp4')  # Replace with your video file path
    #player.load_video('video_5.mp4')  # Replace with your video file path
    sys.exit(app.exec_())
