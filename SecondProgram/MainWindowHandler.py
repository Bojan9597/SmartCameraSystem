from MainWindowWA import MainWindowWA
from MainWindowPtz import  MainWindowPTZ
from PySide2.QtCore import QTimer, Slot
from ErrorHandler import ErrorHandler
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QLabel, QGridLayout,QDesktopWidget
import cv2
from CoordinatesCalculator import CoordinatesCalculator
from onvif import ONVIFCamera
from PySide2.QtGui import QGuiApplication, QScreen


class MainWindowHandler:
    screen = None
    def __init__(self, mainWIndowWA, mainWindowPTZ):
        self.mainWindowWA = mainWIndowWA
        self.mainWindowPTZ = mainWindowPTZ
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
        self.mainWindowWA.moveToPositionSignal.connect(self.mainWindowPTZ.moveToPosition)
        self.mainWindowWA.mousePressEvent = self.video_label_mousePressEvent

    def update_video_frames(self):
        try:
            if self.readWA and self.captureWA is not None and self.captureWA.isOpened():
                retWA, frameWA = self.captureWA.read()
                if retWA == False:
                    self.captureWA = cv2.VideoCapture(self.mainWindowWA.camera_url_wa)
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
            if self.mainWindowWA.selectedFile != "" and self.mainWindowWA.fileIsSelected == True:
                self.mainWindowWA.fileIsSelected = False
                self.mainWindowWA.coordinatesCalculator = CoordinatesCalculator(self.mainWindowWA.selectedFile)
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
    
    def handleLoginPTZ(self):
        try:
            with open('../ConfigurationPTZ.txt', 'r') as f:
                usernamePTZ = f.readline().strip()
                passwordPTZ = f.readline().strip()
                ip_addressPTZ = f.readline().strip()
                cameraResolution = f.readline().strip().split(', ')

            width, height = map(float, cameraResolution)
            aspectRatioPTZ =  height / width
            screen = QGuiApplication.primaryScreen().availableGeometry()
            self.mainWindowPTZ.setGeometry(10, 10, screen.width() , int((screen.width()) * aspectRatioPTZ) + 2*self.mainWindowPTZ.camera_label.height())

            self.mainWindowPTZ.setMaximumSize(screen.width() , int((screen.width()) * aspectRatioPTZ) + 2*self.mainWindowPTZ.camera_label.height())
            self.mainWindowPTZ.video_label.setMaximumSize(screen.width(), int((screen.width()) * aspectRatioPTZ))

            self.mainWindowPTZ.camera_url_ptz = self.getOnvifStream(usernamePTZ,passwordPTZ,ip_addressPTZ)
            self.capturePTZ = cv2.VideoCapture(self.mainWindowPTZ.camera_url_ptz)
            self.readPTZ = True
            print(
                f"Login successful for source 1. Username: {usernamePTZ}, Password: {passwordPTZ}, IP Address: {ip_addressPTZ}")
            print("Login successful! Streaming video...")

            camera_data = {"ip": ip_addressPTZ, "port": 80, "username": usernamePTZ, "password": passwordPTZ}
            self.mainWindowPTZ.ptz_handler.make_ptz_handler(self.mainWindowPTZ, None, camera_data)


        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error in login handler for PTZ \n{e}")
            print(e)

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
            self.mainWindowWA.setGeometry(10, 10, screen.width() , int((screen.width()) * aspectRatioWA) + 2*self.mainWindowWA.camera_label.height())

            self.mainWindowWA.setMaximumSize(screen.width() , int((screen.width()) * aspectRatioWA) + 2*self.mainWindowWA.camera_label.height())
            self.mainWindowWA.video_label.setMaximumSize(screen.width(), int((screen.width()) * aspectRatioWA))
            self.mainWindowWA.camera_url_wa = self.getOnvifStream(usernameWA,passwordWA,ip_addressWA)
            self.captureWA = cv2.VideoCapture(self.mainWindowWA.camera_url_wa)
            self.readWA = True
            print(
                f"Login successful for source 1. Username: {usernameWA}, Password: {passwordWA}, IP Address: {ip_addressWA}")
            print("Login successful! Streaming video...")
        except Exception as e:

            ErrorHandler.displayErrorMessage(f"This is error in login handler for WA \n{e}")
    def video_label_mousePressEvent(self, event):
        try:
            if self.mainWindowWA.coordinatesCalculator != None:
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
                        newX, newY = self.mainWindowWA.coordinatesCalculator.getTiltAndPan(x, y)
                        print(f"Coordinates in the frame: ({newX}, {newY})")
                        self.mainWindowWA.moveToPositionSignal.emit(newX,newY)
            else:
                ErrorHandler.displayErrorMessage("Select Calibration file")

        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error in mouse press event for WA camera: \n {e}")

    @Slot(str, str, str, str, str)
    def handleIsFileSelected(self,selectedFile):
        self.selectedFile = selectedFile