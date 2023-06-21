from pynput import keyboard
from onvif import ONVIFCamera
import zeep
import time
from PyQt5.QtWidgets import QMessageBox
from ErrorHandler import  ErrorHandler

class Ptz_Handler:
    requestAbsolute = ""
    request = ""
    def __init__(self,mainWindow):
        self.mainWindow = mainWindow
    def get_position(self,MainWindow, ptz, media_profile):
        # Get the PTZ position using the ONVIF camera
        try:
            # Get the PTZ status from the camera
            status = ptz.GetStatus({'ProfileToken': media_profile.token})

            # Get the position information
            position = status.Position

            # Extract the relevant coordinates and zoom information
            x = position.PanTilt.x
            y = position.PanTilt.y
            zoom = position.Zoom.x

            return x, y, zoom
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"Error in get position function: \n {e}")
            return 0, 0, 0
    def make_ptz_handler(self,MainWindow, cmdfile, config):
        try:
            mycam = ONVIFCamera(config['ip'], config['port'], config['username'], config['password'])
            # Create media service object
            media = mycam.create_media_service()
            # Create ptz service object
            MainWindow.ptz = mycam.create_ptz_service()

            # Get target profile
            zeep.xsd.simple.AnySimpleType.pythonvalue = self.zeep_pythonvalue
            MainWindow.media_profile = media.GetProfiles()[0]

            # Get PTZ configuration options for getting continuous move range
            self.request = MainWindow.ptz.create_type('GetConfigurationOptions')
            self.requestAbsolute = MainWindow.ptz.create_type('GetConfigurationOptions')
            self.request.ConfigurationToken = MainWindow.media_profile.PTZConfiguration.token
            self.requestAbsolute.ConfigurationToken = MainWindow.media_profile.PTZConfiguration.token
            ptz_configuration_options = MainWindow.ptz.GetConfigurationOptions(self.request)
            ptz_configuration_options_absolute = MainWindow.ptz.GetConfigurationOptions(self.requestAbsolute)


            self.request = MainWindow.ptz.create_type('ContinuousMove')
            self.requestAbsolute = MainWindow.ptz.create_type('AbsoluteMove')
            self.request.ProfileToken = MainWindow.media_profile.token
            self.requestAbsolute.ProfileToken = MainWindow.media_profile.token
            MainWindow.ptz.Stop({'ProfileToken': MainWindow.media_profile.token})
            if  self.requestAbsolute.Position is None:
                self.requestAbsolute.Position = MainWindow.ptz.GetStatus({'ProfileToken': MainWindow.media_profile.token}).Position
                self.requestAbsolute.Position.PanTilt.space = \
                ptz_configuration_options_absolute.Spaces.AbsolutePanTiltPositionSpace[0].URI
                self.requestAbsolute.Position.Zoom.space = \
                ptz_configuration_options_absolute.Spaces.AbsoluteZoomPositionSpace[0].URI

            if self.request.Velocity is None:
                self.request.Velocity = MainWindow.ptz.GetStatus({'ProfileToken': MainWindow.media_profile.token}).Position
                self.request.Velocity = MainWindow.ptz.GetStatus({'ProfileToken': MainWindow.media_profile.token}).Position
                self.request.Velocity.PanTilt.space = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].URI
                self.request.Velocity.Zoom.space = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].URI

            # Get range of pan and tilt
            # NOTE: X and Y are velocity vector
            self.XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
            self.XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
            self.YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
            self.YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min

            #
            # pressed
            #
            PRESSED = set()
            if cmdfile is None:
                txt = None
            else:
                txt = open(cmdfile, "w")
            t0 = time.time()
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"Error in make ptz handler function: \n {e}")
        def handle_key_press(key):
            if self.mainWindow.isActiveWindow():
                try:
                    try:
                        key = key.char
                    except AttributeError:
                        key = str(key)

                    if key not in PRESSED:
                        PRESSED.add(key)
                        # print("* pressed: " + key)
                    else:
                        # the user is holding down the key
                        return

                    t = time.time() - t0

                    if key == "i":  # p
                        self.zoom_up(MainWindow.ptz)
                        print(self.get_position(MainWindow ,MainWindow.ptz, MainWindow.media_profile))
                        if txt is None:
                            print("+")
                        else:
                            txt.write("%.2f\t--\t%s\n" % (t, "+"))
                            txt.flush()
                    if key == "o":  # m
                        self.zoom_down(MainWindow.ptz)
                        print(self.get_position(MainWindow ,MainWindow.ptz, MainWindow.media_profile))
                        if txt is None:
                            print("-")
                        else:
                            txt.write("%.2f\t--\t%s\n" % (t, "-"))
                            txt.flush()
                except Exception as e:
                    ErrorHandler.displayErrorMessage(f"Error in handle key press function: \n {e}")

        def handle_key_release(key):
            if self.mainWindow.isActiveWindow():
                try:
                    try:
                        key = key.char
                    except AttributeError:
                        key = str(key)

                    t = time.time() - t0

                    if key in PRESSED:
                        PRESSED.remove(key)
                        if len(PRESSED) == 0:
                            self.stop_move(MainWindow.ptz)
                            if txt is None:
                                print("x")
                            else:
                                txt.write("%.2f\t--\t%s\n" % (t, "x"))
                                txt.flush()
                    # print("* released: " + key)
                except Exception as e:
                    ErrorHandler.displayErrorMessage(f"Error in handle key release: \n {e}")

        listener = keyboard.Listener(on_press=handle_key_press, on_release=handle_key_release)
        listener.start()

    
    def zeep_pythonvalue(self, xmlvalue):
        return xmlvalue
    def zoom_up(self, ptz):
        try:
            self.request.Velocity.Zoom.x = 1
            self.request.Velocity.PanTilt.x = 0
            self.request.Velocity.PanTilt.y = 0
            ptz.ContinuousMove(self.request)
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error message in zoom up")


    def zoom_down(self, ptz):
        try:
            self.request.Velocity.Zoom.x = -1
            self.request.Velocity.PanTilt.x = 0
            self.request.Velocity.PanTilt.y = 0
            ptz.ContinuousMove(self.request)
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error message in zoom down")


    def stop_move(self, ptz):
        try:
            ptz.Stop({'ProfileToken': self.request.ProfileToken})
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error message in stop move")

    def displayErrorMessage(self, message):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setWindowTitle("Error")
        msgBox.setText(message)
        msgBox.exec_()
    def move_to_position(self, ptz, x, y):
        try:
            # set position to x, y
            print("Moving to position")
            self.requestAbsolute.Position.PanTilt.x = x
            self.requestAbsolute.Position.PanTilt.y = y

            ptz.AbsoluteMove(self.requestAbsolute)
        except Exception as e:
            print(f"Error moving the camera: {str(e)}")
