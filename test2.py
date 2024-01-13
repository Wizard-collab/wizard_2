import cv2
from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import traceback
import time
import logging
from multiprocessing import Process, Queue

logger = logging.getLogger(__name__)

# Create a global QApplication instance
app = QtWidgets.QApplication(sys.argv)

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

        self.video_stream = VideoStream()
        self.connect_functions()
        self.resize(1920, 1080)

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

class BufferProcess(Process):
    def __init__(self, video_path, queue):
        super(BufferProcess, self).__init__()
        self.video_path = video_path
        self.queue = queue

    def run(self):
        cap = cv2.VideoCapture(self.video_path)
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame = resize_frame(frame, max_width=1920, max_height=1080)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                #height, width, channel = frame.shape
                #bytes_per_line = 3 * width
                #q_image = QtGui.QImage(frame_rgb.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
                #pixmap = QtGui.QPixmap.fromImage(q_image)

                img_bytes = cv2.imencode('.png', frame_rgb)[1].tobytes()

                self.queue.put(img_bytes)

        except Exception as e:
            logger.critical(str(traceback.format_exc()))
        finally:
            cap.release()

class VideoStream(QtCore.QThread):
    pixmap_signal = QtCore.pyqtSignal(object)
    buffered_signal = QtCore.pyqtSignal(object)
    fps_signal = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super(VideoStream, self).__init__(parent)
        self.running = False
        self.queue = Queue()

    def open_video(self, video_path):
        self.buffer_process = BufferProcess(video_path, self.queue)
        self.buffer_process.start()

    def play(self):
        self.running = True
        self.start()

    def set_frame_displayed(self):
        self.frame_displayed = True

    def run(self):
        try:
            target_frame_time = 1 / 24
            start_time = time.monotonic()
            f_time = start_time

            while self.running:
                elapsed_time = time.monotonic() - f_time

                img_bytes = self.queue.get()
                if not img_bytes:
                    self.running = False
                    break

                # Reconstruct QPixmap from image data
                q_image = QtGui.QImage.fromData(img_bytes)
                pixmap = QtGui.QPixmap.fromImage(q_image)

                self.frame_displayed = False
                self.pixmap_signal.emit(pixmap)
                while not self.frame_displayed:
                    pass

                time_to_wait = max(0, target_frame_time - elapsed_time)
                current_fps = 1 / (elapsed_time + time_to_wait) if (elapsed_time + time_to_wait) > 0 else 0
                self.fps_signal.emit(current_fps)

                time_to_wait = max(0, target_frame_time - elapsed_time)
                time.sleep(time_to_wait)
                f_time += target_frame_time

            logger.critical(time.monotonic() - start_time)

        except Exception as e:
            logger.critical(str(traceback.format_exc()))
        finally:
            self.buffer_process.join()

def resize_frame(frame, max_width, max_height):
    height, width = frame.shape[:2]

    ratio = min(max_width / width, max_height / height)
    new_width = int(width * ratio)
    new_height = int(height * ratio)

    resized_frame = cv2.resize(frame, (new_width, new_height))
    return resized_frame

if __name__ == '__main__':
    player = VideoPlayer()
    player.show()
    player.load_video('video_5.mp4')  # Replace with your video file path
    sys.exit(app.exec_())
