#@+leo-ver=4-thin
#@+node:jpenner.20050305105206:@thin TennisForTwo.py
#@@language python

import pygame, math, cPickle, sys, StringIO, socket, re, urllib, random
from pygame.locals import *
from twisted.internet import task, reactor, protocol, udp
from widgets import *

#@+others
#@+node:jpenner.20050601180947:Helper / Misc
#@+others
#@+node:jpenner.20050305105934:Constants
#constants
SCREENRECT  = Rect(0, 0, 640, 480)
GRAVITY     = 0.25
FRICTION    = 4
BALL_STARTX = 100
BALL_STARTY = 350

SINGLE_PLAYER = 10
#@nonl
#@-node:jpenner.20050305105934:Constants
#@+node:jpenner.20050310195953:Globals
#globals
class Game:
    currentplayer = 1
    AIPlayer = 0
    SeverPort = 7554
    Port = None
    
    logfile = None
#@nonl
#@-node:jpenner.20050310195953:Globals
#@+node:jpenner.20050424164431:Logging
def startLogging(fn):
    Game.logfile = open(fn, 'wt')
    
def log(text):
    if Game.logfile <> None:
        Game.logfile.write(str(text) + '\n')

def stopLogging():
    Game.logfile.close()
#@nonl
#@-node:jpenner.20050424164431:Logging
#@+node:jpenner.20050427175747:Angles
def makeAngle(pos):
    xdist = pos[0] - Game.ball.rect.centerx
    ydist = pos[1] - Game.ball.rect.centery
    return math.atan2(ydist, xdist)
               
def anglePos(rect, angle, radius):
    return( (rect.centerx + (math.cos(angle) * radius)), (rect.centery + (math.sin(angle) * radius)))

def velocityFromAngle(angle):
    return (math.cos(angle) * 12, math.sin(angle) * 9)
#@-node:jpenner.20050427175747:Angles
#@+node:jpenner.20050605110605:IP address
def getMyIP():
    try:
        f = urllib.urlopen('http://checkip.dyndns.org')
        s = f.read()
        log("checkip: " + s)
        m = re.search('Current IP Address: ([\d]*\.[\d]*\.[\d]*\.[\d]*)', s)
        outsideip = m.group(0)
        log("outside ip: " + outsideip)
    except:
        outsideip = None

    try:
        insideip = socket.gethostbyname(socket.gethostname())
        log("inside ip: " + insideip)
    except:
        insideip = None

    if (outsideip == None) and (insideip == None):
        ip = "Unknown"
    else:
        if (outsideip == None):
             ip = insideip + " (Firewalled / Proxied?)"
        else:
             ip = outsideip
             if (insideip <> None) and (insideip <> outsideip):
                 ip = ip + " (Firewalled?)"
    return ip
#@-node:jpenner.20050605110605:IP address
#@-others
#@nonl
#@-node:jpenner.20050601180947:Helper / Misc
#@+node:jpenner.20050305124252:Events
#@+others
#@+node:jpenner.20050305130011.1:Event Manager
class EventManager:
    def __init__(self):
        self.queue = []
        self.handlers = [[] for i in range(NUM_EVENTS)]
        
    def postEvent(self,event):
        self.queue.append(event);

    def tick(self):
        for event in self.queue:
            for handler in self.handlers[event.type]:
                handler(event)
        self.queue = []
    
    def registerHandler(self, evtype, func):
        if (evtype == NUM_EVENTS):
            for i in range(NUM_EVENTS):
                self.registerHandler(i, func)
        else:
            self.handlers[evtype].append(func)
#@nonl
#@-node:jpenner.20050305130011.1:Event Manager
#@+node:jpenner.20050305130011:Types
EV_HIT              = 0
EV_SCORE            = 1
EV_BOUNCE           = 2
EV_PLAYER_UPDATE    = 3
EV_SERVE            = 4
EV_CLICK            = 5
EV_BALLPOS          = 6
EV_CONNECT          = 7
EV_PLAYER_SWITCH    = 8
EV_HELLO            = 9
NUM_EVENTS          = 10
   
