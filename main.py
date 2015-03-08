import pygame
import patterns
import device
import compositor
import lightstrip
import ui
import time
import nanokontrol
import audio
import timebase
import newlux

pygame.init()
pygame.midi.init()

screen=ui.init()

framerate = pygame.time.Clock()
go = True

try:
    nk2=nanokontrol.NanoKontrol2()
except nanokontrol.NanoKontrol2.NoDeviceException:
    nk2 = None

nk_knob_map={'Knob0':0,'Knob1':1,'Knob2':2,'Knob3':3,'Knob4':4,'Knob5':5,'Knob6':6,'Knob7':7}
nk_slider_map={'Slider0':0,'Slider1':1,'Slider2':2,'Slider3':3,'Slider4':4,'Slider5':5,'Slider6':6,'Slider7':7}

pattern_bank=[patterns.Full,patterns.Segment,patterns.Wave,patterns.Strobe, patterns.Bounce, patterns.Rainbow]

ah=audio.AudioHandler()

tb=timebase.Timebase()
tb.freq=140./60

NUMSLOTS = 8

class Control:
    def __init__(self,name,value=0.0, map_fn=None, display_fn=None):
        self.name=name
        self.value=value
        self.knob=None
        nop = lambda x: x
        self.map_fn = map_fn or (lambda x: x)
        self.display_fn = display_fn or (lambda x: "{:0.2f}".format(x))

    def to_pair(self):
        return (self.name, self.map_fn(self.value))

    def display_value(self):
        return self.display_fn(self.map_fn(self.value))

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
        nop = lambda x: x
        self.controls = []
        for control in pattern.controls:
            map_fn = getattr(pattern, "map_{}".format(control), None)
            display_fn = getattr(pattern, "display_{}".format(control), None)
            initial = getattr(pattern, "initial_{}".format(control), 0.0)
            self.controls.append(Control(control, value=initial, map_fn=map_fn, display_fn=display_fn))
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

luxbus = None
for i in range(3):
    try: 
        luxbus = newlux.LuxBus("/dev/ttyUSB%d" % i)
    except Exception as e:
        print i, e
        pass
if luxbus is None:
    print "No lux bus found"
else:
    print "Lux bus found"


"""
devices = []
for i in range(10):
    try:
        d = device.LuxDevice("/dev/ttyUSB%d" % i)
        devices.append(d)
    except Exception as e:
        print i, e
        pass
print "Found %d devices" % len(devices)
"""

class StripGroup(object):
    def __init__(self, devs, ids, name):
        self.bank = [BankPattern(p) for p in pattern_bank]
        self.slots = [None]*NUMSLOTS
        #self.devices = [devices[i] for i in devs if i < len(devices)]
        if luxbus is not None:
            self.devices = [newlux.LEDStrip(luxbus, i, 50) for i in ids]
            print "initialized devices: ", map(hex, ids)
        else:
            self.devices = []
        self.name = name
        self.is_active = False

#groups = [StripGroup([0], [0xF], "main"), StripGroup([0], [0xF0], "background"), StripGroup([0], [0xF00], "underglow")]
groups = [StripGroup([0], [0xFF], "main")]

lo=Knob('lo')
mid=Knob('mid')
hi=Knob('hi')
glob=[lo,mid,hi]
nk_knobs=[Knob('NK '+str(i+1)) for i in range(NUMSLOTS)]
nk_sliders=[Knob('NK S '+str(i+1)) for i in range(NUMSLOTS)]

def knobs(slot):
    return [None]+[nk_knobs[slot]]+glob

def alpha_knobs(slot):
    return [nk_sliders[slot]]

#interface=ui.UI(screen,bank,slots,knobs,alpha_knobs,tb)
interface=ui.UI(screen,groups,knobs,alpha_knobs,tb)


ah.start()

while go:
    framerate.tick(60)

    t=tb.get_time()

    for group in groups:
        frames=[]
        for slot in group.slots:
            if slot is not None:
                slot.update_pattern(t)
                frames.append((slot.frame,slot.alpha_control.value))

        frame = compositor.composite(frames)
        [d.send_frame(frame) for d in group.devices]
        time.sleep(0.003)

        if group.is_active:
            interface.master.frame=frame


    interface.render()

    pygame.display.update()

    if nk2 is not None:
        for (k,v) in nk2.get_events():
            if k in nk_knob_map:
                nk_knobs[nk_knob_map[k]].update(v)
            if k in nk_slider_map:
                nk_sliders[nk_slider_map[k]].update(v)

    lo.update(ah.lo)
    mid.update(ah.mid)
    hi.update(ah.hi)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            go = False
        if event.type in [pygame.MOUSEBUTTONUP,pygame.MOUSEBUTTONDOWN,pygame.MOUSEMOTION]:
            relpos=event.pos
            interface.mouse(relpos,event)
        if event.type in [pygame.KEYDOWN]:
            interface.keydown(event.key)

ah.stop()
