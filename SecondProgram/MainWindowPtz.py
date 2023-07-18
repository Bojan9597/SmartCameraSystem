import cv2
from PySide2.QtWidgets import QWidget, QLabel, QGridLayout,QDesktopWidget
from PySide2.QtGui import QPixmap
from PySide2.QtCore import Qt
from PySide2.QtCore import Slot
from ErrorHandler import ErrorHandler
from Ptz_Handler import Ptz_Handler
from threading import Thread
from onvif import ONVIFCamera
from PySide2.QtGui import QGuiApplication, QImage
import threading
import time

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
        self.selectedFile = ""
        self.fileIsSelected = False
        self.screenWidth = screen.width()*2//3
        self.screenHeight = screen.height()*2//3
        self.ptz_handler = Ptz_Handler(self)
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
        ptz_background = QPixmap("images/ptzCamera.png")
        self.video_label.setPixmap(ptz_background.scaled(self.width(), self.height(), Qt.KeepAspectRatio))
        # Create the grid layout for the main window
        grid = QGridLayout()
        self.setLayout(grid)

        # Add labels to the grid layout
        grid.addWidget(self.camera_label, 0, 0)
        grid.addWidget(self.video_label, 1, 0)

        # Start capturing video frames
        self.capturePTZ = None
        self.capturePTZLock = threading.Lock()

        self.readPTZ = False
        self.handleLoginPTZ()

        ptz_thread = Thread(target=self.update_video_frames)
        ptz_thread.daemon = True
        ptz_thread.start()


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

    def update_video_frames(self):
        while True:
            time.sleep(0.02)
            try:
                if not self.capturePTZLock.locked():
                    self.capturePTZLock.acquire()  # Acquire the lock
                if self.readPTZ and self.capturePTZ is not None and self.capturePTZ.isOpened():
                    retPTZ, framePTZ = self.capturePTZ.read()
                    if not self.capturePTZLock.locked():
                        self.capturePTZLock.release()  # Release the lock
                    if retPTZ == False:
                        self.capturePTZ = cv2.VideoCapture(self.camera_url_ptz)
                    if retPTZ:
                        framePTZ_rgb = cv2.cvtColor(framePTZ, cv2.COLOR_BGR2RGB)
                        # Add the red cross to the frame
                        self.add_red_cross(framePTZ_rgb)

                        imagePTZ = QImage(
                            framePTZ_rgb.data,
                            framePTZ_rgb.shape[1],
                            framePTZ_rgb.shape[0],
                            QImage.Format_RGB888
                        )
                        scaled_imagePTZ = imagePTZ.scaled(
                            self.video_label.width(),
                            self.video_label.height(),
                            Qt.KeepAspectRatio
                        )
                        self.video_label.setPixmap(QPixmap.fromImage(scaled_imagePTZ))
            except Exception as e:
                ErrorHandler.displayErrorMessage(f"This is error in updating PTZ frames: \n {e}")

    def getOnvifStream(self, username,password,ip_address):
        try:
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
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error in getting ONVIF stream: \n {e}")
            print(f"This is error in getting ONVIF stream: \n {e}")
        
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
            screenPosX = (screen.width())//4
            self.setGeometry(screenPosX, 10, self.screenWidth , int((self.screenWidth) * aspectRatioPTZ) + 2*self.camera_label.height())

            self.setMaximumSize(screen.width() , int((screen.width()) * aspectRatioPTZ) + 2*self.camera_label.height())
            self.video_label.setMaximumSize(self.screenWidth, int((self.screenWidth) * aspectRatioPTZ))
            self.video_label.setStyleSheet("border: 3px solid red;")

            self.camera_url_ptz = self.getOnvifStream(usernamePTZ,passwordPTZ,ip_addressPTZ)
            self.capturePTZLock.acquire()  # Acquire the lock
            self.capturePTZ = cv2.VideoCapture(self.camera_url_ptz)
            self.capturePTZLock.release()  # Release the lock
            self.readPTZ = True
            print(
                f"Login successful for source 1. Username: {usernamePTZ}, Password: {passwordPTZ}, IP Address: {ip_addressPTZ}")
            print("Login successful! Streaming video...")

            camera_data = {"ip": ip_addressPTZ, "port": 80, "username": usernamePTZ, "password": passwordPTZ}
            self.ptz_handler.make_ptz_handler(self, None, camera_data)


        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error in login handler for PTZ \n{e}")
            print(e)


    @Slot(str)
    def handleIsFileSelected(self,selectedFile):
        self.selectedFile = selectedFile
    


