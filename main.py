from PyQt5 import QtWidgets, uic
import sys

# ---------------------Default Values--------------------- #
PCMode = False
VCMode = True
Vt = 510
Pcontrol = 9
PEEP = 5
Oxygen = 50

PatHeight = 174
PatIBW = 0


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
        self.VCButton = self.findChild(QtWidgets.QPushButton, 'VC')
        self.PCButton = self.findChild(QtWidgets.QPushButton, 'PC')
        self.MaleButton = self.findChild(QtWidgets.QPushButton, 'Male')
        self.FemaleButton = self.findChild(QtWidgets.QPushButton, 'Female')
        self.PatHeightButton = self.findChild(QtWidgets.QPushButton, 'PatHeight')
        self.PreopCheckButton = self.findChild(QtWidgets.QPushButton, 'PreopCheck') # Don't need
        self.StartVentilationButton = self.findChild(QtWidgets.QPushButton, 'StartVentilation')
        self.IBWLabel = self.findChild(QtWidgets.QLabel, 'IBW')

        # -----------For testing-----------
        self.plusminus = PlusMinus()
        self.plus = self.plusminus.plusButton
        self.minus = self.plusminus.minusButton

        # ---------------------Connect Buttons to Methods--------------------- #
        self.MaleButton.clicked.connect(self.maleIBW)
        self.FemaleButton.clicked.connect(self.femaleIBW)
        self.PatHeightButton.clicked.connect(self.buttonState)
        self.plus.clicked.connect(self.PatAddHeight)
        self.minus.clicked.connect(self.PatSubtractHeight)
        self.StartVentilationButton.clicked.connect(self.startVentilation)

        if PCMode:
            self.PCButton.setChecked(True)
            self.VCButton.setChecked(False)
        elif VCMode:
            self.VCButton.setChecked(True)
            self.PCButton.setChecked(False)

        self.show()

    def buttonState(self):
        if self.PatHeightButton.isChecked():
            self.plusminus.show()
        else:
            self.plusminus.close()

    def startVentilation(self):
        global PCMode, VCMode
        if self.PCButton.isChecked():
            PCMode = True
            VCMode = False
            homeWindow.ventModeLabel.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; font-weight:600;\">PC</span></p></body></html>")
            homeWindow.VolPresButton.setText("{}\ncmH2O".format(str(Pcontrol)))
            homeWindow.VolPresLabel.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:14pt;\">Pcontrol</span></p><p align=\"center\"><br/></p></body></html>")
        elif self.VCButton.isChecked():
            VCMode = True
            PCMode = False
            homeWindow.ventModeLabel.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; font-weight:600;\">VC</span></p></body></html>")
            homeWindow.VolPresButton.setText("{}\nml".format(str(Vt)))
            homeWindow.VolPresLabel.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:14pt;\">Vt</span></p><p align=\"center\"><br/></p></body></html>")
        self.close()

    def PatAddHeight(self):
        global PatHeight
        if self.PatHeightButton.isChecked():
            PatHeight += 2
            if self.MaleButton.isChecked():
                self.maleIBW()
            elif self.FemaleButton.isChecked():
                self.femaleIBW()

    def PatSubtractHeight(self):
        global PatHeight
        if self.PatHeightButton.isChecked():
            PatHeight -= 2
            if self.MaleButton.isChecked():
                self.maleIBW()
            elif self.FemaleButton.isChecked():
                self.femaleIBW()

    def maleIBW(self):
        global PatIBW, PatHeight
        self.PatHeightButton.setText("{}\ncm".format(str(PatHeight)))
        PatIBW = int(round(50+(0.91*(PatHeight - 152.4)), 0)) # Calculate IBW and round
        self.IBWLabel.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:28pt;\">{}</span></p></body></html>".format(str(PatIBW)))

    def femaleIBW(self):
        global PatIBW, PatHeight
        self.PatHeightButton.setText("{}\ncm".format(str(PatHeight)))
        PatIBW = int(round(45.5+(0.91*(PatHeight - 152.4)), 0)) # Calculate IBW and round
        self.IBWLabel.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:28pt;\">{}</span></p></body></html>".format(str(PatIBW)))


