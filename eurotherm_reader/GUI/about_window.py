from eurotherm_reader.GUI.styles import style, img
from PyQt5 import QtCore, QtGui, QtWidgets
from eurotherm_reader.GUI.auxilary_classes import MainWindow, Canvas, ThreadSignals, NewThread

class About(QtWidgets.QTableWidget):
    """
        About class
        ===========
            Pretty simple- this class is for the about window in the gui.


    :arg
    """

    def __init__(self, parent=None):
        super(About, self).__init__(parent)

        # icon
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(img["icon"]), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.Active
        self.setWindowIcon(icon)
        # set style sheet
        self.setStyleSheet(style["main_window"])
        # widgets
        self.setObjectName("Form")
        self.setFixedSize(460, 341)
        self.line = QtWidgets.QFrame(self)
        self.line.setGeometry(QtCore.QRect(0, 30, 450, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.about_label = QtWidgets.QLabel(self)
        self.about_label.setGeometry(QtCore.QRect(10, 10, 401, 20))
        self.about_label.setObjectName("about_label")
        self.about_icon = QtWidgets.QLabel(self)
        self.about_icon.setGeometry(QtCore.QRect(10, 10, 121, 21))
        self.about_icon.setText("")
        self.about_icon.setPixmap(QtGui.QPixmap(img["icon"]))
        self.about_icon.setScaledContents(True)
        self.about_icon.setObjectName("about_icon")
        self.about_text = QtWidgets.QTextEdit(self)
        self.about_text.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.about_text.setGeometry(QtCore.QRect(10, 40, 440, 241))
        self.about_text.setObjectName("textEdit")

        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(160, 290, 111, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.close)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        # Add about info:
        about_txt = r"../docs/app_about.txt"  # relative path

        with open(about_txt, "r") as f:
            data = f.read()
        try:
            self.about_text.append(data)
        except Exception:
            self.about_text.append("ERROR- cannot find about txt")

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "About"))
        self.about_label.setText(_translate("Form", style["about_label"]))
        self.pushButton.setText(_translate("Form", "OK"))

    def update(self, label):
        label.adjustSize()
