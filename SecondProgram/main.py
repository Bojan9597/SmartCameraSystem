import sys
from PySide2.QtWidgets import QApplication
from MainWindowPTZ import MainWindowPTZ
from MainWindowWA import MainWindowWA

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindowWA = MainWindowWA()
    mainWindowPTZ = MainWindowPTZ()
    mainWindowWA.moveToPositionSignal.connect(mainWindowPTZ.moveToPosition)
    mainWindowWA.fileIsSelectedSignal.connect(mainWindowPTZ.handleIsFileSelected)
    mainWindowWA.show()
    mainWindowPTZ.show()

    sys.exit(app.exec_())