# ---------------------Home Window Class--------------------- #
class Home(QtWidgets.QMainWindow):
    def __init__(self):
        super(Home, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('home.ui', self)  # Load the .ui file

        # ---------------------Find Widgets--------------------- #
        self.ModesButton = self.findChild(QtWidgets.QPushButton, 'Modes')
        self.VolPresButton = self.findChild(QtWidgets.QPushButton, 'VolPres')
        self.PEEPButton = self.findChild(QtWidgets.QPushButton, 'PEEP')
        self.OxygenButton = self.findChild(QtWidgets.QPushButton, 'Oxygen')
        self.ControlsButton = self.findChild(QtWidgets.QPushButton, 'Controls')
        self.AlarmsButton = self.findChild(QtWidgets.QPushButton, 'Alarms')
        self.SystemButton = self.findChild(QtWidgets.QPushButton, 'System')
        self.EventsButton = self.findChild(QtWidgets.QPushButton, 'Events')
        self.UtilitiesButton = self.findChild(QtWidgets.QPushButton, 'Utilities')
        self.MonitoringButton = self.findChild(QtWidgets.QPushButton, 'Monitoring')

        self.ventModeLabel = self.findChild(QtWidgets.QLabel, 'Ventilation_Mode')
        self.VolPresLabel = self.findChild(QtWidgets.QLabel, 'VolPres_Label')

        # -----------For testing-----------
        self.plusminus = PlusMinus()
        self.plus = self.plusminus.plusButton
        self.minus = self.plusminus.minusButton

        # ---------------------Connect Buttons to Methods--------------------- #
        self.ModesButton.clicked.connect(self.openModesWindow)
        self.VolPresButton.clicked.connect(self.buttonState)
        self.PEEPButton.clicked.connect(self.buttonState)
        self.OxygenButton.clicked.connect(self.buttonState)
        self.plus.clicked.connect(self.plusClicked)
        self.minus.clicked.connect(self.minusClicked)

        self.show()  # Show the GUI

    # ---------------------Methods--------------------- #
    def buttonState(self):
        if self.VolPresButton.isChecked() or self.PEEPButton.isChecked() or self.OxygenButton.isChecked():
            self.plusminus.show()
        else:
            self.plusminus.close()

    def plusClicked(self):
        global Vt, Pcontrol, PEEP, Oxygen, VCMode, PCMode
        if self.VolPresButton.isChecked():
            if VCMode:
                Vt += 10
                self.VolPresButton.setText("{}\nml".format(str(Vt)))
            elif PCMode:
                Pcontrol += 1
                self.VolPresButton.setText("{}\ncmH2O".format(str(Pcontrol)))

        elif self.PEEPButton.isChecked():
            PEEP += 1
            self.PEEPButton.setText("{}\ncmH2O".format(str(PEEP)))
        elif self.OxygenButton.isChecked():
            Oxygen += 1
            self.OxygenButton.setText("{}\n%".format(str(Oxygen)))

    def minusClicked(self):
        global Vt, Pcontrol, PEEP, Oxygen, VCMode, PCMode
        if self.VolPresButton.isChecked():
            if VCMode:
                Vt -= 10
                self.VolPresButton.setText("{}\nml".format(str(Vt)))
            elif PCMode:
                Pcontrol -= 1
                self.VolPresButton.setText("{}\ncmH2O".format(str(Pcontrol)))

        elif self.PEEPButton.isChecked():
            PEEP -= 1
            self.PEEPButton.setText("{}\ncmH2O".format(str(PEEP)))
        elif self.OxygenButton.isChecked():
            Oxygen -= 1
            self.OxygenButton.setText("{}\n%".format(str(Oxygen)))

    def openModesWindow(self):
        self.ModesWindow = Modes()
        self.ModesWindow.show()


# ---------------------Modes Window Class--------------------- #
class Modes(QtWidgets.QMainWindow):
    def __init__(self):
        super(Modes, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('modes.ui', self)  # Load the .ui file
        global PCMode, VCMode

        # ---------------------Find Widgets--------------------- #
        self.PCButton = self.findChild(QtWidgets.QPushButton, 'PC')
        self.VCButton = self.findChild(QtWidgets.QPushButton, 'VC')
        self.CancelButton = self.findChild(QtWidgets.QPushButton, 'Cancel')
        self.ConfirmButton = self.findChild(QtWidgets.QPushButton, 'Confirm')

        # ---------------------Connect Buttons to Methods--------------------- #
        self.CancelButton.clicked.connect(self.cancel)
        self.ConfirmButton.clicked.connect(self.confirm)

        if PCMode:
            self.PCButton.setChecked(True)
            self.VCButton.setChecked(False)
        elif VCMode:
            self.VCButton.setChecked(True)
            self.PCButton.setChecked(False)

    # ---------------------Methods--------------------- #
    def confirm(self):
        global PCMode, VCMode
        if self.PCButton.isChecked():
            PCMode = True
            VCMode = False
            homeWindow.ventModeLabel.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; font-weight:600;\">PC</span></p></body></html>")
            homeWindow.VolPresButton.setText("{}\ncmH2O".format(str(Pcontrol)))
            homeWindow.VolPresLabel.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:14pt;\">Pcontrol</span></p><p align=\"center\"><br/></p></body></html>")
        elif self.VCButton.isChecked():
            VCMode = True
            PCMode = False
            homeWindow.ventModeLabel.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; font-weight:600;\">VC</span></p></body></html>")
            homeWindow.VolPresButton.setText("{}\nml".format(str(Vt)))
            homeWindow.VolPresLabel.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:14pt;\">Vt</span></p><p align=\"center\"><br/></p></body></html>")
        self.close()

    def cancel(self):
        self.close()


app = QtWidgets.QApplication(sys.argv)  # Create an instance of QtWidgets.QApplication
homeWindow = Home()  # Create an instance of our class
startWindow = Start()

app.exec_()  # Start the application