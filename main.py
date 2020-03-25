import uasyncio as asyncio
import io
import network_async
import mqtt_io
import garbage
from mqtt_as import config

# Main
def main():

    # Setup i/o 's
    button0 = io.Input(5, 500) # Called every 500 msec
    #counter1 = io.Counter(4, 500) # Called every 500 msec
    led0 = io.Output(14, 500) # Called every 500 msec
    #analog0 = io.Analog(0.0977, -12, 10000) # Temp = adc/10,24 # Called every 10,000 msec

    # Setup MQTT
	## Configure MQTT BROKER/SERVER AND TOPIC
    SERVER = "192.168.0.100"
    TOPIC = b"sensors/wemos"

    tag_led0 = mqtt_io.OutputTag(led0,"button0led0")
    tag_button0 = mqtt_io.InputTag(button0, "button0led0")
    #tag_counter1 = mqtt_io.CounterTag(counter1, "counter1")
    #tag_analog0 = mqtt_io.AnalogTag(analog0,"temperature0")

    mqtt = mqtt_io.MqttWrapper(SERVER, TOPIC, config, 1000) # Called every 1000 msec

    mqtt.addinput(tag_button0)
    #mqtt.addinput(tag_counter1)
    mqtt.addoutput(tag_led0)
    #mqtt.addinput(tag_analog0)


    # Setup network
    network_connect = network_async.network_connect()

    # Setup scheduled garbage collection
    garbageCollector = garbage.garbage(90000) # Called every 90 sec"

    # Start scheduler
    loop = asyncio.get_event_loop()
    loop.run_forever()

# execute main()
main()
