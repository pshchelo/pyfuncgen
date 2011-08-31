from distutils.core import setup
import py2exe
from appinfo import about
about['name'] += ' console'
setup(
    console=['agilentgrow.py'],
    data_files = ["agilentgrow.bat",],
    zipfile = None,
    options={"py2exe":{
        "bundle_files":1,
        "dist_dir":'agilentgrow'
            }
        },
    **about)
