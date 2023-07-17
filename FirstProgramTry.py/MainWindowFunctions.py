import sys
from onvif import ONVIFCamera
from ErrorHandler import ErrorHandler
import cv2

def getOnvifStream(mainWindow, username,password,ip_address):
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

def left_label_mousePressEvent(mainWindow, event):
        try:
            if not mainWindow.isWAChoosed:
                mainWindow.isWAChoosed = True
                if mainWindow.isWAChoosed:
                    mainWindow.left_label.setStyleSheet('border: none;')
                    mainWindow.right_label.setStyleSheet('border: 3px solid blue; padding: 1px;')
                if mainWindow.captureWA is not None and mainWindow.captureWA.isOpened():
                    # Get the mouse position relative to the label
                    pos = event.pos()
                    width_ratio = pos.x() / mainWindow.left_label.width()
                    height_ratio = pos.y() / mainWindow.left_label.height()

                    # Get the frame dimensions
                    retWA, frameWA = mainWindow.captureWA.read()
                    if retWA:
                        frame_height, frame_width, _ = frameWA.shape

                        # Calculate the coordinates in the frame
                        x = int(width_ratio * frame_width)
                        y = int(height_ratio * frame_height)
                        print(x,y)
                        mainWindow.coordinates.extend((x, y))
                        print(mainWindow.coordinates)
        except Exception as e:
            print(f"This is error in handling left label mouse press: \n {e}")

def keyPressEvent(mainWindow, event):
    try:
        key = event.key()
        if key == Qt.Key_U:  # 'u' key
            mainWindow.isWAChoosed = False
            if len(mainWindow.coordinates) % 5 != 0:  # Length is not divisible by 5
                if len(mainWindow.coordinates) >= 2:
                    mainWindow.coordinates.pop()
                    mainWindow.coordinates.pop()
            elif len(mainWindow.coordinates) % 5 == 0:  # Length is divisible by 5
                if len(mainWindow.coordinates) >= 5:
                    for _ in range(5):
                        mainWindow.coordinates.pop()
            ErrorHandler.displayMessage(f"Last coordinates are removed")
            print(mainWindow.coordinates)
        elif key == Qt.Key_E:  # 'e' key
            mainWindow.coordinates = []
            ErrorHandler.displayMessage(f"Coordinates emptied")
    except Exception as e:
        ErrorHandler.displayErrorMessage(f"Error in handling key press events: \n {e}")

def readCoordinatesFromFile(mainWindow, selectedFile):
    try:
        with open(selectedFile, 'r') as file:
            lines = file.readlines()
        coordinates = []
        # Process each line and extract the values
        for line in lines:
            line = line.strip()
            if line.startswith("X:"):
                parts = line.split(", ")
                x = int(parts[0].split(":")[1].strip())
                y = int(parts[1].split(":")[1].strip())
                pan = float(parts[2].split(":")[1].strip())
                tilt = float(parts[3].split(":")[1].strip())
                zoom = float(parts[4].split(":")[1].strip())

                # Add the values to the coordinates array
                coordinates.extend((x, y, pan, tilt, zoom))
        return coordinates
    except Exception as e:
        return []
        ErrorHandler.displayErrorMessage("File does not exist, calibration must be done from beggining")

def calculateWindowCoordinates(mainWindow, source, width, height):
    if source =="1":
        aspectRatioPTZ = height/width
        mainWindow.left_label.setMaximumSize(mainWindow.width() // 2 - 30, int((mainWindow.width() // 2 - 30) * aspectRatioPTZ))
        mainWindow.left_label.setStyleSheet('border: 3px solid blue; padding: 1px;')
    if source == "2":
        aspectRatioWA = height/ width
        mainWindow.right_label.setMaximumSize(mainWindow.width() // 2 - 30, int(((mainWindow.width() // 2 - 30)*aspectRatioWA)))
        mainWindow.left_label.setStyleSheet('border: 3px solid blue; padding: 1px;')