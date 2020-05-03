from PyQt5 import QtWidgets, uic
import sys


# ---------------------Home Window Class--------------------- #
class Home(QtWidgets.QMainWindow):
    def __init__(self):
        super(Home, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('home.ui', self)  # Load the .ui file

        # ---------------------Find Button Widgets--------------------- #
        self.ModesButton = self.findChild(QtWidgets.QPushButton, 'Modes')
        self.MinVolButton = self.findChild(QtWidgets.QPushButton, 'MinVol')
        self.PEEPButton = self.findChild(QtWidgets.QPushButton, 'PEEP')
        self.OxygenButton = self.findChild(QtWidgets.QPushButton, 'Oxygen')
        self.ControlsButton = self.findChild(QtWidgets.QPushButton, 'Controls')
        self.AlarmsButton = self.findChild(QtWidgets.QPushButton, 'Alarms')
        self.SystemButton = self.findChild(QtWidgets.QPushButton, 'System')
        self.EventsButton = self.findChild(QtWidgets.QPushButton, 'Events')
        self.UtilitiesButton = self.findChild(QtWidgets.QPushButton, 'Utilities')
        self.MonitoringButton = self.findChild(QtWidgets.QPushButton, 'Monitoring')

        # ---------------------Connect Buttons to Methods--------------------- #
        self.ModesButton.clicked.connect(self.openModesWindow)

        self.show()  # Show the GUI

    # ---------------------Methods--------------------- #
    def openModesWindow(self):
        self.ModesWindow = Modes()
        self.ModesWindow.show()


# ---------------------Modes Window Class--------------------- #
class Modes(QtWidgets.QMainWindow):
    def __init__(self):
        super(Modes, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('modes.ui', self)  # Load the .ui file

        # ---------------------Find Button Widgets--------------------- #
        self.CMVButton = self.findChild(QtWidgets.QPushButton, 'CMV')
        self.SIMVButton = self.findChild(QtWidgets.QPushButton, 'SIMV')
        self.PCVButton = self.findChild(QtWidgets.QPushButton, 'PCV')
        self.PSIMVButton = self.findChild(QtWidgets.QPushButton, 'PISMV')
        self.SPONTButton = self.findChild(QtWidgets.QPushButton, 'SPONT')
        self.DuoPAPButton = self.findChild(QtWidgets.QPushButton, 'DuoPAP')
        self.APRVButton = self.findChild(QtWidgets.QPushButton, 'APRV')
        self.ASVButton = self.findChild(QtWidgets.QPushButton, 'ASV')
        self.NIVButton = self.findChild(QtWidgets.QPushButton, 'NIV')
        self.NIVSTButton = self.findChild(QtWidgets.QPushButton, 'NIVST')
        self.CMVButton = self.findChild(QtWidgets.QPushButton, 'CMV')
        self.CancelButton = self.findChild(QtWidgets.QPushButton, 'Cancel')
        self.ConfirmButton = self.findChild(QtWidgets.QPushButton, 'Confirm')

        # ---------------------Connect Buttons to Methods--------------------- #
        self.CancelButton.clicked.connect(self.cancel)
        self.ConfirmButton.clicked.connect(self.confirm)

    # ---------------------Methods--------------------- #
    def confirm(self):
        # add save code here
        self.close()

    def cancel(self):
        self.close()



app = QtWidgets.QApplication(sys.argv)  # Create an instance of QtWidgets.QApplication
window = Home()  # Create an instance of our class

app.exec_()  # Start the application
