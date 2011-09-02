"""Abstracts the Agilent Function Generator A, pyVISA-based

"""
from funcgen import instrument, FuncGen

class AgilentFuncGen(FuncGen):
    """Represents an Agilent 33220A function generator"""
    def __init__(self, devname):
        super(AgilentFuncGen, self).__init__(devname)
        self.freqrange = (1.0e-6, 2.0e7)
        self.minampl = 1.e-2 #for 50 Ohm output
        self.maxout = 5 # for 50 Ohm output
        self.freqacc = "%.6f"
        self.amplacc = "%.4f"
        self.offsetacc = '%.4f'
            
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
        
    def _set_freq(self, f):
        f = self._clip_freq(f)
        fstr = self.freqacc%f
        self.dev.write("FREQ %s"%fstr)
    def _get_freq(self):
        return float(self.dev.ask("FREQ?"))
    freq = property(_get_freq, _set_freq, None, "Field frequency")
    
    def _set_ampl(self, u):
        u = self._clip_ampl(u)
        ustr = self.amplacc%u
        self.dev.write("VOLT %s"%ustr)
    def _get_ampl(self):
        return float(self.dev.ask("VOLT?"))
    ampl = property(_get_ampl, _set_ampl, None, "Field amplitude")

    def _set_offset(self, offset):
        offset = self._clip_offset(offset)
        offsetstr = self.offsetacc%offset
        self.dev.write("VOLT:OFF %s"%offsetstr)
    def _get_offset(self):
        return float(self.dev.ask("VOLT:OFF?"))
    offset = property(_get_offset, _set_offset, None, "Field DC Offset")
    
    def apply(self, f, u=None, offset=None, mode='SIN'):
        if mode.upper() in self.modes:
            f = self._clip_freq(f)
            cmd = mode.upper() + ' '+ self.freqacc%f
            if u:
                u = self._clip_ampl(u)
                cmd += ', '
                cmd += self.amplacc%u
                if offset:
                    offset = self._clip_offset(offset)
                    cmd += ', '
                    cmd += self.offsetacc%offset
            self.dev.write("APPL:%s"%cmd)
        
    def clear_display(self):
        self.dev.write("DISP:TEXT:CLE")
    
    def set_display(self, *lines):
        if len(lines) == 1:
            text = lines[0]
        else:
            text = '\r'.join(lines)
        self.dev.write("DISP:TEXT '%s'"%text)
