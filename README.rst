==========
pyFuncGen
==========

Waveform function generator control
===================================

This software allows to remotely control a wavefrom function generator 
and run defined voltage/frequency protocols on it. It mainly targets 
electroformation of giant lipid unilamellar vesicles, but can also be used for 
GUV electrodeformation experiments.

The program is written in Python using pyVISA or pySerial to communicate 
to the device and wxPython for graphical user interface.

Currently supported:

=========== =========    =============
**Company** **Model**    **Interface**
----------- ---------    -------------
Agilent     33220A       VISA
TTI         TGA1230      serial
=========== =========    =============