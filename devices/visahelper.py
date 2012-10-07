# -*- coding: utf-8 -*-
"""catch situation of pyVISA not installed or 
installed with no low-level VISA implementation present

Created on Sat Oct 06 21:02:34 2012

@author: Pavlo Shchelokovskyy

"""

try:
    from visa import get_instruments_list, instrument, VisaIOError
except (ImportError, AttributeError):
    print "Warning! Using dummies instead of real VISA."
    # Dummy substitutes for developing/debugging 
    # on platforms without pyVISA / VISA implementation
    def get_devices():
        return ['test device 1', 'test device 2']

    def instrument(name):
        return DummyDevice(name)

    class DummyDevice(object):
        def __init__(self, name):
            self.name = name
            self.u = 0.1
            self.f = 10000.0
            self.offset = 0
            self.output = 0
        def write(self, s):
            print '%s - %s'%(self.name, s)
            cmd_words = s.split()
            cmd = cmd_words[0]
            s_params = ' '.join(cmd_words[1:])
            params = s_params.split(', ')
            if cmd[0] == 'FREQ':
                self.f = float(params[0])
            elif cmd_words[0] == 'VOLT':
                self.u = float(params[0])
            elif  'APPL' == cmd.split(':')[0]:
                self.f = float(params[0])
                if len(params) > 1:
                    self.u = float(params[1])
                    if len(params) == 3:
                        self.offset=params[2]
        def close(self):
            del self
        def ask(self, cmd):
            print '%s was asked for "%s"'%(self.name, cmd)
            cmd_words = cmd.split()
            if cmd_words[0] == 'FREQ?':
                return self.f
            elif cmd_words[0] == 'VOLT?':
                return self.u
            elif cmd_words[0] == 'VOLT:OFFS?':
                return self.offset
            elif cmd_words[0] == '*IDN?':
                return self.name
            elif cmd_words[0] == 'OUTP?':
                return self.output
    
    class VisaIOError(Exception):
        pass
    # end of dummy classes and functions
else:
    def get_devices():
        """Return list of connected VISA devices.
        
        Wrapper for pyVISA's get_instruments_list(). Use this preferably,
        since it handles situation of working VISA/pyVISA environment
        but no devices connected by returning an empty list.
        """
        try:
            devlist = get_instruments_list()
        except VisaIOError:
            devlist = []
        return devlist
