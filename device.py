import lux
import struct

class LuxDevice:
    def __init__(self, port="/dev/ttyUSB0"):
        self.lux_device=lux.SingleLuxDevice(port,baudrate=3000000)

    def color_to_device(self,(r,g,b)):
        g/=2
        b/=2

        r=int(round(r*31))
        g=int(round(g*31))
        b=int(round(b*31))
        val = 0x8000 | (r << 5) | g | (b << 10)
        if val == 0x8000 | (1 << 5):
            val = 0x8000
        return val

    def render(self,frame):
        frame=[self.color_to_device(p) for p in frame]
        frame=struct.pack('H'*len(frame),*frame)
        frame=struct.unpack('B'*len(frame),frame)
        self.lux_device.framed_packet(frame,addr=0x00,flags=0x00)
