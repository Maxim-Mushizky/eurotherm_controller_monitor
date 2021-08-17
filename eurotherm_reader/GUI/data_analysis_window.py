from eurotherm_reader.GUI.styles import style, img
from eurotherm_reader.analysis.cal_analysis import ThermocoupleStatistics
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import pandas as pd


class TCDataAnalysis(QtWidgets.QTableWidget):

    def __init__(self, parent=None, time_format="yyyy-MM-dd HH:mm:ss"):
        super(TCDataAnalysis, self).__init__(parent)

        # icon
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(img["icon"]), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.Active
        self.setWindowIcon(icon)
        # set style sheet
        self.setStyleSheet(style["main_window"])
        self.setObjectName("Data Analysis")
        self.resize(483, 443)
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.header_label = QtWidgets.QLabel(self)
        self.header_label.setObjectName("header_label")

        # variables
        self.data_fold = self.setpoints_path = r"../data"
        self.time_format = time_format
        self.setpoints = ""

        self.gridLayout.addWidget(self.header_label, 0, 0, 1, 7)
        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 1, 0, 1, 7)
        self.selectdata_label = QtWidgets.QLabel(self)
        self.selectdata_label.setObjectName("selectdata_label")
        self.gridLayout.addWidget(self.selectdata_label, 2, 0, 1, 7)
        self.choose_fold_button = QtWidgets.QPushButton(self)
        self.choose_fold_button.setMaximumSize(QtCore.QSize(16777215, 41))
        self.choose_fold_button.setObjectName("choose_fold_button")
        self.gridLayout.addWidget(self.choose_fold_button, 3, 0, 1, 2)
        self.fold_name_lineEdit = QtWidgets.QLineEdit(self)
        self.fold_name_lineEdit.setEnabled(False)
        self.fold_name_lineEdit.setObjectName("fold_name_lineEdit")
        self.gridLayout.addWidget(self.fold_name_lineEdit, 3, 2, 1, 5)
        self.unit1_name_label = QtWidgets.QLabel(self)
        self.unit1_name_label.setObjectName("unit1_name_label")
        self.gridLayout.addWidget(self.unit1_name_label, 4, 0, 1, 2)
        self.unit1_name = QtWidgets.QLineEdit(self)
        self.unit1_name.setObjectName("unit1_name")
        self.gridLayout.addWidget(self.unit1_name, 4, 2, 1, 1)
        self.TC1_name_label = QtWidgets.QLabel(self)
        self.TC1_name_label.setObjectName("TC1_name_label")
        self.gridLayout.addWidget(self.TC1_name_label, 4, 3, 1, 2)
        self.tc1_name = QtWidgets.QLineEdit(self)
        self.tc1_name.setObjectName("tc1_name")
        self.gridLayout.addWidget(self.tc1_name, 4, 5, 1, 2)
        self.unit2_name_label = QtWidgets.QLabel(self)
        self.unit2_name_label.setObjectName("unit2_name_label")
        self.gridLayout.addWidget(self.unit2_name_label, 5, 0, 1, 2)
        self.unit2_name = QtWidgets.QLineEdit(self)
        self.unit2_name.setObjectName("unit2_name")
        self.gridLayout.addWidget(self.unit2_name, 5, 2, 1, 1)
        self.tc2_name_label = QtWidgets.QLabel(self)
        self.tc2_name_label.setObjectName("tc2_name_label")
        self.gridLayout.addWidget(self.tc2_name_label, 5, 3, 1, 2)
        self.tc2_name = QtWidgets.QLineEdit(self)
        self.tc2_name.setObjectName("tc2_name")
        self.gridLayout.addWidget(self.tc2_name, 5, 5, 1, 2)
        self.line_2 = QtWidgets.QFrame(self)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 6, 0, 1, 7)
        self.test_period_label = QtWidgets.QLabel(self)
        self.test_period_label.setObjectName("test_period_label")
        self.gridLayout.addWidget(self.test_period_label, 7, 1, 1, 2)
        self.test_param_label = QtWidgets.QLabel(self)
        self.test_param_label.setObjectName("test_param_label")
        self.gridLayout.addWidget(self.test_param_label, 7, 4, 1, 3)
        self.start_date_label = QtWidgets.QLabel(self)
        self.start_date_label.setObjectName("start_date_label")
        self.gridLayout.addWidget(self.start_date_label, 8, 0, 1, 1)
        self.start_date = QtWidgets.QDateTimeEdit(self)
        self.start_date.setObjectName("start_date")
        self.gridLayout.addWidget(self.start_date, 8, 1, 1, 2)
        self.label_13 = QtWidgets.QLabel(self)
        self.label_13.setObjectName("label_13")
        self.gridLayout.addWidget(self.label_13, 8, 3, 1, 2)
        self.heat_time = QtWidgets.QLineEdit(self)
        self.heat_time.setObjectName("heat_time")
        self.gridLayout.addWidget(self.heat_time, 8, 6, 1, 1)
        self.end_date_label = QtWidgets.QLabel(self)
        self.end_date_label.setObjectName("end_date_label")
        self.gridLayout.addWidget(self.end_date_label, 9, 0, 1, 1)
        self.end_date = QtWidgets.QDateTimeEdit(self)
        self.end_date.setObjectName("end_date")
        self.gridLayout.addWidget(self.end_date, 9, 1, 1, 2)
        self.label_11 = QtWidgets.QLabel(self)
        self.label_11.setObjectName("label_11")
        self.gridLayout.addWidget(self.label_11, 9, 3, 1, 2)
        self.test_time = QtWidgets.QLineEdit(self)
        self.test_time.setObjectName("test_time")
        self.gridLayout.addWidget(self.test_time, 9, 6, 1, 1)
        self.label_15 = QtWidgets.QLabel(self)
        self.label_15.setObjectName("label_15")
        self.gridLayout.addWidget(self.label_15, 10, 0, 1, 7)
        self.date_sort_checkbox = QtWidgets.QCheckBox(self)
        self.date_sort_checkbox.setObjectName("mean_stdev_2")
        self.gridLayout.addWidget(self.date_sort_checkbox, 11, 0, 1, 2)
        self.label_10 = QtWidgets.QLabel(self)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 11, 4, 1, 2)
        self.temp_range = QtWidgets.QLineEdit(self)
        self.temp_range.setObjectName("temp_range")
        self.gridLayout.addWidget(self.temp_range, 11, 6, 1, 1)
        self.get_test_presets = QtWidgets.QPushButton(self)
        self.get_test_presets.setMaximumSize(QtCore.QSize(16777215, 41))
        self.get_test_presets.setObjectName("get_test_presets")
        self.gridLayout.addWidget(self.get_test_presets, 12, 4, 1, 3)
        self.line_3 = QtWidgets.QFrame(self)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridLayout.addWidget(self.line_3, 13, 0, 1, 7)
        self.mean_stdev = QtWidgets.QCheckBox(self)
        self.mean_stdev.setObjectName("mean_stdev")
        self.gridLayout.addWidget(self.mean_stdev, 14, 0, 1, 2)
        self.max_min = QtWidgets.QCheckBox(self)
        self.max_min.setObjectName("max_min")
        self.gridLayout.addWidget(self.max_min, 15, 0, 1, 2)
        self.analyze_button = QtWidgets.QPushButton(self)
        self.analyze_button.setObjectName("analyze_button")
        self.gridLayout.addWidget(self.analyze_button, 16, 2, 1, 1)
        self.cancel_button = QtWidgets.QPushButton(self)
        self.cancel_button.setObjectName("cancel_button")
        self.gridLayout.addWidget(self.cancel_button, 16, 3, 1, 1)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.call_widgets_interactions()
        self.call_toolTips()

    def call_widgets_interactions(self):
        """  interactive widgets call """

        # Button triggers
        self.choose_fold_button.clicked.connect(self.get_data_folder)
        self.analyze_button.clicked.connect(self.analyze_tc_data)
        self.cancel_button.clicked.connect(self.close)
        self.get_test_presets.clicked.connect(self.get_test_setpoints)

        # checkbox
        self.max_min.setChecked(True)
        self.mean_stdev.setChecked(True)
        self.date_sort_checkbox.setChecked(True)

        # timeEdit
        # change time display format
        self.start_date.setDisplayFormat(self.time_format)
        self.end_date.setDisplayFormat(self.time_format)

        # set current_datetime
        current_dateTime = QtCore.QDateTime.currentDateTime()
        self.start_date.setDateTime(current_dateTime)
        self.end_date.setDateTime(current_dateTime)

    def call_toolTips(self):
        """
        This method contains all tool tip helpers for this tool.
        I know it's not best when the text is within the .py file, but it can easily be changed to json, csv, txt
        or whatever other text based format (or another py file)
        """
        self.choose_fold_button.setToolTip("Select folder containing the specific test TCReader log files")
        self.get_test_presets.setToolTip("Select the test set points (temperatures that you want statistics for)")
        self.selectdata_label.setToolTip("In this section select the folder with the .csv log files and name the "
                                         "units and TCs you want to analyze.\n "
                                         "The tool will concatenate all files with the same unit names, so make sure "
                                         "to place only files that you require to analyze.")
        self.date_sort_checkbox.setToolTip("Sort csv log files in respect to time")
        self.temp_range.setToolTip("Temperature range around the set points to be analyzed")
        self.mean_stdev.setToolTip("Add mean and standard deviation of each set point to output")
        self.max_min.setToolTip("Add max and minimum of each set point to output")
        self.analyze_button.setToolTip("Perform analysis and output it to test folder ")

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("TC Test Analysis", "TC Test Analysis"))
        self.header_label.setToolTip(_translate("Form",
                                                "<html><head/><body><p align=\"center\"><span style=\" font-weight:600; text-decoration: underline;\"><br/>Data Analysis</span></p></body></html>"))
        self.header_label.setText(_translate("Form",
                                             "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; font-weight:600;\">Thermocouple data analysis</span></p></body></html>"))
        self.selectdata_label.setText(
            _translate("Form", "<html><head/><body><p align=\"center\">Select data</p></body></html>"))
        self.choose_fold_button.setText(_translate("Form", "Choose folder"))
        self.unit1_name_label.setText(_translate("Form", "Unit 1 name"))
        self.TC1_name_label.setText(_translate("Form", "TC 1 name"))
        self.unit2_name_label.setText(_translate("Form", "Unit 2 name"))
        self.tc2_name_label.setText(_translate("Form", "TC 2 name"))
        self.test_period_label.setText(
            _translate("Form", "<html><head/><body><p align=\"center\">Test period</p></body></html>"))
        self.test_param_label.setText(
            _translate("Form", "<html><head/><body><p align=\"center\">Test parameters</p></body></html>"))
        self.start_date_label.setText(_translate("Form", "Start date"))
        self.label_13.setText(_translate("Form", "Heat time [m]"))
        self.end_date_label.setText(_translate("Form", "end date"))
        self.label_11.setText(_translate("Form", "Test time [m]"))
        self.label_15.setText(_translate("Form", "<html><head/><body><p align=\"center\">Analysis</p></body></html>"))
        self.date_sort_checkbox.setText(_translate("Form", "sort dates"))
        self.label_10.setText(_translate("Form", "Temp range"))
        self.get_test_presets.setText(_translate("Form", "Test set points"))
        self.mean_stdev.setText(_translate("Form", "mean and stdev"))
        self.max_min.setText(_translate("Form", "max and min"))
        self.analyze_button.setText(_translate("Form", "Analyze"))
        self.cancel_button.setText(_translate("Form", "Cancel"))

    def get_data_folder(self):
        # Wrapper for function calling
        dir_selected = str(QFileDialog.getExistingDirectory(self, 'Select Directory', self.data_fold))
        if dir_selected != "":
            self.data_fold = dir_selected
            self.fold_name_lineEdit.setText(dir_selected)
            print(f"The folder for analysis: {self.data_fold}")

    def get_test_setpoints(self):
        """
        Receive the test presets in csv and txt format.

        """
        self.setpoints_path = str(QFileDialog.getOpenFileName(self, "Select test setpoint file", self.setpoints_path,
                                                              "text files (*.txt *.csv)")[0])

        try:
            setpoints_df = pd.read_csv(self.setpoints_path, skip_blank_lines=True)
            self.setpoints = list(setpoints_df.iloc[:, 0].values)

        except Exception as e:
            pass

    def analyze_tc_data(self):
        # main method of this class
        # run a full analysis using the ThermocoupleStatistics class

        start_date = self.start_date.dateTime().toString(self.time_format)
        end_date = self.end_date.dateTime().toString(self.time_format)

        tc_names = [self.tc1_name.text(), self.tc2_name.text()]
        unit1_name = self.unit1_name.text()
        unit2_name = self.unit2_name.text()

        try:
            self.TC_analysis = ThermocoupleStatistics.from_folders(self.data_fold,
                                                                   unit1_name=unit1_name,
                                                                   unit2_name=unit2_name)

            self.TC_analysis.test_setpoints = self.setpoints
            self.TC_analysis.tc_names = tc_names
            self.TC_analysis.concat_channels(heat_time=int(self.heat_time.text()),
                                             test_period=int(self.test_time.text()),
                                             date_sort=self.date_sort_checkbox.checkState())

            self.TC_analysis.quick_filter(test_period=int(self.test_time.text()),
                                          start_date=start_date,
                                          end_date=end_date,
                                          date_sort=self.date_sort_checkbox)

            ret_val = self.TC_analysis.cal_summary(to_csv=True,
                                                   suffixes=self.TC_analysis.tc_names,
                                                   save_dir=self.data_fold,
                                                   max_min=self.max_min.checkState(),
                                                   mean_std=self.mean_stdev.checkState()
                                                   )
        except Exception as e:
            msg_header = f"{type(e)}"
            msg = f"{e.args[0]}"
            print(f"{msg_header}: {msg}")
            QMessageBox.critical(self, msg_header, msg, QMessageBox.Ok)
