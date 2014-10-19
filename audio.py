import pyaudio
import threading
import struct
import numpy
from collections import deque

def lpf(data,mem,alpha):
    return mem+alpha*(data-mem)

def diode_lpf(data,mem,alpha):
    if data > mem:
        return data
    return mem+alpha*(data-mem)

def agc(data,hist,memory):
    hist.append(data)
    if len(hist)>memory:
        hist.popleft()
    small=min(hist)
    large=max(hist)
    if large == small:
        return 0.3
    return (float(data)-small)/(large-small)

class AudioHandler(threading.Thread):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 48000
    RANGES = [(20,200),(200,1200),(1200,2400)]
    ALPHA = 0.2
    MEMORY = 2000

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon=True
        self.pa=pyaudio.PyAudio()

        self.in_stream = self.pa.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK)

        self.lo=0
        self.mid=0
        self.hi=0

        self.go=True

    def run(self):
        out_mem=[0.]*len(self.RANGES)
        out_hist=[deque() for i in range(len(self.RANGES))]

        while self.go:
            for i in range(20):
                data = self.in_stream.read(self.CHUNK)
                a=self.in_stream.get_read_available()
                if a<self.CHUNK:
                    break
            samples = struct.unpack('h'*self.CHUNK,data)
            fft=numpy.fft.rfft(samples)
            fft=abs(fft)**2

            out=[]
            for (low,high) in self.RANGES:
                low_bucket=int(self.CHUNK*low/self.RATE)
                high_bucket=int(self.CHUNK*high/self.RATE)
                result=sum(fft[low_bucket:high_bucket])
                out.append(result)

            for i in range(len(self.RANGES)):
                out[i]=diode_lpf(out[i],out_mem[i],self.ALPHA)
                out_mem[i]=out[i]
                out[i]=agc(out[i],out_hist[i],self.MEMORY)

            self.lo=out[0]
            self.mid=out[1]
            self.hi=out[2]

    def stop(self):
        self.go=False
        self.join()
