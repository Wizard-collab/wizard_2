# -*- coding: utf-8 -*-

import sys

from PyQt5.QtCore import QEvent
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow


class MyMainWindow(QMainWindow):
    """
    A subclass of the QMainWindow with the eventFilter method.
    """

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.TouchBegin:  # Catch the TouchBegin event.
            print('We have a touch begin')
            return True
        elif event.type() == QEvent.TouchEnd:  # Catch the TouchEnd event.
            print('We have a touch end')
            return True

        return super(MyMainWindow, self).eventFilter(obj, event)


def main():
    app = QApplication(sys.argv)

    # Create a window.
    win = MyMainWindow()
    win.resize(800, 800)
    win.setWindowTitle('Touch Event Example')

    # Tell the window that we accept touch events.
    win.setAttribute(Qt.WA_AcceptTouchEvents, True)

    # Install an event filter to filter the touch events.
    win.installEventFilter(win)

    # Show the window and execute the app.
    win.show()

    d=QtWidgets.QDialog()
    d.exec_()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()