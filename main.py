from PyQt5.QtWidgets import QDesktopWidget
from PyQt5 import QtWidgets, QtCore, uic
from smbus2 import SMBus
import pyqtgraph as pg
import subprocess
import threading
import time
import sys

bus = SMBus(1)
addr = 0x8

pg.setConfigOption('background', (10, 10, 30))
graphResolution = 10
Xscale = 100

testMode = False
if not testMode:
    from pyky040 import pyky040
# ---------------------Default Values--------------------- #
graphTimeout = 10

Vt = 510
Pcontrol = 9
PEEP = 5
Oxygen = 50
Rate = 14
I_Ratio = 1
E_Ratio = 1
Flowtrigger = 5
PatHeight = 174
PatIBW = 0
PCMode = False
VCMode = True
StopFlow = True
StopVolume = False

Vt_register = 1
BPM_register = 2
I_Ratio_register = 3
E_Ratio_register = 4
PEEP_register = 5
volume_register = 6
flow_register = 7
pressure_register = 8


# --------------------Functions--------------------- #
def send_packet(address, register, value):
    packet = []
    while value > 255:
        packet.append(255)
        value -= 255
    if value > 0:
        packet.append(value)

    packet.insert(0, register)
    bus.write_i2c_block_data(address, 0, packet)

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
        x = int((screen.width() / 2) - (widget.width() / 2))
        y = int((screen.height() - widget.height()) / 2)
        self.move(x - 400, y + 120)

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

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        # ---------------------Find Widgets--------------------- #
        self.VCButton = self.findChild(QtWidgets.QPushButton, 'VC')
        self.PCButton = self.findChild(QtWidgets.QPushButton, 'PC')
        self.MaleButton = self.findChild(QtWidgets.QPushButton, 'Male')
        self.FemaleButton = self.findChild(QtWidgets.QPushButton, 'Female')
        self.PatHeightButton = self.findChild(QtWidgets.QPushButton, 'PatHeight')
        self.PreopCheckButton = self.findChild(QtWidgets.QPushButton, 'PreopCheck')  # Don't need
        self.StartVentilationButton = self.findChild(QtWidgets.QPushButton, 'StartVentilation')
        self.IBWLabel = self.findChild(QtWidgets.QLabel, 'IBW')

        # -----------For testing-----------
        # self.plusminus = PlusMinus()
        # self.plus = self.plusminus.plusButton
        # self.minus = self.plusminus.minusButton

        # ---------------------Connect Buttons to Methods--------------------- #
        self.PCButton.clicked.connect(self.setPCMode)
        self.VCButton.clicked.connect(self.setVCMode)
        self.MaleButton.clicked.connect(self.maleIBW)
        self.FemaleButton.clicked.connect(self.femaleIBW)
        # self.PatHeightButton.clicked.connect(self.buttonState)
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
        self.move(x - 90, y + 20)

    # def buttonState(self):
    #     if self.PatHeightButton.isChecked():
    #         self.plusminus.show()
    #     else:
    #         self.plusminus.close()

    def setPCMode(self):
        global PCMode, VCMode
        if self.PCButton.isChecked():
            PCMode = True
            VCMode = False
            homeWindow.ventModeLabel.setText(
                "<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; font-weight:600;\">PC</span></p></body></html>")
            homeWindow.VolPresButton.setText("{}\ncmH2O".format(str(Pcontrol)))
            homeWindow.VolPresLabel.setText(
                "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt;\">Pcontrol</span></p><p align=\"center\"><br/></p></body></html>")

    def setVCMode(self):
        global PCMode, VCMode
        if self.VCButton.isChecked():
            VCMode = True
            PCMode = False
            homeWindow.ventModeLabel.setText(
                "<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; font-weight:600;\">VC</span></p></body></html>")
            homeWindow.VolPresButton.setText("{}\nml".format(str(Vt)))
            homeWindow.VolPresLabel.setText(
                "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt;\">Vt</span></p><p align=\"center\"><br/></p></body></html>")

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
        Vt = 8 * PatIBW  # Calculate initial Vt setting
        self.PatHeightButton.setText("{}\ncm".format(str(PatHeight)))
        self.IBWLabel.setText(
            "<html><head/><body><p align=\"center\"><span style=\" font-size:28pt;\">{}</span></p></body></html>".format(
                str(PatIBW)))
        if VCMode:
            homeWindow.VolPresButton.setText("{}\nml".format(str(Vt)))

    def femaleIBW(self):
        global PatIBW, PatHeight, Vt, VCMode
        PatIBW = int(round(45.5 + (0.91 * (PatHeight - 152.4)), 0))  # Calculate IBW and round
        Vt = 8 * PatIBW  # Calculate initial Vt setting
        self.PatHeightButton.setText("{}\ncm".format(str(PatHeight)))
        self.IBWLabel.setText(
            "<html><head/><body><p align=\"center\"><span style=\" font-size:28pt;\">{}</span></p></body></html>".format(
                str(PatIBW)))
        if VCMode:
            homeWindow.VolPresButton.setText("{}\nml".format(str(Vt)))


