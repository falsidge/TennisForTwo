<?xml version="1.0" encoding="UTF-8"?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.603318250377">
	<global_window_position top="25" left="10" height="734" width="1280"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="jpenner.20050319120705" a="E"><vh>Files</vh>
<v t="jpenner.20050305105206" a="E"
expanded="jpenner.20050601180947,jpenner.20050305124252,jpenner.20050319143816,jpenner.20050604112932,jpenner.20050605102056,jpenner.20050305121157,jpenner.20050306103246,jpenner.20050305122430,"><vh>@thin TennisForTwo.py</vh></v>
<v t="jpenner.20050604112932.1"
expanded="jpenner.20050604112932.6,jpenner.20050604112932.16,jpenner.20050604112932.30,jpenner.20050604112932.41,"><vh>@thin widgets.py</vh></v>
<v t="jpenner.20050604113053"
expanded="jpenner.20050604113053.2,"><vh>@thin widgetsdemo.py</vh></v>
<v t="jpenner.20050319120621"><vh>@thin pygame2exe.py</vh></v>
<v t="jpenner.20050604144534"><vh>@thin pygame2app.py</vh></v>
</v>
<v t="jpenner.20050605105545"><vh>Tasks</vh>
<v t="jpenner.20050605105545.1" a="E"><vh>Starting menu</vh>
<v t="jpenner.20050604113053.3"><vh>__init__</vh></v>
<v t="jpenner.20050605102056.1"><vh>&lt;&lt; Menu layout &gt;&gt;</vh></v>
</v>
</v>
<v t="jpenner.20050319120705.1" a="E"><vh>Utilities</vh>
<v t="jpenner.20050305121227" a="E"><vh>@run TennisForTwo.py</vh></v>
<v t="jpenner.20050320113047"><vh>@run TennisForTwo.py client localhost 7554</vh></v>
<v t="jpenner.20050604113053.7" a="E"><vh>@run widgetsdemo.py</vh></v>
<v t="jpenner.20050307190605"><vh>@run PyGame2Exe.py py2exe</vh></v>
<v t="jpenner.20050604144534.1"><vh>@run python2.4 pygame2app.py py2app</vh></v>
</v>
</vnodes>
<tnodes>
<t tx="jpenner.20050305121227"></t>
<t tx="jpenner.20050307190605"></t>
<t tx="jpenner.20050319120621">@ignore
@language python
#make standalone, needs at least pygame-1.5.3 and py2exe-0.3.1

from distutils.core import setup
import sys, os, pygame, shutil, glob
import py2exe        

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
      windows=[script],
      data_files=[("data", glob.glob("data\\*"))]
     )

</t>
<t tx="jpenner.20050319120705"></t>
<t tx="jpenner.20050319120705.1"></t>
<t tx="jpenner.20050320113047"></t>
<t tx="jpenner.20050604113053.3">def __init__( self ):
	"""Initialize Demo Class"""
	# instead of pygame.init(), initialize modules manually to 
	# avoid initing pygame.sound
	pygame.display.init()
	pygame.font.init()
	
	# setup screen
	screen = pygame.display.set_mode( (640, 480), DOUBLEBUF )
	pygame.display.set_caption( 'WidgetsDemo' )
	
	# request regular event for updating animation
	self.DRAWEVENT = USEREVENT + 1
	pygame.time.set_timer( self.DRAWEVENT, 33 ) #33 == 30fps
	
	# filter events
	badevents = [NOEVENT, ACTIVEEVENT, JOYAXISMOTION, JOYBALLMOTION, JOYHATMOTION, JOYBUTTONDOWN ,JOYBUTTONUP, VIDEORESIZE, SYSWMEVENT, NUMEVENTS]
	goodevents = [self.DRAWEVENT, KEYDOWN, KEYUP, MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP, QUIT ]
	pygame.event.set_blocked( badevents )
	
	# initialize the WidgetWindow base class
	WidgetWindow.__init__( self, screen )
	
	# create special widgets
	edit = EditClass( self, self.editaction, (325, 300, 265, 25), "text" )
	self.page = PageClass( self, (325, 25, 265, 275), GRAY )
	
	# put the widgets in the window
	self.addwidget( MultiLineTextClass( self, (25, 25, 250, 145), "MultiLineTextClass\n(transparent)\nHas automatic word wrapping.", 36 ) )
	self.addwidget( MultiLineTextClass( self, (25, 195, 250, 145), "MultiLineTextClass\n(with background)\nHas automatic word wrapping.", 36, WHITE, BLACK ) )
	self.addwidget( EditClass( self, self.editaction, (25, 350, 150, 30), "second edit box" ), TABTARGET )
	self.addwidget( TextClass( self, (25, 400, 590, 19), "TextClass (transparent)", 20 ) )
	self.addwidget( TextClass( self, (25, 440, 590, 19), "TextClass (with background)", 20, WHITE, BLACK ) )
	self.addwidget( self.page )
	self.addwidget( edit, TABTARGET )
	self.addwidget( ButtonClass( self, self.buttonaction, (205, 110, 200, 105), "This button overlaps" ) )
	
	# set keyboard focus to the edit widget
	edit.focus()
	
	# initial screen draw
	self.eventproc( pygame.event.Event( NOEVENT, {} ) )
	
	# animation data
	self.animrect = Rect( (325, 350, 265, 50) )
	self.animline = Rect( self.animrect )
	self.animline.width = 5
	self.animline.left = self.animrect.left
</t>
<t tx="jpenner.20050604113053.7"></t>
<t tx="jpenner.20050604144534.1"></t>
<t tx="jpenner.20050605102056.1">self.addwidget(TextClass(self, (120, 40, 400, 30), "Tennis For Two", 36))

self.addwidget(ButtonClass(self, self.startSingle, (120, 120, 400, 30), "Start Single-Player Game"))

self.addwidget(TextClass(self, (120, 190, 400, 20), "Your IP Address: " + getMyIP()))
self.addwidget(TextClass(self, (120, 215, 60, 20), "Port:"))
self.serverPort = EditClass(self, None, (180, 215, 60, 20), "7554")
self.addwidget(self.serverPort)
self.addwidget(ButtonClass(self, self.startServer, (120, 240, 400, 30), "Start Server"))

self.addwidget(TextClass(self, (120, 310, 160, 20), "Server Address:"))
self.clientAddr = EditClass(self, None, (280, 310, 240, 20))
self.addwidget(self.clientAddr)
self.addwidget(TextClass(self, (120, 335, 60, 20), "Port:"))
self.clientPort = EditClass(self, None, (180, 335, 60, 20), "7554")
self.addwidget(self.clientPort)
self.addwidget(ButtonClass(self, self.startClient, (120, 360, 400, 30), "Start Client"))
</t>
<t tx="jpenner.20050605105545"></t>
<t tx="jpenner.20050605105545.1"></t>
</tnodes>
</leo_file>
