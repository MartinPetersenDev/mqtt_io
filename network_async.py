import network
import uasyncio as asyncio

# Wifi connect function

class network_connect:

    def __init__(self):
        # Configure with SSID AND PSK
        self._ssid = ''
        self._psk = ''

        self._sta_if = network.WLAN(network.STA_IF)
        self._ap_if = network.WLAN(network.AP_IF)

        # Disable wifi
        self._sta_if.active(False)
        self._ap_if.active(False)

        loop = asyncio.get_event_loop()
        loop.create_task(self.run())

    async def run(self):
        while True:
            if not self._sta_if.isconnected():
                print('[network] Connecting to network', self._ssid)
                self._sta_if.active(True)

            self._sta_if.connect(self._ssid, self._psk)
            print('[network] ', self._sta_if.ifconfig())

            await asyncio.sleep(10)
