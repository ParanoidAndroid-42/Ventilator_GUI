from PyQt5 import QtWidgets, uic
import sys
from windows import *

app = QtWidgets.QApplication(sys.argv)  # Create an instance of QtWidgets.QApplication
homeWindow = Home()  # Create an instance of our class
startWindow = Start()

app.exec_()  # Start the application
