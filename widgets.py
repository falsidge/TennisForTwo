#@+leo-ver=4-thin
#@+node:jpenner.20050604112932.1:@thin widgets.py
#@@language python
#@<< widgets declarations >>
#@+node:jpenner.20050604112932.2:<< widgets declarations >>
#!/usr/bin/env python
#
# Widgets.py
# Copyright (C) 2003 Michael Leonhard
# http://tamale.net/
#
# version 1.0 RC1 (2003/07/06 00:19)

import string, pygame, pygame.event, pygame.font
from pygame.locals import *

# initialize modules
pygame.font.init()

TABTARGET = 1
BACKWARD = 1
# keyboard repeat event
KEYREPEAT = NUMEVENTS - 1
KEYREPEATTIME = 50 #in milliseconds
KEYREPEATWAIT = 10

# colors
WHITE = (0xFF, 0xFF, 0xFF, 0xFF)
NAVYBLUE = (0x22, 0x44, 0x66, 0xFF)
BLACK = (0x00, 0x00, 0x00, 0xFF)
DARKGRAY = (0x40, 0x40, 0x40, 0xFF)
GRAY = (0x80, 0x80, 0x80, 0xFF)
RED = (0xFF, 0x00, 0x00, 0xFF)
BLUE = (0x00, 0x00, 0xFF, 0xFF)
GREEN = (0x00, 0xFF, 0x00, 0xFF)
YELLOW = (0x00, 0xFF, 0xFF, 0xFF)

#@-node:jpenner.20050604112932.2:<< widgets declarations >>
#@nl
#@+others
#@+node:jpenner.20050604112932.3:class WidgetException
class WidgetException( Exception ):
    """Widget Exception class"""
    #@    @+others
    #@+node:jpenner.20050604112932.4:__init__
    def __init__( self, reason ):
        """Initialize a new Widget exception"""
        self.reason = reason
    #@-node:jpenner.20050604112932.4:__init__
    #@+node:jpenner.20050604112932.5:__str__
    def __str__( self ):
        """String representation of exception"""
        return repr(self.reason)
    #@-node:jpenner.20050604112932.5:__str__
    #@-others
#@-node:jpenner.20050604112932.3:class WidgetException
#@+node:jpenner.20050604112932.6:class WidgetWindow

