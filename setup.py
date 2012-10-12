from cx_Freeze import setup, Executable

about = {'name':'pyFuncGen',
		'version':'0.5',
		'description':'Function Generator Control',
		'long_description':'Control (GUI) and Run automated protocols (GUI/CLI) on Function Generator',
		'author':'Pavlo Shchelokovskyy',
		'author_email':'shchelokovskyy@gmail.com',
		'url':'http://bitbucket.org/pshchelo/pyfuncgen',
}

includes = []
excludes=[]
packages = ["devices", "visa", "serial"]
include_files = ['docs', ("scripts/agilentgrow.bat", "agilentgrow.bat")]

gui_exe = Executable(script='wxfuncgen.pyw',
                     base='Win32GUI',
                     icon='res\Function_Generator.ico')

cli_exe = Executable(script='agilentgrow.py')

setup(options={"build_exe": {'includes':includes, 'excludes':excludes, 
                             'packages':packages, 
                             'include_files':include_files,
                             'compressed':True,
                             'append_script_to_exe':True}},
        executables=[gui_exe, cli_exe],
        **about)
