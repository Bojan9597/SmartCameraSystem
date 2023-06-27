import cv2
from PySide2.QtWidgets import QWidget, QLabel, QGridLayout,QDesktopWidget
from PySide2.QtGui import QPixmap
from PySide2.QtCore import Qt, QTimer
from CoordinatesCalculator import CoordinatesCalculator
from PySide2.QtCore import Slot
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
        screen = QDesktopWidget().screenGeometry()
        initial_width = screen.width()
        initial_height = 650
        self.setMaximumWidth(initial_width)
        self.setGeometry(0, 0, initial_width, initial_height)

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

    @Slot(float, float)
    def moveToPosition(self, x, y):
        try:
            move_thread = Thread(target=self.ptz_handler.move_to_position,
                                 args=(self.ptz, x, y))
            move_thread.start()
        except Exception as e:
            print(f"This is exception in moving to position {e}")

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




