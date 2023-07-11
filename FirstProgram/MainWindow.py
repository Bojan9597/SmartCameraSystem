import cv2
from PySide2.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QLineEdit, QMessageBox, QSizePolicy, QDesktopWidget, QPushButton
from PySide2.QtGui import QImage, QPixmap, QFont
from PySide2.QtCore import Qt, QTimer, Slot
from Ptz_Handler import *
from ErrorHandler import ErrorHandler
import threading
from MainWindowFunctions import *

class MainWindow(QWidget):
    coordinates = []
    saveprefix = ""
    # Camera login information
    camera_url_ptz = ""
    camera_url_wa = ""
    ptz = ""
    media_profile =""
    isWAChoosed = False
    def __init__(self):
        super().__init__()
        self.ptz_handler = Ptz_Handler()
        self.isNewCalibration = True
        self.selectedFile = "CalibrationCoordinates.txt"
        self.setWindowTitle("Calibration Program")
        self.frameWidthPTZ, self.frameHeightPTZ = 0, 0
        self.frameWidthWA, self.frameHeightWA = 0, 0
        screen = QDesktopWidget().screenGeometry()
        initial_width = screen.width()
        initial_height = 650
        self.setMaximumWidth(initial_width)
        self.setGeometry(0, 100, initial_width, initial_height)
        self.setStyleSheet("background-color: #C9A098;")
        # Create the grid layout for the main window
        grid = QGridLayout()
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)
        self.setLayout(grid)

        # Create a placeholder label
        placeholder_label = QLabel()
        placeholder_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        placeholder_label.setMinimumHeight(30)

        # Create left and right labels for displaying video frames
        self.left_label = QLabel()
        self.right_label = QLabel()

        # Create WA coordinates labels
        wa_coordinates_label = QLabel("WA Coordinates")
        wa_coordinates_label.setFont(QFont("Arial", 16, QFont.Bold))
        wa_coordinates_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)  # Set the size policy
        wa_coordinates_label.setMinimumHeight(30)

        # Create PTZ coordinates labels
        ptz_coordinates_label = QLabel("PTZ Coordinates")
        ptz_coordinates_label.setFont(QFont("Arial", 16, QFont.Bold))
        ptz_coordinates_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)  # Set the size policy
        ptz_coordinates_label.setMinimumHeight(30)

        # Create label and button for selecting corresponding coordinate
        select_label = QLabel("Select corresponding coordinate:")
        select_label.setAlignment(Qt.AlignCenter)
        select_label.setFont(QFont("Arial", 12, QFont.Bold))

        # Create button for registering pan and tilt
        self.register_button = QPushButton("Register Pan and Tilt")
        self.register_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.register_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        # Add labels, button, and select label to the grid layout
        grid.addWidget(wa_coordinates_label, 0, 0, 1, 2, Qt.AlignCenter)
        grid.addWidget(ptz_coordinates_label, 0, 2, 1, 2, Qt.AlignCenter)
        grid.addWidget(select_label, 1, 0, 1, 2, Qt.AlignCenter)
        grid.addWidget(self.register_button, 1, 2, 1, 2, Qt.AlignCenter)

        # Add placeholder label, left and right labels to the grid layout
        grid.addWidget(placeholder_label, 2, 0, 1, 2)
        grid.addWidget(self.left_label, 3, 0, 1, 2)
        grid.addWidget(self.right_label, 3, 2, 1, 2)

        # Set the alignment and size policy for the labels
        self.left_label.setAlignment(Qt.AlignCenter)
        self.right_label.setAlignment(Qt.AlignCenter)
        self.left_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.right_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Set the background images for the labels
        wa_background = QPixmap(
            "images/wideAngleCamera.png")
        ptz_background = QPixmap(
            "images/ptzCamera.png")
        self.left_label.setPixmap(wa_background.scaled(self.width() // 2, self.height() - 100, Qt.KeepAspectRatio))
        self.right_label.setPixmap(ptz_background.scaled(self.width() // 2, self.height() - 100, Qt.KeepAspectRatio))

        # Start capturing video frames
        self.captureWA = None
        self.capturePTZ = None
        self.readWA = False
        self.readPTZ = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video_frames)
        self.timer.start(1)  # Set the desired frame update interval (in milliseconds)

        # Enable mouse tracking on the labels
        self.left_label.setMouseTracking(True)
        self.right_label.setMouseTracking(True)

        # Connect mouse press event to the labels
        self.left_label.mousePressEvent = lambda event: left_label_mousePressEvent(self, event)
        self.register_button.mousePressEvent = lambda event: register_button_mousePressEvent(self, event)

    ###############################   Functions  ################################################################
    @Slot(str, bool)
    def handleFileSelected(self, selectedFile, isNewCalibration):
        self.selectedFile = selectedFile
        self.isNewCalibration = isNewCalibration
        if self.isNewCalibration:
            pass
        elif self.coordinates == []:
            self.coordinates.extend(self.readCoordinatesFromFile(self.selectedFile))
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
    
    @Slot(str, str, str, str, str, bool)
    def handleLogin(self, source, username, password, ip_address, selectedFile, isNewCalibraion):

        try:
            try:
                self.isNewCalibration = isNewCalibraion
                if self.isNewCalibration:
                    pass
                elif self.coordinates == []:
                    self.coordinates.extend(self.readCoordinatesFromFile(self.selectedFile))

                # Write the coordinates to the file
                camera_url = self.getOnvifStream(username,password,ip_address)
                capture = cv2.VideoCapture(camera_url)

                def connect_to_camera():
                    capture.open(camera_url)

                timeout_seconds = 7
                connect_thread = threading.Thread(target=connect_to_camera)
                connect_thread.start()
                connect_thread.join(timeout_seconds)

                if connect_thread.is_alive() or not capture.isOpened():
                    # Connection attempt timed out or failed
                    capture.release()
                    ErrorHandler.displayMessage(
                        "Failed to connect to the camera. Please check the credentials and camera settings.")
                    return

                if source == "1":
                    self.camera_url_wa = camera_url
                    self.captureWA = capture
                    self.readWA = True
                    self.frameWidthWA, self.frameHeightWA = self.captureWA.get(cv2.CAP_PROP_FRAME_WIDTH), self.captureWA.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    calculateWindowCoordinates(self, source, self.frameWidthWA,self.frameHeightWA)
                    print(
                        f"Login successful for source 1. Username: {username}, Password: {password}, IP Address: {ip_address}")
                    try:
                        with open("ConfigurationWA.txt", "w") as f:
                            f.write(f"{username}\n")
                            f.write(f"{password}\n")
                            f.write(f"{ip_address}\n")
                            f.write(
                                f"{self.captureWA.get(cv2.CAP_PROP_FRAME_WIDTH)} , {self.captureWA.get(cv2.CAP_PROP_FRAME_HEIGHT)} \n")
                    except Exception as e:
                        ErrorHandler.displayErrorMessage("Can not open file ConfigurationWA.txt")
                elif source == "2":
                    self.camera_url_ptz = camera_url
                    self.capturePTZ = capture
                    self.readPTZ = True
                    self.frameWidthPTZ, self.frameHeightPTZ = self.capturePTZ.get(cv2.CAP_PROP_FRAME_WIDTH), self.capturePTZ.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    calculateWindowCoordinates(self, source, self.frameWidthPTZ, self.frameHeightPTZ)
                    print(
                        f"Login successful for source 2. Username: {username}, Password: {password}, IP Address: {ip_address}")
                    try:
                        with open("ConfigurationPTZ.txt", "w") as f:
                            f.write(f"{username}\n")
                            f.write(f"{password}\n")
                            f.write(f"{ip_address}\n")
                            f.write(
                                f"{self.capturePTZ.get(cv2.CAP_PROP_FRAME_WIDTH)} , {self.capturePTZ.get(cv2.CAP_PROP_FRAME_HEIGHT)} \n")
                    except Exception as e:
                        ErrorHandler.displayErrorMessage("Can not open file ConfigurationPTZ.txt")
                # Continue with streaming video
                print("Login successful! Streaming video...")
            except Exception as e:
                ErrorHandler.displayErrorMessage(f"Error in login handler: \n {e}")

            # Check if the PTZ camera is successfully loaded
            if source == "2" and (not self.capturePTZ.isOpened() or not self.readPTZ):
                return

            # Check if the WA camera is successfully loaded
            if source == "1" and (not self.captureWA.isOpened() or not self.readWA):
                return

            camera_data = {"ip": ip_address, "port": 80, "username": username, "password": password}
            if source == "2":
                if self.saveprefix != "":
                    self.ptz_handler.make_ptz_handler(self, self.saveprefix + ".txt", camera_data)
                else:
                    self.ptz_handler.make_ptz_handler(self, None, camera_data)

            # Continue with streaming video
            print("Login successful! Streaming video...")
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"Error in login handler: \n {e}")

    def update_video_frames(self):
        try:
            if self.readWA and self.captureWA is not None and self.captureWA.isOpened():
                retWA, frameWA = self.captureWA.read()
                if retWA == False:
                    self.captureWA = cv2.VideoCapture(self.camera_url_wa)
                if retWA:
                    frameWA_rgb = cv2.cvtColor(frameWA, cv2.COLOR_BGR2RGB)
                    self.add_dots_on_image(frameWA_rgb)
                    imageWA = QImage(
                        frameWA_rgb.data,
                        frameWA_rgb.shape[1],
                        frameWA_rgb.shape[0],
                        QImage.Format_RGB888
                    )
                    scaled_imageWA = imageWA.scaled(
                        self.left_label.width(),
                        self.left_label.height(),
                        Qt.KeepAspectRatio
                    )
                    self.left_label.setPixmap(QPixmap.fromImage(scaled_imageWA))
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error in updating WA frames: \n {e}")
        try:
            if self.readPTZ and self.capturePTZ is not None and self.capturePTZ.isOpened():
                retPTZ, framePTZ = self.capturePTZ.read()
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
                        self.right_label.width(),
                        self.right_label.height(),
                        Qt.KeepAspectRatio
                    )
                    self.right_label.setPixmap(QPixmap.fromImage(scaled_imagePTZ))
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error in updating PTZ frames: \n {e}")

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

    def add_dots_on_image(self,frame):
        width, height = frame.shape[:2]
        for i in range(6):
            for j in range(5):
                cv2.circle(frame, (int(height/5*i), int(width/4*j)), 10, (0, 0, 255), -1)