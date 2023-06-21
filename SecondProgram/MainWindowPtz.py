import cv2
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout,QDesktopWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from CoordinatesCalculator import CoordinatesCalculator
from PyQt5.QtCore import pyqtSlot
from ErrorHandler import ErrorHandler
from Ptz_Handler import Ptz_Handler
from threading import Thread

class MainWindowPTZ(QWidget):
    camera_url_PTZ = ""
    camera_url_ptz = ""
    saveprefix = ""
    media_profile = ""
    request = ""
    counter =0
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window PTZ")
        screen = QDesktopWidget().screenGeometry()
        self.screenWidth = screen.width()
        self.screenHeight = screen.height()
        self.ptz_handler = Ptz_Handler(self)
        # Create a label for displaying the camera name
        self.camera_label = QLabel("PTZ Camera")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMaximumHeight(30)

        # Create a label for displaying the video frame
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        # Set the background image for the video label
        ptz_background = QPixmap(
            "images/ptzCamera.png")
        self.video_label.setPixmap(ptz_background.scaled(self.width(), self.height(), Qt.KeepAspectRatio))

        # Create the grid layout for the main window
        grid = QGridLayout()
        self.setLayout(grid)

        # Add labels to the grid layout
        grid.addWidget(self.camera_label, 0, 0)
        grid.addWidget(self.video_label, 1, 0)

        # Start capturing video frames
        self.capturePTZ = None
        self.readPTZ = False

        # self.handleLogin()

    @pyqtSlot(float, float)
    def moveToPosition(self, x, y):
        try:
            move_thread = Thread(target=self.ptz_handler.move_to_position,
                                 args=(self.ptz, x, y))
            move_thread.start()
        except Exception as e:
            print(f"This is exception in moving to position {e}")
    def handleLogin(self):
        try:
            with open('../ConfigurationPTZ.txt', 'r') as f:
                usernamePTZ = f.readline().strip()
                passwordPTZ = f.readline().strip()
                ip_addressPTZ = f.readline().strip()
                cameraResolution = f.readline().strip().split(', ')

            width, height = map(float, cameraResolution)
            screenWidthPTZ, screenHeightPTZ = self.calculateWindowDimensions(width,height)
            self.video_label.setMinimumSize(screenWidthPTZ,screenHeightPTZ)
            self.video_label.setMaximumSize(screenWidthPTZ,screenHeightPTZ+30)
            self.setMaximumWidth(QDesktopWidget().screenGeometry().width())
            self.setGeometry(0,200,screenWidthPTZ, screenHeightPTZ)
            self.camera_url_ptz = f"rtsp://{usernamePTZ}:{passwordPTZ}@{ip_addressPTZ}/Streaming/Channels/1"
            self.capturePTZ = cv2.VideoCapture(self.camera_url_ptz)
            self.readPTZ = True
            print(
                f"Login successful for source 1. Username: {usernamePTZ}, Password: {passwordPTZ}, IP Address: {ip_addressPTZ}")
            print("Login successful! Streaming video...")

            camera_data = {"ip": ip_addressPTZ, "port": 80, "username": usernamePTZ, "password": passwordPTZ}
            self.ptz_handler.make_ptz_handler(self, None, camera_data)


        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error in login handler for PTZ \n{e}")
    def add_red_cross(self, frame):
        try:
            # Get the frame dimensions
            frame_height, frame_width, _ = frame.shape

            # Calculate the center coordinates
            center_x = frame_width // 2
            center_y = frame_height // 2

            # Define the cross line properties
            color = (255, 0, 0)  # Red color
            thickness = 2

            # Draw the cross lines
            cv2.line(frame, (center_x - 20, center_y), (center_x + 20, center_y), color, thickness)
            cv2.line(frame, (center_x, center_y - 20), (center_x, center_y + 20), color, thickness)
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error in adding red cross: \n {e}")

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
            ErrorHandler.displayErrorMessage(f"Error in calculating Window dimensions for PTZ camera: \n {e}")




