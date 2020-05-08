from PyQt5.QtWidgets import QDesktopWidget
from PyQt5 import QtWidgets, QtCore, uic
from pyky040 import pyky040
import pyqtgraph as pg
import threading
import sys

import pymemcache
shared = pymemcache.Client(('localhost', 11211))

pg.setConfigOption('background', (10, 10, 30))
graphResolution = 20
Xscale = 100

# ---------------------Default Values--------------------- #
Vt = 510
Pcontrol = 9
PEEP = 5
Oxygen = 50
PatHeight = 174
PatIBW = 0
PCMode = False
VCMode = True
StopFlow = True
StopVolume = False
# ---------------------Sensor Values--------------------- #
flowRateSensor = 0
pressureSensor = 0


# ---------------------Plus Minus Window Class--------------------- #
class FlowSlider(QtWidgets.QMainWindow):
    def __init__(self):
        super(FlowSlider, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('flowSlider.ui', self)  # Load the .ui file

        # ---------------------Find Widgets--------------------- #
        self.flowRate = self.findChild(QtWidgets.QSlider, 'flowRate')

        self.show()


# ---------------------Plus Minus Window Class--------------------- #
class PlusMinus(QtWidgets.QMainWindow):
    def __init__(self):
        super(PlusMinus, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('plusMinus.ui', self)  # Load the .ui file

        # ---------------------Find Widgets--------------------- #
        self.plusButton = self.findChild(QtWidgets.QPushButton, 'plus')
        self.minusButton = self.findChild(QtWidgets.QPushButton, 'minus')


# ---------------------Monitoring Window Class--------------------- #
class Monitoring(QtWidgets.QMainWindow):
    def __init__(self):
        super(Monitoring, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('raspberry_pi/monitoring.ui', self)  # Load the .ui file
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        # ---------------------Find Widgets--------------------- #
        self.flow = self.findChild(QtWidgets.QPushButton, 'Flow')
        self.volume = self.findChild(QtWidgets.QPushButton, 'Volume')

        # ---------------------Connect Buttons to Methods--------------------- #
        self.flow.clicked.connect(self.setFlow)
        self.volume.clicked.connect(self.setVolume)

        self.cleared = False

        self.setScreenLocation()

        # ---------------------Methods--------------------- #
    def setScreenLocation(self):
        screen = QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = (screen.width() / 2) - (widget.width() / 2)
        y = (screen.height() - widget.height()) / 2
        self.move(x - 300, y + 150)

    def setFlow(self):
        global StopVolume, StopFlow
        StopVolume = True
        StopFlow = False
        homeWindow.dataIndex = 0
        homeWindow.flowRatePlotter()
        self.close()

    def setVolume(self):
        global StopVolume, StopFlow
        StopVolume = False
        StopFlow = True
        homeWindow.dataIndex = 0
        homeWindow.volumePlotter()
        self.close()


# ---------------------Start Window Class--------------------- #
class Start(QtWidgets.QMainWindow):
    def __init__(self):
        super(Start, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('start.ui', self)  # Load the .ui file

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowStaysOnTopHint)


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
        self.PCButton.clicked.connect(self.setPCMode)
        self.VCButton.clicked.connect(self.setVCMode)
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

        self.setScreenLocation()
        self.show()

        # ---------------------Methods--------------------- #
    def setScreenLocation(self):
        screen = QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = (screen.width() / 2) - (widget.width() / 2)
        y = (screen.height() - widget.height()) / 2
        self.move(x-90, y+20)

    def buttonState(self):
        if self.PatHeightButton.isChecked():
            self.plusminus.show()
        else:
            self.plusminus.close()

    def setPCMode(self):
        global PCMode, VCMode
        if self.PCButton.isChecked():
            PCMode = True
            VCMode = False
            homeWindow.ventModeLabel.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; font-weight:600;\">PC</span></p></body></html>")
            homeWindow.VolPresButton.setText("{}\ncmH2O".format(str(Pcontrol)))
            homeWindow.VolPresLabel.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:14pt;\">Pcontrol</span></p><p align=\"center\"><br/></p></body></html>")

    def setVCMode(self):
        global PCMode, VCMode
        if self.VCButton.isChecked():
            VCMode = True
            PCMode = False
            homeWindow.ventModeLabel.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; font-weight:600;\">VC</span></p></body></html>")
            homeWindow.VolPresButton.setText("{}\nml".format(str(Vt)))
            homeWindow.VolPresLabel.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:14pt;\">Vt</span></p><p align=\"center\"><br/></p></body></html>")

    def startVentilation(self):
        # start ventilation code
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
        global PatIBW, PatHeight, Vt, VCMode
        PatIBW = int(round(50 + (0.91 * (PatHeight - 152.4)), 0))  # Calculate IBW and round
        Vt = 8 * PatIBW                                            # Calculate initial Vt setting
        self.PatHeightButton.setText("{}\ncm".format(str(PatHeight)))
        self.IBWLabel.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:28pt;\">{}</span></p></body></html>".format(str(PatIBW)))
        if VCMode:
            homeWindow.VolPresButton.setText("{}\nml".format(str(Vt)))

    def femaleIBW(self):
        global PatIBW, PatHeight, Vt, VCMode
        PatIBW = int(round(45.5 + (0.91 * (PatHeight - 152.4)), 0))  # Calculate IBW and round
        Vt = 8 * PatIBW                                              # Calculate initial Vt setting
        self.PatHeightButton.setText("{}\ncm".format(str(PatHeight)))
        self.IBWLabel.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:28pt;\">{}</span></p></body></html>".format(str(PatIBW)))
        if VCMode:
            homeWindow.VolPresButton.setText("{}\nml".format(str(Vt)))


