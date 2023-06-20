import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QLineEdit, QMessageBox, QSizePolicy, QDesktopWidget, QPushButton
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from Ptz_Handler import *
from ErrorHandler import ErrorHandler
import threading

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
        self.selectedFile = ""
        self.setWindowTitle("Main Window")

        screen = QDesktopWidget().screenGeometry()
        initial_width = screen.width()
        initial_height = 650
        self.setMaximumWidth(initial_width)
        self.setGeometry(0, 100, initial_width, initial_height)
        self.setStyleSheet("background-color: #C9A098;")
        # Create left and right labels for displaying video frames
        self.left_label = QLabel()
        self.right_label = QLabel()

        # Create the grid layout for the main window
        grid = QGridLayout()
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)
        self.setLayout(grid)

        # Create PTZ coordinates labels
        wa_coordinates_label = QLabel("WA Coordinates")
        wa_coordinates_label.setFont(QFont("Arial", 16, QFont.Bold))
        wa_coordinates_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)  # Set the size policy

        # Create WA coordinates labels
        ptz_coordinates_label = QLabel("PTZ Coordinates")
        ptz_coordinates_label.setFont(QFont("Arial", 16, QFont.Bold))
        ptz_coordinates_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)  # Set the size policy

        # Create label and button for selecting corresponding coordinate
        select_label = QLabel("Select corresponding coordinate:")
        select_label.setAlignment(Qt.AlignCenter)
        select_label.setFont(QFont("Arial", 12, QFont.Bold))

        # Create button for registering pan and tilt
        register_button = QPushButton("Register Pan and Tilt")
        register_button.setFont(QFont("Arial", 12, QFont.Bold))
        register_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        # Add labels, button, and select label to the grid layout
        grid.addWidget(wa_coordinates_label, 0, 0, 1, 2, Qt.AlignCenter)
        grid.addWidget(ptz_coordinates_label, 0, 2, 1, 2, Qt.AlignCenter)
        grid.addWidget(select_label, 1, 0, 1, 2, Qt.AlignCenter)
        grid.addWidget(register_button, 1, 2, 1, 2, Qt.AlignCenter)

        # Add left and right labels to the grid layout
        grid.addWidget(self.left_label, 2, 0, 1, 2)
        grid.addWidget(self.right_label, 2, 2, 1, 2)

        # Set the alignment and size policy for the labels
        self.left_label.setAlignment(Qt.AlignCenter)
        self.right_label.setAlignment(Qt.AlignCenter)
        self.left_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.right_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Set the background images for the labels
        wa_background = QPixmap(
            "C:/Users/bojan/Desktop/Once_DE_Project/Once_DE_Project/FirstProgram/images/wideAngleCamera.png")
        ptz_background = QPixmap(
            "C:/Users/bojan/Desktop/Once_DE_Project/Once_DE_Project/FirstProgram/images/ptzCamera.png")
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
        self.left_label.mousePressEvent = self.left_label_mousePressEvent
        register_button.mousePressEvent = self.register_button_mousePressEvent

    ###############################   Functions  ################################################################
    @pyqtSlot(str)
    def handleFileSelected(self, selectedFile):
        self.selectedFile = selectedFile

    @pyqtSlot(str, str, str, str, str)
    def handleLogin(self, source, username, password, ip_address, selectedFile):
        try:
            try:
                camera_url = f"rtsp://{username}:{password}@{ip_address}/Streaming/Channels/1"
                capture = cv2.VideoCapture()

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
                    print(
                        f"Login successful for source 1. Username: {username}, Password: {password}, IP Address: {ip_address}")
                    with open("../SecondProgram/ConfigurationWA.txt", "w") as f:
                        f.write(f"{username}\n")
                        f.write(f"{password}\n")
                        f.write(f"{ip_address}\n")
                        f.write(
                            f"{self.captureWA.get(cv2.CAP_PROP_FRAME_WIDTH)} , {self.captureWA.get(cv2.CAP_PROP_FRAME_HEIGHT)} \n")
                elif source == "2":
                    self.camera_url_ptz = camera_url
                    self.capturePTZ = capture
                    self.readPTZ = True
                    print(
                        f"Login successful for source 2. Username: {username}, Password: {password}, IP Address: {ip_address}")
                    with open("../SecondProgram/ConfigurationPTZ.txt", "w") as f:
                        f.write(f"{username}\n")
                        f.write(f"{password}\n")
                        f.write(f"{ip_address}\n")
                        f.write(
                            f"{self.capturePTZ.get(cv2.CAP_PROP_FRAME_WIDTH)} , {self.capturePTZ.get(cv2.CAP_PROP_FRAME_HEIGHT)} \n")

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
                        self.right_label.width(),
                        self.right_label.height(),
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
                        self.left_label.width(),
                        self.left_label.height(),
                        Qt.KeepAspectRatio
                    )
                    self.right_label.setPixmap(QPixmap.fromImage(scaled_imagePTZ))
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error in updating PTZ frames: \n {e}")

    def left_label_mousePressEvent(self, event):
        try:
            if not self.isWAChoosed:
                self.isWAChoosed = True
                if self.captureWA is not None and self.captureWA.isOpened():
                    # Get the mouse position relative to the label
                    pos = event.pos()
                    width_ratio = pos.x() / self.left_label.width()
                    height_ratio = pos.y() / self.left_label.height()

                    # Get the frame dimensions
                    retWA, frameWA = self.captureWA.read()
                    if retWA:
                        frame_height, frame_width, _ = frameWA.shape

                        # Calculate the coordinates in the frame
                        x = int(width_ratio * frame_width)
                        y = int(height_ratio * frame_height)
                        print(x,y)
                        self.coordinates.extend((x, y))
                        print(self.coordinates)
        except Exception as e:
            print(f"This is error in handling left label mouse press: \n {e}")

    def register_button_mousePressEvent(self, event):
        try:
            print(self.selectedFile)
            if self.isWAChoosed:
                self.isWAChoosed = False
                if self.capturePTZ is not None and self.capturePTZ.isOpened():
                    # Get the mouse position relative to the label
                    pos = event.pos()
                    width_ratio = pos.x() / self.right_label.width()
                    height_ratio = pos.y() / self.right_label.height()

                    # Get the frame dimensions
                    retPTZ, framePTZ = self.capturePTZ.read()
                    if retPTZ:
                        frame_height, frame_width, _ = framePTZ.shape

                        # Calculate the coordinates in the frame
                        x = int(width_ratio * frame_width)
                        y = int(height_ratio * frame_height)
                        print(x,y)
                        x,y,zoom = self.ptz_handler.get_position(self,self.ptz,self.media_profile)
                        self.coordinates.extend((x, y, zoom))

                        # Write the coordinates to the file
                        if len(self.coordinates)/5 >= 4:
                            with open(self.selectedFile, "w") as file:
                                for i in range(int(len(self.coordinates) / 5)):
                                    file.write(
                                        f"X: {self.coordinates[i * 5 + 0]}, Y: {self.coordinates[i * 5 + 1]}, pan: {self.coordinates[i * 5 + 2]}, "
                                        f"tilt: {self.coordinates[i * 5 + 3]}, zoom: {self.coordinates[i * 5 + 4]}\n")
                        print(self.coordinates)

        except Exception as e:
            ErrorHandler.displayErrorMessage(f"Error in register button press event: \n {e}")

    def keyPressEvent(self, event):
        try:
            key = event.key()
            if key == Qt.Key_U:  # 'u' key
                self.isWAChoosed = False
                if len(self.coordinates) % 5 != 0:  # Length is not divisible by 5
                    if len(self.coordinates) >= 2:
                        self.coordinates.pop()
                        self.coordinates.pop()
                elif len(self.coordinates) % 5 == 0:  # Length is divisible by 5
                    if len(self.coordinates) >= 5:
                        for _ in range(5):
                            self.coordinates.pop()
                ErrorHandler.displayMessage(f"Last coordinates are removed")
                print(self.coordinates)
            elif key == Qt.Key_E:  # 'e' key
                self.coordinates = []
                ErrorHandler.displayMessage(f"Coordinates emptied")
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"Error in handling key press events: \n {e}")