class WidgetWindow:
    #@    @+others
    #@+node:jpenner.20050604112932.7:__init__
    def __init__( self, screen, background = NAVYBLUE ):
        """Initialize WidgetWindow class"""
        # data
        self.screen = screen
        self.widgets = []
        self.reversewidgets = []
        self.taborder = []
        self.mousedest = None
        self.keydest = None
        self.background = background
        self.dirtyrect = self.screen.get_rect()
        self.focuslosecallback = None
        self.lastkeydownevent = None
        self.keyrepeatwaitcount = 0
        
        # initial blank screen draw
        self.eventproc( pygame.event.Event( NOEVENT, {} ) )
    #@-node:jpenner.20050604112932.7:__init__
    #@+node:jpenner.20050604112932.8:addwidget
    def addwidget( self, widget, tabable=None ):
        """Add a widget to the window"""
        self.widgets.append( widget )
        self.reversewidgets.insert( 0, widget )
        self.invalidaterect( widget.rect )
        
        # widget is tabable
        if tabable:
            # add to tab order
            self.taborder.append( widget )
    #@-node:jpenner.20050604112932.8:addwidget
    #@+node:jpenner.20050604112932.9:prevtab
    def prevtab( self, widget ):
        """Switch the keyboard focus to the previous widget in the tab order"""
        # call nexttab with the BACKWARD option
        self.nexttab( widget, BACKWARD )
    #@-node:jpenner.20050604112932.9:prevtab
    #@+node:jpenner.20050604112932.10:nexttab
    def nexttab( self, widget, backward=None ):
        """Switch the keyboard focus to next widget in the tab order"""
        
        last = len( self.taborder ) - 1
        
        # no tabable widgets available
        if last < 0:
            # error
            raise WidgetException( "no tabable widgets available" )
        
        # no focus currently
        if not self.keydest:
            # moving backward
            if backward:
                # set to last widget in taborder
                self.taborder[last].focus()
            # moving forward
            else:
                # set to first widget in taborder
                self.taborder[0].focus()
            return
        
        # catch exception
        try:
            # find index of focused widget
            focused = self.taborder.index( self.keydest )
    
            # moving backward
            if backward:
                # next widget
                focused -= 1
                # was first widget
                if focused < 0:
                    # use last widget
                    focused = last
            # moving forward
            else:
                # next widget
                focused += 1
                # was last widget
                if focused > last:
                    # use first widget
                    focused = 0
        
        # currently focused widget is not in tab order
        except ValueError:
            # moving backward
            if backward:
                # use the last widget in the tab order
                focused = last
            # moving forward
            else:
                # use the first widget in the tab order
                focused = 0
        
        # focus the widget
        self.taborder[focused].focus()
    #@-node:jpenner.20050604112932.10:nexttab
    #@+node:jpenner.20050604112932.11:grabmouse
    def grabmouse( self, widget ):
        """Cause all mouse messages to be received by specified widget"""
        self.mousedest = widget
    #@-node:jpenner.20050604112932.11:grabmouse
    #@+node:jpenner.20050604112932.12:grabkey
    def grabkey( self, widget, focuslosecallback = None, sendrepeats = None ):
        """Cause all keyboard messages to be received by specified widget"""
        # previous widget requested callback
        if self.keydest and self.focuslosecallback:
            # inform widget that it is losing key focus
            self.focuslosecallback( self.keydest )
        
        # widget not specified so unset
        if widget == None:
            # unregister event
            pygame.time.set_timer( KEYREPEAT, 0 )
            # keyboard focus is unset
            self.keydest = None
            self.focuslosingcallback = None
        
        # widget is specified
        else:
            # remember widget and specified callback
            self.keydest = widget
            self.focuslosecallback = focuslosecallback
            
            # keyboard repeats were requested
            if sendrepeats:
                # register regular event for repeats
                pygame.time.set_timer( KEYREPEAT, KEYREPEATTIME )
        
        # stop current repeat
        self.lastkeydownevent = None
        self.keyrepeatwaitcount = 0
    #@-node:jpenner.20050604112932.12:grabkey
    #@+node:jpenner.20050604112932.13:invalidaterect
    def invalidaterect( self, rect=None ):
        """Cause the specified region of the screen to be redrawn"""
        # no rect supplied
        if not rect:
            # use entire screen
            self.dirtyrect = self.screen.get_rect()
            return
        
        # previous invalid rect exists
        if self.dirtyrect:
            # combine the two regions
            self.dirtyrect.union_ip( rect )
        # this is first invalid rect
        else: self.dirtyrect = Rect( rect )
    #@-node:jpenner.20050604112932.13:invalidaterect
    #@+node:jpenner.20050604112932.14:dispatch
    def dispatch( self, event ):
        """Send the event to the widget under the mouse"""
        # check each widget, youngest to oldest
        for w in self.reversewidgets:
            # event occurs in widget's region
            if w.rect.collidepoint( event.pos ):
                # let the widget process the event
                w.eventproc( event )
                # only deliver event to one widget
                break
    #@-node:jpenner.20050604112932.14:dispatch
    #@+node:jpenner.20050604112932.15:eventproc
    def eventproc( self, event ):
        """Dispatch events to widgets and redraw the screen"""
        # mouse events
        if event.type == MOUSEMOTION or event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP:
            # mouse is grabbed
            if self.mousedest != None:
                self.mousedest.eventproc( event )
            # not grabbed
            else: self.dispatch( event )
        
        # keyboard events
        elif event.type == KEYDOWN or event.type == KEYUP:
            # keyboard is grabbed
            if self.keydest:
                # send the keyboard event to the widget that has keyboard focus
                self.keydest.eventproc( event )
                # keydown event
                if event.type == KEYDOWN:
                    # save the event for repeats
                    self.lastkeydownevent = event
                    # reset the wait count
                    self.keyrepeatwaitcount = 0
                # keyup event
                else:
                    # no repeats after keyup
                    self.lastkeydownevent = None
        
        # regular event for keyboard repeats
        elif  event.type == KEYREPEAT:
            # keyboard is grabbed
            if self.keydest:
                # keydown event was saved
                if self.lastkeydownevent:
                    # waited long enough
                    if self.keyrepeatwaitcount > KEYREPEATWAIT:
                        # resend the keydown event to the widget
                        self.keydest.eventproc( self.lastkeydownevent )
                    # must wait longer
                    else: self.keyrepeatwaitcount += 1
        
        # there is stuff to be drawn
        if self.dirtyrect:
            # draw the background of the area to be drawn
            self.screen.set_clip( self.dirtyrect )
            self.screen.fill( self.background, self.dirtyrect )
            
            # check each widget
            for w in self.widgets:
                # widget is covered by invalidated rectangle
                if self.dirtyrect.colliderect( w.rect ):
                    # keep the clipping area
                    self.screen.set_clip( self.dirtyrect )
                    
                    # draw the widget
                    w.draw( self.screen )
            
            # debug clipping regions
            #self.screen.set_clip()
            #self.screen.fill( (self.debugred, self.debugred, self.debugred, 0x80), self.dirtyrect )
            #self.debugred += 16
            #self.debugred %= 256
            
            # screen is clean
            self.dirtyrect = None
            
            # flip the display
            pygame.display.update()
    #@-node:jpenner.20050604112932.15:eventproc
    #@-others
