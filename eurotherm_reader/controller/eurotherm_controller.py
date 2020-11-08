import minimalmodbus
from eurotherm_reader.controller.serial_ports import SerialPorts
from sys import stdout
from os import path
from os import mkdir
from datetime import datetime
import matplotlib.pyplot as plt
from tkinter import _tkinter
from serial.serialutil import SerialException


class Eurotherm2400( minimalmodbus.Instrument ):
    #TODO- turn this into an abstract class
    """Instrument class for Eurotherm 2400 process controller.

    Args:
        * portname (str): port name
        * slaveaddress (int): slave address in the range 1 to 247

    Inherits from the instrument abstract class
    """

    def __init__(self, portname, slaveaddress, timeout = 0.1, baudrate = 9200):
        minimalmodbus.Instrument.__init__(self, portname, slaveaddress)
        self.close_port_after_each_call = True
        self.serial.baudrate = baudrate
        self.serial.timeout = timeout
        self.event = None # init events var

        self.unit_id = self.id # don't want to call each the register

        
    @property
    def timeout(self):
        return self.serial.timeout

    @timeout.setter
    def timeout(self, new_timeout):
        try:
            self.serial.timeout = new_timeout
        except Exception as e:
            print(f"cannot finish this process:\n{e.args} ")

    @property
    def baudrate(self):
        return self.serial.baudrate

    @baudrate.setter
    def baudrate(self,new_val):
        try:
           self.serial.baudrate = new_val
        except Exception as e:
            print(f"cannot finish this process:\n{e.args} ")

    def get_temp(self, cycles_to_connect = 200):
        """Return the process value (PV) for loop1 which is the temperature in Celsius."""
        connection_attempt = 0
        try:
            temp = self.read_register(1, 1, functioncode=3)
            self.event = None
            return temp
        except SerialException as e:
            self.event = e.args
            return 0.0
        except FileNotFoundError as e:
            self.event = e.args
            return 0.0
        except Exception as e:
            self.event = e.args
            return 0.0

    def is_manual_temp(self):
        """Return True if loop1 is in manual mode."""
        return self.read_register(1, 1) > 0

    def get_sptarget_loop1(self):
        """Return the setpoint (SP) target for loop1."""
        return self.read_register(2, 1)

    def get_sp_loop1(self):
        """Return the (working) setpoint (SP) for loop1."""
        return self.read_register(5, 1)

    def get_output_level(self):
        """% Output level """
        return self.read_register(3,1)

    def set_sp_loop1(self, value):
        """Set the SP1 for loop1.

        Note that this is not necessarily the working setpoint.

        Args:
            value (float): Setpoint (most often in degrees)
        """
        self.write_register(24, value, 1)

    def disable_sprate_loop1(self):
        """Disable the setpoint (SP) change rate for loop1. """
        VALUE = 1
        self.write_register(76, VALUE, 0)

    def get_cntrl_status_word(self):
        return self.read_register(76,10)
    
    def __get_datetime(self, strf="%d-%m-%Y %H:%M:%S"):
        """ PRIVATE- return the current datetime for file saving purposes"""
        now = datetime.now()
        current_time = now.strftime(strf)
        return current_time

    def log_temp(self, temp = None, fName = f"log", tc_port_couple ='', save_dir =r"../data", fType ='csv'):
        """ Log temperature in a csv file"""
        time = self.__get_datetime(strf="%d-%m-%Y")
        fEnd = ".".join([time,fType])
        fName = f"unit {self.unit_id}-{tc_port_couple}" + fName
        fName = " ".join([fName,fEnd])

        if path.exists(save_dir):
            PATH = path.join(save_dir, fName)
        else:
            mkdir(save_dir)
            PATH = path.join(save_dir, fName)

        if path.exists(PATH):
            try:
                with open(PATH, 'a') as f:
                    time = self.__get_datetime("%H:%M:%S")
                    if not temp: temp = self.get_temp()
                    f.write(f"{time},{temp},{self.event}\n")
            except PermissionError:
                event =  f"Please close file {PATH} to record data "
                self.event = event
                print(event)
        else:
            with open(PATH, 'a') as f:
                f.write("time,temperature,event\n")
    
    def get_heater_current(self):
        """ Heater current (With PDSIO mode 2) """
        return self.read_register(80,1)

    def search_register(self, reg, functioncode= 3, number_of_decimals = 3, **kwargs):
        """ Read any register content"""
        return self.read_register(reg, number_of_decimals = number_of_decimals, functioncode = functioncode, **kwargs)

    def _write_to_any(self, REG, VALUE, **kwargs):
        """PRIVATE- Freely write to any register """
        self.write_register(REG, VALUE, **kwargs)


    @property
    def id(self):
        """
        read id the customer identity the unit
        Note- Customer identity is given by the user (CI-Systems here)
        COMMENT
        =======
            This method can be used to ping the devices to make sure they are indeed controllers
            and not another media
        """
        try:
            return self.read_register(629, 0)
        except SerialException as e:
            self.event = f"{type(e): {e.args}}"
            return False

