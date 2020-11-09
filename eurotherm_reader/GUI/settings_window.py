# -*- coding: utf-8 -*-


from eurotherm_reader.GUI.styles import style, img
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox


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

