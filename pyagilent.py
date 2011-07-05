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

##import visa

def get_devices():
    try:
        devlist = visa.get_instruments_list()
    except VisaIOError:
        devlist = []
    return devlist
    
def connect(devname):
    print "Connect not implemented. Device supplied: %s"%devname
    try:
        device = visa.instrument(devname)
    except VisaIOError:
        device=None
    return device
    
def disconnect(device):
    print "Disconnect not implemented. Device supplied: %s"%device
    device.write("OUTP OFF")
    device.write("DISP:TEXT:CLE")
    device.write("SYST:COMM:RLST LOC")
    device.close()
    
def set_freq(device, freq):
    device.write("FREQ %d"%freq)

def set_volt(device, volt):
    device.write("VOLT %d"%volt)

def display(device, line1, line2=None):
    if line2:
        line1 = '\r'.join(line1,line2)
    device.write("DISP:TEXT '%s'"%line1)

def _main():
    pass

if __name__=='__main__':
    _main()