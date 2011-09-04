pyFuncGen - Waveform function generator control made with pyVISA
================================================================

This software allows to remotely control the Agilent 33220A wavefrom function generator and run defined voltage/frequency protocols on it. It mainly targets electroformation of giant lipid unilamellar vesicles, but can also be used for GUV electrodeformation experiments.
The program is written in Python using pyVISA to communicate to the device and wxPython for graphical user interface.
The package includes two programs:
wxagilent - GUI program, recommended
agilentgrow - very simple command line version, allowing only to run an up to three-staged protocol (for legacy systems).

REQUIREMENTS
First of all, you need an installed and working VISA interface drivers (e.g. from Agilent Technologies or from National Instruments).

Running from source:
Any OS with Python, pyVISA and wxPython installed (developed/tested with Python 2.7.2, pyVISA 1.3 and wxPython 2.8.12.1).

Running the compiled version for Windows:
Windows 2000 or higher for commandline interface version (can be tweaked to support Win9x, see SUPPORTING LEGACY SYSTEMS)
Windows XP or higher for GUI version (can be tweaked to support older versions, see SUPPORTING LEGACY SYSTEMS).

FILES
The compiled version for Windows contains the following files:
+--docs				Documentation and license
|_ agilentgrow.bat		Helper script for CLI version
|_ agilentgrow.exe		CLI version
|_ library.zip			Dependencies
|_ wxagilent.exe		GUI version

RUNNING
To run the program you will actually need the library.zip and the executable you want to run (the CLI or GUI version). See more in the Manual.

SUPPORTING LEGACY SYSTEMS
Lack of support for Win9x version in CLI version is due to the omission of w9xpopen.exe from dependencies. Modify setup.py to include this file in the distribution and recompile the executable.
Lack of GUI support for Windows 2000 (and earlier) stems from its non-unicode nature. If you succedd to install all the dependencies of the source version under such system (Python, pyVISA and non-unicode wxPython), than you must be able to run the GUI version and to compile it to native Windows executable.


CUSTOMIZATION
The program was developed for Agilent Technologies 33220A function generator in the first place, but can be accomodated for any other function generator supporting VISA interface. For this you would simply write your class similar to AgilentFuncGen inheriting from FuncGen, overriding the methods and using neccesary actual textual commands to be sent to device.