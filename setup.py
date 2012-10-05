from distutils.core import setup
import py2exe
from appinfo import about

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
"""%{'prog':about['name']}

setup(    
    windows = [
        {
        'script':'wxfuncgen.py',
        'icon_resources': [(1, "res/Function_generator.png")],
        'other_resources': [( 24, 1, manifest)],
        }
    ],
    console = ['agilentgrow.py'],
    data_files = ["scripts/agilentgrow.bat",
                            ('docs',['LICENSE.txt','docs/MANUAL.txt'])],
    options = {'py2exe':{
        'bundle_files':1,
        'dll_excludes':['w9xpopen.exe']
        },
                    },
    **about)
