import time
from network import WLAN
from mqtt.mqtt import MQTTClient
import pop
import json
import machine

file_path_wifi = "/flash/wifi.json"
file_path_data = "/flash/sfdata.json"

# def load_wifi_demo():
#     wifi_data = None
#     with open(file_path, "r") as f:
#         wifi_data = json.load(f)
#     return wifi_data

# def save_wifi_demo(wifi_data):
#     with open(file_path, "w") as f:
#         f.write(json.dumps(wifi_data))

# def save_wifi_config(wifi_name, password):
#     config = {"wifi_name": wifi_name, "password": password}
#     with open(file_path, "w") as file:
#         json.dump(config, file, indent=4)
#     print("WiFi configuration saved: {}".format(config))


def load_wifi(file_path_wifi):
    with open(file_path_wifi, 'r') as file:
        data = json.load(file)
        if isinstance(data, list) and len(data) > 0:
            latest_wifi = None
            for wifi in data:
                if wifi["activate"] == 1:
                    latest_wifi = wifi
                    break
            # print(latest_wifi)
            return latest_wifi.get("wifi_name"), latest_wifi.get("password")
        else:
            return None, None
    
def connect_to_wifi(wifi_name, password):
    wlan = WLAN(mode=WLAN.STA)  
    wlan.connect(wifi_name, auth=(WLAN.WPA2, password), timeout=5000)
    while not wlan.isconnected():
        # print("Try to connect again...")
        time.sleep(1)
        wlan.connect(wifi_name, auth=(WLAN.WPA2, password), timeout=5000)

    # print("Connected to WiFi")
    # print("Network Config: {}".format(wlan.ifconfig()))

wifi_name, password = load_wifi(file_path_wifi)
connect_to_wifi(wifi_name, password)


# Print IP to LCD
my_ip = str(wlan.ifconfig()[0])
textlcd.print(my_ip)

ADAFRUIT_AIO_USERNAME = "SmartFarmUSTH"
ADAFRUIT_AIO_KEY      = ""

OUT_CHANNEL = "SmartFarmUSTH/feeds/sfout"
IN_CHANNEL = "SmartFarmUSTH/feeds/sfinp"
WIFI_OUT = "SmartFarmUSTH/feeds/wfout"

client = MQTTClient("id1", "io.adafruit.com",user=ADAFRUIT_AIO_USERNAME, password=ADAFRUIT_AIO_KEY, port=1883)

# sensors
co2 = pop.CO2()
light = pop.Light(0x5C)
# tphg = pop.Tphg(0x76)

# def save_data_sf(co2, light):
#     config = {"co2": co2, "ligth": light}
#     with open(file_path_data, "w") as f:
#         f.write(json.dumps(config))

# save_data_sf(co2.read(),light.read())

win_var = pop.Window()
fan = pop.Fan()
rgb = pop.RgbLedBar()
    
def sub_cb(topic, msg):
    topic = topic.decode()
    msg = msg.decode()
    if topic == IN_CHANNEL:
        if msg == "win_close":
            win_var.close()
        elif msg == "win_open":
            win_var.open()
        elif msg == "light_open":
            rgb.on()
            rgb.setColor([255, 255, 255])
        elif msg == "light_close":
            rgb.off()
        elif msg == "fan_open":
            fan.on()
        elif msg == "fan_close":
            fan.off()         
        elif msg == "/flash/wifi.json":
            with open(msg, 'r') as file:
                data = json.load(file)
            payload = json.dumps(data)
            client.publish(WIFI_OUT, payload)
        elif msg.startswith("wifi_"):
            wname = msg[5:]
            path = "/flash/wifi.json"
            with open(path, 'r') as file:
                data = json.load(file)
                for wifi in data:
                    if wifi["activate"] == 1:
                        wifi["activate"] = 0
                for wifi in data:
                    if wifi["wifi_name"] == wname:
                        wifi["activate"] = 1
                with open(file_path_wifi, "w2") as f:
                    f.write(json.dumps(data))
            machine.reset()


client.set_callback(sub_cb)
client.connect()
client.subscribe(topic=IN_CHANNEL)

# print("Ready to connect MQTT...")
while True:
    # payload = {"co2": co2.read(), "light": light.read()}
    payload = { "CO2":0, "Light_0x5C":0, "Temperature":0, "Humidity":0}
    payload['CO2'] = int(co2.read())
    payload['Light_0x5C'] = int(light_in.read())
    payload['Temperature'], _, b1['Humidity'], _ = tphg_in.read()
    client.publish(OUT_CHANNEL, json.dumps(payload))
    client.check_msg()
    time.sleep(5)

