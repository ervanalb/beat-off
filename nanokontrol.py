#!/usr/bin/env python

import time
import pygame.midi

input_map={
    0:'Slider0',
    1:'Slider1',
    2:'Slider2',
    3:'Slider3',
    4:'Slider4',
    5:'Slider5',
    6:'Slider6',
    7:'Slider7',
    16:'Knob0',
    17:'Knob1',
    18:'Knob2',
    19:'Knob3',
    20:'Knob4',
    21:'Knob5',
    22:'Knob6',
    23:'Knob7',
}

class NanoKontrol2(object):
    MAX_EVENTS = 100
    class NoDeviceException(Exception):
        pass

    def __init__(self):
        input_dev_id=None
        output_dev_id=None
        for dev in range(pygame.midi.get_count()):
            _interface, name, inp, outp, opened = pygame.midi.get_device_info(dev)
            if "nanoKONTROL2" not in name:
                continue
            if inp: 
                input_dev_id = dev
            if outp: 
                output_dev_id = dev
        if input_dev_id is None or output_dev_id is None:
            raise NanoKontrol2.NoDeviceException("Could not find NanoKontrol2!")

        self.input_dev=pygame.midi.Input(input_dev_id)
        self.output_dev=pygame.midi.Output(output_dev_id)

    def close(self):
        self.input_dev.close()
        self.output_dev.close()

#    def set_led(self, note, state, force=False):
#        if force or self.led_state[note] != state:
#            self.output_dev.write_short(176, note, 127 if state else 0)
#        self.led_state[note] = state

    def get_events(self):
        raw_events = self.input_dev.read(self.MAX_EVENTS)
        return [(input_map[channel],float(data)/127) for ((status, channel, data, _data2),timestamp) in raw_events if channel in input_map]

if __name__ == "__main__":
    pygame.midi.init()
    nk = NanoKontrol2()
    while True:
        for ev in nk.get_events():
            print ev
