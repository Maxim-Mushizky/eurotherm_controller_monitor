import serial.tools.list_ports
import serial
import sys
import glob

class SerialPorts():

    def __init__(self, include_links = True):
        # Items are returned in no particular order. It may make sense to sort the items.
        # Also note that the reported strings are different across platforms and operating systems,
        # even for the same device.
        self.ports = serial.tools.list_ports.comports(include_links = include_links) # ports class\
        self.__set_port_list()

    def __set_port_list(self):
        """ Get a list of all available serial ports"""

        self._coms = [str(i.device) for i in sorted(self.ports)]

    def get_com_list(self):
        try:
            if len(self._coms) > 0:
                return self._coms
            else:
                return self._coms
                print("No available com ports found")
        except NameError:
            pass

    def get_com_list_TEST(self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        self._coms = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.dtr =  False
                s.close()

                self._coms.append(port)
            except (OSError, serial.SerialException):
                pass
        return self._coms


    def __chk_com(self, port_name, baudrate = 9200,parity =serial.PARITY_EVEN,stopbits =serial.STOPBITS_ONE, timeout = 0.5,**kwargs ):
        with serial.Serial(port=port_name,
                           baudrate =baudrate,
                           parity = parity,
                           stopbits = stopbits,
                           bytesize = serial.EIGHTBITS,
                           timeout =timeout,
                           **kwargs) as s:
            print(f"connection succesful: {port_name} with param:\n"
                  f"baudrate: {baudrate} Bd\n"
                  f"parity: {parity}\n"
                  f"stopbits: {stopbits}\n"
                  f"timeout: {timeout} sec")

    def get_com_status(self, **kwargs):
        """ loop throught a list of available com ports and check if connection is still good"""
        for com in self._coms:
            self.__chk_com(port_name=com)