class Event:
    def __init__(self, type):
        self.type = type
        self.fromplayer = Game.myplayer
        
class ClickEvent (Event):
    def __init__(self, (xvel, yvel), player):
        Event.__init__(self, EV_CLICK)
        self.xvel = xvel
        self.yvel = yvel
        self.player = player
                
class HitEvent (Event):
    def __init__(self, xvel, yvel):
        Event.__init__(self, EV_HIT)
        self.xvel = xvel
        self.yvel = yvel
        
class ScoreEvent (Event):
    def __init__(self, player):
        Event.__init__(self, EV_SCORE)
        self.player = player
        
class BounceEvent (Event):
    def __init__(self):
        Event.__init__(self, EV_BOUNCE)
                
class PlayerUpdateEvent (Event):
    def __init__(self):
        Event.__init__(self, EV_PLAYER_UPDATE)
                
class ServeEvent (Event):
    def __init__(self):
        Event.__init__(self, EV_SERVE)
        
class BallPosEvent (Event):
    def __init__(self, x, y):
        Event.__init__(self, EV_BALLPOS)
        self.x = x
        self.y = y
        
class ConnectEvent (Event):
    def __init__(self):
        Event.__init__(self, EV_CONNECT)
        
class PlayerSwitchEvent (Event):
    lastseq = 0
    def __init__(self, xvel, yvel, xpos, ypos, stopped):
        Event.__init__(self, EV_PLAYER_SWITCH)
        self.xvel = xvel
        self.yvel = yvel
        self.xpos = xpos
        self.ypos = ypos
        self.stopped = stopped
        self.seq = PlayerSwitchEvent.lastseq
        PlayerSwitchEvent.lastseq = PlayerSwitchEvent.lastseq + 1

class HelloEvent(Event):
    def __init__(self):
        Event.__init__(self, EV_HELLO)

#@-node:jpenner.20050305130011:Types
#@-others
#@nonl
#@-node:jpenner.20050305124252:Events
#@+node:jpenner.20050319143816:Networking
#@+others
#@+node:jpenner.20050320120319:Message
class TFTMessage:
    def __init__(self, sequence, event):
        self.sequence = sequence
        self.event = event
#@nonl
#@-node:jpenner.20050320120319:Message
#@+node:jpenner.20050424135832:Protocol
class TFTProtocol (protocol.DatagramProtocol):
    def __init__(self):
        self.mysequence = 0
        self.hissequence = -1
        self.address = None
        Game.evMgr.registerHandler(EV_BALLPOS, self.sendEvent)
        Game.evMgr.registerHandler(EV_SERVE, self.sendEvent)
        Game.evMgr.registerHandler(EV_PLAYER_SWITCH, self.sendEvent)
        Game.evMgr.registerHandler(EV_CONNECT, self.connectTransport)

    def startProtocol(self):
        if self.address <> None:
            log (self.address)

    def datagramReceived(self, data, address):
        if self.address == None:
            self.address = address
            log(address)
        msg = cPickle.Unpickler(StringIO.StringIO(data)).load()
        
        if (msg.sequence > self.hissequence):
            self.hissequence = msg.sequence
            if msg.event <> None:
                log ("get " + str(msg.event.type) + ": " + str(msg.event.fromplayer))
                Game.evMgr.postEvent(msg.event)
        
    def sendEvent(self, event):
        if (self.address <> None) and (self.transport <> None) and (event.fromplayer == Game.myplayer):
            log ("send " + str(event.type))
            self.mysequence = self.mysequence + 1
            s = StringIO.StringIO()
            cPickle.Pickler(s).dump(TFTMessage(self.mysequence, event))
            self.transport.write(s.getvalue(), self.address)
            
    def connectTransport(self, event):
        Game.evMgr.postEvent(HelloEvent())

        

