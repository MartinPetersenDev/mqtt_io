from mqtt_as import MQTTClient, config
import uasyncio as asyncio
#from machine import Pin
import utime
import ujson


class Tag:
    def __init__(self, object, tagname):
        self.object = object
        self.tagname = tagname


class InputTag(Tag):
    def value(self):
        if self.object.value() == 1:
            return ujson.dumps({self.tagname: "on"})
        else:
            return ujson.dumps({self.tagname: "off"})

    def has_new_value(self):
        return self.object.has_new_value()


class OutputTag(Tag):
    def value(self):
        return ujson.dumps({self.tagname: self.object.value()})

    def update(self, msg):
        try:
            obj = ujson.loads(msg)

            if obj.get(self.tagname) == "on":
                self.object.on()
            elif obj.get(self.tagname) == "off":
                self.object.off()

        except Exception:
            pass


class CounterTag(Tag):
    def value(self):
        return ujson.dumps({self.tagname: self.object.value()})

    def has_new_value(self):
        return self.object.has_new_value()


class AnalogTag(Tag):
    def value(self):
        return ujson.dumps({self.tagname: self.object.value()})

    def has_new_value(self):
        return self.object.has_new_value()


class MqttWrapper:

    _inputtags = []
    _outputtags = []
    _wct = 0  # worst case tick-time
    _bct = 0  # best case tick-time
    _t_start = 0
    _t_diff = 0
    _t_intervalstart = 0
    _t_interval = 0
    _adj_update_ms = 0  # internal automatically adjusted updatetime
    _adj_done = 0  # flag to detect adjustment done
    _t_err = 0

    def __init__(self, server, topic, config, update_ms):
        self._config = config
        self._config['subs_cb'] = self.callback
        self._config['connect_coro'] = self.conn_han
        self._config['server'] = server
        self._topic = topic
        self._update_ms = update_ms
        self._adj_update_ms = update_ms
        MQTTClient.DEBUG = True  # Optional: print diagnostic messages
        self._client = MQTTClient(self._config)
        loop = asyncio.get_event_loop()
        loop.create_task(self.run())

    def addinput(self, tag):
        self._inputtags.append(tag)

    def addoutput(self, tag):
        self._outputtags.append(tag)

    def callback(self, topic, msg):
        for t in self._outputtags:
            t.update(msg)

    async def conn_han(self, client):
        print("[MQTT] start subscribing")
        await self._client.subscribe(self._topic, 1)

    async def run(self):
        #self._statusled.on()  # set statusled solid on, to indicate mqtt is starting
        await self._client.connect()
        print("[MQTT] start publishing")
        while True:
            # Store tick times to calculate execution time and task interval times
            self._t_intervalstart = utime.ticks_ms()
            await asyncio.sleep_ms(self._adj_update_ms)
            self._t_start = utime.ticks_ms()

            # If WiFi is down the following will pause for the duration.
            for t in self._inputtags:
                if t.has_new_value():
                    await self._client.publish(self._topic, t.value(), qos=0)

            # Calculate tick times
            self._t_diff = utime.ticks_ms() - self._t_start
            self._t_interval = utime.ticks_ms() - self._t_intervalstart
            #print("[MQTT] Execution time is %d, task interval is %d, _adj_update is %d" % (self._t_diff, self._t_interval, self._adj_update_ms))

            # Auto adjust update time, until _t_interval is within requested update_ms +- 2%
            if self._adj_done == 0 and (self._t_interval > (self._update_ms + self._update_ms // 50) or self._t_interval < (self._update_ms - self._update_ms // 20)):
                self._t_err = self._update_ms - self._t_interval
                self._adj_update_ms += self._t_err//10
            else:
                self._adj_done = 1
