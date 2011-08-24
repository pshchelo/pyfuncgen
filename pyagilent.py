"""Control the Agilent function generator with PyVISA over USB

With working visa implementation but without any connected devices:
from visa import ... works fine
get_instruments_list throws VisaIOError exception

With pyvisa installed but without a working visa implementation:
from visa import ... fails with AttributeError: function 'viOpen' not found
"""
from __future__ import division
from sys import stdout, exit
import argparse
from time import time, sleep

# catch situation of pyVISA not installed or installed with no low-level VISA implementation present
try:
    from visa import get_instruments_list, instrument, VisaIOError
except (ImportError, AttributeError):
    print "Warning! Using dummies instead of real VISA."
    # Dummy substitutes for developing/debugging 
    # on platforms without pyVISA / VISA implementation
    def get_devices():
        return ['dev1', 'dev2']

    def instrument(name):
        return DummyDevice(name)

    class DummyDevice(object):
        def __init__(self, name):
            self.name = name
            self.u = 0.1
            self.f = 10000.0
        def write(self, cmd):
            print '%s - %s'%(self.name, cmd)
            cmd_words = cmd.split()
            if cmd_words[0] == 'FREQ':
                self.f = float(cmd_words[1])
            elif cmd_words[0] == 'VOLT':
                self.u = float(cmd_words[1])
        def close(self):
            del self
        def ask(self, cmd):
            print '%s was asked for "%s"'%(self.name, cmd)
            cmd_words = cmd.split()
            if cmd_words[0] == 'FREQ?':
                return self.f
            elif cmd_words[0] == 'VOLT?':
                return self.u
            elif cmd_words[0] == '*IDN?':
                return self.name
    
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

class AgilentFuncGen(object):
    #TODO: hide getters and setters of properties where it makes sense
    #TODO: complete apply function, may be ditching freq and freq
    #TODO: check for actual supported precision of freq and ampl
    """Represents a function generator"""
    def __init__(self, devname):
        try:
            self.dev = instrument(devname)
        except:
            self.dev = None
    
    def _whoami(self):
        return self.dev.ask("*IDN?")
    whoami = property(_whoami, None, None, 'Internal device name')
    
    def connect(self):
        self.dev.write("SYST:COMM:RLST REM")
    
    def disconnect(self):
        self.dev.write("SYST:COMM:RLST LOC")
    
    def reset(self):
        self.dev.write("*RST")
        
    def close(self):
        self.dev.close()
    
    def out_off(self):
        self.dev.write("OUTP OFF")

    def out_on(self):
        self.dev.write("OUTP ON")
    
    def set_output(self, value):
        if value:
            self.out_on()
        else:
            self.out_off()
    def get_output(self):
        return bool(self.dev.ask("OUTP?"))
    output = property(get_output, set_output, None, "State of the device output")
    
    def set_freq(self, f):
        self.dev.write("FREQ %.6f"%f)
    def get_freq(self):
        return float(self.dev.ask("FREQ?"))
    freq = property(get_freq, set_freq, None, "Field frequency")
    def set_ampl(self, u):
        self.dev.write("VOLT %.2f"%u)
    def get_ampl(self):
        return float(self.dev.ask("VOLT?"))
    ampl = property(get_ampl, set_ampl, None, "Field amplitude")
    
    def apply_sin(self, f, u=None, offset=None, mode='SIN'):
        accepted_modes = ['SIN','SQU','RAMP','DC','NOIS','PULS','USER']
        f_str = '%.6f'%f
        if u:
            u_str = '%.2f'%u
        else:
            u_str = ''
        if offset:
            offset_str = '%.2f'%offset
        else:
            offset_str = ''
        if mode.upper() in accepted_modes:
            self.dev.write("APPL:%s %s %s %s")%(mode, f_str, u_str, oddset_str)
        
    def clear_display(self):
        self.dev.write("DISP:TEXT:CLE")
    
    def set_display(self, *lines):
        if len(lines) == 1:
            text = lines[0]
        else:
            text = '\r'.join(lines)
        self.dev.write("DISP:TEXT '%s'"%text)
        
