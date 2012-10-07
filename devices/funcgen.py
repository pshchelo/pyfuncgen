"""Abstraction of general function generator, pyVISA-based.

Provides a class to define the API, that must be subclassed.

"""

class FuncGen(object):
    """This is an abstraction of general pyVISA-based function generator.
    
    This meta-class defines the API, and most methods must be overriden 
    in the subclass and provide specific VISA commands set by manufacturer."""
    def __init__(self, device):
        #check that device has minimal necessary interface
        needed_methods = set(('write', 'ask', 'colse'))
        if needed_methods.issubset(set(dir(device))):
            self.dev = device
        else:
            self.dev = None

    def _get_modes(self):
        raise NotImplementedError("Must be implemented in subclass")
    modes = property(_get_modes, None, None, "Supported output modes")
    
    def whoami(self):
        """Return internal device name
        
        Pretty standard command, but might be overloaded in subclass
        """
        return self.dev.ask("*IDN?")
    
    def connect(self):
        raise NotImplementedError("Must be implemented in subclass")
    
    def disconnect(self):
        raise NotImplementedError("Must be implemented in subclass")
    
    def reset(self):
        """Pretty standard command, but might be overloaded in subclass"""
        self.dev.write("*RST")
        
    def close(self):
        """This is provided by pyVISA, so it is there for granted."""
        self.dev.close()
    
    def _set_output(self, value):
        raise NotImplementedError("Must be implemented in subclass")
    def _get_output(self):
        raise NotImplementedError("Must be implemented in subclass")
    output = property(_get_output, _set_output, None, "State of the device output")
    
    def _set_freq(self, f):
        raise NotImplementedError("Must be implemented in subclass")
    def _get_freq(self):
        raise NotImplementedError("Must be implemented in subclass")
    freq = property(_get_freq, _set_freq, None, "Field frequency")
    
    def _set_ampl(self, u):
        raise NotImplementedError("Must be implemented in subclass")
    def _get_ampl(self):
        raise NotImplementedError("Must be implemented in subclass")
    ampl = property(_get_ampl, _set_ampl, None, "Field amplitude")
    
    def _set_offset(self, u):
        raise NotImplementedError("Must be implemented in subclass")
    def _get_offset(self):
        raise NotImplementedError("Must be implemented in subclass")
    offset = property(_get_offset, _set_offset, None, "Field DC offset")
    
    def clear_display(self):
        raise NotImplementedError("Must be implemented in subclass")
    
    def set_display(self, *lines):
        raise NotImplementedError("Must be implemented in subclass")
