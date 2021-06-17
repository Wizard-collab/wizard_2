import PyWizard
from wizard.gui import tree_widget
import sys
from PyQt5 import QtWidgets, QtCore, QtGui

app = QtWidgets.QApplication(sys.argv)
my_tree_widget = tree_widget.tree_widget()
my_tree_widget.show()
sys.exit(app.exec_())