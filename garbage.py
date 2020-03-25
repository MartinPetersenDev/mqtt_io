import gc
import uasyncio as asyncio


class garbage:

    def __init__(self, rate_ms):
        self._rate_ms = rate_ms
        loop = asyncio.get_event_loop()
        loop.create_task(self.run())

    async def run(self):
        while True:
            gc.collect()
            print("[gc] Garbage collected")
            await asyncio.sleep_ms(self._rate_ms)


