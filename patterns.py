import lightstrip
import colorsys
import math

def mkcolor(h,s=1.,v=1.):
    return colorsys.hsv_to_rgb(h,s,v)

class Full:
    controls=[
        'color'
    ]

    def render(self,t,color):
        (r,g,b)=mkcolor(color)
        strip=[(r,g,b,1)]*lightstrip.STRIP_LENGTH
        return strip

class Segment:
    controls=[
        'color',
        'start',
        'stop'
    ]

    def render(self,t,color,start,stop):
        (r,g,b)=mkcolor(color)
        strip=[(0,0,0,0)]*lightstrip.STRIP_LENGTH
        ends=(int(start*lightstrip.STRIP_LENGTH),int(stop*lightstrip.STRIP_LENGTH))
        for i in range(min(ends),max(ends)):
            strip[i]=(r,g,b,1)
        return strip

class Wave:
    controls=[
        'color',
        'frequency',
        'velocity'
    ]

    def __init__(self):
        self.lt=0
        self.x=0

    def render(self,t,color,frequency,velocity):
        def f(x):
            return (math.sin(x*2*math.pi)+1)/2

        (r,g,b)=mkcolor(color)
        strip=[]
        dt=t-self.lt
        self.lt=t
        fr=frequency*10
        self.x+=dt*velocity*4*fr
        for i in range(lightstrip.STRIP_LENGTH):
            d=float(i)/lightstrip.STRIP_LENGTH
            a=f(d*fr+self.x)
            strip.append((r,g,b,a))
        return strip

