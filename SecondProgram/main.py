import sys
from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QApplication
from MainWindowWA import MainWindowWA
from MainWindowPtz import MainWindowPTZ
from MainWindowHandler import MainWindowHandler

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindowHandler = MainWindowHandler()
    sys.exit(app.exec_())