# ---------------------Home Window Class--------------------- #
class Home(QtWidgets.QMainWindow):
    def __init__(self):
        super(Home, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('raspberry_pi/home.ui', self)  # Load the .ui file
        global Xscale, graphResolution, testMode

        # ---------------------Find Widgets--------------------- #
        self.ModesButton = self.findChild(QtWidgets.QPushButton, 'Modes')
        self.VolPresButton = self.findChild(QtWidgets.QPushButton, 'VolPres')
        self.PEEPButton = self.findChild(QtWidgets.QPushButton, 'PEEP')
        # self.OxygenButton = self.findChild(QtWidgets.QPushButton, 'Oxygen')
        self.ControlsButton = self.findChild(QtWidgets.QPushButton, 'Controls')
        self.AlarmsButton = self.findChild(QtWidgets.QPushButton, 'Alarms')
        self.SystemButton = self.findChild(QtWidgets.QPushButton, 'System')
        self.EventsButton = self.findChild(QtWidgets.QPushButton, 'Events')
        self.UtilitiesButton = self.findChild(QtWidgets.QPushButton, 'Utilities')
        self.MonitoringButton = self.findChild(QtWidgets.QPushButton, 'Monitoring')
        self.WarningButton = self.findChild(QtWidgets.QPushButton, 'Warning')

        self.ventModeLabel = self.findChild(QtWidgets.QLabel, 'Ventilation_Mode')
        self.VolPresLabel = self.findChild(QtWidgets.QLabel, 'VolPres_Label')

        # -----------Graph Setup---------
        pg.setConfigOptions(antialias=True)
        self.volumeGraph = self.findChild(QtWidgets.QWidget, 'VolumeWidget')
        self.volumeXAxis = self.volumeGraph.getAxis("bottom")
        self.volumeCurve = self.volumeGraph.getPlotItem().plot()

        self.flowGraph = self.findChild(QtWidgets.QWidget, 'FlowWidget')
        self.flowXAxis = self.flowGraph.getAxis("bottom")
        self.flowCurve = self.flowGraph.getPlotItem().plot()

        self.pressureGraph = self.findChild(QtWidgets.QWidget, 'PressureWidget')
        self.pressureXAxis = self.pressureGraph.getAxis("bottom")
        self.pressureCurve = self.pressureGraph.getPlotItem().plot()

        self.timer = QtCore.QTimer()
        self.volumeData = [0]
        self.flowData = [0]
        self.pressureData = [0]
        self.volumeFirstRun = True
        self.flowFirstRun = True
        self.pressureFirstRun = True

        for i in range(Xscale * graphResolution):
            self.volumeData.append(0)
        for i in range(Xscale * graphResolution):
            self.flowData.append(0)
        for i in range(Xscale * graphResolution):
            self.pressureData.append(0)
        self.dataIndex = 0

        # -----------Encoder Setup---------
        if not testMode:
            self.inc_counter = 0
            self.dec_counter = 0
            self.encoder = pyky040.Encoder(CLK=17, DT=18, SW=26)
            self.encoder.setup(loop=True, step=1, inc_callback=self.increment, dec_callback=self.decrement)
            self.encoder_thread = threading.Thread(target=self.encoder.watch)
            self.encoder_thread.start()

        # ---------------------Connect Buttons to Methods--------------------- #
        self.ModesButton.clicked.connect(self.openModesWindow)
        self.SystemButton.clicked.connect(self.openSystemWindow)
        self.ControlsButton.clicked.connect(self.openControlsWindow)
        self.WarningButton.clicked.connect(self.warningAcknowledged)
        self.VolPresButton.clicked.connect(self.VolPresClicked)
        self.PEEPButton.clicked.connect(self.PEEPClicked)
        # self.OxygenButton.clicked.connect(self.buttonState)
        # self.plus.clicked.connect(self.plusClicked)
        # self.minus.clicked.connect(self.minusClicked)

        self.WarningButton.hide()
        self.setScreenLocation()
        self.warningTimeout = time.time() + 3
        self.volumePlotter()
        self.flowRatePlotter()
        self.pressurePlotter()
        # self.show()
        if not testMode:
            self.showFullScreen()  # Show the GUI
        else:
            self.show()

    # ---------------------Methods--------------------- #
    def volumePlotter(self):
        global Xscale, graphResolution, graphTimeout
        if self.volumeFirstRun:
            self.volumeGraph.hideButtons()
            self.volumeGraph.setMouseEnabled(x=False, y=False)
            self.volumeGraph.setMenuEnabled(enableMenu=False)
            self.volumeGraph.setRange(xRange=(0, Xscale * graphResolution), yRange=(0, 800), disableAutoRange=True)
            self.volumeXAxis.setScale(scale=((graphResolution / 100) / graphResolution))
            self.volumeGraph.setLabel("left", text="Volume ml")
            self.volumeCurve.setPen(pg.mkPen('g'))
            self.timer.timeout.connect(self.volumeUpdater)
            self.timer.start(graphTimeout)
            self.volumeFirstRun = False
        else:
            self.timer.timeout.connect(self.volumeUpdater)

    def volumeUpdater(self):
        global Xscale, graphResolution, StopVolume
        self.volumeData[:-1] = self.volumeData[1:]
        try:
            string = ''
            send_packet(addr, volume_register, 1)
            block = bus.read_i2c_block_data(addr, 0, 7)
            block1 = bus.read_i2c_block_data(addr, 0, 7)
            if block == block1:
                for i in block:
                    string += chr(i)
                try:
                    self.volumeData[-1] = float(string)
                except ValueError:
                    self.volumeUpdater()
                string = ''
                self.warningTimeout = time.time() + 3
        except OSError:
            if time.time() > self.warningTimeout:
                self.setWarning(1)
                self.warningTimeout = time.time() + 3
        self.volumeCurve.setData(self.volumeData, antialias=True)
        # if self.dataIndex <= Xscale*graphResolution:  #and int(shared.get('breathCounter')) < 3: #
        #     self.volumeData[self.dataIndex] = int(shared.get('lungVolume'))
        #     self.curve.setData(self.volumeData)
        #     self.dataIndex += 1
        # else: #int(shared.get('breathCounter')) == 3:
        #     self.dataIndex = 0
        #     self.curve.setData(self.volumeData, antialias=True)

    def flowRatePlotter(self):
        global Xscale, graphResolution, graphTimeout
        if self.flowFirstRun:
            self.flowGraph.hideButtons()
            self.flowGraph.setMouseEnabled(x=False, y=False)
            self.flowGraph.setMenuEnabled(enableMenu=False)
            self.flowGraph.setRange(xRange=(0, Xscale * graphResolution), yRange=(-100, 100), disableAutoRange=True)
            self.flowXAxis.setScale(scale=((graphResolution / 100) / graphResolution))
            # self.graph.addLine(y=0, x=None)
            self.flowGraph.setLabel("left", text="Flow L/min")
            self.flowCurve.setPen(pg.mkPen('m', width=2))
            self.timer.timeout.connect(self.flowRateUpdater)
            self.timer.start(graphTimeout)
            self.flowFirstRun = False
        else:
            self.timer.timeout.connect(self.flowRateUpdater)

    def flowRateUpdater(self):
        global Xscale, graphResolution, StopFlow
        self.flowData[:-1] = self.flowData[1:]
        try:
            string = ''
            send_packet(addr, flow_register, 1)
            block = bus.read_i2c_block_data(addr, 0, 7)
            block1 = bus.read_i2c_block_data(addr, 0, 7)
            if block == block1:
                for i in block:
                    string += chr(i)

                try:
                    self.flowData[-1] = float(string)
                except ValueError:
                    self.flowRateUpdater()
                string = ''
                self.warningTimeout = time.time() + 3
        except OSError:
            if time.time() > self.warningTimeout:
                self.setWarning(1)
                self.warningTimeout = time.time() + 3
        self.flowCurve.setData(self.flowData, antialias=True)
        # if self.dataIndex <= Xscale*graphResolution and int(shared.get('breathCounter')) < 3:
        #     #self.flowData[self.dataIndex] = slider.flowRate.value()
        #     self.flowData[self.dataIndex] = int(float(shared.get('flow')))
        #     self.curve.setData(self.flowData)
        #     self.dataIndex += 1
        # elif int(shared.get('breathCounter')) == 3:
        #     self.dataIndex = 0
        #     self.curve.setData(self.flowData, antialias=True)

    def pressurePlotter(self):
        global Xscale, graphResolution, graphTimeout
        if self.pressureFirstRun:
            self.pressureGraph.hideButtons()
            self.pressureGraph.setMouseEnabled(x=False, y=False)
            self.pressureGraph.setMenuEnabled(enableMenu=False)
            self.pressureGraph.setRange(xRange=(0, Xscale * graphResolution), yRange=(0, 20), disableAutoRange=True)
            self.pressureXAxis.setScale(scale=((graphResolution / 100) / graphResolution))
            self.pressureGraph.setLabel("left", text="Paw cmH2O")
            self.pressureCurve.setPen(pg.mkPen('y'))
            self.timer.timeout.connect(self.pressureUpdater)
            self.timer.start(graphTimeout)
            self.pressureFirstRun = False
        else:
            self.timer.timeout.connect(self.pressureUpdater)

    def pressureUpdater(self):
        global Xscale, graphResolution, StopVolume
        self.pressureData[:-1] = self.pressureData[1:]
        try:
            string = ''
            send_packet(addr, pressure_register, 1)
            block = bus.read_i2c_block_data(addr, 0, 5)
            block1 = bus.read_i2c_block_data(addr, 0, 5)
            if block == block1:
                for i in block:
                    string += chr(i)

                try:
                    self.pressureData[-1] = float(string)
                except ValueError:
                    self.pressureUpdater()
                string = ''
                self.warningTimeout = time.time() + 3
        except OSError:
            if time.time() > self.warningTimeout:
                self.setWarning(1)
                self.warningTimeout = time.time() + 3
        self.pressureCurve.setData(self.pressureData, antialias=True)

    def setScreenLocation(self):
        screen = QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = (screen.width() / 2) - (widget.width() / 2)
        y = (screen.height() - widget.height()) / 2
        self.move(x, y)

    def VolPresClicked(self):
        if self.PEEPButton.isChecked():
            self.PEEPButton.setChecked(False)

    def PEEPClicked(self):
        if self.VolPresButton.isChecked():
            self.VolPresButton.setChecked(False)

    def increment(self, scale_position):
        if self.inc_counter > 1:
            self.plusClicked()
            self.inc_counter = 0
            self.dec_counter = 0
        else:
            self.inc_counter += 1

    def decrement(self, scale_position):
        if self.dec_counter > 1:
            self.minusClicked()
            self.dec_counter = 0
            self.inc_counter = 0
        else:
            self.dec_counter += 1

    def plusClicked(self):
        global Vt, Pcontrol, PEEP, Oxygen, VCMode, PCMode
        if self.VolPresButton.isChecked():
            if VCMode:
                Vt += 10
                self.VolPresButton.setText("{}\nml".format(str(Vt)))
                send_packet(addr, Vt_register, Vt)
            elif PCMode:
                Pcontrol += 1
                self.VolPresButton.setText("{}\ncmH2O".format(str(Pcontrol)))

        elif self.PEEPButton.isChecked():
            PEEP += 1
            self.PEEPButton.setText("{}\ncmH2O".format(str(PEEP)))
            send_packet(addr, PEEP_register, PEEP)

        # elif self.OxygenButton.isChecked():
        #     Oxygen += 1
        #     self.OxygenButton.setText("{}\n%".format(str(Oxygen)))

    def minusClicked(self):
        global Vt, Pcontrol, PEEP, Oxygen, VCMode, PCMode
        if self.VolPresButton.isChecked():
            if VCMode:
                Vt -= 10
                self.VolPresButton.setText("{}\nml".format(str(Vt)))
                send_packet(addr, Vt_register, Vt)
            elif PCMode:
                Pcontrol -= 1
                self.VolPresButton.setText("{}\ncmH2O".format(str(Pcontrol)))

        elif self.PEEPButton.isChecked():
            PEEP -= 1
            self.PEEPButton.setText("{}\ncmH2O".format(str(PEEP)))
            send_packet(addr, PEEP_register, PEEP)

        # elif self.OxygenButton.isChecked():
        #     Oxygen -= 1
        #     self.OxygenButton.setText("{}\n%".format(str(Oxygen)))

    def openModesWindow(self):
        self.ModesWindow = Modes()
        self.ModesWindow.show()

    def openMonitoringWindow(self):
        self.MonitoringWindow = Monitoring()
        self.MonitoringWindow.show()

    def openSystemWindow(self):
        self.SystemWindow = System()
        self.SystemWindow.show()

    def openControlsWindow(self):
        self.VolPresButton.setChecked(False)
        self.PEEPButton.setChecked(False)
        self.ControlsWindow = Controls()
        self.ControlsWindow.show()

    def setWarning(self, warning_number):
        if warning_number == 1:                             # Control board disconnected
            self.WarningButton.setText("CB Disconnected")
            self.WarningButton.show()

    def warningAcknowledged(self):
        self.WarningButton.hide()


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
        x = int((screen.width() / 2) - (widget.width() / 2))
        y = int((screen.height() - widget.height()) / 2)
        self.move(x + 10, y - 60)

    def confirm(self):
        global PCMode, VCMode
        if self.PCButton.isChecked():
            PCMode = True
            VCMode = False
            homeWindow.ventModeLabel.setText(
                "<html><head/><body><p align=\"center\"><span style=\" font-size:26pt; font-weight:600;\">PC</span></p></body></html>")
            homeWindow.VolPresButton.setText("{}\ncmH2O".format(str(Pcontrol)))
            homeWindow.VolPresLabel.setText(
                "<html><head/><body><p align=\"center\"><span style=\" font-size:16pt;\">Pcontrol</span></p><p align=\"center\"><br/></p></body></html>")
        elif self.VCButton.isChecked():
            VCMode = True
            PCMode = False
            homeWindow.ventModeLabel.setText(
                "<html><head/><body><p align=\"center\"><span style=\" font-size:26pt; font-weight:600;\">VC</span></p></body></html>")
            homeWindow.VolPresButton.setText("{}\nml".format(str(Vt)))
            homeWindow.VolPresLabel.setText(
                "<html><head/><body><p align=\"center\"><span style=\" font-size:16pt;\">Vt</span></p><p align=\"center\"><br/></p></body></html>")
        self.close()

    def cancel(self):
        self.close()


# ---------------------System Window Class--------------------- #
class System(QtWidgets.QMainWindow):
    def __init__(self):
        super(System, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('raspberry_pi/system.ui', self)  # Load the .ui file
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        # ---------------------Find Widgets--------------------- #
        self.ShutdownButton = self.findChild(QtWidgets.QPushButton, 'shutdown')
        self.CancelButton = self.findChild(QtWidgets.QPushButton, 'cancel')

        # ---------------------Connect Buttons to Methods--------------------- #
        self.ShutdownButton.clicked.connect(self.shutdownMethod)
        self.CancelButton.clicked.connect(self.cancelMethod)

        self.setScreenLocation()

        # ---------------------Methods--------------------- #

    def setScreenLocation(self):
        screen = QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = int((screen.width() / 2) - (widget.width() / 2))
        y = int((screen.height() - widget.height()) / 2)
        self.move(x - 50, y - 100)

    def shutdownMethod(self):
        homeWindow.close()
        self.close()

    def cancelMethod(self):
        self.close()


# ---------------------Controls Window Class--------------------- #
class Controls(QtWidgets.QMainWindow):
    def __init__(self):
        global I_Ratio, E_Ratio, Rate, Flowtrigger, testMode
        super(Controls, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('raspberry_pi/controls.ui', self)  # Load the .ui file
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        # ---------------------Find Widgets--------------------- #
        self.ConfirmButton = self.findChild(QtWidgets.QPushButton, 'Confirm')
        self.CancelButton = self.findChild(QtWidgets.QPushButton, 'Cancel')
        self.IERatioButton = self.findChild(QtWidgets.QPushButton, 'IERatio')
        self.RateButton = self.findChild(QtWidgets.QPushButton, 'Rate')
        self.FlowtriggerButton = self.findChild(QtWidgets.QPushButton, 'Flowtrigger')

        # -----------Encoder Setup---------
        if not testMode:
            self.inc_counter = 0
            self.dec_counter = 0
            self.encoder = pyky040.Encoder(CLK=17, DT=18, SW=26)
            self.encoder.setup(loop=True, step=1, inc_callback=self.increment, dec_callback=self.decrement)
            self.encoder_thread = threading.Thread(target=self.encoder.watch)
            self.encoder_thread.start()

        # ---------------------Connect Buttons to Methods--------------------- #
        self.ConfirmButton.clicked.connect(self.confirmMethod)
        self.CancelButton.clicked.connect(self.cancelMethod)
        self.IERatioButton.clicked.connect(self.IEClicked)
        self.RateButton.clicked.connect(self.RateClicked)
        self.FlowtriggerButton.clicked.connect(self.FlowClicked)

        self.setScreenLocation()
        self.IERatioButton.setText("{}:{}".format(str(I_Ratio), str(E_Ratio)))
        self.RateButton.setText("{}\nb/min".format(str(Rate)))
        self.FlowtriggerButton.setText("{}\nl/min".format(str(Flowtrigger)))

        # ---------------------Methods--------------------- #

    def setScreenLocation(self):
        screen = QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = int((screen.width() / 2) - (widget.width() / 2))
        y = int((screen.height() - widget.height()) / 2)
        self.move(x + 5, y + 60)

    def increment(self, scale_position):
        if self.inc_counter > 1:
            self.plusClicked()
            self.inc_counter = 0
            self.dec_counter = 0
        else:
            self.inc_counter += 1

    def decrement(self, scale_position):
        if self.dec_counter > 1:
            self.minusClicked()
            self.dec_counter = 0
            self.inc_counter = 0
        else:
            self.dec_counter += 1

    def plusClicked(self):
        global I_Ratio, E_Ratio, Rate, Flowtrigger
        if self.IERatioButton.isChecked():
            if I_Ratio >= E_Ratio:
                I_Ratio = round(I_Ratio + .1, 2)
                self.IERatioButton.setText("{}:{}".format(str(I_Ratio), str(E_Ratio)))
            elif E_Ratio > I_Ratio:
                E_Ratio = round(E_Ratio - .1, 2)
                self.IERatioButton.setText("{}:{}".format(str(I_Ratio), str(E_Ratio)))
            I_Ratio_int = int(I_Ratio*100)
            E_Ratio_int = int(E_Ratio*100)
            send_packet(addr, I_Ratio_register, I_Ratio_int)
            send_packet(addr, E_Ratio_register, E_Ratio_int)

        elif self.RateButton.isChecked():
            Rate += 1
            self.RateButton.setText("{}\nb/min".format(str(Rate)))
            send_packet(addr, BPM_register, Rate)

        elif self.FlowtriggerButton.isChecked():
            Flowtrigger += .5
            self.FlowtriggerButton.setText("{}\nl/min".format(str(Flowtrigger)))
            # shared.set('Flowtrigger', Flowtrigger)  # -------------------------------------- Add I2C

    def minusClicked(self):
        global I_Ratio, E_Ratio, Rate, Flowtrigger

        if self.IERatioButton.isChecked():
            if E_Ratio >= I_Ratio:
                E_Ratio = round(E_Ratio + .1, 2)
                self.IERatioButton.setText("{}:{}".format(str(I_Ratio), str(E_Ratio)))
            elif I_Ratio > E_Ratio:
                I_Ratio = round(I_Ratio - .1, 2)
                self.IERatioButton.setText("{}:{}".format(str(I_Ratio), str(E_Ratio)))
            I_Ratio_int = int(I_Ratio * 100)
            E_Ratio_int = int(E_Ratio * 100)
            send_packet(addr, I_Ratio_register, I_Ratio_int)
            send_packet(addr, E_Ratio_register, E_Ratio_int)

        elif self.RateButton.isChecked():
            Rate -= 1
            self.RateButton.setText("{}\nb/min".format(str(Rate)))
            send_packet(addr, BPM_register, Rate)

        elif self.FlowtriggerButton.isChecked():
            Flowtrigger -= .5
            self.FlowtriggerButton.setText("{}\nl/min".format(str(Flowtrigger)))
            # shared.set('Flowtrigger', Flowtrigger)  # -------------------------------------- Add I2C

    def cancelMethod(self):
        self.IERatioButton.setChecked(False)
        self.RateButton.setChecked(False)
        self.FlowtriggerButton.setChecked(False)
        self.close()

    def confirmMethod(self):
        self.IERatioButton.setChecked(False)
        self.RateButton.setChecked(False)
        self.FlowtriggerButton.setChecked(False)
        self.close()

    def IEClicked(self):
        if self.RateButton.isChecked():
            self.RateButton.setChecked(False)
        if self.FlowtriggerButton.isChecked():
            self.FlowtriggerButton.setChecked(False)

    def RateClicked(self):
        if self.IERatioButton.isChecked():
            self.IERatioButton.setChecked(False)
        if self.FlowtriggerButton.isChecked():
            self.FlowtriggerButton.setChecked(False)

    def FlowClicked(self):
        if self.IERatioButton.isChecked():
            self.IERatioButton.setChecked(False)
        if self.RateButton.isChecked():
            self.RateButton.setChecked(False)


app = QtWidgets.QApplication(sys.argv)  # Create an instance of QtWidgets.QApplication
homeWindow = Home()  # Create an instance of our class
app.exec_()  # Start the application

# model = subprocess.Popen(['python3', 'VCModel_v2.py'])