#@-node:jpenner.20050424135832:Protocol
#@-others
#@-node:jpenner.20050319143816:Networking
#@+node:jpenner.20050604112932:Menu
#@+others
#@+node:jpenner.20050605142055:Base Menu
class BaseMenu(WidgetWindow):
    def __init__(self):
        WidgetWindow.__init__(self, Game.screen)

        self.menuLayout()

    def onEnter(self):
        self.invalidaterect()
        self.eventproc( pygame.event.Event( NOEVENT, {} ) )

    def tick(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                reactor.stop()
            try:
                self.eventproc(event)
            except:
                pass

#@-node:jpenner.20050605142055:Base Menu
#@+node:jpenner.20050605102056:Main Menu
class MainMenu(BaseMenu):
    def menuLayout(self):
        #@        << Menu layout >>
        #@+node:jpenner.20050605102056.1:<< Menu layout >>
        self.addwidget(TextClass(self, (120, 40, 400, 30), "Tennis For Two", 36))
        
        self.addwidget(ButtonClass(self, self.startSingle, (120, 120, 400, 30), "Start Single-Player Game"))
        self.addwidget(ButtonClass(self, self.startAI, (120, 155, 400, 30), "Start Game Vs. Tennis-O-Tron"))
        
        self.addwidget(TextClass(self, (120, 220, 450, 20), "Your IP Address: " + getMyIP()))
        self.addwidget(TextClass(self, (120, 245, 60, 20), "Port:"))
        self.serverPort = EditClass(self, None, (180, 245, 60, 20), "7554")
        self.addwidget(self.serverPort)
        self.addwidget(ButtonClass(self, self.startServer, (120, 270, 400, 30), "Start Server"))
        
        self.addwidget(TextClass(self, (120, 310, 160, 20), "Server Address:"))
        self.clientAddr = EditClass(self, None, (280, 310, 240, 20))
        self.addwidget(self.clientAddr)
        self.addwidget(TextClass(self, (120, 335, 60, 20), "Port:"))
        self.clientPort = EditClass(self, None, (180, 335, 60, 20), "7554")
        self.addwidget(self.clientPort)
        self.addwidget(ButtonClass(self, self.startClient, (120, 360, 400, 30), "Start Client"))
        #@-node:jpenner.20050605102056.1:<< Menu layout >>
        #@nl
        
    def startSingle(self):
        Game.myplayer = SINGLE_PLAYER
        Game.isClient = False
        Game.rules.infinitehits = True
        Game.gameMgr.changeState(Game.gameMgr.STATE_SINGLE_PLAYER)

    def startAI(self):
        Game.myplayer = 1
        Game.isClient = False
        Game.AIPlayer = 2
        Game.gameMgr.changeState(Game.gameMgr.STATE_SINGLE_PLAYER)
        
    def startServer(self):
        Game.myplayer = 1
        Game.isClient = False
        Game.ServerPort = int(self.serverPort.text)
        Game.gameMgr.changeState(Game.gameMgr.STATE_WAIT_FOR_CLIENT)
    
    def startClient(self):
        Game.myplayer = 2
        Game.isClient = True
        Game.ServerPort = int(self.clientPort.text)
        Game.ServerIP = self.clientAddr.text
        Game.gameMgr.changeState(Game.gameMgr.STATE_CONNECT)
#@-node:jpenner.20050605102056:Main Menu
#@+node:jpenner.20050605173506:Server Wait Screen
class ServerWait(BaseMenu):
    def menuLayout(self):
        self.addwidget(TextClass(self, (120, 180, 400, 40), "Waiting For Client...", 48))
        self.addwidget(ButtonClass(self, self.cancel, (120, 360, 400, 30), "Cancel"))

        self.connected = False
        Game.evMgr.registerHandler(EV_HELLO, self.connect)

    def cancel(self):
        Game.gameMgr.changeState(Game.gameMgr.STATE_MENU)

    def connect(self, ev):
        self.connected = True
        
    def tick(self):
        BaseMenu.tick(self)
        if self.connected:
            self.connected = False
            Game.gameMgr.changeState(Game.gameMgr.STATE_NETWORK_GAME)
#@nonl
#@-node:jpenner.20050605173506:Server Wait Screen
#@+node:jpenner.20050605180040:Client Wait Screen
class ClientWait(BaseMenu):
    def menuLayout(self):
        self.addwidget(TextClass(self, (120, 180, 400, 40), "Contacting Server...", 48))
        self.addwidget(ButtonClass(self, self.cancel, (120, 360, 400, 30), "Cancel"))

        self.connected = False
        Game.evMgr.registerHandler(EV_BALLPOS, self.connect)

    def cancel(self):
        Game.gameMgr.changeState(Game.gameMgr.STATE_MENU)

    def connect(self, ev):
        self.connected = True
        
    def tick(self):
        BaseMenu.tick(self)
        if self.connected:
            self.connected = False
            Game.gameMgr.changeState(Game.gameMgr.STATE_NETWORK_GAME)
        else:
            Game.network.sendEvent(ConnectEvent())

#@-node:jpenner.20050605180040:Client Wait Screen
#@+node:jpenner.20050616085506:Failure Screen
class FailScreen(BaseMenu):
    def menuLayout(self):
        self.errText = MultiLineTextClass(self, (120, 60, 400, 270), "", 24)
        self.addwidget(self.errText)
        self.addwidget(ButtonClass(self, self.ok, (120, 360, 400, 30), "OK"))

    def ok(self):
        Game.gameMgr.changeState(Game.gameMgr.STATE_MENU)
    
    def onEnter(self):
        BaseMenu.onEnter(self)
        self.errText.settext(Game.failure)
#@nonl
#@-node:jpenner.20050616085506:Failure Screen
#@-others
#@-node:jpenner.20050604112932:Menu
#@+node:jpenner.20050305121157:Game
#@+others
#@+node:jpenner.20050604175241:Graphics
#@+others
#@+node:jpenner.20050604192205:Generic Graphics Manager
class GameGraphicsMgr:
    def __init__(self):
        self.all = pygame.sprite.RenderUpdates()
    
        self.bkg = pygame.Surface((SCREENRECT.width, SCREENRECT.height))
        self.bkg.fill(pygame.color.Color("black"))

        self.trackedSprites = []

    def trackSprite(self, sprite, spriteToTrack):
        self.trackedSprites.append({'sprite': sprite, 'spriteToTrack': spriteToTrack})

    def clearScreen(self):
        Game.screen.set_clip()
        Game.screen.fill(pygame.color.Color("black"))
        pygame.display.update()
                    
    def tick(self):       
        for item in self.trackedSprites:
            item['sprite'].rect.centerx = item['spriteToTrack'].rect.centerx
            item['sprite'].rect.centery = item['spriteToTrack'].rect.centery
        
        self.all.clear(Game.screen, self.bkg)
        self.all.update()       
        dirty = self.all.draw(Game.screen)
        pygame.display.update(dirty)

#@-node:jpenner.20050604192205:Generic Graphics Manager
#@+node:jpenner.20050604175241.1:TFT Graphics Manager
class TFTGraphicsMgr(GameGraphicsMgr):
    def __init__(self):
        GameGraphicsMgr.__init__(self)
        Floor.containers = self.all
        Net.containers = self.all
        Ball.containers = self.all
        ShotLine.containers = self.all
    
        Game.ball = Ball(BALL_STARTX, BALL_STARTY)
        Game.floor = Floor()
        Game.net = Net()
        self.shotLine = ShotLine()

        self.trackSprite(self.shotLine, Game.ball)
        
    def tick(self):
        self.shotLine.updateAngle()
        GameGraphicsMgr.tick(self)
#@-node:jpenner.20050604175241.1:TFT Graphics Manager
#@+node:jpenner.20050305120654:Sprites
#@+others
#@+node:jpenner.20050305112032:Floor
class Floor(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.Surface((SCREENRECT.width - (SCREENRECT.width / 8), SCREENRECT.height / 96))
        self.image.fill(pygame.color.Color("white"))
        self.rect = self.image.get_rect()
        self.reloading = 0
        self.rect.centerx = SCREENRECT.centerx
        self.rect.bottom = SCREENRECT.bottom * 0.875
        self.origtop = self.rect.top
        self.facing = -1

        
#@nonl
#@-node:jpenner.20050305112032:Floor
#@+node:jpenner.20050305120626:Net
class Net(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.Surface((SCREENRECT.width / 128, SCREENRECT.height / 12))
        self.image.fill(pygame.color.Color("white"))
        self.rect = self.image.get_rect()
        self.reloading = 0
        self.rect.centerx = SCREENRECT.centerx
        self.rect.bottom = SCREENRECT.bottom * 0.875
        self.origtop = self.rect.top
        self.facing = -1

        
#@-node:jpenner.20050305120626:Net
#@+node:jpenner.20050427175728:Ball
class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.Surface((SCREENRECT.width / 128, SCREENRECT.height / 96))
        self.image.fill(pygame.color.Color("white"))
        self.rect = self.image.get_rect()
        self.reloading = 0
        self.rect.centerx = x
        self.rect.centery = y
        self.origtop = self.rect.top
        self.facing = -1
        
    def currentPlayer(self):
        if self.rect.centerx < Game.net.rect.centerx:
            return 1
        else:
            return 2

        

#@-node:jpenner.20050427175728:Ball
#@+node:jpenner.20050305123236:Shot Line
class ShotLine(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.Surface((SCREENRECT.width / 32, SCREENRECT.height / 24), SRCALPHA)
        self.image.set_colorkey(pygame.color.Color("purple"))
        self.rect = self.image.get_rect()
        self.updateAngle()       
        self.reloading = 0
        self.origtop = self.rect.top
        self.facing = -1       
                
    def updateAngle(self):
        angle = makeAngle(pygame.mouse.get_pos())
        self.image.fill(pygame.color.Color("purple")) # clear
        pygame.draw.line(self.image, pygame.color.Color("white"), 
                        anglePos(self.image.get_rect(), angle, 6), anglePos(self.image.get_rect(),angle,12))

        
#@-node:jpenner.20050305123236:Shot Line
#@-others
#@nonl
#@-node:jpenner.20050305120654:Sprites
#@-others
#@nonl
#@-node:jpenner.20050604175241:Graphics
#@+node:jpenner.20050320112219:Physics
#@+others
#@+node:jpenner.20050424152556:Physics Manager
class PhysicsMgr:
    def __init__(self):
        self.gamePhysics = PhysicsEngine()
        self.netPhysics = NetworkPhysicsEngine()
        
        Game.evMgr.registerHandler(EV_PLAYER_UPDATE, self.switchEngines)
        Game.evMgr.registerHandler(EV_PLAYER_SWITCH, self.switchToGame)

    def onEnter(self):
        if Game.currentplayer == Game.myplayer:
            self.current = self.gamePhysics
        else:
            self.current = self.netPhysics
        self.lastSeq = -1
        
    def switchEngines(self, ev):
        if Game.ball.currentPlayer() <> Game.myplayer:
            self.current = self.netPhysics
            self.current.switchStarted = True
        else:
            self.current = self.gamePhysics
    
    def switchToGame(self, ev):
        if ev.fromplayer <> Game.myplayer:
            if ev.seq > self.lastSeq:
                self.lastSeq = ev.seq
                self.gamePhysics.resync(ev)
                Game.evMgr.postEvent(PlayerUpdateEvent())


    def tick(self):
        self.current.tick()
#@nonl
#@-node:jpenner.20050424152556:Physics Manager
#@+node:jpenner.20050306103246:Game Physics
class PhysicsEngine:
    def __init__(self):
        Game.evMgr.registerHandler(EV_HIT, self.hitHandler)
        Game.evMgr.registerHandler(EV_SERVE, self.serveHandler)
        
        self.xvel = 0
        self.yvel = 0
        self.stopped = True
        
    def tick(self):
        # only do gravity / collision detection if ball is moving
        if not self.stopped:
            # Gravity
            self.yvel += GRAVITY
                        
            #@            << Floor collision >>
            #@+node:jpenner.20050310185348:<< Floor collision >>
            if (Game.ball.rect.bottom + self.yvel) > Game.floor.rect.top:
                self.yvel = -abs(self.yvel) + FRICTION
                if self.yvel > 0:
                    self.yvel = 0
                    self.xvel = 0
                    self.stopped = True
            
                Game.evMgr.postEvent(BounceEvent())
            #@nonl
            #@-node:jpenner.20050310185348:<< Floor collision >>
            #@nl
            #@            << Net collision >>
            #@+node:jpenner.20050310185348.1:<< Net collision >>
            if (( ((Game.ball.rect.right < Game.net.rect.left) and ((Game.ball.rect.right + self.xvel) >= Game.net.rect.left) ) or
                  ((Game.ball.rect.left > Game.net.rect.right) and ((Game.ball.rect.left + self.xvel) <= Game.net.rect.right) ) ) and
                  ((Game.ball.rect.bottom + self.yvel) > Game.net.rect.top)):
                        self.xvel = -self.xvel
            
            #@-node:jpenner.20050310185348.1:<< Net collision >>
            #@nl
            #@            << Switch players >>
            #@+node:jpenner.20050310185414:<< Switch players >>
            if ((Game.ball.rect.centerx < Game.net.rect.centerx) and ((Game.ball.rect.centerx + self.xvel) >= Game.net.rect.centerx) or
                (Game.ball.rect.centerx >= Game.net.rect.centerx) and ((Game.ball.rect.centerx + self.xvel) < Game.net.rect.centerx)):
                    Game.evMgr.postEvent(PlayerUpdateEvent())
            
            #@-node:jpenner.20050310185414:<< Switch players >>
            #@nl
            
            Game.ball.rect.centerx += self.xvel
            Game.ball.rect.centery += self.yvel
            
        Game.evMgr.postEvent(BallPosEvent(Game.ball.rect.centerx, Game.ball.rect.centery))
        Game.switchEv = PlayerSwitchEvent(self.xvel, self.yvel, Game.ball.rect.centerx, Game.ball.rect.centery, self.stopped)
       
    def hitHandler(self,hitEvent):
        self.xvel = hitEvent.xvel
        self.yvel = hitEvent.yvel
        self.stopped = False

    def serveHandler(self, ev):
        self.stopped = True

    def resync(self, ev):
        self.xvel = ev.xvel
        self.yvel = ev.yvel
        Game.ball.rect.centerx = ev.xpos
        Game.ball.rect.centery = ev.ypos
        self.stopped = ev.stopped
        
#@nonl
#@-node:jpenner.20050306103246:Game Physics
#@+node:jpenner.20050320112219.1:Network Physics
class NetworkPhysicsEngine:
    def __init__(self):
        Game.evMgr.registerHandler(EV_BALLPOS, self.updatePos)
        self.switchStarted = False
        
    def updatePos(self, ev):
        if (ev.fromplayer <> Game.myplayer):
            self.switchStarted = False
            Game.ball.rect.centerx = ev.x
            Game.ball.rect.centery = ev.y

    def tick(self):
        log ("netphysics")
        if self.switchStarted:
            Game.evMgr.postEvent(Game.switchEv)

#@-node:jpenner.20050320112219.1:Network Physics
#@-others
#@nonl
#@-node:jpenner.20050320112219:Physics
#@+node:jpenner.20050615085910:AI
class AIPlayer:
    def tick(self):
        if random.randint(0,13) == 1:
            angle = math.radians(random.randint(180 + 10, 270 - 10))
            Game.evMgr.postEvent( ClickEvent(velocityFromAngle(angle), Game.AIPlayer) )
        
#@-node:jpenner.20050615085910:AI
#@+node:jpenner.20050307180329:Sound
class SoundEngine:
    def __init__(self):
        f = { EV_HIT: 'hit.wav',
              EV_BOUNCE: 'bounce.wav',
              EV_SCORE: 'score.wav',
              EV_HELLO: 'connect.wav' }

        self.sound = {}
        for evtype, filename in f.iteritems():
            try:
                self.sound[evtype] = pygame.mixer.Sound('data/' + filename)
                Game.evMgr.registerHandler(evtype, self.noise)
            except:
                pass
                
    def noise(self, ev):
        self.sound[ev.type].play()
        
        
#@-node:jpenner.20050307180329:Sound
#@+node:jpenner.20050312135503:Rules
class RuleManager:
    def __init__(self):
        Game.evMgr.registerHandler(EV_CLICK, self.clickHandler)
        Game.evMgr.registerHandler(EV_SERVE, self.serveHandler)
        Game.evMgr.registerHandler(EV_PLAYER_UPDATE, self.updateHandler)
        self.playerhit = False
        self.infinitehits = False
        Game.currentplayer = 1
        
    def clickHandler(self, ev):
        if not self.playerhit and (ev.player == Game.currentplayer or ev.player == SINGLE_PLAYER):
            Game.evMgr.postEvent(HitEvent(ev.xvel, ev.yvel))
            if not self.infinitehits:
                self.playerhit = True
    
    def updateHandler(self, ev):
        self.playerhit = False
        Game.currentplayer = Game.ball.currentPlayer()
    
    def serveHandler(self, ev):  
        Game.ball.rect.centerx = BALL_STARTX
        Game.ball.rect.centery = BALL_STARTY
        Game.evMgr.postEvent(PlayerUpdateEvent())
            
            
#@-node:jpenner.20050312135503:Rules
#@+node:jpenner.20050310200258:Input
class InputManager:
    def tick(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                reactor.stop()
            self.sdl_event(event)
            
    def sdl_event(self, event):        
        if event.type == MOUSEBUTTONUP:
            angle = makeAngle(event.pos)
            Game.evMgr.postEvent( ClickEvent(velocityFromAngle(angle), Game.myplayer) )
            
        if event.type == KEYUP:
            Game.evMgr.postEvent( ServeEvent() )
            
#@nonl
#@-node:jpenner.20050310200258:Input
#@+node:jpenner.20050305122430:Game Loop

#@+others
#@+node:jpenner.20050606072251:State Machine
class GameState:
    def __init__(self, manager, onenter = None, onexit = None):
        def doNothing(): pass

        if manager <> None:
            self.tick = manager.tick
        else:
            self.tick = doNothing

        if onenter <> None:
            self.enter = onenter
        else:
            self.enter = doNothing

        if onexit <> None:
            self.exit = onexit
        else:
            self.exit = doNothing
        
class StateMachine:
    def __init__(self, states, initialState = 0):
        self.state = initialState
        self.states = states
        self.states[self.state].enter()
        self.newstate = -1
        
    def changeState(self, newstate):
        # Don't change states in the middle of a tick!
        self.newstate = newstate
        
    def tick(self):
        if self.newstate >= 0:
            self.states[self.state].exit()
            self.state = self.newstate
            self.states[self.state].enter()
            self.newstate = -1
            
        self.states[self.state].tick()

class GameLoop:
    def __init__(self, managers):
        self.managers = managers

    def tick(self):
        for manager in self.managers:
            manager.tick()
#@-node:jpenner.20050606072251:State Machine
#@+node:jpenner.20050606072251.1:Game Manager
class GameMgr (StateMachine):
    def __init__(self):
        self.STATE_MENU = 0
        self.STATE_NETWORK_GAME = 1
        self.STATE_SINGLE_PLAYER = 2
        self.STATE_WAIT_FOR_CLIENT = 3
        self.STATE_CONNECT = 4
        self.STATE_FAILURE = 5
                
        inputMgr = InputManager()
        self.graphicsMgr = TFTGraphicsMgr()
        self.physicsMgr = PhysicsMgr()

        mainMenu = MainMenu()
        failScreen = FailScreen()
        self.serverWait = ServerWait()
        self.clientWait = ClientWait()
        
        StateMachine.__init__(self,
            [GameState(mainMenu, mainMenu.onEnter),
             GameState(GameLoop([inputMgr, Game.evMgr, self.physicsMgr, self.graphicsMgr]), self.gameEnter),
             GameState(GameLoop([inputMgr, AIPlayer(), Game.evMgr, PhysicsEngine(), self.graphicsMgr]), self.gameEnter),
             GameState(GameLoop([Game.evMgr, self.serverWait]), self.serverEnter, self.networkExit),
             GameState(GameLoop([Game.evMgr, self.clientWait]), self.clientEnter, self.networkExit),
             GameState(failScreen, failScreen.onEnter, self.networkExit)
            ])

    def gameEnter(self):
        self.graphicsMgr.clearScreen()
        self.physicsMgr.onEnter()

    def clientEnter(self):
        self.clientWait.onEnter()

        Game.network = TFTProtocol()
        def onResolve(ip):
            Game.network.address = (ip, Game.ServerPort)
            Game.port = reactor.listenUDP(0, Game.network)
        def onFail(err):
            Game.failure = err.getErrorMessage()
            self.changeState(self.STATE_FAILURE)
        reactor.resolve(Game.ServerIP).addCallback(onResolve).addErrback(onFail)

    def serverEnter(self):
        self.serverWait.onEnter()        

        Game.network = TFTProtocol()
        try:
            Game.port = reactor.listenUDP(Game.ServerPort, Game.network)
            log ("Listening on " + str(Game.ServerPort))
        except:
            Game.failure = "Unable to listen on UDP port " + str(Game.ServerPort) + ".  Make sure nothing else is using that port, and you have the proper permissions to create a server on it."
            self.changeState(self.STATE_FAILURE)

    def networkExit(self):
        if ((self.newstate == self.STATE_MENU) or (self.newstate == self.STATE_FAILURE)) and (Game.port <> None):  # cancelled
            Game.port.stopListening()
#@-node:jpenner.20050606072251.1:Game Manager
#@-others


#@-node:jpenner.20050305122430:Game Loop
#@+node:jpenner.20050319125841:Setup
def main():
    random.seed()
    pygame.init()

#    startLogging('tennis.log')

    pygame.display.set_caption('Tennis For Two')
    pygame.display.set_icon(pygame.image.load('tennis.bmp'))
    
    Game.screen = pygame.display.set_mode(SCREENRECT.size, DOUBLEBUF, 16)

    Game.evMgr = EventManager()    
    Game.sound = SoundEngine()   
    Game.rules = RuleManager()
    Game.gameMgr = GameMgr()
    
    task.LoopingCall(Game.gameMgr.tick).start(0.03)

    reactor.run()
    
    #cleanup
#    stopLogging()




#@-node:jpenner.20050319125841:Setup
#@-others
#@nonl
#@-node:jpenner.20050305121157:Game
#@-others

if __name__ == '__main__': main()
#@nonl
#@-node:jpenner.20050305105206:@thin TennisForTwo.py
#@-leo
