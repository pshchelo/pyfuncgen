"""Abstraction of general function generator, pyVISA-based.

Provides meta-class, that must be subclassed.

"""

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
            self.offset = 0
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
            elif cmd_words[0] == 'VOLT:OFF?':
                return self.offset
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
            #TODO: why not empty list?
            devlist = ['no devices']
        return devlist

class FuncGen(object):
    """This is an abstraction of general pyVISA-based function generator.
    
    This meta-class defines the API, and most methods must be overriden 
    in the subclass and provide specific VISA commands setted by manufacturer."""
    def __init__(self, devname):
        try:
            self.dev = instrument(devname)
        except:
            self.dev = None

    def _get_modes(self):
        print "Must be implemented in subclass"
    modes = property(_get_modes, None, None, "Supported output modes")
    
    def _whoami(self):
        """Pretty standard command, but might be overloaded in subclass"""
        return self.dev.ask("*IDN?")
    whoami = property(_whoami, None, None, 'Internal device name')
    
    def connect(self):
        print "Must be implemented in subclass"
    
    def disconnect(self):
        print "Must be implemented in subclass"
    
    def reset(self):
        """Pretty standard command, but might be overloaded in subclass"""
        self.dev.write("*RST")
        
    def close(self):
        """THis is provided by pyVISA, so it is there for granted."""
        self.dev.close()
    
    def _set_output(self, value):
        print "Must be implemented in subclass"
    def _get_output(self):
        print "Must be implemented in subclass"
    output = property(_get_output, _set_output, None, "State of the device output")
    
    def _set_freq(self, f):
        print "Must be implemented in subclass"
    def _get_freq(self):
        print "Must be implemented in subclass"
    freq = property(_get_freq, _set_freq, None, "Field frequency")
    
    def _set_ampl(self, u):
        print "Must be implemented in subclass"
    def _get_ampl(self):
        print "Must be implemented in subclass"
    ampl = property(_get_ampl, _set_ampl, None, "Field amplitude")
    
    def clear_display(self):
        print "Must be implemented in subclass"
    
    def set_display(self, *lines):
        print "Must be implemented in subclass"
