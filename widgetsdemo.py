#@+leo-ver=4-thin
#@+node:jpenner.20050604113053:@thin widgetsdemo.py
#@@language python
#@<< widgetsdemo declarations >>
#@+node:jpenner.20050604113053.1:<< widgetsdemo declarations >>
#!/usr/bin/env python
#
# WidgetsDemo.py demonstrates the usage Widgets.py
# Copyright (C) 2003 Michael Leonhard
# http://tamale.net/
#
# version 1.0 RC1 (2003/07/06 00:42)

import pygame, pygame.display, pygame.event, pygame.time, pygame.font, pygame.draw
from pygame.locals import *
import math, string
from widgets import *

#@-node:jpenner.20050604113053.1:<< widgetsdemo declarations >>
#@nl
#@+others
#@+node:jpenner.20050604113053.2:class WidgetsDemo
class WidgetsDemo( WidgetWindow ):
    #@	@+others
    #@+node:jpenner.20050604113053.3:__init__
    def __init__( self ):
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
    #@-node:jpenner.20050604113053.3:__init__
    #@+node:jpenner.20050604113053.4:loop
    def loop( self ):
    	"""Program loop"""
    	while 1:
    		# get the next event
    		event = pygame.event.wait()
    		# Redraw the animation
    		if event.type == self.DRAWEVENT:
    			# get all pending DRAWEVENTs
    			pending = pygame.event.get( self.DRAWEVENT )
    			# number of events we are doing
    			num = len( pending ) + 1
    			
    			# reset the clipping region
    			self.screen.set_clip()
    			# erase the animation
    			self.screen.fill( self.background, self.animline )
    			
    			# update the animation
    			self.animline.left += 1 * num
    			# line is outside the region
    			while not self.animline.colliderect( self.animrect ):
    				# move it back to the left
    				self.animline.left -= self.animrect.width
    			# draw the animation
    			self.screen.fill( RED, self.animline )
    			# flip the display
    			pygame.display.update()
    
    		# user pressed the X button to close the window
    		elif event.type == QUIT: break
    		# pass the even to the widgets
    		else: self.eventproc( event )
    	
    	#clean up
    	pygame.time.set_timer( self.DRAWEVENT, 0 )
    	pygame.quit()
    #@-node:jpenner.20050604113053.4:loop
    #@+node:jpenner.20050604113053.5:editaction
    def editaction( self, widget ):
    	"""Function called when enter key is pressed"""
    	self.page.append( widget.text )
    	widget.settext( "" )
    #@-node:jpenner.20050604113053.5:editaction
    #@+node:jpenner.20050604113053.6:buttonaction
    def buttonaction( self ):
    	"""Function called when button is pressed"""
    	self.page.append( "ACTION" )
    #@-node:jpenner.20050604113053.6:buttonaction
    #@-others
#@-node:jpenner.20050604113053.2:class WidgetsDemo
#@-others

demo = WidgetsDemo()
demo.loop()
#@-node:jpenner.20050604113053:@thin widgetsdemo.py
#@-leo
