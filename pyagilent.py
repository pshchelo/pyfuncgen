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
##from visa import get_instruments_list, instrument
def get_instruments_list():
    return ['dev1', 'dev2']
def instrument(name):
    return DumbDevice(name)
class DumbDevice(object):
    def __init__(self, name):
        self.name = name
    def write(self, cmd):
        print '%s - %s'%(self.name, cmd)
    def close(self):
        del self

def get_devices():
    try:
        devlist = get_instruments_list()
    except:
        devlist = []
    return devlist
    
def connect(devname):
    try:
        device = instrument(devname)
        device.write("*RST")
    except VisaIOError:
        device=None
    return device
    
def disconnect(device):
    dev_off(device)
    device.write("DISP:TEXT:CLE")
    device.write("SYST:COMM:RLST LOC")
    device.close()

def dev_on(device):
        device.write("OUTP ON")
        
def dev_off(device):
        device.write("OUTP OFF")
        
def set_freq(device, freq):
    device.write("FREQ %d"%freq)

def set_volt(device, volt):
    device.write("VOLT %d"%volt)

def set_display(device, line1, line2=None):
    if line2:
        line1 = '\r'.join((line1,line2))
    device.write("DISP:TEXT '%s'"%line1)

def update_disp(device, mesg, u, f, t):
    T = '%i:%i'%(t//60, t%60)
    line1 = "%s - %s"%(mesg, T)
    line2 = '%.2f Vpp, %.2f Hz'%(u,f)
    set_display(device, line1, line2)
    print '\n'.join((line1, line2))
    
def update_finished(device, t):
    T = '%i:%i'%(t//60, t%60)
    set_display(device, 'FINISHED', T)
    print '\n'.join(('FINISHED', T))
    
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
    optparser.add_argument('-t1', type=float, default=30,
        help='Duration of growing stage, min')
    optparser.add_argument('-t2', type=float, default=60,
        help='Duration of resting stage, min')
    optparser.add_argument('-t3', type=float, default=30, 
        help='Duration of detachment stage, min')
    optparser.add_argument('-dt', type=float, default=5, 
        help='Update interval of values/displays, sec')
    
    args = optparser.parse_args()
    
    if args.list:
        pprint.pprint(get_instruments_list())
        sys.exit(0)
    
    devname = args.device
    Ustart = args.u1
    Uend = args.u2
    Fmain = args.f1
    Fdetach = args.f2
    Tgrow = args.t1
    Trest = args.t2
    Tdetach = args.t3
    Trez = args.dt

    dev = connect(devname)
    
    #growing stage
    Ngrow = Tgrow*60//Trez
    U = linspace(Ustart, Uend, Ngrow)
    set_freq(dev, Fmain)
##    dev_on(dev)
    for i, u in enumerate(U):
        time.sleep(Trez)
        set_volt(dev, u)
        Tremain = Tgrow*60-i*Trez
        update_disp(dev, 'Growing', u, Fmain, Tremain)
    
    #resting stage
    set_freq(dev, Fmain)
    set_volt(dev, Uend)
    Nrest = Trest*60//Trez
    for i in range(Nrest):
        time.sleep(Trez)
        Tremain = Trest*60-i*Trez
        update_disp(dev, 'Resting', Uend, Fmain, Tremain)
        
    #detachment stage
    set_volt(dev, Uend)
    Ndetach = Tdetach*60//Trez
    F = linspace(Fmain, Fdetach, Ndetach)
    for i, f in enumerate(F):
        time.sleep(Trez)
        ser_freq(dev, f)
        Tremain = Tdetach*60-i*Trez
        update_disp(dev, 'Detaching', Uend, f, Tremain)
    
    #after-counter
    stop = False
    start = time.time()
    while not stop:
        time.sleep(Trez)
        T = time.time()- start
        update_finished(dev, T)

    

if __name__=='__main__':
    grow_3stages()