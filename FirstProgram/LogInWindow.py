from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QGridLayout, QFileDialog
from PyQt5.QtCore import pyqtSignal
from ErrorHandler import ErrorHandler
import os

class LoginWindow(QWidget):
    loginSuccessful = pyqtSignal(str, str, str, str, str)
    fileSelected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(200, 200, 400, 200)

        self.selectedFile = ""
        # Create a grid layout
        grid = QGridLayout()
        self.setLayout(grid)

        # Create username label and textbox for the first column
        username_label1 = QLabel("Username:")
        username_textbox1 = QLineEdit()
        username_textbox1.setObjectName("username1")

        # Create password label and textbox for the first column
        password_label1 = QLabel("Password:")
        password_textbox1 = QLineEdit()
        password_textbox1.setEchoMode(QLineEdit.Password)  # Mask password with *
        password_textbox1.setObjectName("password1")

        # Create PTZ camera IP address label and textbox for the first column
        ip_label1 = QLabel("WA Camera IP:")
        ip_textbox1 = QLineEdit()
        ip_textbox1.setObjectName("ip_address1")

        # Create the login button for the first column
        login_button1 = QPushButton("Log In")
        login_button1.clicked.connect(lambda: self.login_clicked("1"))

        # Create username label and textbox for the second column
        username_label2 = QLabel("Username:")
        username_textbox2 = QLineEdit()
        username_textbox2.setObjectName("username2")

        # Create password label and textbox for the second column
        password_label2 = QLabel("Password:")
        password_textbox2 = QLineEdit()
        password_textbox2.setEchoMode(QLineEdit.Password)  # Mask password with *
        password_textbox2.setObjectName("password2")

        # Create PTZ camera IP address label and textbox for the second column
        ip_label2 = QLabel("PTZ Camera IP:")
        ip_textbox2 = QLineEdit()
        ip_textbox2.setObjectName("ip_address2")

        # Create the login button for the second column
        login_button2 = QPushButton("Log In")
        login_button2.clicked.connect(lambda: self.login_clicked("2"))

        # Create the file chooser button
        self.file_button = QPushButton("Choose File")
        self.file_button.clicked.connect(self.choose_file)

        # Add widgets to the grid layout for the first column
        grid.addWidget(username_label1, 0, 0)
        grid.addWidget(username_textbox1, 0, 1)
        grid.addWidget(password_label1, 1, 0)
        grid.addWidget(password_textbox1, 1, 1)
        grid.addWidget(ip_label1, 2, 0)
        grid.addWidget(ip_textbox1, 2, 1)
        grid.addWidget(login_button1, 3, 0, 1, 2)

        # Add widgets to the grid layout for the second column
        grid.addWidget(username_label2, 0, 2)
        grid.addWidget(username_textbox2, 0, 3)
        grid.addWidget(password_label2, 1, 2)
        grid.addWidget(password_textbox2, 1, 3)
        grid.addWidget(ip_label2, 2, 2)
        grid.addWidget(ip_textbox2, 2, 3)
        grid.addWidget(login_button2, 3, 2, 1, 2)

        # Add the file chooser button below the grid layout
        grid.addWidget(self.file_button, 4, 0, 1, 4)

        # Call the function to set default values for the left column
        self.set_default_values(username_textbox1, password_textbox1, ip_textbox1, "../SecondProgram/ConfigurationWA.txt")

        # Call the function to set default values for the right column
        self.set_default_values(username_textbox2, password_textbox2, ip_textbox2, "../SecondProgram/ConfigurationPTZ.txt")

    def choose_file(self):
        file_dialog = QFileDialog()
        file_dialog.exec_()
        selected_file = file_dialog.selectedFiles()
        if selected_file:
            print("Selected file:", selected_file[0])
        self.selectedFile = os.path.abspath(selected_file[0])
        self.file_button.setText(f"File is choosen: {self.selectedFile}")
        self.fileSelected.emit(self.selectedFile)

    def login_clicked(self, column):
        # Handle login button click
        print("Login clicked for column:", column)

    def login_clicked(self, source):
        try:
            # Retrieve the username, password, and IP address based on the source
            username = self.findChild(QLineEdit, f"username{source}").text()
            password = self.findChild(QLineEdit, f"password{source}").text()
            ip_address = self.findChild(QLineEdit, f"ip_address{source}").text()

            # Perform the login authentication (replace with your own logic)
            self.loginSuccessful.emit(source, username, password, ip_address, self.selectedFile)

            # Clear the username and password fields
            self.findChild(QLineEdit, f"username{source}").clear()
            self.findChild(QLineEdit, f"password{source}").clear()
            self.findChild(QLineEdit, f"ip_address{source}").clear()
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"This is error in login clicked function: \n {e}")

    def set_default_values(self, username_textbox, password_textbox, ip_textbox, config_file):
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as file:
                    lines = file.readlines()
                    if len(lines) >= 3:
                        username = lines[0].strip()
                        password = lines[1].strip()
                        ip_address = lines[2].strip()
                        username_textbox.setText(username)
                        password_textbox.setText(password)
                        ip_textbox.setText(ip_address)
            except Exception as e:
                ErrorHandler.displayErrorMessage(f"This is an error in setting default values in text boxes:\n{e}")
        else:
            print("Configuration files do not exist")