def update_disp(device, mesg, u, f, t):
    if u:
        u = '%.2f'%u
    else:
        u = '--'
    if f:
        f = '%.2f'%f
    else:
        f = '--'
    T = '%i:%02i'%(t//60, t%60)
    line1 = "%s - %s"%(mesg, T)
    line2 = '%s Vpp | %s Hz'%(u,f)
    device.set_display(line1, line2)
    line = line2+' | %s'%T
    update_stdout(line)
    
def update_stdout(line):
    blank = ' '*40
    stdout.write('\r%s\r%s'%(blank, line))
    stdout.flush()
    
def grow_3stages():
    """Grow vesicles in 3 stages"""
    #parsing arguments
    optparser = argparse.ArgumentParser(description=
    "Grow vesicles in 3 stages.", epilog='(Defaults) are for high salinity.')
    optparser.add_argument('-l', '--list', action='store_true', 
        help='List available devices and exit')
    if len(get_devices()) == 0:
        defaultdevice = None
    else:
        defaultdevice = get_devices()[0]
    optparser.add_argument('device', choices=get_devices(),
        default=defaultdevice,
        help='Device code to connect with (first found)', nargs='?')
    optparser.add_argument('-u1', type=float, default=0.1,
        help='Initial voltage, Vpp (0.1)')
    optparser.add_argument('-u2', type=float, default=2.5,
        help='Final voltage, Vpp (2.5)')
    optparser.add_argument('-f1', type=float, default=500,
        help='Main frequency, Hz (500)')
    optparser.add_argument('-f2', type=float, default=50,
        help='Detachment frequency, Hz (50)')
    optparser.add_argument('-t1', type=int, default=30,
        help='Duration of growing stage, min (30)')
    optparser.add_argument('-t2', type=int, default=60,
        help='Duration of resting stage, min (60)')
    optparser.add_argument('-t3', type=int, default=30, 
        help='Duration of detachment stage, min (30)')
    optparser.add_argument('-dt', type=int, default=5, 
        help='Update interval of values/displays, sec (5)')
    
    args = optparser.parse_args()
    
    if args.list:
        print get_devices()
        exit(0)

    Ustart = args.u1
    Uend = args.u2
    Fmain = args.f1
    Fdetach = args.f2
    Tgrow = args.t1
    Trest = args.t2
    Tdetach = args.t3
    Trez = args.dt

    fg = AgilentFuncGen(args.device)
    fg.connect()
    if not fg.dev:
        print 'could not connect to device %s'%fg.devname
        exit(0)
    
    #growing stage
    stage = 'Growing'
    print '\n'+stage
    Ngrow = Tgrow*60//Trez
    StepUgrow = (Uend-Ustart)/Ngrow
    U = [Ustart+i*StepUgrow for i in range(Ngrow+1)]
    fg.set_freq(Fmain)
    fg.set_ampl(Ustart)
    fg.out_on()
    for i, u in enumerate(U):
        fg.set_ampl(u)
        Tremain = Tgrow*60-i*Trez
        update_disp(fg, stage, u, Fmain, Tremain)
        sleep(Trez)
    
    #resting stage
    stage = 'Resting'
    print '\n'+stage
    Nrest = Trest*60//Trez
    for i in range(Nrest):
        Tremain = Trest*60-i*Trez
        update_disp(fg, stage, Uend, Fmain, Tremain)
        sleep(Trez)
        
    #detachment stage
    stage = 'Detaching'
    print '\n'+stage
    Ndetach = Tdetach*60//Trez
    StepFdetach = (Fdetach-Fmain)/Ndetach
    F = [Fmain+i*StepFdetach for i in range(Ndetach+1)]
    for i, f in enumerate(F):
        fg.set_freq(f)
        Tremain = Tdetach*60-i*Trez
        update_disp(fg, stage, Uend, f, Tremain)
        sleep(Trez)
    
    #after-counter
    stage = 'Finished'
    print '\n'+stage
    fg.out_off()
    print "Hit Ctrl-C to stop"
    start = time()
    while True:
        try:
            sleep(Trez)
            T = time()- start
            update_disp(fg, stage, None, None, T)
        except KeyboardInterrupt:
            break
    fg.clear_display()
    fg.disconnect()
    fg.close()
    
if __name__=='__main__':
    grow_3stages()
