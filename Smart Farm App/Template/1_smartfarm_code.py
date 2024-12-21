import time
from network import WLAN
from mqtt.mqtt import MQTTClient
import pop
import json

# Load wifi name and password from conf.json
data = []
with open('wifi') as f:
    for line in f:
        data.append(json.loads(line))

wlan = WLAN(mode=WLAN.STA)
wlan.connect("CoderTapSu", auth=(WLAN.WPA2, "minh0511"), timeout=5000)

while not wlan.isconnected():
    print("Try to connect again...")
    time.sleep(1)
    wlan.connect("CoderTapSu", auth=(WLAN.WPA2, "minh0511"), timeout=5000)
print("Connected to WiFi")

# Print IP to LCD
my_ip = str(wlan.ifconfig()[0])
textlcd = pop.Textlcd()
textlcd.print(my_ip)

ADAFRUIT_AIO_USERNAME = "SmartFarmUSTH"
# ADAFRUIT_AIO_KEY      = ""

OUT_CHANNEL = "SmartFarmUSTH/feeds/sfout"
IN_CHANNEL = "SmartFarmUSTH/feeds/sfinp"

client = MQTTClient("id1", "io.adafruit.com",user=ADAFRUIT_AIO_USERNAME, password=ADAFRUIT_AIO_KEY, port=1883)

# sensors
co2_var = pop.CO2()

# control
win_var = pop.Window()

def sub_cb(topic, msg):
    topic = topic.decode()
    msg = msg.decode()
    if topic == IN_CHANNEL:
        if msg == "win_close":
           win_var.close()
        elif msg == "win_open":
            win_var.open()
        elif msg == "wifi_<NEW_WIFI>":
            # Update new wifi name and pass in conf.json file
            pass
   
client.set_callback(sub_cb)
client.connect()
client.subscribe(topic=IN_CHANNEL)

print("Ready to connect MQTT...")
while True:
    client.publish(topic=OUT_CHANNEL, msg=str(co2_var.read()))
    client.check_msg()
    time.sleep(10)