#@-node:jpenner.20050604112932.6:class WidgetWindow
#@+node:jpenner.20050604112932.16:class ButtonClass

class ButtonClass:
    #@    @+others
    #@+node:jpenner.20050604112932.17:__init__
    def __init__( self, manager, action, rect, text="OK", foreground=WHITE, shadowcolor=BLACK, textcolor=BLACK, fontsize=24 ):
        """Initialize the Button class"""
        self.action = action
        self.manager = manager
        self.rect = Rect( rect )
        self.text = None
        self.foreground = foreground
        self.shadowcolor = shadowcolor
        self.textcolor = textcolor
        self.pressed = 0
        self.buttondown = 0
        
        # button area
        self.button = Rect( self.rect )
        self.button.width -= 5
        self.button.height -= 5
        
        # shadow area
        self.shadow = Rect( self.button )
        self.shadow.right += 5
        self.shadow.bottom += 5
        
        # font
        self.font = pygame.font.Font( "freesansbold.ttf", fontsize )
        
        # update button text
        self.settext( text )
    #@-node:jpenner.20050604112932.17:__init__
    #@+node:jpenner.20050604112932.18:settext
    def settext( self, text ):
        # new text is same as old
        if self.text == text:
            # do nothing
            return
        
        # save text for action functions
        self.text = text
        # remove trailing whitespace
        text = text.rstrip()
        # if text is empty
        if len( text ) == 0:
            # use a space
            text = " "
        
        # make text
        self.surface = self.font.render( text, 1, self.textcolor, self.foreground )
        # optimize for blitting
        self.surface = self.surface.convert()
        
        # text position (unpressed)
        textrect = self.surface.get_rect()
        textrect.center = self.button.center
        self.textrect = Rect( textrect )
        
        # text position (pressed)
        textrect.center = self.shadow.center
        self.textrectpressed = textrect
        
        # cause widget to be drawn
        self.manager.invalidaterect( self.rect )
    #@-node:jpenner.20050604112932.18:settext
    #@+node:jpenner.20050604112932.19:eventproc
    def eventproc( self, event ):
        """Process mouse events"""
        # button is clicked
        if event.type == MOUSEBUTTONDOWN and self.button.collidepoint( event.pos):
            self.pressed = 1
            self.manager.invalidaterect( self.rect )
            # watch the mouse
            self.buttondown = 1
            self.manager.grabmouse( self )
        
        # button is released
        if event.type == MOUSEBUTTONUP and self.buttondown == 1:
            # done watching the mouse
            self.buttondown = 0
            self.manager.grabmouse( None )
    
            # button was in pressed position
            if self.pressed == 1:
                self.pressed = 0
                self.manager.invalidaterect( self.rect )
    
                # do button action
                self.action()
        
        # mouse cursor moves and holds mouse button
        if event.type == MOUSEMOTION and self.buttondown == 1:
            # button is in pressed position
            if self.pressed == 1:
                # cursor is not over the button
                if not self.rect.collidepoint( event.pos ):
                    # button becomes unpressed
                    self.pressed = 0
                    self.manager.invalidaterect( self.rect )
            # button is in unpressed position
            else:
                # cursor is over the button
                if self.button.collidepoint( event.pos ):
                    # button becomes pressed 
                    self.pressed = 1
                    self.manager.invalidaterect( self.rect )
    #@-node:jpenner.20050604112932.19:eventproc
    #@+node:jpenner.20050604112932.20:draw
    def draw( self, screen ):
        """Draw the widget"""
        # clip our drawing
        screen.set_clip( screen.get_clip().clip( self.rect ) )
        
        # button is in pressed state
        if self.pressed == 1:
            # draw the button
            screen.fill( self.foreground, self.shadow )
            # blit the text
            screen.blit( self.surface, self.textrectpressed )
    
        
        # button is in unpressed state
        else:
            # draw the shadow
            screen.fill( self.shadowcolor, self.shadow )
        
            # draw the button
            screen.fill( self.foreground, self.button )
    
            # blit the text
            screen.blit( self.surface, self.textrect )
    #@-node:jpenner.20050604112932.20:draw
    #@-others
