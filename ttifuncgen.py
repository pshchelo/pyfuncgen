# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 12:01:38 2012

@author: Pavlo Shchelokovskyy
"""
import time
import serial
from serial.tools.list_ports import comports

def list_serial():
    """Return a list of available serial ports in the form suitable to pass to pyserial"""
    seriallist = []
    for item in comports():
        seriallist.append(item[0])
    return seriallist
    
class TTIserial(object):
    """Represents a TTI1230 function generator

    May as well work for other devices of the same manufacturer.   
    """
    def __init__(self, port, **kwargs):
        """kwargs are for serial.Serial object"""
        self.portconfigs = kwargs
        # these settings are needed for communication to work
        self.portconfigs['xonxoff'] = True
        
        self.port = port
        self.dev = None
        
#TODO: check real params for TTI1230
        #these are the specs of TTI1240
        self.minampl = 0
        self.maxout = 10
        self.ampldigits = 3
        self.freqdigits = 3
        self.freqrange = (1.0e-6, 16e6)

        self.connect()

        # these are default settings when the device is powered on
        self.offsetstate = 0
        self.amplstate = 2
        self.freqstate = 10
        self.outputstate = False
        self.modestate = "SINE"
        self._init_state
        
    def _init_state(self):
        self.ampl = self.amplstate
        self.offset = self.offsetstate
        self.freq = self.freqstate
        self.output = self.outputstate
        self.mode = self.modestate
        
    def _get_modes(self):
        return ['SINE', 'SQUARE', 'TRIANG', 'DC', 
                'POSRMP', 'NEGRMP', 'COSINE', 'HAVSIN', 
                'HAVCOS', 'SINC', 'PULSE', 'PULSTRN', 'ARB', 'SEQ']
    modes = property(_get_modes, None, None, "Supported output modes")
    
    def connect(self):
        if not bool(self.dev):
            self.dev = serial.Serial(self.port, **self.portconfigs)
          
    def write(self, string):
        if bool(self.dev):
            self.dev.write("%s\n"%string)
        
    def read(self):
        if bool(self.dev):
            text = self.dev.read(self.dev.inWaiting())
            return text.replace('\r\n', '')
        
    def disconnect(self):
        if bool(self.dev):
            self.write("LOCAL")
    
    def close(self):
        if bool(self.dev):
            self.dev.close()
            self.dev = None
        
    def whoami(self):
        """Internal device name"""
        if bool(self.dev):
            self.write("*IDN?")
            #XXX: pause needed for device to form response
            time.sleep(0.06)
            return self.read()
    
    def set_display(self, *lines):
        """Dummy function, since device does not support it"""
        pass
    def clear_display(self):
        """Dummy function, since device does not support it"""
        pass

    def _set_mode(self, mode):
        if mode in self._get_modes():
            self.write("mode %s"%mode)
        self.modestate = mode
    def _get_mode(self):
        return self.modestate
    mode = property(_get_mode, _set_mode, None, "Waveform of the output")

    def _set_output(self, value):
        if value:
            self.write("output ON")
        else:
            self.write("output OFF")
        self.outputstate = bool(value)
    def _get_output(self):
        return self.outputstate
    output = property(_get_output, _set_output, None, "State of the device output")
    
    def _set_freq(self, f):
        f = self._clip_freq(f)
        self.write("WAVFREQ %s"%f)
        self.freqstate = f
    def _get_freq(self):
        return self.freqstate
    freq = property(_get_freq, _set_freq, None, "Field frequency")
    
    def _set_ampl(self, u):
        u = self._clip_ampl(u)
        self.write("AMPL %s"%u)
        self.amplstate = u
    def _get_ampl(self):
        return self.amplstate
    ampl = property(_get_ampl, _set_ampl, None, "Field amplitude")
    
    def _set_offset(self, u):
        u = self._set_offset(u)
        self.write("DCOFFS %s"%u)
        self.offsetstate = u
    def _get_offset(self):
        return self.offsetstate
    offset = property(_get_offset, _set_offset, None, "Field DC offset")

    def _clip_freq(self, f):
        min, max = self.freqrange
        if f < min:
            return min
        elif f > max:
            return max
        else:
            return f
        
    def _clip_ampl(self, u):
        if u < self.minampl:
            return self.minampl
        elif self.offset + u/2 > self.maxout:
            return 2*(self.maxout - self.offset)
        elif self.offset - u/2 < -self.maxout:
            return 2*(self.maxout + self.offset)
        else:
            return u
    
    def _clip_offset(self, offset):
        if offset + self.ampl/2 > self.maxout:
            return self.maxout - self.ampl/2
        elif offset - self.ampl/2 < -self.maxout:
            return self.ampl/2 - self.maxout
        else:
            return offset
            
    def apply(self, f, u):
        self.freq = f
        self.ampl = u
    
    