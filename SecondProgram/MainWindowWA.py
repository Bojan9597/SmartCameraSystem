import os.path

import cv2
from PySide2.QtWidgets import QApplication, QWidget, QLabel, QGridLayout,QDesktopWidget, QFileDialog, QPushButton, QDialog
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtCore import Qt, QTimer
from CoordinatesCalculator import CoordinatesCalculator
from PySide2.QtCore import Signal
from ErrorHandler import ErrorHandler
from onvif import ONVIFCamera
from PySide2.QtGui import QGuiApplication, QScreen
from threading import Thread
import threading
import time

class MainWindowWA(QWidget):
    camera_url_WA = ""
    camera_url_wa = ""
    saveprefix = ""
    media_profile = ""
    request = ""
    moveToPositionSignal = Signal(float, float)
    fileIsSelectedSignal = Signal(str)


    def __init__(self):
        super().__init__()
        self.coordinatesCalculator = None
        self.selectedFile = ""
        self.fileIsSelected = False
        self.setWindowTitle("Main Window WA")
        screen = QDesktopWidget().screenGeometry()
        self.screenWidth = screen.width()*2//3
        self.screenHeight = screen.height()*2//3
        self.frameWidth = 0
        self.frameHeight = 0

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
            "images/wideAngleCamera.png")
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
        self.captureWALock = threading.Lock()
        self.handleLoginWA()
        # Enable mouse tracking on the label
        self.video_label.setMouseTracking(True)
        self.mousePressEvent = self.video_label_mousePressEvent
        wa_thread = Thread(target = self.update_video_frames)
        wa_thread.daemon = True
        wa_thread.start()

    def choose_file(self):
        file_dialog = QFileDialog()
        file_dialog.exec_()
        if file_dialog.result() == QDialog.Accepted:
            selected_file = file_dialog.selectedFiles()
        if selected_file:
            print("Selected file:", selected_file[0])
        self.selectedFile = os.path.abspath(selected_file[0])
        self.fileIsSelected = True
        self.file_button.setText(f"File is chosen: {self.selectedFile}")
        self.fileIsSelectedSignal.emit(self.selectedFile)
        self.coordinatesCalculator = CoordinatesCalculator(self.selectedFile)

    def video_label_mousePressEvent(self, event):
        try:
            if self.coordinatesCalculator is not None:
                if not self.captureWALock.locked():
                    self.captureWALock.acquire()
                if self.captureWA is not None and self.captureWA.isOpened():
                    # Get the mouse position relative to the label
                    pos = self.video_label.mapFrom(self, event.pos())
                    width_ratio = pos.x() / self.video_label.width()
                    height_ratio = pos.y() / self.video_label.height()
                    
                    # Get the frame dimensions
                    if self.captureWALock.locked():
                        self.captureWALock.release()
  
                    frame_width, frame_height= self.captureWA.get(cv2.CAP_PROP_FRAME_WIDTH),self.captureWA.get(cv2.CAP_PROP_FRAME_HEIGHT)

                    # Calculate the coordinates in the frame
                    x = int(width_ratio * frame_width)
                    y = int(height_ratio * frame_height)
                    if x <0 or y <0:
                        return


                    self.corespondingX = x
                    self.corespondingY = y
                    print(self.corespondingX, self.corespondingY)

                    newX, newY = self.coordinatesCalculator.getTiltAndPan(x, y)
                    print(f"Coordinates in the frame: ({newX}, {newY})")
                    self.moveToPositionSignal.emit(newX, newY)
            else:
                ErrorHandler.displayErrorMessage("Select Calibration file")

        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is an error in the mouse press event for WA camera: \n {e}")

    def handleLoginWA(self):
        try:
            with open('../ConfigurationWA.txt', 'r') as f:
                usernameWA = f.readline().strip()
                passwordWA = f.readline().strip()
                ip_addressWA = f.readline().strip()
                cameraResolution = f.readline().strip().split(', ')

            width, height = map(float, cameraResolution)
            aspectRatioWA = height/width
            screen = QGuiApplication.primaryScreen().availableGeometry()
            self.setGeometry(10, 10, self.screenWidth , int((self.screenWidth) * aspectRatioWA) + 2*self.camera_label.height())

            self.setMaximumSize(screen.width() , int((screen.width()) * aspectRatioWA) + 2*self.camera_label.height())
            self.video_label.setMaximumSize(self.screenWidth, int((self.screenWidth) * aspectRatioWA))
            self.video_label.setStyleSheet("border: 3px solid blue;")
            self.camera_url_wa = self.getOnvifStream(usernameWA,passwordWA,ip_addressWA)
            self.captureWA = cv2.VideoCapture(self.camera_url_wa)
            self.readWA = True
            print(
                f"Login successful for source 1. Username: {usernameWA}, Password: {passwordWA}, IP Address: {ip_addressWA}")
            print("Login successful! Streaming video...")
        except Exception as e:

            ErrorHandler.displayErrorMessage(f"This is error in login handler for WA \n{e}")


    def getOnvifStream(self, username,password,ip_address):
        camera = ONVIFCamera(ip_address, 80, username, password)

        # Get media service
        media_service = camera.create_media_service()

        # Get available profiles
        profiles = media_service.GetProfiles()

        # Select the first profile
        profile_token = profiles[0].token
        # Get the stream URI
        stream_uri = media_service.GetStreamUri({
        'StreamSetup': {'Stream': 'RTP-Unicast', 'Transport': {'Protocol': 'RTSP'}},
        'ProfileToken': profile_token
        })
        camera_url =  stream_uri.Uri
        camera_url = camera_url.replace('rtsp://', f"rtsp://{username}:{password}@")
        return camera_url
    
    def update_video_frames(self):
        while True:
            time.sleep(0.02)
            try:
                if self.readWA and self.captureWA is not None and self.captureWA.isOpened():
                    retWA, frameWA = self.captureWA.read()
                    if retWA == False:
                        self.captureWA = cv2.VideoCapture(self.camera_url_wa)
                    if retWA:
                        frameWA_rgb = cv2.cvtColor(frameWA, cv2.COLOR_BGR2RGB)

                        imageWA = QImage(
                            frameWA_rgb.data,
                            frameWA_rgb.shape[1],
                            frameWA_rgb.shape[0],
                            QImage.Format_RGB888
                        )
                        scaled_imageWA = imageWA.scaled(
                            self.video_label.width(),
                            self.video_label.height(),
                            Qt.KeepAspectRatio
                        )
                        self.video_label.setPixmap(QPixmap.fromImage(scaled_imageWA))
            except Exception as e:
                ErrorHandler.displayErrorMessage(f"This is error in updating WA frames: \n {e}")