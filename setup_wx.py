from distutils.core import setup
import py2exe

APPNAME = 'pyFuncGen'

# this manifest enables the standard Windows XP/Vista-looking theme
manifest = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

    </dependentAssembly>
  </dependency>
</assembly>
"""%{'prog':APPNAME}

setup(
    name = APPNAME,
    version = '0.2.1',
    description = 'Function Generator Control',
    long_description = 'Control and run automated protocols on Function Generator',
    author = 'Pavlo Shchelokovskyy',
    author_email = 'shchelokovskyy@gmail.com',
    url = 'http://sites.google.com/shchelokovskyy',
    
    windows =[
                        {
                            'script':'wxagilent.pyw',
                            ## 'icon_resources': [(1, "icon.ico")],
                            'other_resources': [( 24, 1, manifest)],
                        }
                    ],
    
    data_files = [
                        ('res', ['res/agilentgui.xrc']),
                        ],
    ## zipfile = None,
    
    options = {'py2exe':{
                                    "bundle_files":1,
                                    },
                    }
)