#@-node:jpenner.20050604112932.16:class ButtonClass
#@+node:jpenner.20050604112932.21:class PageClass

class PageClass:
    #@    @+others
    #@+node:jpenner.20050604112932.22:eventproc
    def eventproc( self, event ):
        """Process mouse events"""
        # button is clicked
        if event.type == MOUSEBUTTONDOWN:
            (x, y) = event.pos
            # click is on the scroll shuttle
            if self.shuttlerect.collidepoint( event.pos ):
                # distance from the click to the bottom of the shuttle
                self.clickoffset = self.shuttlerect.bottom - y
                # begin scrolling
                self.manager.grabmouse( self )
                self.scrollgrabbed = 1
        
        # button is released
        if event.type == MOUSEBUTTONUP:
            # currently scrolling
            if self.scrollgrabbed == 1:
                # final scroll position
                self.scroll( event.pos )
                # done scrolling
                self.manager.grabmouse( None )
                self.scrollgrabbed = 0
        
        # mouse cursor moves
        if event.type == MOUSEMOTION:
            # scroll bar is grabbed
            if self.scrollgrabbed == 1: self.scroll( event.pos )
    #@-node:jpenner.20050604112932.22:eventproc
    #@+node:jpenner.20050604112932.23:__init__
    def __init__( self, manager, rect, background=(0, 0, 0, 0), fontsize=24, maxlines=40, foreground=WHITE ):
        """Initialize scrollable text display"""
        self.manager = manager
        self.rect = Rect( rect )
        self.background = background
        self.font = pygame.font.Font( "freesansbold.ttf", fontsize )
        self.maxlines = maxlines
        self.foreground = foreground
        
        # Scroll bar
        scrollwidth = 10
        self.scrollgrabbed = 0
        
        # list of surfaces with line text, youngest is first
        self.lines = []
    
        # line that is visible at the bottom of page (0 is youngest line)
        self.showline = 0
        
        # page rect
        self.pagerect = Rect( rect )
        self.pagerect.width -= scrollwidth
        
        # scrollbar area
        self.scrollrect = Rect( rect )
        self.scrollrect.width = scrollwidth
        self.scrollrect.right = self.rect.right
        
        # shuttle initially fills scrollbar
        self.shuttlerect = Rect( self.scrollrect )
        
        # blank line to start with
        self.append( " " )
    #@-node:jpenner.20050604112932.23:__init__
    #@+node:jpenner.20050604112932.24:append
    def append( self, newtext, foreground=None ):
        """Add one or more new lines"""
        # use default foreground color
        if foreground == None: foreground = self.foreground
        
        # expand tabs
        newtext = newtext.expandtabs()
        
        # split text into lines
        for line in newtext.splitlines():
                # append the line
                self.appendline( line, foreground )
    #@-node:jpenner.20050604112932.24:append
    #@+node:jpenner.20050604112932.25:fits
    def fits( self, text ):
        """Check if text fits on one line"""
        # size of the text
        (fw, fh) = self.font.size( text )
        # too wide
        if fw > self.pagerect.width: return 0
        return 1
    #@-node:jpenner.20050604112932.25:fits
    #@+node:jpenner.20050604112932.26:appendline
    def appendline( self, newtext, foreground ):
        """Find and prepare each line of new text"""
        # remove trailing whitespace
        newtext = newtext.rstrip()
        
        # find largest piece of text that will fit on one line
        pt = len( newtext )
        while not self.fits( newtext[:pt] ):
            # find the last space
            pt = newtext.rfind( " ", 0, pt )
            # no spaces left
            if pt == -1: break
        
        # first word doesn't fit
        if pt == -1:
            # break word
            pt = len( newtext )
            while not self.fits( newtext[:pt] ):
                # not even one letter will fit
                if pt == 1: raise Exception
                # move the break one letter to the left
                pt -= 1
        # found string that fits on line
        else:
            # include the space
            pt += 1
        
        # this text fits on the line
        thistext = newtext[:pt]
        
        # check that line is not empty
        if len( thistext ) == 0:
            # use a space
            thistext = " "
        
        # make a new surface
        surface = self.font.render( thistext, 1, foreground, self.background )
    
        # optimize for blitting with transparency
        surface = surface.convert()
        
        # all of the lines should be the same height
        self.lineheight = surface.get_height()
        # add the line surface to the list
        self.lines.insert( 0, surface )
        # too many lines
        while len( self.lines ) > self.maxlines:
            # discard last line
            del self.lines[-1]
        
        # if not scrolled to the bottom
        if self.showline != 0:
            # keep scroll bar on same line
            self.showline += 1
            # if line disappears then stay at the top
            if self.showline >= len( self.lines ): self.showline = len( self.lines ) - 1
        
        # resize scrollbar
        self.scrollcheck()
        
        # text that wouldn't fit
        newtext = newtext[pt:]
        
        # leftover wrapped text
        if len( newtext ) > 0:
            # do the leftovers
            self.appendline( newtext, foreground )
        # no more lines to be added
        else:
            # need screen update
            self.manager.invalidaterect( self.rect )
    #@-node:jpenner.20050604112932.26:appendline
    #@+node:jpenner.20050604112932.27:scrollcheck
    def scrollcheck( self ):
        """Adjust the scroll shuttle after text is added"""
        #print ""
        
        # How many lines are visible?
        visiblelines = self.pagerect.height / self.lineheight
        #print "visiblelines", visiblelines
        
        #print "lines", len( self.lines )
        
        # All the lines fit on the page
        if len( self.lines ) <= visiblelines:
            self.shuttlerect = Rect( self.scrollrect )
            return
        
        # keep the oldest line at the top or above the page
        if self.showline > len( self.lines ) - visiblelines:
            self.showline = len( self.lines ) - visiblelines
        
        # Determine height of the shuttle
        self.shuttlerect.height = int( (float( visiblelines ) / float( len( self.lines ) )) * float( self.pagerect.height ) )
        #print "shuttle height", self.shuttlerect.height
        
        # Number of lines that are off the page (top and bottom)
        linetravel = len( self.lines ) - visiblelines
        #print "linetravel", linetravel
        
        # Pixels on the scroll bar representing the off-page lines
        travel = self.scrollrect.height - self.shuttlerect.height
        #print "travel", travel
        
        # Distance in scrollbar-pixels of the youngest visible line to the youngest line
        x = int( (float( self.showline ) / float( linetravel )) * float( travel ) )
        #print "x", x
        
        # Move the scroll bar to keep this distance from the bottom
        self.shuttlerect.bottom = self.scrollrect.bottom - x
        #print "shuttle top", self.shuttlerect.top
        
        # keep shuttle on scroll bar
        self.shuttlerect.clamp_ip( self.scrollrect )
        #print "shuttle", self.shuttlerect
    
        # will need redraw
        self.manager.invalidaterect( self.rect )
    #@-node:jpenner.20050604112932.27:scrollcheck
    #@+node:jpenner.20050604112932.28:scroll
    def scroll( self, xxx_todo_changeme ):
        """Adjust the scroll shuttle and visible text when the user scrolls"""
        (x, y) = xxx_todo_changeme
        self.shuttlerect.bottom = self.clickoffset + y
        # keep shuttle on scroll bar
        self.shuttlerect.clamp_ip( self.scrollrect )
        #print "shuttle", self.shuttlerect
        
        # redraw scroll bar
        self.manager.invalidaterect( self.scrollrect )
        
        #print "lines", len( self.lines )
        
        # Pixels that the scrollbar can slide
        travel = self.scrollrect.height - self.shuttlerect.height
        #print "travel", travel
        # Number of lines that fit on the page
        visiblelines = self.pagerect.height / self.lineheight
        #print "visiblelines", visiblelines
        
        # All the lines fit on the page
        if len( self.lines ) <= visiblelines:
            # Keep the youngest line at the bottom
            self.showline = 0
            return
        
        # How many lines the scrollbar can slide through
        linetravel = len( self.lines ) - visiblelines
        #print "linetravel", linetravel
        
        # Distance in pixels of the scroll bar to the top
        x = self.shuttlerect.top - self.scrollrect.top
        #print "x", x
        # Number of oldest lines that should be above the top of the page
        l = int( (float( x ) / float( travel )) * float( linetravel ) )
        #print "l", l
        
        # Remember the current scroll position
        oldshowline = self.showline
        
        # Determine the new scroll position: this is oldest line, 
        # then down to oldest visible line, then down to youngest visible line
        self.showline = len( self.lines ) - l - visiblelines
        #print "showline", self.showline
        
        # text has moved
        if oldshowline != self.showline:
            # need to redraw text
            self.manager.invalidaterect( self.rect )
    #@-node:jpenner.20050604112932.28:scroll
    #@+node:jpenner.20050604112932.29:draw
    def draw( self, screen ):
        """Draw the widget"""
        # clip our drawing
        screen.set_clip( screen.get_clip().clip( self.rect ) )
        # clear the page area
        screen.fill( self.background, self.pagerect )
        
        # start at the bottom
        y = self.pagerect.bottom
        # draw each line
        for surface in self.lines[self.showline:]:
            # move up one line (upper left corner)
            y -= self.lineheight
            # blit it to the screen
            screen.blit( surface, (self.rect.left, y) )
            # drew the topmost visible line
            if y <= self.rect.top: break
        
        #draw scroll bar
        screen.fill( self.background, self.scrollrect )
        screen.fill( self.foreground, self.shuttlerect )
    #@-node:jpenner.20050604112932.29:draw
    #@-others
