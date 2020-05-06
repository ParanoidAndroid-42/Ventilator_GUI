from PyQt5 import QtWidgets, uic
import sys

PCMode = True
VCMode = False


# ---------------------Plus Minus Window Class--------------------- #
class PlusMinus(QtWidgets.QMainWindow):
    def __init__(self):
        super(PlusMinus, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('plusMinus.ui', self)  # Load the .ui file

        # ---------------------Find Widgets--------------------- #
        self.plusButton = self.findChild(QtWidgets.QPushButton, 'plus')
        self.minusButton = self.findChild(QtWidgets.QPushButton, 'minus')


# ---------------------Start Window Class--------------------- #
class Start(QtWidgets.QMainWindow):
    def __init__(self):
        super(Start, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('start.ui', self)  # Load the .ui file

        # ---------------------Find Widgets--------------------- #
        self.ASVButton = self.findChild(QtWidgets.QPushButton, 'ASV')
        self.NIVButton = self.findChild(QtWidgets.QPushButton, 'NIV')
        self.CPRButton = self.findChild(QtWidgets.QPushButton, 'CPR')
        self.MaleButton = self.findChild(QtWidgets.QPushButton, 'Male')
        self.FemaleButton = self.findChild(QtWidgets.QPushButton, 'Female')
        self.PatHeightButton = self.findChild(QtWidgets.QPushButton, 'PatHeight')
        self.PreopCheckButton = self.findChild(QtWidgets.QPushButton, 'PreopCheck')
        self.StartVentilationButton = self.findChild(QtWidgets.QPushButton, 'StartVentilation')
        self.IBWLabel = self.findChild(QtWidgets.QLabel, 'IBW')

        # -----------For testing-----------
        self.plusminus = PlusMinus()
        self.plus = self.plusminus.plusButton
        self.minus = self.plusminus.minusButton

        self.PatHeight = 174
        self.PatIBW = 0

        # ---------------------Connect Buttons to Methods--------------------- #
        self.MaleButton.clicked.connect(self.maleIBW)
        self.FemaleButton.clicked.connect(self.femaleIBW)
        self.PatHeightButton.clicked.connect(self.buttonState)
        self.plus.clicked.connect(self.PatAddHeight)
        self.minus.clicked.connect(self.PatSubtractHeight)
        self.StartVentilationButton.clicked.connect(self.startVentilation)

        self.show()

    def buttonState(self):
        if self.PatHeightButton.isChecked():
            self.plusminus.show()
        else:
            self.plusminus.close()

    def startVentilation(self):
        # save settings and start ventilation
        self.close()

    def PatAddHeight(self):
        if self.PatHeightButton.isChecked():
            self.PatHeight += 2
            if self.MaleButton.isChecked():
                self.maleIBW()
            elif self.FemaleButton.isChecked():
                self.femaleIBW()

    def PatSubtractHeight(self):
        if self.PatHeightButton.isChecked():
            self.PatHeight -= 2
            if self.MaleButton.isChecked():
                self.maleIBW()
            elif self.FemaleButton.isChecked():
                self.femaleIBW()

    def maleIBW(self):
        self.PatHeightButton.setText("{}\ncm".format(str(self.PatHeight)))
        self.PatIBW = int(round(50+(0.91*(self.PatHeight - 152.4)), 0)) # Calculate IBW and round
        self.IBWLabel.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:28pt;\">{}</span></p></body></html>".format(str(self.PatIBW)))

    def femaleIBW(self):
        self.PatHeightButton.setText("{}\ncm".format(str(self.PatHeight)))
        self.PatIBW = int(round(45.5+(0.91*(self.PatHeight - 152.4)), 0)) # Calculate IBW and round
        self.IBWLabel.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:28pt;\">{}</span></p></body></html>".format(str(self.PatIBW)))


