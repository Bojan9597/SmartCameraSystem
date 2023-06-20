import os.path

import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout,QDesktopWidget, QFileDialog, QPushButton
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer
from CoordinatesCalculator import CoordinatesCalculator
from PyQt5.QtCore import pyqtSignal
from ErrorHandler import ErrorHandler
class MainWindowWA(QWidget):
    camera_url_WA = ""
    camera_url_wa = ""
    saveprefix = ""
    media_profile = ""
    request = ""
    moveToPositionSignal = pyqtSignal(float, float)
    fileIsSelectedSignal = pyqtSignal(str)


    def __init__(self):
        super().__init__()
        self.coordinatesCalculator = None
        self.selectedFile = ""
        self.fileIsSelected = False
        self.setWindowTitle("Main Window WA")
        screen = QDesktopWidget().screenGeometry()
        self.screenWidth = screen.width()
        self.screenHeight = screen.height()

        # Create a label for displaying the camera name
        self.camera_label = QLabel("WA Camera")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMaximumHeight(30)

        # Create the "Choose File" button
        self.file_button = QPushButton("Choose File")
        self.file_button.clicked.connect(self.choose_file)

        # Create a label for displaying the video frame
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        # Set the background image for the video label
        wa_background = QPixmap(
            "C:/Users/bojan/Desktop/Once_DE_Project/Once_DE_Project/FirstProgram/images/wideAngleCamera.png")
        self.video_label.setPixmap(wa_background.scaled(self.width(), self.height(), Qt.KeepAspectRatio))

        # Create the grid layout for the main window
        grid = QGridLayout()
        self.setLayout(grid)

        # Add labels and button to the grid layout
        grid.addWidget(self.camera_label, 0, 0)
        grid.addWidget(self.file_button, 1, 0)
        grid.addWidget(self.video_label, 2, 0)

        # Start capturing video frames
        self.captureWA = None
        self.readWA = False

        # Enable mouse tracking on the label
        self.video_label.setMouseTracking(True)

    def choose_file(self):
        file_dialog = QFileDialog()
        file_dialog.exec_()
        selected_file = file_dialog.selectedFiles()
        if selected_file:
            print("Selected file:", selected_file[0])
        self.selectedFile = os.path.abspath(selected_file[0])
        self.fileIsSelected = True
        self.file_button.setText(f"File is chosen: {self.selectedFile}")
        self.fileIsSelectedSignal.emit(self.selectedFile)



    def handleLogin(self):
        try:
            with open('ConfigurationWA.txt', 'r') as f:
                usernameWA = f.readline().strip()
                passwordWA = f.readline().strip()
                ip_addressWA = f.readline().strip()
                cameraResolution = f.readline().strip().split(', ')

            width, height = map(float, cameraResolution)
            screenWidthWA, screenHeightWA = self.calculateWindowDimensions(width,height)
            self.video_label.setMinimumSize(screenWidthWA,screenHeightWA)
            self.video_label.setMaximumSize(screenWidthWA,screenHeightWA+30)
            self.setMaximumWidth(QDesktopWidget().screenGeometry().width())
            self.setGeometry(0,0,screenWidthWA, screenHeightWA)
            self.camera_url_wa = f"rtsp://{usernameWA}:{passwordWA}@{ip_addressWA}/Streaming/Channels/1"
            self.captureWA = cv2.VideoCapture(self.camera_url_wa)
            self.readWA = True
            print(
                f"Login successful for source 1. Username: {usernameWA}, Password: {passwordWA}, IP Address: {ip_addressWA}")
            print("Login successful! Streaming video...")
        except Exception as e:

            ErrorHandler.displayErrorMessage(f"This is error in login handler for WA \n{e}")

    def calculateWindowDimensions(self, width, height):
        try:
            aspect_ratioPTZ = width / height
            current_screen = QDesktopWidget().screenGeometry(self)
            screenWidthPTZ = current_screen.width()
            screenHeightPTZ = current_screen.height()

            aspect_ratio = screenWidthPTZ / screenHeightPTZ
            if aspect_ratioPTZ > aspect_ratio:
                widthPTZ = screenWidthPTZ
                heightPTZ = widthPTZ / aspect_ratioPTZ
            else:
                heightPTZ = screenHeightPTZ
                widthPTZ = heightPTZ * aspect_ratioPTZ

            return widthPTZ * 0.9, heightPTZ * 0.9
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"Error in calculating Window dimensions for WA camera: \n {e}")