#@-node:jpenner.20050604112932.21:class PageClass
#@+node:jpenner.20050604112932.30:class EditClass

class EditClass:
    #@    @+others
    #@+node:jpenner.20050604112932.31:__init__
    def __init__( self, manager, action, rect, initialtext="", fontsize=24, maxchars=60, foreground=WHITE, background=DARKGRAY ):
        """Initialize the Edit class"""
        rect = Rect( rect )
        self.manager = manager
        self.action = action
        self.rect = Rect(rect)
        self.font = pygame.font.Font( "freesansbold.ttf", fontsize )
        self.maxchars = maxchars
        self.foreground = foreground
        self.background = background
        self.blitoffset = 0
        self.allowed = """`1234567890-=    qwertyuiop[]\\asdfghjkl;'zxcvbnm,./ ~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<?"""
        self.focused = None
        self.text = None
        
        # caret
        self.font.set_underline( 1 )
        self.caret = self.font.render( "_", 1, self.foreground, self.background )
        self.font.set_underline( 0 )
        self.caretwidth = self.caret.get_width()
        self.caretvisible = None
        
        # hide the caret
        self.hidecaret()
        
        # Start out with the default text
        self.settext( initialtext )
    #@-node:jpenner.20050604112932.31:__init__
    #@+node:jpenner.20050604112932.32:eventproc
    def eventproc( self, event ):
        """Process mouse and keyboard events"""
        # mouse click
        if event.type == MOUSEBUTTONDOWN:
            # grab keyboard focus
            self.focus()
        
        # key press
        elif event.type == KEYDOWN:
            # don't have keyboard focus
            if not self.focused:
                # raise exception
                raise WidgetException( "Edit class not focused but received keyboard message" )
            
            # backspace
            if event.key == K_BACKSPACE:
                # remove last character
                self.settext( self.text[:-1] )
            # enter
            elif event.key == K_RETURN:
                # report it to the manager
                self.action( self )
            # tab
            elif event.key == K_TAB:
                # send focus to next widget in taborder
                self.manager.nexttab( self, pygame.key.get_mods() & KMOD_SHIFT )
            # some other key
            else:
                # buffer is at max
                if len( self.text ) >= self.maxchars: return
                
                # convert key to character code
                try:
                    character = str( event.unicode )
                    # character is not allowed
                    if self.allowed.find(character) == -1: 
                        return
                    # add it to the buffer
                    self.settext( self.text + character )
                except: return
    #@nonl
    #@-node:jpenner.20050604112932.32:eventproc
    #@+node:jpenner.20050604112932.33:showcaret
    def showcaret( self ):
        self.caretvisible = 1
        # widest section of text that can be visible
        self.renderwidth = self.rect.width - self.caretwidth
        # rightmost edge of text, leaving room for caret
        self.renderright = self.rect.right - self.caretwidth
        # will need redraw
        self.manager.invalidaterect( self.rect )
    #@-node:jpenner.20050604112932.33:showcaret
    #@+node:jpenner.20050604112932.34:hidecaret
    def hidecaret( self ):
        self.caretvisible = 0
        # text can now take up whole width of widget
        self.renderwidth = self.rect.width
        # rightmost edge of text
        self.renderright = self.rect.right
        # will need redraw
        self.manager.invalidaterect( self.rect )
    #@-node:jpenner.20050604112932.34:hidecaret
    #@+node:jpenner.20050604112932.35:focus
    def focus( self ):
        """Grab keyboard focus"""
        # already focused
        if self.focused: return
        
        # get keyboard focus from widget window
        self.manager.grabkey( self, self.unfocusCALLBACK, 1 )
    
        # keyboard focus is gained
        self.focused = 1
        # show the caret
        self.showcaret()
    #@-node:jpenner.20050604112932.35:focus
    #@+node:jpenner.20050604112932.36:unfocusCALLBACK
    def unfocusCALLBACK( self, widget ):
        """Called by manager when keyboard focus is lost"""
        
        # don't have focus
        if not self.focused: return
        
        # keyboard focus is lost
        self.focused = None
        # hide the caret
        self.hidecaret()
    #@-node:jpenner.20050604112932.36:unfocusCALLBACK
    #@+node:jpenner.20050604112932.37:settext
    def settext( self, newtext ):
        """Replace the edit box text"""
        
        # no change in text
        if self.text == newtext: return
        
        # udpate widget with new text
        self.text = newtext
        self.maketext()
    #@-node:jpenner.20050604112932.37:settext
    #@+node:jpenner.20050604112932.38:slidecheck
    def slidecheck( self ):
        """Adjust the position of the text to keep the last portion visible"""
        # we can assume that self.surface != None
        
        # width of text that we have to display
        width = self.surface.get_width()
        
        # text doesn't fit
        if width > self.renderwidth:
            # align the right edge
            self.blitoffset = self.renderright - width
        # text fits
        else:
            # align the left edge
            self.blitoffset = self.rect.left
        
        # caret position (to the right of text)
        self.caretleft = self.blitoffset + width
    #@-node:jpenner.20050604112932.38:slidecheck
    #@+node:jpenner.20050604112932.39:maketext
    def maketext( self ):
        """Prepare the new text for display"""
        
        # will need redraw
        self.manager.invalidaterect( self.rect )
        
        # text is empty
        if not len( self.text ):
            # clear the surface
            self.surface = None
            # caret at far left
            self.caretleft = self.rect.left
            return
        
        # make a new surface
        self.surface = self.font.render( self.text, 1, self.foreground, self.background )
        
        # text has transparent background
        if self.background == None: 
            # optimize for blitting with transparency
            self.surface = self.surface.convert_alpha()
        # opaque background
        else:
            # optimize for normal blitting
            self.surface = self.surface.convert()
        
        # adjust the new text position horizontally
        self.slidecheck()
    #@-node:jpenner.20050604112932.39:maketext
    #@+node:jpenner.20050604112932.40:draw
    def draw( self, screen ):
        """Draw the widget"""
        # clip our drawing
        screen.set_clip( screen.get_clip().clip( self.rect ) )
        
        # widget is not transparent
        if self.background:
            # clear the area
            screen.fill( self.background, self.rect )
        
        # not empty
        if self.surface:
            # blit it to the screen
            screen.blit( self.surface, (self.blitoffset, self.rect.top) )
        
        # caret is visible
        if self.caretvisible:
            # blit the caret
            screen.blit( self.caret, (self.caretleft, self.rect.top ) )
    #@-node:jpenner.20050604112932.40:draw
    #@-others
