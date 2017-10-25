import os, pty, serial

class Simulator(object):

    def __init__(self):
        self.master, self.slave = pty.openpty()
        self.s_name = os.ttyname(self.slave)
        self.ser = serial.Serial(self.s_name)

    def send_msg(self, string):
        self.ser.write(string)
        print "msg sent!"

    def get_msg(self):
        _msg = os.read(self.master, 1000)
        print "get msg: ", _msg