class CK20(Eurotherm2400):
    """
    purpose of this class is act as a display for the eurotherm controllers class:
    Class inherits from EuroTherm2400 and SerialPorts classes. Try to simulate
    a real controller """

    def __init__(self, portname, slaveaddress):
        Eurotherm2400.__init__(self, portname, slaveaddress)
        self.temp_list = [] # instantiate a list containing the EuroTherm controller temperatures


    def temp_display(self, fig, ax, **kwargs):
        """ display temperature- intended for main loop  """
        color = 'tab:blue'
        # plt.cla()
        try:
            ax.cla()
            ax.plot(self.temp_list, color= color , **kwargs)
            ax.set_ylabel("R-Type TC temp [$\circ$C]", fontsize=12)
            # ax.set_ylim([min(temp_list), max(temp_list)])
            fig.canvas.draw()
            plt.pause(self.timeout)
        except _tkinter.TclError:
            self.event = "shut down window"
            self.log_temp()
        except Exception as e:
            self.event = e
            self.log_temp()
        finally:
            pass

    def print_temp(self):
        """ display in console the temperature in degrees celsius """
        temp = self.get_temp()
        stdout.write("\r%.2f degC" % temp)
        stdout.flush()

    def _append_temp(self):
        """ private method- append temperature measurements """
        self.temp_list.append(self.get_temp())

    def _display(self, fig, ax, print_temp = False, plot_temp = True):
        """ main loop to display the temperature """

        self._append_temp()
        if print_temp: self.print_temp()
        if plot_temp: self.temp_display(fig,ax)
            
    def main_loop(self, plt_style = 'seaborn-whitegrid'):
        """ main loop - purposes to simulate operation in a GUI"""
        fig,ax = plt.subplots()
        with plt.style.context([plt_style]):
            while True:
                self._display(fig,ax)
                self.log_temp()

    @classmethod
    def search(cls, *args, **kwargs):
        """
        method to activate the ck20 by searching ports and returning a list of possible connections.
        return: list of controller objects if ports are found, else return False with error msg.
        """
        com = SerialPorts()
        port_list= com.get_com_list()
        ck20_devices = [] # empty list of ck20 connected
        if len(port_list) > 0:
            for port in port_list:
                instrument = (port,1) # port and slave number
                ck20_devices.append(cls(*instrument, *args, **kwargs))
            return ck20_devices

        else:
            print("No devices found or cannot connect to devices")
            return False
    @classmethod
    def connect_to_device(cls, *device_settings, MAX_ATTEMPTS=1000):
        # purpose to try to connect MAX_ATTEMPTS times to a port, slaveaddress tuple
        # break in cases - connection sucessful, other exception occurs and ofc if connect_attempts>MAX_ATTEMPTS
        # return None if no connection is successful or the controller object
        connect_attempts = 0
        CK20_caller = None
        while connect_attempts < MAX_ATTEMPTS:
            try:
                CK20_caller = cls(*device_settings)
            except SerialException:
                connect_attempts += 1
            except Exception as e:
                print(f"{type(e)}- {e.args}")
                break
            else:
                break
        return CK20_caller