#@-node:jpenner.20050604112932.30:class EditClass
#@+node:jpenner.20050604112932.41:class TextClass

class TextClass:
    #@    @+others
    #@+node:jpenner.20050604112932.42:eventproc
    def eventproc( self, event ): return
    #@-node:jpenner.20050604112932.42:eventproc
    #@+node:jpenner.20050604112932.43:__init__
    def __init__( self, manager, rect, text="", fontsize=24, foreground=WHITE, background=None ):
        """Initialize the Text class"""
        rect = Rect( rect )
        self.manager = manager
        self.text = text
        self.rect = Rect(rect)
        self.foreground = foreground
        self.background = background
        self.font = pygame.font.Font( "freesansbold.ttf", fontsize )
        self.settext( text )
    #@-node:jpenner.20050604112932.43:__init__
    #@+node:jpenner.20050604112932.44:settext
    def settext( self, newtext ):
        """Replace the text in the widget"""
        # expand tabs
        newtext = newtext.expandtabs()
        # remove trailing whitespace
        self.text = newtext.rstrip()
        # update surface
        self.maketext()
    #@-node:jpenner.20050604112932.44:settext
    #@+node:jpenner.20050604112932.45:maketext
    def maketext( self ):
        """Prepare the text for display"""
        # if text is empty
        if len( self.text ) == 0:
            # use a space
            self.text = " "
        # transparent background
        if self.background == None:
            # make text
            self.surface = self.font.render( self.text, 1, self.foreground )
            # optimize for blitting with transparency
            self.surface = self.surface.convert_alpha()
        # opaque background
        else:
            # make text
            self.surface = self.font.render( self.text, 1, self.foreground, self.background )
            # optimize for blitting
            self.surface = self.surface.convert()
        # need screen update
        self.manager.invalidaterect( self.rect )
    #@-node:jpenner.20050604112932.45:maketext
    #@+node:jpenner.20050604112932.46:draw
    def draw( self, screen ):
        """Draw the widget"""
        # clip our drawing
        screen.set_clip( screen.get_clip().clip( self.rect ) )
        # background is set
        if self.background != None:
            # fill background
            screen.fill( self.background, self.rect )
        # blit text to the screen
        screen.blit( self.surface, self.rect )
    #@-node:jpenner.20050604112932.46:draw
    #@-others
