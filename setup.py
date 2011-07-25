from distutils.core import setup
import py2exe

setup(
        console=['pyagilent.py'],
        data_files = ["pyagilent.bat",],
        options={"py2exe":{
                            "excludes":["pywin", "pywin.debugger", 
                                            "pywin.debugger.dbgcon",
                                            "pywin.dialogs", "pywin.dialogs.list",
                                            "Tkconstants","Tkinter","tcl"],
                            "bundle_files":1,
                                        }
                    }
        )
