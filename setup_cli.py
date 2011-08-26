from distutils.core import setup
import py2exe
from appinfo import about
about['name'] += ' console'
setup(
    console=['pyagilent.py'],
    data_files = ["pyagilent.bat",],
    zipfile = None,
    options={"py2exe":{
        "bundle_files":1,
        "dist_dir":'pyagilent'
            }
        },
    **about)
