from distutils.core import setup
import py2exe

APPNAME = 'pyFuncGen'

# this manifest enables the standard Windows XP/Vista-looking theme
manifest = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
  />
  <description>%(prog)s</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel
            level="asInvoker"
            uiAccess="false">
        </requestedExecutionLevel>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
            type="win32"
            name="Microsoft.VC90.CRT"
            version="9.0.21022.8"
            processorArchitecture="x86"
            publicKeyToken="1fc8b3b9a1e18e3b">
      </assemblyIdentity>
    </dependentAssembly>
  </dependency>
  <dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
  </dependency>
</assembly>
"""%{'prog':APPNAME}

setup(
    name = APPNAME,
    version = '0.3.1',
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
    
    ## data_files = [
                        ## ('res', ['res/agilentgui.xrc']),
                        ## ],
    ## zipfile = None,
    
    options = {'py2exe':{
                                    "bundle_files":1,
                                    },
                    }
)