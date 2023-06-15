from PyQt5.QtWidgets import QMessageBox

class ErrorHandler:
    @staticmethod
    def displayErrorMessage(message):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setWindowTitle("Error")
        msgBox.setText(message)
        msgBox.exec_()

    @staticmethod
    def displayMessage(message):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setWindowTitle("Message")
        msgBox.setText(message)
        msgBox.exec_()