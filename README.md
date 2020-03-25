# MQTT_IO 


##1 GENERAL INFORMATION
This is a collection of example code meant to explore using uasyncio and microPython 
as a deterministic (kinda-realtime) cooperative task scheduled for GPIO and MQTT, running 
on a small embedded devices.

The present code was setup to run on a ESP8266, connecting to a mosquitto MQTT broker. 

##2 BASIC FUNCTIONALITY

The code has the following basic functionality:

-   I/O objects reads or writes GPIO or ADC at a configurable interval
-   Tag objects assigns a tagname to I/O objects  
-   A wrapper for mqtt_as pub/sub's all tag objects with broker incl. configured 
    tagname, and executes callback functions to update GPIO (see example)   
-   Network stuff, reconnect etc. is handled automatically
-   Some debugging info is sent to REPL.
-   It has blinkenlights

##3 CONFIGURATION

Configure network_async.py with your WiFi SSID and PSK.

##4 EXAMPLE


Input *tag_button0* and *output tag_led0* are both assigned tagname *"button0led0"*, and are now linked via the broker.

When *tag_button0* reads 1, status *"on"* is published to the MQTT broker. 
Tag_led0 which is subscribing to the same topic and *tagname* receives status *"on"* and sets output to 1.
 
1) button0 reads GPIO=1
2) tag_button0 publish to topic=*"sensors"* {*"button0led0"*: *"on"*}
3) tag_led0 subscribes to topic=*"sensors"* {*"button0led0"*: *"on"*}
4) led0 writes GPIO=1
