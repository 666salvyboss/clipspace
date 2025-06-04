import sqlite3

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QCheckBox, QLineEdit
from PyQt5.QtCore import Qt
import sys
from PyQt5.QtGui import QIcon

from PY_flow import decrypt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.butn = QPushButton("copy history", self)
        self.butn_2 = QPushButton("Search", self)


        self.label = QLabel("Work at your pace", self)

        self.setWindowTitle("Alive 1")
        self.setGeometry(500, 50 , 200, 200)
        self.setWindowIcon(QIcon("cenastartscreen1.png"))

        self.checkbox = QCheckBox("delete", self)

        self.text_screen = QLineEdit(self)
        self.initui()


    def initui(self):
        self.butn.setGeometry(50,150,100, 40)
        self.butn.setStyleSheet("font-size: 10px;")
        self.butn.clicked.connect(self.on_click)

        self.label.setGeometry(0,150,500,100)
        self.label.setStyleSheet("font-size: 13px;")

        self.checkbox.setGeometry(0,50,500,100)
        self.checkbox.setStyleSheet("font-site: 30px;"
                                    "font-family: Arial;")
        self.checkbox.setChecked(False)
        self.checkbox.stateChanged.connect(self.checkbox_changed)

        self.text_screen.setGeometry(10, 10, 200, 40)
        self.text_screen.setStyleSheet("font-style: 25px;"
                                       "font-family: Bold;")
        self.text_screen.setPlaceholderText("search")

        self.butn_2.setGeometry(210, 10, 100, 40)
        self.butn_2.clicked.connect(self.submit)

    def checkbox_changed(self, state):
        if state == Qt.Checked:
            print("working")

    def submit(self):
        text = self.text_screen.text()
        print(text)

    def on_click(self):
        self.butn.setText("Clicked!")
        self.butn.setDisabled(True)
        self.label.setText("software for everyone")


def main():
    app = QApplication(sys.argv)  # used to process any command line argument intended for it
    window = MainWindow()
    window.show()  # displays window default behaviour is to hide itself
    sys.exit(app.exec_())  # waits for user input

if __name__ == "__main__":
    main()