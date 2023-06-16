from MainWindowWA import MainWindowWA
from MainWindowPtz import  MainWindowPTZ
from PyQt5.QtCore import QTimer
from ErrorHandler import ErrorHandler
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout,QDesktopWidget
import cv2
class MainWindowHandler:
    def __init__(self):
        self.mainWindowWA = MainWindowWA()
        self.mainWindowPTZ = MainWindowPTZ()
        self.mainWindowWA.moveToPositionSignal.connect(self.mainWindowPTZ.moveToPosition)
        self.mainWindowWA.mousePressEvent = self.video_label_mousePressEvent
        self.captureWA = None
        self.readWA = False
        self.capturePTZ = None
        self.readPTZ = False
        self.handleLoginWA()
        self.handleLoginPTZ()
        # Start capturing video frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_video_frames)
        self.timer.start(1)  # Set the desired frame update interval (in milliseconds)
        self.mainWindowWA.show()
        self.mainWindowPTZ.show()

    def update_video_frames(self):
        try:
            if self.readWA and self.captureWA is not None and self.captureWA.isOpened():
                retWA, frameWA = self.captureWA.read()
                if retWA == False:
                    self.captureWA = cv2.VideoCapture(self.mainWindowWA.camera_url_wa)
                    print("h\nh\nh\nh\nh\n")
                if retWA:
                    frameWA_rgb = cv2.cvtColor(frameWA, cv2.COLOR_BGR2RGB)

                    imageWA = QImage(
                        frameWA_rgb.data,
                        frameWA_rgb.shape[1],
                        frameWA_rgb.shape[0],
                        QImage.Format_RGB888
                    )
                    scaled_imageWA = imageWA.scaled(
                        self.mainWindowWA.video_label.width(),
                        self.mainWindowWA.video_label.height(),
                        Qt.KeepAspectRatio
                    )
                    self.mainWindowWA.video_label.setPixmap(QPixmap.fromImage(scaled_imageWA))
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error in updating WA frames: \n {e}")
        try:
            if self.readPTZ and self.capturePTZ is not None and self.capturePTZ.isOpened():
                retPTZ, framePTZ = self.capturePTZ.read()
                if retPTZ == False:
                    self.capturePTZ = cv2.VideoCapture(self.mainWindowPTZ.camera_url_ptz)
                if retPTZ:
                    framePTZ_rgb = cv2.cvtColor(framePTZ, cv2.COLOR_BGR2RGB)
                    # Add the red cross to the frame
                    self.mainWindowPTZ.add_red_cross(framePTZ_rgb)

                    imagePTZ = QImage(
                        framePTZ_rgb.data,
                        framePTZ_rgb.shape[1],
                        framePTZ_rgb.shape[0],
                        QImage.Format_RGB888
                    )
                    scaled_imagePTZ = imagePTZ.scaled(
                        self.mainWindowPTZ.video_label.width(),
                        self.mainWindowPTZ.video_label.height(),
                        Qt.KeepAspectRatio
                    )
                    self.mainWindowPTZ.video_label.setPixmap(QPixmap.fromImage(scaled_imagePTZ))
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error in updating PTZ frames: \n {e}")
    def handleLoginPTZ(self):
        try:
            with open('ConfigurationPTZ.txt', 'r') as f:
                usernamePTZ = f.readline().strip()
                passwordPTZ = f.readline().strip()
                ip_addressPTZ = f.readline().strip()
                cameraResolution = f.readline().strip().split(', ')

            width, height = map(float, cameraResolution)
            screenWidthPTZ, screenHeightPTZ = self.mainWindowWA.calculateWindowDimensions(width,height)
            self.mainWindowPTZ.video_label.setMinimumSize(screenWidthPTZ,screenHeightPTZ)
            self.mainWindowPTZ.video_label.setMaximumSize(screenWidthPTZ,screenHeightPTZ+30)
            self.mainWindowPTZ.setMaximumWidth(QDesktopWidget().screenGeometry().width())
            self.mainWindowPTZ.setGeometry(0,200,screenWidthPTZ, screenHeightPTZ)
            self.mainWindowPTZ.camera_url_ptz = f"rtsp://{usernamePTZ}:{passwordPTZ}@{ip_addressPTZ}/Streaming/Channels/1"
            self.capturePTZ = cv2.VideoCapture(self.mainWindowPTZ.camera_url_ptz)
            self.readPTZ = True
            print(
                f"Login successful for source 1. Username: {usernamePTZ}, Password: {passwordPTZ}, IP Address: {ip_addressPTZ}")
            print("Login successful! Streaming video...")

            camera_data = {"ip": ip_addressPTZ, "port": 80, "username": usernamePTZ, "password": passwordPTZ}
            self.mainWindowPTZ.ptz_handler.make_ptz_handler(self.mainWindowPTZ, None, camera_data)


        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error in login handler for PTZ \n{e}")

    def handleLoginWA(self):
        try:
            with open('ConfigurationWA.txt', 'r') as f:
                usernameWA = f.readline().strip()
                passwordWA = f.readline().strip()
                ip_addressWA = f.readline().strip()
                cameraResolution = f.readline().strip().split(', ')

            width, height = map(float, cameraResolution)
            screenWidthWA, screenHeightWA = self.mainWindowWA.calculateWindowDimensions(width,height)
            self.mainWindowWA.video_label.setMinimumSize(screenWidthWA,screenHeightWA)
            self.mainWindowWA.video_label.setMaximumSize(screenWidthWA,screenHeightWA+30)
            self.mainWindowWA.setMaximumWidth(QDesktopWidget().screenGeometry().width())
            self.mainWindowWA.setGeometry(0,0,screenWidthWA, screenHeightWA)
            self.mainWindowWA.camera_url_wa = f"rtsp://{usernameWA}:{passwordWA}@{ip_addressWA}/Streaming/Channels/1"
            self.captureWA = cv2.VideoCapture(self.mainWindowWA.camera_url_wa)
            self.readWA = True
            print(
                f"Login successful for source 1. Username: {usernameWA}, Password: {passwordWA}, IP Address: {ip_addressWA}")
            print("Login successful! Streaming video...")
        except Exception as e:

            ErrorHandler.displayErrorMessage(f"This is error in login handler for WA \n{e}")
    def video_label_mousePressEvent(self, event):
        try:
            if self.captureWA is not None and self.captureWA.isOpened():

                # Get the mouse position relative to the label
                pos = event.pos()
                width_ratio = pos.x() / self.mainWindowWA.width()
                height_ratio = pos.y() / self.mainWindowWA.height()
                print("hah")
                # Get the frame dimensions
                retWA, frameWA = self.captureWA.read()
                if retWA:
                    frame_height, frame_width, _ = frameWA.shape

                    # Calculate the coordinates in the frame
                    x = int(width_ratio * frame_width)
                    y = int(height_ratio * frame_height)

                    # Calculate the coordinates in the frame
                    self.corespondingX = x
                    self.corespondingY = y
                    print(self.corespondingX, self.corespondingY)
                    print("this bellow is x, y")
                    print(x,y)
                    newX, newY = self.mainWindowWA.coordinatesCalculator.calculate_corresponding_coordinate(x, y)
                    print(f"Coordinates in the frame: ({newX}, {newY})")
                    self.mainWindowWA.moveToPositionSignal.emit(newX,newY)
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error in mouse press event for WA camera: \n {e}")