# ---------------------Home Window Class--------------------- #
class Home(QtWidgets.QMainWindow):
    def __init__(self):
        super(Home, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('raspberry_pi/home.ui', self)  # Load the .ui file
        global Xscale, graphResolution

        # ---------------------Find Widgets--------------------- #
        self.ModesButton = self.findChild(QtWidgets.QPushButton, 'Modes')
        self.VolPresButton = self.findChild(QtWidgets.QPushButton, 'VolPres')
        self.PEEPButton = self.findChild(QtWidgets.QPushButton, 'PEEP')
        #self.OxygenButton = self.findChild(QtWidgets.QPushButton, 'Oxygen')
        self.ControlsButton = self.findChild(QtWidgets.QPushButton, 'Controls')
        self.AlarmsButton = self.findChild(QtWidgets.QPushButton, 'Alarms')
        self.SystemButton = self.findChild(QtWidgets.QPushButton, 'System')
        self.EventsButton = self.findChild(QtWidgets.QPushButton, 'Events')
        self.UtilitiesButton = self.findChild(QtWidgets.QPushButton, 'Utilities')
        self.MonitoringButton = self.findChild(QtWidgets.QPushButton, 'Monitoring')

        self.ventModeLabel = self.findChild(QtWidgets.QLabel, 'Ventilation_Mode')
        self.VolPresLabel = self.findChild(QtWidgets.QLabel, 'VolPres_Label')

        # Graph stuff
        pg.setConfigOptions(antialias=True)
        self.graph = self.findChild(QtWidgets.QWidget, 'graphWidget')
        self.xAxis = self.graph.getAxis("bottom")
        self.curve = self.graph.getPlotItem().plot()
        self.timer = QtCore.QTimer()
        self.volumeData = [0]
        self.flowData = [0]
        for i in range(Xscale*graphResolution):
            self.volumeData.append(0)
        for i in range(Xscale*graphResolution):
            self.flowData.append(0)
        self.dataIndex = 0

        # -----------Encoder Setup---------
        self.counter = 0
        self.encoder = pyky040.Encoder(CLK=17, DT=18, SW=26)
        self.encoder.setup(loop=True, step=1, inc_callback=self.increment, dec_callback=self.decrement)
        self.encoder_thread = threading.Thread(target=self.encoder.watch)
        self.encoder_thread.start()

        # -----------For testing-----------
        self.plusminus = PlusMinus()
        self.plus = self.plusminus.plusButton
        self.minus = self.plusminus.minusButton

        # ---------------------Connect Buttons to Methods--------------------- #
        self.ModesButton.clicked.connect(self.openModesWindow)
        self.MonitoringButton.clicked.connect(self.openMonitoringWindow)
        self.VolPresButton.clicked.connect(self.buttonState)
        self.PEEPButton.clicked.connect(self.buttonState)
        #self.OxygenButton.clicked.connect(self.buttonState)
        self.plus.clicked.connect(self.plusClicked)
        self.minus.clicked.connect(self.minusClicked)

        self.setScreenLocation()
        self.showFullScreen()  # Show the GUI

    # ---------------------Methods--------------------- #
    def volumePlotter(self):
        global Xscale, graphResolution, StopVolume
        self.graph.setMouseEnabled(x=False, y=False)
        self.graph.setMenuEnabled(enableMenu=False)
        self.graph.setRange(xRange=(0, Xscale * graphResolution), yRange=(0, 800), disableAutoRange=True)
        self.xAxis.setScale(scale=((graphResolution/100) / graphResolution))
        self.graph.setLabel("left", text="Volume ml")
        self.curve.setPen(pg.mkPen('g'))
        self.timer.timeout.connect(self.volumeUpdater)
        self.timer.start(0)

    def volumeUpdater(self):
        global Xscale, graphResolution, StopVolume
        if not StopVolume:
            self.volumeData[:-1] = self.volumeData[1:]
            self.volumeData[-1] = int(shared.get('lungVolume'))
            self.curve.setData(self.volumeData, antialias=True)

            # if self.dataIndex <= Xscale*graphResolution:  #and int(shared.get('breathCounter')) < 3: #
            #     self.volumeData[self.dataIndex] = int(shared.get('lungVolume'))
            #     self.curve.setData(self.volumeData)
            #     self.dataIndex += 1
            # else: #int(shared.get('breathCounter')) == 3:
            #     self.dataIndex = 0
            #     self.curve.setData(self.volumeData, antialias=True)

    def flowRatePlotter(self):
        global Xscale, graphResolution, StopFlow
        self.graph.setMouseEnabled(x=False, y=False)
        self.graph.setMenuEnabled(enableMenu=False)
        self.graph.setRange(xRange=(0, Xscale*graphResolution), yRange=(-100, 100), disableAutoRange=True)
        self.xAxis.setScale(scale=((graphResolution/100) / graphResolution))
        #self.graph.addLine(y=0, x=None)
        self.graph.setLabel("left", text="Flow L/min")
        self.curve.setPen(pg.mkPen('m', width=2))
        self.timer.timeout.connect(self.flowRateUpdater)
        self.timer.start(0)
        if StopFlow:
            self.timer.stop()

    def flowRateUpdater(self):
        global Xscale, graphResolution, StopFlow
        if not StopFlow:
            self.flowData[:-1] = self.flowData[1:]
            self.flowData[-1] = int(float(shared.get('flow')))
            self.curve.setData(self.flowData, antialias=True)

            # if self.dataIndex <= Xscale*graphResolution and int(shared.get('breathCounter')) < 3:
            #     #self.flowData[self.dataIndex] = slider.flowRate.value()
            #     self.flowData[self.dataIndex] = int(float(shared.get('flow')))
            #     self.curve.setData(self.flowData)
            #     self.dataIndex += 1
            # elif int(shared.get('breathCounter')) == 3:
            #     self.dataIndex = 0
            #     self.curve.setData(self.flowData, antialias=True)

    def setScreenLocation(self):
        screen = QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = (screen.width() / 2) - (widget.width() / 2)
        y = (screen.height() - widget.height()) / 2
        self.move(x, y)

    def buttonState(self):
        if self.VolPresButton.isChecked() or self.PEEPButton.isChecked():
            self.plusminus.show()
        else:
            self.plusminus.close()

    def increment(self, scale_position):
        if self.counter > 2:
            self.plusClicked()
        else:
            self.counter += 1

    def decrement(self, scale_position):
        if self.counter > 2:
            self.minusClicked()
        else:
            self.counter += 1

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
        # elif self.OxygenButton.isChecked():
        #     Oxygen += 1
        #     self.OxygenButton.setText("{}\n%".format(str(Oxygen)))

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
        # elif self.OxygenButton.isChecked():
        #     Oxygen -= 1
        #     self.OxygenButton.setText("{}\n%".format(str(Oxygen)))

    def openModesWindow(self):
        self.ModesWindow = Modes()
        self.ModesWindow.show()

    def openMonitoringWindow(self):
        self.MonitoringWindow = Monitoring()
        self.MonitoringWindow.show()


# ---------------------Modes Window Class--------------------- #
class Modes(QtWidgets.QMainWindow):
    def __init__(self):
        super(Modes, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('raspberry_pi/modes.ui', self)  # Load the .ui file
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
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

        self.setScreenLocation()

    # ---------------------Methods--------------------- #
    def setScreenLocation(self):
        screen = QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = (screen.width() / 2) - (widget.width() / 2)
        y = (screen.height() - widget.height()) / 2
        self.move(x+10, y-25)

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

app.exec_()  # Start the application
