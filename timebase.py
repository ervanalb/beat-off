import time

class Timebase:
    def __init__(self):
        self.freq=0
        self.lt=time.time()
        self.lx=0

    def get_str(self):
        return "{0:.2} BPM".format(self.freq*60)

    def get_time(self):
        t=time.time()
        dt=self.lt-t
        self.lx+=dt*freq
        return self.lx
