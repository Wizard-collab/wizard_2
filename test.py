from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import sys

class Window(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.resize(800,800)
        self.pies_list = []

    def add_pie(self, percent_factor=0, color='gray'):
        self.pies_list.append([percent_factor, color])

    def paintEvent(self, event):
        # Define area
        rectangle = QtCore.QRectF(0,0,self.width(), self.height())
        last_angle = 0

        painter = QtGui.QPainter(self)

        for pie in self.pies_list:
            painter.setPen(QtGui.QPen(QtGui.QColor('transparent'), 0))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(pie[1]), QtCore.Qt.SolidPattern))
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
            angle = 360*pie[0]/100
            spanAngle = int(angle*16)
            painter.drawPie(rectangle, last_angle, spanAngle)
            last_angle = spanAngle


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_win = Window()
    main_win.add_pie(30, 'blue')
    main_win.add_pie(70, 'red')
    main_win.show()
    sys.exit(app.exec())