#@-node:jpenner.20050604112932.41:class TextClass
#@+node:jpenner.20050604112932.47:class MultiLineTextClass

class MultiLineTextClass:
    #@    @+others
    #@+node:jpenner.20050604112932.48:eventproc
    def eventproc( self, event ): return
    #@-node:jpenner.20050604112932.48:eventproc
    #@+node:jpenner.20050604112932.49:__init__
    def __init__( self, manager, rect, text="", fontsize=24, foreground=WHITE, background=None ):
        """Initialize the MultLineText class"""
        rect = Rect( rect )
        self.manager = manager
        self.lines = []
        self.rect = Rect(rect)
        self.foreground = foreground
        self.background = background
        self.font = pygame.font.Font( "freesansbold.ttf", fontsize )
        self.settext( text )
    #@-node:jpenner.20050604112932.49:__init__
    #@+node:jpenner.20050604112932.50:settext
    def settext( self, newtext ):
        """Replace the text of the widget"""
    
        self.lines = [] # clear current text
        # expand tabs
        newtext = newtext.expandtabs()
        # append each line separately
        for line in newtext.splitlines():
                self.appendline( line )
    #@-node:jpenner.20050604112932.50:settext
    #@+node:jpenner.20050604112932.51:fits
    def fits( self, text ):
        """Determine if the text fits on one line"""
        # size of the text
        (fw, fh) = self.font.size( text )
        # too wide
        if fw > self.rect.width: return 0
        return 1
    #@-node:jpenner.20050604112932.51:fits
    #@+node:jpenner.20050604112932.52:appendline
    def appendline( self, newtext ):
        """Prepare the lines of new text for display"""
        # remove trailing whitespace
        newtext = newtext.rstrip()
        
        # find largest piece of text that will fit on one line
        pt = len( newtext )
        while not self.fits( newtext[:pt] ):
            # find the last space
            pt = newtext.rfind( " ", 0, pt )
            # no spaces left
            if pt == -1: break
        
        # first word doesn't fit
        if pt == -1:
            # break word
            pt = len( newtext )
            while not self.fits( newtext[:pt] ):
                # not even one letter will fit
                if pt == 1: raise Exception
                # move the break one letter to the left
                pt -= 1
        # found string that fits on line
        else:
            # include the space
            pt += 1
        
        # line that will fit
        thisline = newtext[:pt]
    
        # check that line is not empty
        if len( thisline ) == 0:
            # use a space
            thisline = " "
        
        # transparent background
        if self.background == None:
            # make text
            surface = self.font.render( thisline, 1, self.foreground )
            # optimize for blitting with transparency
            surface = surface.convert_alpha()
        # opaque background
        else:
            # make text
            surface = self.font.render( thisline, 1, self.foreground, self.background )
            # optimize for blitting
            surface = surface.convert()
    
        self.lineheight = surface.get_height()
        self.lines.append( surface )
        
        # text that wouldn't fit
        newtext = newtext[pt:]
    
        # remove trailing whitespace
        #newtext = newtext.rstrip()
    
        # leftover wrapped text
        if len( newtext ) > 0:
            # make lines out of it
            self.appendline( newtext )
        # last line to be appended
        else:
            # need screen update
            self.manager.invalidaterect( self.rect )
    #@-node:jpenner.20050604112932.52:appendline
    #@+node:jpenner.20050604112932.53:draw
    def draw( self, screen ):
        """Draw the widget"""
        # clip our drawing
        screen.set_clip( screen.get_clip().clip( self.rect ) )
        # background is set
        if self.background != None:
            # fill background
            screen.fill( self.background, self.rect )
        # start at the top
        y = self.rect.top
        # draw each line
        for surface in self.lines:
            # blit it to the screen
            screen.blit( surface, (self.rect.left, y) )
            # next line is lower
            y += self.lineheight
    #@-node:jpenner.20050604112932.53:draw
    #@-others
#@-node:jpenner.20050604112932.47:class MultiLineTextClass
#@-others
#@-node:jpenner.20050604112932.1:@thin widgets.py
#@-leo
