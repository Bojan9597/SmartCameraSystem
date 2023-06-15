from MainWindowWA import MainWindowWA
from MainWindowPtz import  MainWindowPTZ
from PyQt5.QtCore import QTimer
from ErrorHandler import ErrorHandler
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
import cv2
class MainWindowHandler:
    def __init__(self):
        self.mainWindowWA = MainWindowWA()
        self.mainWindowPTZ = MainWindowPTZ()
        self.mainWindowWA.moveToPositionSignal.connect(self.mainWindowPTZ.moveToPosition)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_video_frames)
        self.timer.start(1)  # Set the desired frame update interval (in milliseconds)
        self.mainWindowWA.show()
        self.mainWindowPTZ.show()

    def update_video_frames(self):
        try:
            if self.mainWindowWA.readWA and self.mainWindowWA.captureWA is not None and self.mainWindowWA.captureWA.isOpened():
                retWA, frameWA = self.mainWindowWA.captureWA.read()
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
            if self.mainWindowPTZ.readPTZ and self.mainWindowPTZ.capturePTZ is not None and self.mainWindowPTZ.capturePTZ.isOpened():
                retPTZ, framePTZ = self.mainWindowPTZ.capturePTZ.read()
                if retPTZ:
                    print("hohoho")
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