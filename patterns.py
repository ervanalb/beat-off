import lightstrip
import colorsys
import random
import math

def mkcolor(h,s=1.,v=1.):
    #return mk_yiq_color(h)
    ENDSZ = 0.02
    if h < ENDSZ:
        return (0., 0., 0.)
    elif h > (1.0 - ENDSZ):
        return (1., 1., 1.)
    h = (h - ENDSZ) / (1.0 - 2 * ENDSZ)
    return colorsys.hsv_to_rgb(h,s,v)

def mk_yiq_color(phi, y=0.4, kappa=1.9):
    sign = lambda x: -1 if x < 0 else 1
    phi *= math.pi * 2
    s, c = math.sin(phi), math.cos(phi)
    i = abs(s) ** kappa * sign(s)
    q = abs(c) ** kappa * sign(c)
    return colorsys.yiq_to_rgb(y, i * 0.595, q * 0.522)

mk_initial_color = property(lambda s: random.random())

class Full(object):
    name='full'
    controls=[
        'color', 
    ]

    initial_color = mk_initial_color

    def render(self,t,color):
        (r,g,b)=mkcolor(color)
        strip=[(r,g,b,1)]*lightstrip.STRIP_LENGTH
        return strip

class Segment(object):
    name='segment'
    controls=[
        'color',
        'start',
        'stop'
    ]

    initial_color = mk_initial_color

    def render(self,t,color,start,stop):
        (r,g,b)=mkcolor(color)
        strip=[(0,0,0,0)]*lightstrip.STRIP_LENGTH
        ends=(int((1.0- start)*lightstrip.STRIP_LENGTH),int((stop)*lightstrip.STRIP_LENGTH))
        for i in range(min(ends),max(ends)):
            strip[i]=(r,g,b,1)
        return strip

class Bounce(object):
    name='bounce'
    controls=[
        'color',
        'size',
        'frequency'
    ]
    initial_gamma = 0.4
    initial_color = mk_initial_color

    def __init__(self):
        self.lt=0
        self.x=0

    def map_gamma(self, g):
        return 0.01 + 6 * g

    @staticmethod
    def map_frequency(freq):
        f = int(round(freq * 6))
        return 2 ** (3 - f)

    @staticmethod
    def display_frequency(freq):
        freq = 1.0 / freq
        if freq >= 1:
            return str(int(freq))
        else:
            return "1/{}".format(int(1.0 / freq))

    initial_frequency = 3 / 6.


    def render(self, t, color, size, frequency):
        def f(x):
            #return (math.sin(x*2*math.pi)+1)/2
            t = (x % 1.0) * 2
            if t > 1.0:
                t = 2.0 - t
            return t

        (r,g,b)=mkcolor(color)
        strip=[]
        dt=t-self.lt
        self.lt=t
        self.x+=dt*frequency
        
        pos = f(self.x) * (1.0 - size) 
        strip=[(0,0,0,0)]*lightstrip.STRIP_LENGTH
        start = pos 
        stop = pos + size 
        
        ends=(start*lightstrip.STRIP_LENGTH,stop*lightstrip.STRIP_LENGTH)
        low, high = min(ends), max(ends)
        for i in range(int(low),int(high)):
            strip[i]=(r,g,b,1)
        strip[int(low)] = (r, g, b, 1.0 - (low - int(low)))
        strip[int(high)] = (r, g, b, high - int(high))
        return strip


class Wave(object):
    name='wave'
    controls=[
        'color',
        'frequency',
        'velocity',
        'gamma'
    ]
    initial_color = mk_initial_color
    initial_gamma = 0.4
    initial_frequency = 0.2
    initial_velocity = 0.2

    def __init__(self):
        self.lt=0
        self.x=0


    def map_gamma(self, g):
        return 0.01 + 6 * g

    @staticmethod
    def map_velocity(freq):
        f = int(round(freq * 6))
        return 2 ** (3 - f)

    @staticmethod
    def display_velocity(freq):
        freq = 1.0 / freq
        if freq >= 1:
            return str(int(freq))
        else:
            return "1/{}".format(int(1.0 / freq))

    initial_frequency = 3 / 6.

    def render(self,t,color,frequency,velocity, gamma):
        def f(x):
            return (math.sin(x*2*math.pi)+1)/2

        (r,g,b)=mkcolor(color)
        strip=[]
        dt=t-self.lt
        self.lt=t
        fr=frequency*10
        
        self.x+=dt*velocity*fr
        for i in range(lightstrip.STRIP_LENGTH):
            d=float(i)/lightstrip.STRIP_LENGTH
            a=f(d*fr+self.x) ** gamma
            strip.append((r,g,b,a))
        return strip

class Strobe(object):
    name='strobe'
    controls=[
        'color',
        'frequency',
        'up',
        'down',
    ]
    initial_color = mk_initial_color
    initial_up = 0.1
    initial_down = 0.5

    def __init__(self):
        self.lt=0

    @staticmethod
    def map_frequency(freq):
        f = int(round(freq * 6))
        return 2 ** (f - 3)

    @staticmethod
    def display_frequency(freq):
        if freq >= 1:
            return str(int(freq))
        else:
            return "1/{}".format(int(1.0 / freq))

    initial_frequency = 3 / 6.

    def render(self,t,color,frequency,up,down):
        period=frequency
        (r,g,b)=mkcolor(color)
        if t>=self.lt+period:
            strip=[(r,g,b,1)]*lightstrip.STRIP_LENGTH
            self.lt=math.floor(t/period)*period
        else:
            nt=(math.ceil(t/period)*period-t)/period
            pt=(t-math.floor(t/period)*period)/period
            a=0
            if up > 0 and nt < up:
                a+=1-nt/up
            if down > 0 and pt < down:
                a+=1-pt/down
            strip=[(r,g,b,a)]*lightstrip.STRIP_LENGTH
        return strip

class Rainbow(object):
    name='rainbow'
    controls=[
        'frequency',
        'velocity',
        'Y',
        'kappa',
    ]
    initial_kappa = 0.4
    initial_Y = 0.4
    initial_velocity = 0.2
    initial_frequency = 0.2

    def __init__(self):
        self.lt=0
        self.x=0

    def map_kappa(self, k):
        return 0.01 + 6 * k

    def render(self,t,frequency,velocity, Y, kappa):
        def f(x):
            return x % 1.0

        strip=[]
        dt=t-self.lt
        self.lt=t
        fr=frequency*10
        self.x+=dt*velocity*4*fr
        for i in range(lightstrip.STRIP_LENGTH):
            d=float(i)/lightstrip.STRIP_LENGTH
            pos = f(d*fr+self.x)
            r,g,b = mk_yiq_color(pos, y=Y, kappa=kappa)
            strip.append((r,g,b,1.0))
        return strip
