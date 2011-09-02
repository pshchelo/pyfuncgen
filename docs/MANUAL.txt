===========================================
pyFuncGen - Waveform function generator control made with pyVISA
===========================================
Targeted for Agilent Technologies 33220A function generator in the first place, but can be accomodated for any other function generator supporting VISA interface. For this you would simply write your class similar to AgilentFuncGen inheriting from FuncGen, overriding the methods and using neccesary actual textual commands to be sent to device.

There are two programs available - wxagilent.exe (a preferred one, with graphical user interface) and agilentgrow.exe (a much simpler command-line version for older non-Unicode systems, like Windows 2000 and earlier)

wxAgilent 
======
control the generator manually or execute automatic protocol

What you can do with it
--------------------------
connect to a chosen VISA device or disconnect from currently connected one
set device's frequency and amplitude (no offset setting in GUI yet, although already supported by API)
turn output on or off
compose a protocol to be run on the function generator
save a written protocol for further use or load an existing protocol
run the protocol with possibility to pause or abort it's execution

Connecting to the device
---------------------------
When you start the program it automatically scans your system for available devices and populates the devices dropdown list with found ones. If the list is empy, make sure that the device is connected and hit "refresh" button. If your device list is composed of 'test device 1' and 'test device 2', than you do not have a proper VISA implementation installed.

Press "connect" button to connect to the chosen device. 

Manual Control
----------------
