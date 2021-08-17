from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import (QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot, Qt)
from PyQt5.QtWidgets import QDialog , QFileDialog, QSizePolicy, qApp, QMessageBox

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import traceback, sys



class MainWindow(QtWidgets.QMainWindow):
    # Editing the exit button (in the window- X button) for the MainWindow.
    # Purpose- To accidently not close the window during operation
    # --- explanation for or anyone who doesn't understand the code:
    # This class is inherited from QtWidgets.QMainWindow and overrides(polymorphism),
    # the class method closeEvent.
    # To use in the main_loop call (or when giving it to another class) instead of QtWidgets.QMainWindow.
    # important note for newbies- This ONLY changes the closeEvent method for this class, not for the parent.
    def closeEvent(self, e):
        answer = QMessageBox.question(
            None, "Exit",
            "Are you sure you want to close the application?",
            QMessageBox.Close | QMessageBox.Cancel
        )
        if answer & QMessageBox.Close:
            qApp.exit()
        elif answer & QMessageBox.Cancel:
            e.ignore()



class Canvas(FigureCanvas):
    """
    Canvas class
    ============

        PUPROSE
        =======
            Embeds the matplotlib into the GUI for dynamic plotting

    """
    def __init__(self, parent=None, width=5, height=5, dpi=103):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = [self.fig.add_subplot(111)]
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        color = "lightgray"
        self.fig.set_facecolor(color)

    def plot_tc_temp(self, temps, device_one = f"device 1", device_two = f"device 2", **kwargs):
        """
        Plot Thermocouple (TC) temperature
        ==================================

        args:
            (list) temps- a list of 2 nested lists with values of each TC.
            (str) device_one- name of the first device (as of 09/09/2020 cannot be changed in the GUI )
            (str) device_two- name of the second device (as of 09/09/2020 cannot be changed in the GUI )

        return:
            None

        """
        # @TODO make this ugly function more organized and to make more sense
        colors = [
            'tab:red',
            'tab:blue'
        ]
        for i,_ in enumerate(self.axes):
            self.axes[i].cla()

        ax = self.figure.add_subplot(111)
        ax.plot(temps[0], color=colors[0], label = device_one,  **kwargs)
        ax.set_ylabel("1 R-Type TC temp [$\circ$C]", fontsize=9)
        ax.set_xlabel("# of iterations", fontsize=8)

        if len(temps[1]) > 1:
            if len(self.axes) ==1:
                ax2 = ax.twinx()
                self.axes.append(ax2)
                fig = (4,5)
                self.fig.figsize = fig

            ax2 = self.axes[1]
            ax2.plot(temps[1], color=colors[1], label = device_two, **kwargs)
            ax2.set_ylabel("2 R-Type TC temp [$\circ$C]", fontsize=9)

        if len(temps[1]) == 2:  self.fig.legend(fontsize=8)
        self.fig.canvas.draw()

class ThreadSignals(QObject):
    '''
    Defines a new thread

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class NewThread(QRunnable):
    '''
    NewThread class

    Inherits from QRunnable to handler new thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(NewThread, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = ThreadSignals()

        # Add the callback to our kwargs
        # self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done