# ---------------------Home Window Class--------------------- #
class Home(QtWidgets.QMainWindow):
    def __init__(self):
        super(Home, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('home.ui', self)  # Load the .ui file

        # ---------------------Find Widgets--------------------- #
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

        self.ventModeLabel = self.findChild(QtWidgets.QLabel, 'Ventilation_Mode')

        # -----------For testing-----------
        self.plusminus = PlusMinus()
        self.plus = self.plusminus.plusButton
        self.minus = self.plusminus.minusButton

        self.MinVol = 100
        self.PEEP = 5
        self.Oxygen = 50

        # ---------------------Connect Buttons to Methods--------------------- #
        self.ModesButton.clicked.connect(self.openModesWindow)
        self.MinVolButton.clicked.connect(self.buttonState)
        self.PEEPButton.clicked.connect(self.buttonState)
        self.OxygenButton.clicked.connect(self.buttonState)
        self.plus.clicked.connect(self.plusClicked)
        self.minus.clicked.connect(self.minusClicked)

        self.show()  # Show the GUI

    # ---------------------Methods--------------------- #
    def buttonState(self):
        if self.MinVolButton.isChecked():
            self.plusminus.show()
            #self.PEEPButton.setChecked(False)
            #self.OxygenButton.setChecked(False)
        elif self.PEEPButton.isChecked():
            self.plusminus.show()
            #self.OxygenButton.setChecked(False)
            #self.MinVolButton.setChecked(False)
        elif self.OxygenButton.isChecked:
            self.plusminus.show()
            #self.PEEPButton.setChecked(False)
            #self.MinVolButton.setChecked(False)
        else:
            self.plusminus.close()

    def plusClicked(self):
        if self.MinVolButton.isChecked():
            self.MinVol += 5
            self.MinVolButton.setText("{}\n%".format(str(self.MinVol)))
        elif self.PEEPButton.isChecked():
            self.PEEP += 1
            self.PEEPButton.setText("{}\ncmH2O".format(str(self.PEEP)))
        elif self.OxygenButton.isChecked():
            self.Oxygen += 1
            self.OxygenButton.setText("{}\n%".format(str(self.Oxygen)))

    def minusClicked(self):
        if self.MinVolButton.isChecked():
            self.MinVol -= 5
            self.MinVolButton.setText("{}\n%".format(str(self.MinVol)))
        elif self.PEEPButton.isChecked():
            self.PEEP -= 1
            self.PEEPButton.setText("{}\ncmH2O".format(str(self.PEEP)))
        elif self.OxygenButton.isChecked():
            self.Oxygen -= 1
            self.OxygenButton.setText("{}\n%".format(str(self.Oxygen)))

    def openModesWindow(self):
        self.ModesWindow = Modes()
        self.ModesWindow.show()


# ---------------------Modes Window Class--------------------- #
class Modes(QtWidgets.QMainWindow):
    def __init__(self):
        super(Modes, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('modes.ui', self)  # Load the .ui file

        # ---------------------Find Widgets--------------------- #
        self.PCButton = self.findChild(QtWidgets.QPushButton, 'PC')
        self.VCButton = self.findChild(QtWidgets.QPushButton, 'VC')
        self.CancelButton = self.findChild(QtWidgets.QPushButton, 'Cancel')
        self.ConfirmButton = self.findChild(QtWidgets.QPushButton, 'Confirm')

        # ---------------------Connect Buttons to Methods--------------------- #
        self.PCButton.clicked.connect(self.activate_PC_mode)
        self.VCButton.clicked.connect(self.activate_VC_mode)
        self.CancelButton.clicked.connect(self.cancel)
        self.ConfirmButton.clicked.connect(self.confirm)

    # ---------------------Methods--------------------- #
    def activate_PC_mode(self):
        if self.PCButton.isChecked():
            PCMode = True
            VCMode = False
            homeWindow.ventModeLabel.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; font-weight:600;\">PC</span></p></body></html>")

    def activate_VC_mode(self):
        if self.VCButton.isChecked():
            VCMode = True
            PCMode = False
            homeWindow.ventModeLabel.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; font-weight:600;\">VC</span></p></body></html>")

    def confirm(self):
        # add save code here
        self.close()

    def cancel(self):
        self.close()


app = QtWidgets.QApplication(sys.argv)  # Create an instance of QtWidgets.QApplication
homeWindow = Home()  # Create an instance of our class
startWindow = Start()

app.exec_()  # Start the application