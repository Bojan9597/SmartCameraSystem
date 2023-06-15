import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from MainWindowWA import MainWindowWA
from MainWindowPtz import MainWindowPTZ
from MainWindowHandler import MainWindowHandler

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindowHandler = MainWindowHandler()

    sys.exit(app.exec_())