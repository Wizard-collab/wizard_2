import sys
import os
import logging
from PyQt5 import QtGui, QtWidgets, QtCore

log = logging.getLogger("Foo")
logging.basicConfig(
    level=logging.INFO, format='%(levelname)s: %(filename)s - %(message)s')
log.setLevel(logging.DEBUG)




class ConsolePanelHandler(logging.Handler):

    def __init__(self, parent):
        logging.Handler.__init__(self)
        self.parent = parent

    def emit(self, record):
        self.parent.write(self.format(record))


class Foo(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.textEdit = QtWidgets.QTextEdit(self)
        self.textEdit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.textEdit.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)
        vbox.addWidget(self.textEdit)

    def write(self, s):
        self.textEdit.setFontWeight(QtGui.QFont.Normal)
        self.textEdit.append(s)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    console_panel = Foo()
    handler = ConsolePanelHandler(console_panel)
    log.addHandler(handler)

    log.info("Getting logger {0} - {1}".format(id(log), log.handlers))
    [log.debug("This is normal text " + str(i)) for i in range(5)]
    console_panel.show()

    sys.exit(app.exec_())