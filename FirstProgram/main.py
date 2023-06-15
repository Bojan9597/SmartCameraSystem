import sys
from PyQt5.QtWidgets import QApplication
from LogInWindow import LoginWindow
from MainWindow import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = MainWindow()
    login_window = LoginWindow()

    login_window.loginSuccessful.connect(main_window.handleLogin)

    main_window.show()
    login_window.show()

    sys.exit(app.exec_())
