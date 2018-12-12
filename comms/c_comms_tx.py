# c_comms_tx.py Client-side app demo. Sends switch state to "rx" device.

# Released under the MIT licence.
# Copyright (C) Peter Hinch 2018

# Outage handling: switch chnages during the outage are ignored. When the
# outage ends, the switch state at that time is transmitted.

import gc
import uasyncio as asyncio
gc.collect()
import ujson
import client
import aswitch
import primitives
from machine import Pin


class App():
    def __init__(self, loop, verbose):
        self.verbose = verbose
        led = Pin(2, Pin.OUT, value = 1)  # Optional LED
        # Pushbutton on Cockle board from shrimping.it
        self.switch = aswitch.Switch(Pin(0, Pin.IN))
        self.switch.close_func(lambda : self.must_send.set())
        self.switch.open_func(lambda : self.must_send.set())
        self.must_send = primitives.Event()
        self.cl = client.Client(loop, verbose, led)
        loop.create_task(self.start(loop))

    async def start(self, loop):
        self.verbose and print('App awaiting connection.')
        await self.cl
        self.verbose and print('Got connection')
        while True:
            await self.must_send
            await self.cl.write(ujson.dumps([self.switch()]), False)
            self.must_send.clear()

    def close(self):
        self.cl.close()

loop = asyncio.get_event_loop()
app = App(loop, True)
try:
    loop.run_forever()
finally:
    app.close()
