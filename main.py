# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from classes.mainwindow import MainWindow
import sys
from PyQt5.QtWidgets import QApplication

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # print_hi('PyCharm')
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    app.exec()
