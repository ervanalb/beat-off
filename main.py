import pygame
import patterns
import device
import compositor
import lightstrip
import ui
import time

pygame.init()

screen=ui.init()

framerate = pygame.time.Clock()
go = True

class Control:
    def __init__(self,name,value=0.0):
        self.name=name
        self.value=value
        self.knob=None

    def to_pair(self):
        return (self.name,self.value)

    def set_knob(self,knob):
        if self.knob is not None:
            self.knob.del_control(self)
        if knob is not None:
            knob.add_control(self)
        self.knob=knob

class Knob:
    def __init__(self,name):
        self.name=name
        self.controls=set()

    def add_control(self,control):
        self.controls.add(control)

    def del_control(self,control):
        self.controls.remove(control)

    def update(self,value):
        for c in self.controls:
            c.value=value

class Slot:
    def __init__(self,pattern):
        self.pat = pattern
        self.controls = [Control(c) for c in pattern.controls]
        self.alpha_control = Control('alpha')
        self.ui = ui.Pattern(self)

    def update_pattern(self,t):
        self.frame=self.pat.render(t,**dict([c.to_pair() for c in self.controls]))

    def render(self,surf,pos):
        self.ui.render(surf,pos)

class BankPattern:
    def __init__(self,pattern_cls):
        self.pat=pattern_cls
        self.ui=ui.BankPattern(self)

    def render(self,surf,pos):
        self.ui.render(surf,pos)

    def make(self):
        return Slot(self.pat())

bank = [BankPattern(p) for p in [patterns.Full,patterns.Segment,patterns.Wave]]
slots = [None]*8

env=[Knob(n) for n in ('env','hi','mid','low')]
nanokontrol_knobs=[Knob('NK'+str(i)) for i in range(len(slots))]

def knobs(slot):
    return [None]+[nanokontrol_knobs[slot]]+env

d = device.PrintDevice()

interface=ui.UI(screen,bank,slots,knobs)

while go:
    framerate.tick(60)

    t=time.time()

    frames=[]
    for slot in slots:
        if slot is not None:
            slot.update_pattern(t)
            frames.append((slot.frame,slot.alpha_control.value))

    frame = compositor.composite(frames)

    interface.master.frame=frame

    d.render(frame)

    interface.render()

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            go = False
        if event.type in [pygame.MOUSEBUTTONUP,pygame.MOUSEBUTTONDOWN,pygame.MOUSEMOTION]:
            relpos=event.pos
            interface.mouse(relpos,event)

