import sys
from PySide2.QtWidgets import QApplication
from MainWindowHandler import MainWindowHandler

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindowHandler = MainWindowHandler()
    sys.exit(app.exec_())