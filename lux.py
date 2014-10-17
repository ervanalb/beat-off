import logging
import serial
import time

logger = logging.getLogger(__name__)


class SingleLuxDevice(object):

    def __init__(self, port, baudrate=115200, addr=0x00, flags=0x00):
        self.ser = serial.Serial(port, baudrate)
        self.addresses = {}
        self.addr = addr
        self.flags = flags

    def close(self):
        self.ser.close()

    def raw_packet(self, data):
        logger.debug("Serial Data: %s", ';'.join(map(lambda x: "{:02x}".format(x), data)))
        #print ("Serial Data: %s", ';'.join(map(lambda x: "{:02x}".format(x), data)))
        self.ser.write("".join([chr(d) for d in data]))
        return len(data)

    def flush(self):
        self.ser.flush()

    def cobs_packet(self, data):
        #print ("Not encoded: %s", ';'.join(map(lambda x: "{:02x}".format(x), data)))
        rdata = []
        i = 0
        for d in data[::-1]:
            i += 1
            if d == 0:
                rdata.append(i)
                i = 0
            else:
                rdata.append(d)
        return self.raw_packet([0, i+1] + rdata[::-1])
        

    def framed_packet(self, data=None, flags=None, addr=None):
        if flags is None:
            flags = self.flags
        if addr is None:
            flags = self.addr

        if data is None or len(data) > 250:
            raise Exception("invalid data")
        data=list(data)
        crc_frame = [addr, flags] + data
        checksum = sum(crc_frame) & 0xff
        frame = [len(data), checksum] + crc_frame
        return self.cobs_packet(frame)


class LuxRelayDevice(SingleLuxDevice):
    def __init__(self, *args, **kwargs):
        self.data_buffer = []
        super(self, LuxRelayDevice).__init__(*args, **kwargs)

    def set(self, relay_number, state):
        # 1 -> relay on -> light off
        byte = 0 if state else 1
        byte |= relay_number << 4
        self.data_buffer.append(byte)

    def write(self, addr=None, flags=None):
        data_len = self.framed_packet(data=self.data_buffer, addr=addr, flags=flags)
        self.data_buffer = []
        return data_len

class DummyLuxRelayDevice(object):
    def __init__(self, addr=0x00, flags=0x00, size=16):
        self.addr = addr
        self.flags = flags
        self.size = size
        self.state = [True] * size
        self.next_state = self.state[:]

    def set(self, relay_number, state):
        self.next_state[relay_number] = state

    def write(self, addr=None, **kwargs):
        if addr is None:
            addr = self.addr
        self.state = self.next_state[:]
        print "Relay 0x%x:" % addr, self.state


