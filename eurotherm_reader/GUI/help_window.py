from eurotherm_reader.GUI.styles import style, img
from PyQt5 import QtCore, QtGui, QtWidgets
from eurotherm_reader.GUI import VERSION

class Help(QtWidgets.QTableWidget):
    """
        Settings class

    :arg
    """

    def __init__(self, parent=None):
        super(Help, self).__init__(parent)

        # icon
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(img["icon"]), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.Active
        self.setWindowIcon(icon)
        # set style sheet
        self.setStyleSheet(style["main_window"])
        # widgets

        self.setObjectName("Help")
        self.setFixedSize(749, 698)
        font = QtGui.QFont()
        font.setFamily("Narkisim")
        self.setFont(font)
        self.setMouseTracking(True)
        self.Help_label = QtWidgets.QLabel(self)
        self.Help_label.setGeometry(QtCore.QRect(0, 10, 751, 20))
        self.Help_label.setScaledContents(False)
        self.Help_label.setObjectName("Help_label")
        self.icon = QtWidgets.QLabel(self)
        self.icon.setGeometry(QtCore.QRect(10, 10, 121, 21))
        self.icon.setText("")
        self.icon.setPixmap(QtGui.QPixmap(img["icon"]))
        self.icon.setScaledContents(True)
        self.icon.setObjectName("CI_SEMI")
        self.line = QtWidgets.QFrame(self)
        self.line.setGeometry(QtCore.QRect(0, 30, 751, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.help_img = QtWidgets.QLabel(self)
        self.help_img.setGeometry(QtCore.QRect(10, 50, 728, 591))
        self.help_img.setPixmap(QtGui.QPixmap(img["help_img"]))
        self.help_img.setScaledContents(True)
        self.help_img.setObjectName("help_img")
        self.ok_button = QtWidgets.QPushButton(self)
        self.ok_button.setGeometry(QtCore.QRect(320, 650, 131, 31))
        self.ok_button.setObjectName("ok_button")
        self.ok_button.clicked.connect(self.close)
        self.green_led = QtWidgets.QLabel(self)
        self.green_led.setGeometry(QtCore.QRect(660, 10, 21, 21))
        self.green_led.setPixmap(QtGui.QPixmap(img["green_led"]))
        self.green_led.setScaledContents(True)
        self.green_led.setObjectName("green_led")
        self.blue_led = QtWidgets.QLabel(self)
        self.blue_led.setGeometry(QtCore.QRect(690, 10, 21, 21))
        self.blue_led.setPixmap(QtGui.QPixmap(img["blue led"]))
        self.blue_led.setScaledContents(True)
        self.blue_led.setObjectName("blue_led")
        self.red_led = QtWidgets.QLabel(self)
        self.red_led.setGeometry(QtCore.QRect(720, 10, 21, 21))
        self.red_led.setPixmap(QtGui.QPixmap(img["red_led"]))
        self.red_led.setScaledContents(True)
        self.red_led.setObjectName("red_led")

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Help", "Help"))
        self.Help_label.setText(_translate("Help",
                                           style["Help_label"](VERSION)))
        self.ok_button.setText(_translate("Help", "OK"))
