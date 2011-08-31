"""Abstracts the Agilent Function Generator A, pyVISA-based

"""
from funcgen import instrument, FuncGen

#TODO: check for actual supported range and precision
# for freq and ampl

class AgilentFuncGen(FuncGen):
    """Represents an Agilent 33220A function generator"""
    def __init__(self, devname):
        super(AgilentFuncGen, self).__init__(devname)
            
    def _get_modes(self):
        return ['SIN','SQU','RAMP','DC','NOIS','PULS','USER']
    modes = property(_get_modes, None, None, "Supported output modes")
    
    def connect(self):
        self.dev.write("SYST:COMM:RLST REM")
    
    def disconnect(self):
        self.dev.write("SYST:COMM:RLST LOC")
    
    def _set_output(self, value):
        if value:
            self.dev.write("OUTP ON")
        else:
            self.dev.write("OUTP OFF")
    def _get_output(self):
        return bool(self.dev.ask("OUTP?"))
    output = property(_get_output, _set_output, None, "State of the device output")
    
    def _set_freq(self, f):
        self.dev.write("FREQ %.6f"%f)
    def _get_freq(self):
        return float(self.dev.ask("FREQ?"))
    freq = property(_get_freq, _set_freq, None, "Field frequency")
    
    def _set_ampl(self, u):
        self.dev.write("VOLT %.2f"%u)
    def _get_ampl(self):
        return float(self.dev.ask("VOLT?"))
    ampl = property(_get_ampl, _set_ampl, None, "Field amplitude")
    
    def apply(self, f, u=None, offset=None, mode='SIN'):
        if mode.upper() in self.modes:
            cmd = mode.upper() + ' %.6f'%f
            if u:
                cmd += ', %.2f'%u
                if offset:
                    CMD += ', %.2f'%offset
            self.dev.write("APPL:%s"%cmd)
        
    def clear_display(self):
        self.dev.write("DISP:TEXT:CLE")
    
    def set_display(self, *lines):
        if len(lines) == 1:
            text = lines[0]
        else:
            text = '\r'.join(lines)
        self.dev.write("DISP:TEXT '%s'"%text)
