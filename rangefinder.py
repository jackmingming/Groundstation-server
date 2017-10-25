import serial
import time
from binascii import unhexlify
from simulator import Simulator

class rangefinder(object):

    def __init__(self, port, baudrate, bytesize, stopbits, timeout, _string, send_rate):
        """Init configurations"""
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.stopbits = stopbits
        self.timeout = timeout
        self._string = _string
        self.send_rate = send_rate

    def fetch_response(self):
        _serial = self._init_serial()
        self._send_hex_string(_serial, self._string)
    
    def _init_serial(self):
        try:
            if self.port:   
                _serial_port = serial.Serial(self.port, baudrate=self.baudrate, bytesize=self.bytesize, stopbits=self.stopbits, timeout=self.timeout)
                print "Serial port is open: ", _serial_port.is_open
                print "hex string: ", self._string
                _serial_port.flushInput()
                _serial_port.flushOutput()

            return  _serial_port
        except Exception:
            print "Can't connect to serial."  
    
    def _send_hex_string(self, _serial, _string):
        if _serial.is_open and _string:
            """Send signal to serial prot"""
            print "Send signal: ", repr(unhexlify(_string))
            while True:
                time.sleep(self.send_rate)
                _serial.write(unhexlify(_string))
                _data_size = _serial.inWaiting()
                self._get_data(_serial,_data_size)
        else:
            print "serial is close"

    def _get_data(self, _serial, _size):
        try:
            if _size:
                _receive_data = _serial.read(_size)
                if '\r\n' in _receive_data:
                    _receive_data = _receive_data.split('\r\n')[-4:]
                    _receive_data = _receive_data[0]
                if len(_receive_data) > 0:
                    print "Receive signal: ", _receive_data

                    return _receive_data
        except Exception:
            print "Can't get data from serial."