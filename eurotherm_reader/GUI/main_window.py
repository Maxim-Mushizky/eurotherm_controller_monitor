# -*- coding: utf-8 -*-
"""
controller GUI
========
"""

import traceback, sys
from eurotherm_reader.GUI.styles import style, img
from eurotherm_reader.controller.eurotherm_controller import CK20
from eurotherm_reader.controller.serial_ports import SerialPorts
from eurotherm_reader.analysis.cal_analysis import ThermocoupleStatistics
from eurotherm_reader.GUI.auxilary_classes import MainWindow, Canvas, ThreadSignals, NewThread
from eurotherm_reader.GUI.about_window import About
from eurotherm_reader.GUI.data_analysis_window import TCDataAnalysis
from eurotherm_reader.GUI.help_window import Help
from eurotherm_reader.GUI.settings_window import Thermocouple_settings
from eurotherm_reader import __VERSION__

from datetime import datetime

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import (QThreadPool, Qt)
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from time import sleep


class Ui_MainWindow(QDialog):
    version = __VERSION__

    def setupUi(self, MainWindow):

        self.threadpool = QThreadPool()  # initate ThreadPool

        plt.style.use('seaborn-whitegrid')  # style to be used by all of the plots drawn
        self.temp_log = [[], []]  # init temp log

        self.temp_repr = Canvas(MainWindow, width=4.8, height=3.5, dpi=120)
        self.temp_repr.move(191, 131)
        self.toolbar = NavigationToolbar(self.temp_repr, self)
        ### CALL THE WINDOWS ###
        self.about = About()
        self.help = Help()
        self.tc_settings = Thermocouple_settings()
        self.tc_data_analysis = TCDataAnalysis()

        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.WindowModal)
        MainWindow.resize(805, 602)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(805, 602))
        MainWindow.setMaximumSize(QtCore.QSize(805, 602))
        MainWindow.setFocusPolicy(QtCore.Qt.ClickFocus)
        MainWindow.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(img["icon"]), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.Active
        MainWindow.setWindowIcon(icon)
        MainWindow.setWindowOpacity(0.95)
        MainWindow.setStyleSheet(style["main_window"])
        MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        MainWindow.setDocumentMode(True)
        MainWindow.setTabShape(QtWidgets.QTabWidget.Triangular)
        MainWindow.setDockNestingEnabled(True)
        MainWindow.setUnifiedTitleAndToolBarOnMac(False)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.com_port_select = QtWidgets.QComboBox(self.centralwidget)
        self.com_port_select.setGeometry(QtCore.QRect(20, 60, 111, 21))
        self.com_port_select.setWhatsThis("")
        self.com_port_select.setObjectName("com_port_select")

        self.go_button = QtWidgets.QPushButton(self.centralwidget)
        self.go_button.setGeometry(QtCore.QRect(20, 190, 51, 21))
        self.go_button.setObjectName("go_button")

        # button functionality
        self.go_button.clicked.connect(lambda: self.MainWindow_exec_thread(self.temp_mainloop))
        self.com_port_select_label = QtWidgets.QLabel(self.centralwidget)
        self.com_port_select_label.setGeometry(QtCore.QRect(20, 40, 111, 16))
        self.com_port_select_label.setObjectName("com_port_select_label")

        self.baudrate_select = QtWidgets.QComboBox(self.centralwidget)
        self.baudrate_select.setGeometry(QtCore.QRect(20, 110, 111, 21))
        self.baudrate_select.setObjectName("bauderate_select")
        self.baudrate_select.addItem("")
        self.baudrate_select.addItem("")
        self.baude_rate_select = QtWidgets.QLabel(self.centralwidget)
        self.baude_rate_select.setGeometry(QtCore.QRect(20, 90, 111, 16))
        self.baude_rate_select.setObjectName("baude_rate_select")
        self.timeout_label = QtWidgets.QLabel(self.centralwidget)
        self.timeout_label.setGeometry(QtCore.QRect(20, 140, 111, 16))
        self.timeout_label.setObjectName("timeout_label")

        self.temp_lcd1 = QtWidgets.QLCDNumber(self.centralwidget)
        self.temp_lcd1.setGeometry(QtCore.QRect(585, 50, 181, 51))
        self.temp_lcd1.setStyleSheet(style["temp_lcd_style"])
        self.temp_lcd1.setObjectName("temp_lcd")
        self.temp_lcd1.display(None)

        self.temp_lcd2 = QtWidgets.QLCDNumber(self.centralwidget)
        self.temp_lcd2.setGeometry(QtCore.QRect(190, 50, 181, 51))
        self.temp_lcd2.setStyleSheet(style["temp_lcd_style"])
        self.temp_lcd2.setObjectName("temp_lcd")
        self.temp_lcd2.display(None)

        self.temp_lcds = [self.temp_lcd1, self.temp_lcd2]

        self.timeout = QtWidgets.QLineEdit(self.centralwidget)
        self.timeout.setGeometry(QtCore.QRect(20, 160, 113, 20))
        self.timeout.setObjectName("timeout [s]")
        # preset value:
        self.timeout.setText(str(2))

        self.log_dir_path = r"../data"

        self.stop_button = QtWidgets.QPushButton(self.centralwidget)
        self.stop_button.setGeometry(QtCore.QRect(80, 190, 51, 21))
        self.stop_button.setObjectName("stop_button")
        # event stop_button
        self.stop_button.clicked.connect(self.state_temp_loop)
        self.msg_box = QtWidgets.QTextEdit(self.centralwidget)
        self.msg_box.setGeometry(QtCore.QRect(10, 230, 151, 251))
        self.msg_box.setStyleSheet(style["msg_box_style"])
        self.msg_box.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.msg_box.setObjectName("msg_box")
        self.prev_event = []  # previous log in the msg box
        self.output_dir = QtWidgets.QPushButton(self.centralwidget)
        self.output_dir.setGeometry(QtCore.QRect(10, 490, 151, 21))
        self.output_dir.setStyleSheet("")
        self.output_dir.setObjectName("output_dir")
        self.output_dir.clicked.connect(self.get_log_dir)

        self.icon = QtWidgets.QLabel(self.centralwidget)
        self.icon.setGeometry(QtCore.QRect(360, 0, 181, 31))
        self.icon.setText("")
        self.icon.setPixmap(QtGui.QPixmap(img["icon"]))
        self.icon.setScaledContents(True)
        self.icon.setObjectName("CISEMI")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(-20, 520, 831, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.status_label = QtWidgets.QLabel(self.centralwidget)
        self.status_label.setGeometry(QtCore.QRect(630, 540, 61, 16))
        self.status_label.setObjectName("status_label")
        self.led_light = QtWidgets.QLabel(self.centralwidget)
        self.led_light.setGeometry(QtCore.QRect(770, 540, 21, 21))
        self.led_light.setText("")
        self.led_light.setPixmap(QtGui.QPixmap(img["red_led"]))
        self.led_light.setScaledContents(True)
        self.led_light.setObjectName("led_light")
        self.connect_status = QtWidgets.QLabel(self.centralwidget)
        self.connect_status.setGeometry(QtCore.QRect(690, 540, 61, 21))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.connect_status.sizePolicy().hasHeightForWidth())
        self.connect_status.setSizePolicy(sizePolicy)
        self.connect_status.setText("")
        self.connect_status.setPixmap(QtGui.QPixmap(img["offline"]))
        self.connect_status.setScaledContents(True)
        self.connect_status.setObjectName("connect_status")
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setGeometry(QtCore.QRect(0, 30, 811, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_3.sizePolicy().hasHeightForWidth())
        self.line_3.setSizePolicy(sizePolicy)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.vers_label = QtWidgets.QLabel(self.centralwidget)
        self.vers_label.setGeometry(QtCore.QRect(10, 540, 161, 16))
        self.vers_label.setObjectName("vers_label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 805, 21))
        self.menubar.setObjectName("menubar")

        # headers in the toolbar
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuhelp = QtWidgets.QMenu(self.menubar)
        self.menuhelp.setObjectName("menuhelp")
        self.menusettings = QtWidgets.QMenu(self.menubar)
        self.menusettings.setObjectName("menusettings")
        MainWindow.setMenuBar(self.menubar)

        # actions in each toolbar header
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actioncom_port = QtWidgets.QAction(MainWindow)
        self.actioncom_port.setObjectName("actioncom_port")
        self.actionexit = QtWidgets.QAction(MainWindow)
        self.actionexit.setObjectName("actionexit")
        self.wipe_display = QtWidgets.QAction(MainWindow)
        self.wipe_display.setObjectName("wipe_display")
        self.actionabout = QtWidgets.QAction(MainWindow)
        self.actionabout.setObjectName("actionabout")
        self.actionhelp = QtWidgets.QAction(MainWindow)
        self.actionhelp.setObjectName("actionhelp")
        self.action_tc_settings = QtWidgets.QAction(MainWindow)
        self.action_tc_settings.setObjectName("TC settings")
        self.actionoutput = QtWidgets.QAction(MainWindow)
        self.actionoutput.setObjectName("actionoutput")
        self.menuFile.addAction(self.actioncom_port)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionexit)
        self.menuhelp.addAction(self.actionabout)
        self.menuhelp.addAction(self.actionhelp)
        self.tools = QtWidgets.QAction(MainWindow)
        self.tools.setObjectName("Tools")
        # Add additional tabs to the seetings tab
        self.menusettings.addAction(self.actionoutput)
        self.menusettings.addAction(self.wipe_display)
        self.menusettings.addAction(self.action_tc_settings)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menusettings.menuAction())
        self.menubar.addAction(self.menuhelp.menuAction())
        self.MainWindow_exec_thread(self.chk_ports)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # mouse over tool tip text
        self.output_dir.setToolTip("Select output directory for log files")
        self.go_button.setToolTip("Start temperature measurement")
        self.stop_button.setToolTip("Stop measuring")

        # Special variables
        self.len_of_com_list = 0  # update whenever the comlist has a change of length

    def state_temp_loop(self, state=False):
        self.temp_loop_actiator = state

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "TC controller"))
        self.go_button.setText(_translate("MainWindow", "&Go"))
        self.com_port_select_label.setText(_translate("MainWindow",
                                                      "<html><head/><body><p align=\"center\"><span style=\" font-size:10pt;\">Port</span></p></body></html>"))
        self.baudrate_select.setItemText(0, _translate("MainWindow", "9200"))
        self.baudrate_select.setItemText(1, _translate("MainWindow", "9600"))
        self.baude_rate_select.setText(_translate("MainWindow",
                                                  "<html><head/><body><p align=\"center\"><span style=\" font-size:10pt;\">baudrate</span></p></body></html>"))
        self.timeout_label.setText(
            _translate("MainWindow", "<html><head/><body><p align=\"center\">timeout [s]</p></body></html>"))
        self.stop_button.setText(_translate("MainWindow", "Stop"))
        self.output_dir.setText(_translate("MainWindow", "output directory"))
        self.status_label.setText(_translate("MainWindow", "status:"))
        self.vers_label.setText(
            _translate("MainWindow", f"<html><head/><body><p>{Ui_MainWindow.version}</p></body></html>"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuhelp.setTitle(_translate("MainWindow", "&Help"))
        self.menusettings.setTitle(_translate("MainWindow", "Settings"))

        self.actioncom_port.setText(_translate("MainWindow", "T&C Test analysis"))
        self.actionexit.setText(_translate("MainWindow", "Exit"))
        self.actionabout.setText(_translate("MainWindow", "A&bout"))
        self.actionhelp.setText(_translate("MainWindow", "Help"))
        self.actionoutput.setText(_translate("MainWindow", "Output to"))
        self.wipe_display.setText(_translate("MainWindow", "Clear display"))
        self.action_tc_settings.setText(_translate("MainWindow", "TC settings"))

        # shortcuts
        self.actionexit.setShortcut("Esc")
        self.actionoutput.setShortcut("Ctrl+F")
        self.action_tc_settings.setShortcut("Ctrl+Q")
        self.wipe_display.setShortcut("Ctrl+X")
        # actions :
        self.actionexit.triggered.connect(MainWindow.close)
        self.actionabout.triggered.connect(lambda: self.about.show())
        self.actionhelp.triggered.connect(lambda: self.help.show())
        self.action_tc_settings.triggered.connect(lambda: self.tc_settings.show())
        self.actionoutput.triggered.connect(self.get_log_dir)
        self.wipe_display.triggered.connect(self._wipe_log)
        self.actioncom_port.triggered.connect(lambda: self.tc_data_analysis.show())

    def get_log_dir(self):
        # Wrapper for function calling
        dir_selected = str(QFileDialog.getExistingDirectory(self, 'Select Directory', self.log_dir_path))
        if dir_selected != "":
            self.log_dir_path = dir_selected
            print(f"Log files will now be saved in: {self.log_dir_path}")

    def _wipe_log(self):
        """
        PRIVATE METHOD
        Wipe log of temperature from script's memory. The data is still available in the csv files
        """
        self.temp_log.clear()
        self.temp_log = [[], []]  # init a 2D array


    def find_ports(self):
        # purpose is to to find serial devices attached
        # I have given a really dumb solution for a problem of recognizing non controller/ET devices
        # It will only update the list if the number of devices changes
        # Should be fairly bugless however something must be lurking about for such a dumb solution
        # Anyone reading this- my sincere apology and try looking for HKEY_LOCAL_MACHINE PYQT soltuion in Stackoverflow
        self.com = SerialPorts()
        coms = self.com.get_com_list()
        ET_coms = []  # list of eurotherm/ck devices attached

        if len(coms) != self.len_of_com_list:
            self.len_of_com_list = len(coms)
            for com in coms:
                try:
                    CK20_caller = CK20.connect_to_device(com, 1)
                    is_et_controller = CK20_caller.unit_id
                except Exception:
                    print(f"com {com} isn't a CK/Eurotherm device")
                    pass
                else:
                    ET_coms.append(com)

            if len(coms) > 0:
                self.com_port_select.clear()
                self.com_port_select.addItems(ET_coms)
                self.connect_status.setPixmap(QtGui.QPixmap(img["online"]))
                self.connect_status.resize(21, 21)

            else:
                self.com_port_select.clear()
                self.connect_status.setPixmap(QtGui.QPixmap(img["offline"]))
                self.connect_status.resize(60, 20)

            # try reading the com ports in the main window, if not possible pass
            try:
                # First clear the content of the boxes
                self.tc_settings.com_port_select_1.clear()
                self.tc_settings.com_port_select_2.clear()
                all_items = [self.com_port_select.itemText(i) for i in range(self.com_port_select.count())]
                self.tc_settings.com_port_select_1.addItems(all_items)
                self.tc_settings.com_port_select_2.addItems(all_items)
            except Exception as e:
                pass

    def temp_mainloop(self, cycles_to_respond=1000):

        """
        TEMP MAINLOOP
        =============
            This is the function of the controller.
            It connects to the serial ports, by creating up to 2 controller objects.

            The related functions are:
                sample_devices- sample temp from each device
                    _wait_for_temp
                    _temp_events

            End result is to display the temperature of both channels in:
                lcd_displays
                Canvas object (the plot)
                in the automatically generated csv's

        :param cycles_to_respond: cycles to get a temp read
        """

        if self.com_port_select.count() > 0:
            report = "Begin measuring"
            self.go_button.setEnabled(False)  # don't allow to create new threads
            self.state_temp_loop(True)
            self.append_msg_box(report)

            while self.temp_loop_actiator:
                for num in range(self.com_port_select.count()):
                    # self.MainWindow_exec_thread(lambda: self.sample_devices(cycles_to_respond, num))
                    self.sample_devices(cycles_to_respond, num)
                self.temp_repr.plot_tc_temp(self.temp_log)
                timeo = float(self.timeout.text())  # timeout
                sleep(timeo)
                # -------- record data once in msg box --------

            self.go_button.setEnabled(True)
            self.led_light.setPixmap(QtGui.QPixmap(img["red_led"]))
        else:
            self.append_msg_box("No device is connected")

    def _wait_for_temp(self, device, cycles_to_respond):
        """ PRIVATE METHOD """
        # purpose to not crash if there's a momentary loss of connection with serial port
        wait_temp_response = 0

        try:
            temp = device.get_temp()  # get first read
        except Exception as e:
            temp = 0
        while temp == 0 and wait_temp_response < cycles_to_respond:
            temp = device.get_temp()
            wait_temp_response += 1

        return temp

    @staticmethod
    def check_ports_in_combo(tc_port_combo: "list", port: "str") -> "str":
        """
        Shameful method to help compare the current port in the loop with the tc_port_couple list.
        This could be done much more efficient and cleaner so TODO

        Args:
            tc_port_combo (*list): list from the tc_settings window
            port (*str): current port being used
        Return:
            (*str)
        """
        for combo in tc_port_combo:
            if port in combo:
                return combo
        return ''

    def sample_devices(self, cycles_to_respond, num):
        # --- dual channel ---
        # purpose to break sample_temp in size for easier debugging
        # make single mesaurement of temp

        try:
            port = str(self.com_port_select.itemText(num))
            temp = self._wait_for_temp(self.device[num], cycles_to_respond)
        except Exception as e:

            device_settings = (port, 1)
            CK20_caller = CK20.connect_to_device(*(device_settings), MAX_ATTEMPTS=10000)

            if CK20_caller is None:
                self.state_temp_loop()
                msg = "connection fail"
                self.append_msg_box(msg)
                return

            if type(e) in (AttributeError, NameError):
                print(type(e))
                self.device = []
                self.device.append(CK20_caller)

            elif type(e) is IndexError:
                self.device.append(CK20_caller)

            else:
                print(type(e))
                self.led_light.setPixmap(QtGui.QPixmap(img["red_led"]))
                self.temp_lcds[num].display("ERROR")
                self.append_msg_box(f"{e.args}")
                return

            self.device[num].baudrate = int(self.baudrate_select.currentText())
            self.device[num].close_port_after_each_call = True
            temp = self._wait_for_temp(self.device[num], cycles_to_respond)
        else:
            # block intended to try to reconnect in case connection is lost for several cycles < 1000
            try:
                self._temp_events(temp, self.device[num], num)
            except UnboundLocalError:
                temp = 0
                self._temp_events(temp, self.device[num], num)
            finally:
                # search for the port-tc combo and add to the log files

                self.temp_log[num].append(temp)  # logging the temperature locally (could be directly to csv)

                com_port_pairs = self.tc_settings.tc_port_couple  # for clarity
                tc_port_pair = self.check_ports_in_combo(com_port_pairs, port)  # get '' or port-thermocouple pair str
                self.device[num].log_temp(temp, save_dir=self.log_dir_path, tc_port_couple=tc_port_pair)

        # purpose- updating a msg in the msg_box only once
        try:
            if self.device[num].event != self.prev_event[num] and self.device[num].event != None:
                self.append_msg_box(self.device[num].event)
                self.prev_event[num] = self.device[num].event
        except (NameError, AttributeError, IndexError):
            self.prev_event.append(None)

    def _temp_events(self, temp, device, num, TEMP_MAX=1700) -> None:
        """ PRIVATE METHOD """
        # this method applies for when the temperature measurement is on
        # deals with all related events
        # TODO- this method should be in eurotherm_controllers, not here- find way to implement it there
        if temp == 0:
            self.led_light.setPixmap(QtGui.QPixmap(img["red_led"]))
        elif temp > TEMP_MAX:
            device.event = f"TC not connected to device {device.unit_id}"
            self.led_light.setPixmap(QtGui.QPixmap(img["red_led"]))
        elif not self.temp_lcds[num].checkOverflow(temp):
            device.event = f"TC connected to device {device.unit_id}"
            self.temp_lcds[num].display(temp)
            self.led_light.setPixmap(QtGui.QPixmap(img["green_led"]))
        elif self.temp_lcds[num].checkOverflow(temp):
            self.temp_lcds[num].display("ERROR")
            device.event = "An unexpected error has occured"

    def print_output(self, s):
        print(s)

    def append_msg_box(self, msg, strf="%H:%M:%S"):
        # convience function for appending msgs in the msg_box widget
        now = datetime.now()
        current_time = now.strftime(strf)
        self.msg_box.append(f"{current_time}: {msg}")

    def thread_complete(self, fn):
        reprt = f"{fn.__name__} finished"
        print(reprt)
        self.append_msg_box(reprt)

    def MainWindow_exec_thread(self, fn):
        """
        PURPOSE:
            get any function and execute it with a new thread
        :arg: function to execute with a thread
        """

        temp_meas = NewThread(fn)  # Any other args, kwargs are passed to the run function
        temp_meas.signals.result.connect(self.print_output)
        temp_meas.signals.finished.connect(lambda: self.thread_complete(fn))

        # Execute
        self.threadpool.start(temp_meas)

    def chk_ports(self, s=0.1):
        # Thread to check communication port at an interval s
        while True:
            sleep(s)
            self.find_ports()




class Thermocouple_settings(QtWidgets.QTableWidget):
    """
    Settings of thermocouples
    =========================

        Args:
            TC1 name (*str)
            TC2 name (*str)
            TC1 port (*str)
            TC2 port (*str)
    """

    def __init__(self, parent=None):
        super(Thermocouple_settings, self).__init__(parent)

        # icon
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(img["icon"]), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.Active
        self.setWindowIcon(icon)
        # set style sheet
        self.setStyleSheet(style["main_window"])

        self.setObjectName("TC Settings")
        self.resize(248, 214)
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.tc_settings_label = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tc_settings_label.sizePolicy().hasHeightForWidth())
        self.tc_settings_label.setSizePolicy(sizePolicy)
        self.tc_settings_label.setObjectName("tc_settings_label")
        self.gridLayout.addWidget(self.tc_settings_label, 0, 0, 1, 2)
        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 1, 0, 1, 2)
        self.device_1_box_label = QtWidgets.QLabel(self)  # TC 1
        self.device_1_box_label.setObjectName("device_1_box_label")
        self.gridLayout.addWidget(self.device_1_box_label, 2, 0, 1, 1)
        self.device_1_box = QtWidgets.QLineEdit(self)
        self.device_1_box.setObjectName("device_1_box")
        self.gridLayout.addWidget(self.device_1_box, 2, 1, 1, 1)
        self.device_2_box_label = QtWidgets.QLabel(self)  # TC 2
        self.device_2_box_label.setObjectName("device_2_box_label")
        self.gridLayout.addWidget(self.device_2_box_label, 3, 0, 1, 1)
        self.device_2_box = QtWidgets.QLineEdit(self)
        self.device_2_box.setObjectName("device_2_box")
        self.gridLayout.addWidget(self.device_2_box, 3, 1, 1, 1)
        self.port_1_box_label = QtWidgets.QLabel(self)
        self.port_1_box_label.setObjectName("port_1_box_label")
        self.gridLayout.addWidget(self.port_1_box_label, 4, 0, 1, 1)
        self.com_port_select_1 = QtWidgets.QComboBox(self)
        self.com_port_select_1.setWhatsThis("")
        self.com_port_select_1.setObjectName("com_port_select")
        self.gridLayout.addWidget(self.com_port_select_1, 4, 1, 1, 1)
        self.device_2_port_label = QtWidgets.QLabel(self)
        self.device_2_port_label.setObjectName("device_2_port_label")
        self.gridLayout.addWidget(self.device_2_port_label, 5, 0, 1, 1)
        self.com_port_select_2 = QtWidgets.QComboBox(self)
        self.com_port_select_2.setWhatsThis("")
        self.com_port_select_2.setObjectName("com_port_select_2")
        self.gridLayout.addWidget(self.com_port_select_2, 5, 1, 1, 1)
        self.default_vals = QtWidgets.QCheckBox(self)
        self.default_vals.setObjectName("default_vals")
        self.gridLayout.addWidget(self.default_vals, 6, 0, 1, 2)
        # Setup for the finish dialog
        self.tc_dialog_box = QtWidgets.QDialogButtonBox(self)
        self.tc_dialog_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.tc_dialog_box.setObjectName("tc_dialog_box")
        # Exit dialog
        self.tc_dialog_box.rejected.connect(self.close)
        self.tc_dialog_box.accepted.connect(self.approve_changes)

        self.gridLayout.addWidget(self.tc_dialog_box, 7, 1, 1, 1)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        # init tc_port_couple- this is the combination of the port number and TC name picked
        self.tc_port_couple = ['', '']  # a 2 cell list of strings

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Thermocouple settings", "TC Settings"))
        self.tc_settings_label.setText(_translate("Thermocouple",
                                                  "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; font-weight:600;\">Thermocouple settings</span></p></body></html>"))
        self.device_1_box_label.setText(
            _translate("Form", "<html><head/><body><p align=\"center\">TC 1 name:</p></body></html>"))
        self.device_2_box_label.setText(
            _translate("Form", "<html><head/><body><p align=\"center\">TC 2 name:</p></body></html>"))
        self.port_1_box_label.setText(
            _translate("Form", "<html><head/><body><p align=\"center\">Port 1:</p></body></html>"))
        self.device_2_port_label.setText(
            _translate("Form", "<html><head/><body><p align=\"center\">Port 2:</p></body></html>"))
        self.default_vals.setText(_translate("Form", "use default values"))

    def approve_changes(self):
        """
        Approve changes in the seetings window
        """
        name1 = self.device_1_box.displayText()
        name2 = self.device_2_box.displayText()

        port1 = self.com_port_select_1.currentText()
        port2 = self.com_port_select_2.currentText()
        # Checkbox not enabled
        if not self.default_vals.isChecked():
            if name1 == name2:
                msg_header = "Name error"
                if name1 == '':
                    msg = "Please name your thermocouples or use default values"
                else:
                    msg = f"Both thermocouples are named {name1}.\n" \
                          f"Please make sure they have different names"

                QMessageBox.critical(self, msg_header, msg, QMessageBox.Ok)

                return

            if port1 == port2:
                msg_header = f"Port Error"
                msg = f"Both thermocouples are assigned to the same port {port1}.\n" \
                      f"Please assign them different ports"
                if port1 == '':
                    msg = "No ports were assigned. Please connect a controller to the USB port"

                QMessageBox.critical(self, msg_header, msg, QMessageBox.Ok)

                return

        answer = QMessageBox.question(
            None, "Approve changes",
            "Are you sure you want to proceed with these changes?",
            QMessageBox.Ok | QMessageBox.Cancel
        )
        if answer & QMessageBox.Ok:
            if not self.default_vals.isChecked():
                name_and_port1 = f"{port1}-{name1}-"
                name_and_port2 = f"{port2}-{name2}-"

                self.tc_port_couple = [name_and_port1, name_and_port2]
            else:
                self.tc_port_couple = ['', '']

            print(self.tc_port_couple)
            self.close()
        elif answer & QMessageBox.Cancel:
            pass



def gui_main():
    # main function of the script GUI
    # The rest of the code is the same as for the "normal" text editor.

    app = QtWidgets.QApplication(sys.argv)

    app.setStyle("Fusion")

    # Now use a palette to switch to dark colors:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    main_window = MainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(main_window)
    main_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    sys.exit(app.exec_())
