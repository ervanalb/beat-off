import time

class Timebase:
    def __init__(self):
        self.freq=0
        self.ltime=time.time()
        self.t=0

    def get_time(self):
        t=time.time()
        dt=t-self.ltime
        self.ltime=t
        self.t+=dt*self.freq
        return self.t

    def sync(self):
        self.t=0
