"""Devices supported by pyFuncGen project.

Extending
=========

It should be fairly possible to add support to other devices approximately 
as follows:

- create a Python module in this package named as your device, 
  and add this name to the ``implemented`` list inside this very file.
- your new device module must expose for import:
  
  - a function ``get_devices``, that must return the list of available possibly 
    connected devices (this has to do more with the connection protocol used);
  - a class representing your device, named the same as the module itself.
    The constructor of the class must accept a string from your 
    ``get_devices`` function as a first argument.
    Check the code and the module docstring of ``wxfuncgen.py`` for the 
    attributes and methods that need to be iplemented.

"""

implemented = ['Agilent33220A', 
               'TtiTga1230',
               ]