from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
import sys
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Alive 1")
        self.setGeometry(500, 50 , 200, 200)
        self.setWindowIcon(QIcon("cenastartscreen1.png"))
        label = QLabel("HELLO WORLD", self) # self refers to the window we call  below and instantiated above
        label.setFont(QFont("Arial", 15))
        label.setGeometry(0,0, 500, 100)
        label.setStyleSheet("color: #292929;"""
                            "background-color: #6fdcf7;"
                            "font-weight: bold;"
                            "font-style: italic;"
                            "text-decoration: underline;")
        label.setAlignment(Qt.AlignTop) # allign vertically
    def initui(self):
        pass
def main():
    app = QApplication(sys.argv) # used to process any command line argument intended for it
    window = MainWindow()
    window.show() # displays window default behaviour is to hide itself
    sys.exit(app.exec_()) # waits for user input

if __name__ == "__main__":
    main()