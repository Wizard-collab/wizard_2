import sys
import traceback
from PyQt5 import QtWidgets, QtGui, QtCore


class ErrorApp():
    def __init__(self):
        # Init QApplication, QWidet and QMenu
        self.app = QtWidgets.QApplication([])
        self.widget = QtWidgets.QWidget()
        self.menu = QtWidgets.QMenu("menu", self.widget)

        # Add items to menu
        self.menu_action_raise = self.menu.addAction("Raise")
        self.menu_action_raise.triggered.connect(self.raise_error)

        self.menu_action_exit = self.menu.addAction("Exit")
        self.menu_action_exit.triggered.connect(self.app.exit)

        # Create the tray app
        self.tray = QtWidgets.QSystemTrayIcon(QtGui.QIcon("ressources/icons/add_icon.svg"), self.widget)
        self.tray.setContextMenu(self.menu)

        # Show app
        self.tray.show()

    def raise_error(self):
        assert False


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error catched!:")
    print("error message:\n", tb)
    QtWidgets.QApplication.quit()
    # or QtWidgets.QApplication.exit(0)


sys.excepthook = excepthook
e = ErrorApp()
ret = e.app.exec_()
print("event loop exited")
sys.exit(ret)