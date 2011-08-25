from distutils.core import setup
import py2exe
APPNAME = 'pyFuncGen'
setup(
        name = APPNAME+'console protocol'
        version = '0.3.1',
        description = 'Function Generator Control',
        long_description = 'Run automated protocols on Function Generator',
        author = 'Pavlo Shchelokovskyy',
        author_email = 'shchelokovskyy@gmail.com',
        url = 'http://sites.google.com/shchelokovskyy',
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
