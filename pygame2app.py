#@+leo-ver=4-thin
#@+node:jpenner.20050604144534:@thin pygame2app.py
#@@language python
#make standalone, needs at least pygame-1.5.3 and py2exe-0.3.1

from distutils.core import setup
import sys, os, pygame, shutil, glob
import py2app      

#setup the project variables here.
#i can't claim these will cover all the cases
#you need, but they seem to work for all my
#projects, just change as neeeded.


script = "TennisForTwo.py"	#name of starting .PY
icon_file = ""	    	    	#ICO file for the .EXE (not working well)
optimize = 2 	    	    	#0, 1, or 2; like -O and -OO
dos_console = 0     	    	#set to 0 for no dos shell when run
extra_data = ['data'] #extra files/dirs copied to game
extra_modules = ['pygame.locals']   #extra python modules not auto found






#use the default pygame icon, if none given
if not icon_file:
    path = os.path.split(pygame.__file__)[0]
    icon_file = '"' + os.path.join(path, 'pygame.ico') + '"'
#unfortunately, this cool icon stuff doesn't work in current py2exe :(
#icon_file = ''

project_name = os.path.splitext(os.path.split(script)[1])[0]


#this will create the executable and all dependencies
setup(#name=project_name,
      app=[script],
      data_files=[("data", glob.glob("data\\*"))]
     )


#@-node:jpenner.20050604144534:@thin pygame2app.py
#@-leo
