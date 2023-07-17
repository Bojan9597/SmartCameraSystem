import sys
from pynput import keyboard
from onvif import ONVIFCamera
import zeep
import time
from ErrorHandler import ErrorHandler

class Ptz_Handler:
    XMAX = +1
    XMIN = -1
    YMAX = +1
    YMIN = -1
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
            ErrorHandler.displayErrorMessage(f"Error in get PTZ position: \n {str(e)}")
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
            self.request.ConfigurationToken = MainWindow.media_profile.PTZConfiguration.token
            ptz_configuration_options = MainWindow.ptz.GetConfigurationOptions(self.request)

            self.request = MainWindow.ptz.create_type('ContinuousMove')
            self.request.ProfileToken = MainWindow.media_profile.token
            MainWindow.ptz.Stop({'ProfileToken': MainWindow.media_profile.token})

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
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error in making ptz Handler : \n {e}")

        #
        # pressed
        #
        PRESSED = set()
        if cmdfile is None:
            txt = None
        else:
            txt = open(cmdfile, "w")
        t0 = time.time()

        def handle_key_press(key, MainWindow):
            if MainWindow.isActiveWindow():
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

                    if key == "W" or key == "w" or key == "Key.up":  # w
                        self.move_up(MainWindow, MainWindow.ptz)
                        print(self.get_position(MainWindow ,MainWindow.ptz, MainWindow.media_profile))
                        if txt is None:
                            print("^")
                        else:
                            txt.write("%.2f\t--\t%s\n" % (t, "^"))
                            txt.flush()
                    if key == "S" or key == "s" or key == "Key.down":  # s
                        self.move_down(MainWindow, MainWindow.ptz)
                        print(self.get_position(MainWindow ,MainWindow.ptz, MainWindow.media_profile))
                        if txt is None:
                            print("v")
                        else:
                            txt.write("%.2f\t--\t%s\n" % (t, "v"))
                            txt.flush()
                    if key == "A" or key == "a" or key == "Key.left":  # a
                        self.move_left(MainWindow, MainWindow.ptz)
                        print(self.get_position(MainWindow ,MainWindow.ptz, MainWindow.media_profile))
                        if txt is None:
                            print("<")
                        else:
                            txt.write("%.2f\t--\t%s\n" % (t, "<"))
                            txt.flush()
                    if key == "D" or key == "d" or key == "Key.right":  # d
                        self.move_right(MainWindow, MainWindow.ptz)
                        print(self.get_position(MainWindow ,MainWindow.ptz, MainWindow.media_profile))
                        if txt is None:
                            print(">")
                        else:
                            txt.write("%.2f\t--\t%s\n" % (t, ">"))
                            txt.flush()
                    if key == "I" or key == "i":  # p
                        self.zoom_up(MainWindow, MainWindow.ptz)
                        print(self.get_position(MainWindow ,MainWindow.ptz, MainWindow.media_profile))
                        if txt is None:
                            print("+")
                        else:
                            txt.write("%.2f\t--\t%s\n" % (t, "+"))
                            txt.flush()
                    if key == "O" or key == "o":  # m
                        self.zoom_down(MainWindow, MainWindow.ptz)
                        print(self.get_position(MainWindow ,MainWindow.ptz, MainWindow.media_profile))
                        if txt is None:
                            print("-")
                        else:
                            txt.write("%.2f\t--\t%s\n" % (t, "-"))
                            txt.flush()

                except Exception as e:
                    ErrorHandler.displayErrorMessage(f"This is error in handle key press in PTZ handler: \n {e}")

        def handle_key_release(key):
            try:
                try:
                    key = key.char
                except AttributeError:
                    key = str(key)

                t = time.time() - t0

                if key in PRESSED:
                    PRESSED.remove(key)
                    if len(PRESSED) == 0:
                        self.stop_move(MainWindow, MainWindow.ptz)
                        if txt is None:
                            print("x")
                        else:
                            txt.write("%.2f\t--\t%s\n" % (t, "x"))
                            txt.flush()
                # print("* released: " + key)
            except Exception as e:
                ErrorHandler.displayErrorMessage(f"This is error message in handle key release in PTZ handler: \n {e}")

        listener = keyboard.Listener(on_press=lambda event: handle_key_press(event, MainWindow), on_release=handle_key_release)
        listener.start()

    def zeep_pythonvalue(self, xmlvalue):
        return xmlvalue

    def move_up(self, MainWindow, ptz):
        try:
            self.request.Velocity.Zoom.x = 0
            self.request.Velocity.PanTilt.x = 0
            self.request.Velocity.PanTilt.y = self.YMAX
            ptz.ContinuousMove(self.request)
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error message in move up: \n {e}" )

    def move_down(self,MainWindow, ptz):
        try:
            self.request.Velocity.Zoom.x = 0
            self.request.Velocity.PanTilt.x = 0
            self.request.Velocity.PanTilt.y = self.YMIN
            ptz.ContinuousMove(self.request)
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error message in move down: \n {e}" )

    def move_right(self, MainWindow, ptz):
        try:
            self.request.Velocity.Zoom.x = 0
            self.request.Velocity.PanTilt.x = self.XMAX
            self.request.Velocity.PanTilt.y = 0
            ptz.ContinuousMove(self.request)
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error message in move right: \n {e}" )

    def move_left(self, MainWindow, ptz):
        try:
            self.request.Velocity.Zoom.x = 0
            self.request.Velocity.PanTilt.x = self.XMIN
            self.request.Velocity.PanTilt.y = 0
            ptz.ContinuousMove(self.request)
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error message in move left: \n {e}" )

    def zoom_up(self, MainWindow, ptz):
        try:
            self.request.Velocity.Zoom.x = 1
            self.request.Velocity.PanTilt.x = 0
            self.request.Velocity.PanTilt.y = 0
            ptz.ContinuousMove(self.request)
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error message in zoom up: \n {e}" )

    def zoom_down(self, MainWindow, ptz):
        try:
            self.request.Velocity.Zoom.x = -1
            self.request.Velocity.PanTilt.x = 0
            self.request.Velocity.PanTilt.y = 0
            ptz.ContinuousMove(self.request)
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error message in zoom down: \n {e}" )

    def stop_move(self, MainWindow, ptz):
        try:
            ptz.Stop({'ProfileToken': self.request.ProfileToken})
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error message in stop move: \n {e}" )

