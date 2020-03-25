from machine import Pin, ADC, SPI
import uasyncio as asyncio


class Output:
    def __init__(self, pin, time_ms):
        self._raw_output = Pin(pin, Pin.OUT)
        self._output_flag = 0
        self._time_ms = time_ms
        loop = asyncio.get_event_loop()
        loop.create_task(self.run())

    def value(self):
        return self._raw_output.value()

    def on(self):
        self._output_flag = 1

    def off(self):
        self._output_flag = 0

    async def run (self):
        while True:
            if self._output_flag == 1:
                self._raw_output.on()
            else:
                self._raw_output.off()
            await asyncio.sleep_ms(self._time_ms)


class Input:
    def __init__(self, pin, debounce_ms):
        self._raw_input = Pin(pin, Pin.IN, Pin.PULL_UP)
        self._raw_input.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.irq_callback)
        self._irq_flag = 1
        self._value = 0
        self._debounce = debounce_ms
        self._has_new_value = 0
        self._old_state = 0
        loop = asyncio.get_event_loop()
        loop.create_task(self.run())

    def irq_callback(self, p):
        self._irq_flag = self._raw_input.value()
        #print("IRQ flag is: ", self._irq_flag)

    def value(self):
        self._has_new_value = 0
        return self._value

    def has_new_value(self):
        return self._has_new_value

    async def run(self):
        while True:
            if self._irq_flag == self._raw_input.value() and self._raw_input.value() == 0:
                self._value = 1
                self._has_new_value = 1
            else:
                self._value = 0

            if self._old_state != self._value:
                print("[io] Button:", self._value)

            self._old_state = self._value
            await asyncio.sleep_ms(self._debounce)


class Counter(Input):
    async def run(self):
        while True:
            if self._has_new_value == 0:
                self._value = 0

            if self._irq_flag == self._raw_input.value() and self._raw_input.value() == 0:
                self._value += 1
                self._irq_flag = 1
                self._has_new_value = 1
            print("[io] Counter:", self._value)
            await asyncio.sleep_ms(self._debounce)

    def value(self):
        self._has_new_value = 0
        return int(self._value)


class Analog:
    def __init__(self, scaling, offset, update_ms):
        self._adc = ADC(0)
        self._update_ms = update_ms
        self._has_new_value = 0
        self._value = 0
        self._scaling = scaling
        self._offset = offset
        loop = asyncio.get_event_loop()
        loop.create_task(self.run())

    def value(self):
        return self._value

    def has_new_value(self):
        return self._has_new_value

    async def run(self):
        while True:
            self._value = self._adc.read() * self._scaling + self._offset
            print("[io] Analog0 reads:", self._value)
            self._has_new_value = 1
            await asyncio.sleep_ms(self._update_ms)


class MCP3202(Analog):
    def __init__(self, scaling, offset, update_ms, channel):
        self._adc = ADC(0)
        self._update_ms = update_ms
        self._has_new_value = 0
        self._value = 0
        self._scaling = scaling
        self._offset = offset
        loop = asyncio.get_event_loop()
        loop.create_task(self.run())
        self._ch = channel
        self._cs = Pin(15, Pin.OUT)
        self._bytes = bytearray(3)

        self._spi = SPI(-1, baudrate=100000, polarity=1, phase=0, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
        self._spi.init(baudrate=100000)

    async def run(self):
        while True:
            self._cs.on()
            self._cs.off()
            if self._ch == 1:
                self._bytes = self._spi.read(3, 0xe0)
            else:
                self._bytes = self._spi.read(3, 0xc0)
            self._cs.on()

            self._value = self._bytes[0]*256*256 + self._bytes[1]*256 + self._bytes[2]
            self._value = self._value / 127

            if self._ch == 1:
                print("[io] MCP3202 CH1 reads:", self._value)
            else:
                print("[io] MCP3202 CH0 reads:", self._value)
            self._has_new_value = 1

            await asyncio.sleep_ms(self._update_ms)


class Digital(Input):
    def __init__(self, pin, debounce_ms):
        self._raw_input = Pin(pin, Pin.IN)
        self._raw_input.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.irq_callback)
        self._irq_flag = 0
        self._value = 0
        self._debounce = debounce_ms
        self._has_new_value = 0
        loop = asyncio.get_event_loop()
        loop.create_task(self.run())

    async def run(self):
        while True:
            if self._irq_flag == self._raw_input.value() and self._raw_input.value() == 1:
                self._value = self._raw_input.value()
                self._has_new_value = 1
            else:
                self._value = 0
            print("[io] Digital:", self._raw_input.value())
            await asyncio.sleep_ms(self._debounce)

