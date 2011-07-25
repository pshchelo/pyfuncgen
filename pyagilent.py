"""Control the Agilent function generator with PyVISA over USB
1 : import visa
2 : visa.get_instruments_list()
3 : visa.get_instruments_list()
4 : fg = visa.instrument('USBInstrument2')
5 : fg
6 : fg.write('*RST')
7 : fg.write("FREQ 10")
8 : fg.write("VOLT 0.5")
9 : fg.write("OUTP ON")
10: fg.write("DISP:TEXT 'Voltage 0.5 Vpp\rFrequency 10 Hz'")
11: fg.write("DISP:TEXT:CLE")
12: fg.write("OUTP OFF")
13: fg.clear()
14: fg.close()
15: fg = visa.instrument('USBInstrument2')
16: fg.write("DISP:TEXT 'Voltage 0.5 Vpp\rFrequency 10 Hz'")
17: fg.write("DISP:TEXT:CLE")
18: fg.write("SYST:COMM:RLST LOC")
19: fg.write("*RST")
"""
from __future__ import division
from sys import stdout
## from visa import get_instruments_list, instrument

# Dummy substitutes for real pyVISA classes and functions
# for developing/debugging on platforms without VISA implementation
# and/or connected devices
def get_instruments_list():
    return ['dev1', 'dev2']

def instrument(name):
    return DummyDevice(name)

class DummyDevice(object):
    def __init__(self, name):
        self.name = name
    def write(self, cmd):
        print '%s - %s'%(self.name, cmd)
    def close(self):
        del self
# end of dummy classes and functions         
        

class AgilentFuncGen(object):
    """Represents a said function generator"""
    def __init__(self, devname):
        self.connect(devname)
    
    def connect(self, devname):
        if devname in get_instruments_list():
            self.dev = instrument(devname)
        else:
            self.dev = None
    
    def reset(self):
        self.dev.write("*RST")
        
    def disconnect(self):
        self.out_off()
        self.dev.write("DISP:TEXT:CLE")
        self.reset()
        self.dev.dev.write("SYST:COMM:RLST LOC")
        self.dev.close()
        self.__del__()
    
    def out_off(self):
        self.dev.write("OUTP OFF")

    def out_on(self):
        self.dev.write("OUTP ON")
        
    def set_freq(self, f):
        self.dev.write("FREQ %.6f"%f)
    
    def set_volt(self, u):
        self.dev.write("VOLT %.2f"%u)
    
    def set_display(self, *lines):
        if len(lines) > 1:
            text = lines[0]
        else:
            text = '\r'.join(lines)
        self.dev.write("DISP:TEXT '%s'"%text)
    
    
def get_devices():
    try:
        devlist = get_instruments_list()
    except:
        devlist = []
    return devlist
    

def update_disp(device, mesg, u, f, t):
    if u:
        u = '%.2f'%u
    else:
        u = '--'
    if f:
        f = '%.2f'%f
    else:
        f = '--'
    T = '%i:%i'%(t//60, t%60)
    line1 = "%s - %s"%(mesg, T)
    line2 = '%s Vpp | %s Hz'%(u,f)
    device.set_display(line1, line2)
    line = line2+' | %s'%T
    update_stdout(line)
    
## def update_finished(device, t):
    ## T = '%i:%i'%(t//60, t%60)
    ## device.set_display('FINISHED', T)
    
    
def update_stdout(line):
    stdout.write('\r'+line)
    stdout.flush()
    
def grow_3stages():
    """Grow vesicles in 3 stages"""
    import argparse
    import time
    import sys
    import pprint
    from numpy import linspace
    
    #parsing arguments
    
    optparser = argparse.ArgumentParser(description=
    "Grow vesicles in 3 stages.", epilog='Defaults are for high salinity.')
    optparser.add_argument('-l', '--list', action='store_true', 
        help='Lisl available devices and exit')
    optparser.add_argument('device', choices=get_instruments_list(),
        default=get_instruments_list()[0],
        help='Device code to connect with', nargs='?')
    optparser.add_argument('-u1', type=float, default=0.1,
        help='Initial voltage, Vpp')
    optparser.add_argument('-u2', type=float, default=2.5,
        help='Final voltage, Vpp')
    optparser.add_argument('-f1', type=float, default=500,
        help='Main frequency, Hz')
    optparser.add_argument('-f2', type=float, default=50,
        help='Detachment frequency, Hz')
    optparser.add_argument('-t1', type=int, default=30,
        help='Duration of growing stage, min')
    optparser.add_argument('-t2', type=int, default=60,
        help='Duration of resting stage, min')
    optparser.add_argument('-t3', type=int, default=30, 
        help='Duration of detachment stage, min')
    optparser.add_argument('-dt', type=int, default=5, 
        help='Update interval of values/displays, sec')
    
    args = optparser.parse_args()
    
    if args.list:
        pprint.pprint(get_instruments_list())
        sys.exit(0)

    Ustart = args.u1
    Uend = args.u2
    Fmain = args.f1
    Fdetach = args.f2
    Tgrow = args.t1
    Trest = args.t2
    Tdetach = args.t3
    Trez = args.dt

    fg = AgilentFuncGen(args.device)
    if not fg.dev:
        print 'could not connect to device'
        sys.exit(1)
    
    #growing stage
    stage = 'Growing'
    print stage
    Ngrow = Tgrow*60//Trez
    U = linspace(Ustart, Uend, Ngrow)
    fg.set_freq(Fmain)
    fg.set_volt(Ustart)
    fg.out_on()
    for i, u in enumerate(U):
        time.sleep(Trez)
        fg.set_volt(u)
        Tremain = Tgrow*60-i*Trez
        update_disp(fg, stage, u, Fmain, Tremain)
    
    #resting stage
    stage = 'Resting'
    print stage
    fg.set_freq(Fmain)
    fg.set_volt(Uend)
    Nrest = Trest*60//Trez
    for i in range(Nrest):
        time.sleep(Trez)
        Tremain = Trest*60-i*Trez
        update_disp(fg, stage, Uend, Fmain, Tremain)
        
    #detachment stage
    stage = 'Detaching'
    print stage
    fg.set_volt(Uend)
    Ndetach = Tdetach*60//Trez
    F = linspace(Fmain, Fdetach, Ndetach)
    for i, f in enumerate(F):
        time.sleep(Trez)
        fg.set_freq(f)
        Tremain = Tdetach*60-i*Trez
        update_disp(fg, stage, Uend, f, Tremain)
    
    #after-counter
    stage = 'Finished'
    print stage
    fg.out_off()
    print "Hit Ctrl-C to stop"
    stop = False
    start = time.time()
#TODO: allow for interrupt with any key press
    while not stop:
        time.sleep(Trez)
        T = time.time()- start
        update_disp(fg, stage, None, None, T)
    fg.disconnect()
    
if __name__=='__main__':
    grow_3stages()