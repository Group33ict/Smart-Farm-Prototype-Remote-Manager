import sys
import time
from network import WLAN
import pop
import json
import socket

SSID = "ICTLab Guests"; PASSWORD = "guestsss"
#SSID = "USTH_Student"; PASSWORD = "usth2021!"
#SSID = "iPhone"; PASSWORD = "12345678"
#SSID = "osquizzz"; PASSWORD = "osquizzz"                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 



fan = pop.Fan(); rgb = pop.RgbLedBar(); window = pop.Window(); textlcd = pop.Textlcd(); heater = pop.Heater(); cooler = pop.Cooler()

co2 = pop.CO2(); soil = pop.SoilMoisture(); light_in = pop.Light(0x5C); tphg_in = pop.Tphg(0x76)

fancheck = False; windowcheck = False; ledcheck = False; fanheatcheck = False
Timer = 0

print("Run")
rgb.on()
rgb.setColor([255, 255, 255])
time.sleep(1)
rgb.off()

wlan = WLAN(mode=WLAN.STA)
wlan.connect(SSID, auth=(WLAN.WPA2, PASSWORD))
''''''
connect_cnt = 0
while not wlan.isconnected():
    wlan.connect(SSID, auth=(WLAN.WPA2, PASSWORD))
    time.sleep(0.5)
    print("Connecting to IoT device... ", connect_cnt)
    connect_cnt = connect_cnt + 1

#textlcd.print(wlan.status())

print('Connected.')
my_ip = str(wlan.ifconfig()[0])
textlcd.print(my_ip)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(s)

print ("Socket successfully created")
port = 40674
#s.bind(('172.31.98.185', port))
s.bind(('0.0.0.0', port))
print ("socket binded to %s" %(port))

s.listen(5)  
print ("socket is listening")


'''''' 
while True:
    c, addr = s.accept()
    print ('Got connection from', addr)
    try:
        a = c.recv(1024).decode('utf8')
        a0 = json.loads(a)
        mess = a0['mess']
        print(mess)
    except:
        str = "done"
        a = str.encode('utf-8')
        c.send(a)
        c.close()
        continue
    
    if(mess == "off"):
        break
    elif(mess == "timer"):
        Timer = mess['timer']
        timer(Timer)
    elif(mess == "check"):
        check = {"fancheck": True, "windowcheck": True, "fanheatcheck": True, "rgb1":0, "rgb2":0, "rgb3":0}
        rgbval = rgb.read()
        check['fancheck'] = fancheck; check['windowcheck'] = windowcheck; check['fanheatcheck'] = fanheatcheck
        
        if(ledcheck == True):
            check['rgb1'] = rgbval[0]; check['rgb2'] = rgbval[1]; check['rgb3'] = rgbval[2]
        else:
            check['rgb1'] = 0; check['rgb2'] = 0; check['rgb3'] = 0
            
        check00 = json.dumps(check)
        res1 = check00.encode('utf-8')
        c.send(res1)
    elif(mess == "fanon"):
        fan.on()
        fancheck = True
    elif(mess == "fanoff"):
        fan.off()
        fancheck = False
    elif(mess == "fanheaton"):
        heater.on()
        fanheatcheck = True
    elif(mess == "fanheatoff"):
        heater.off()
        fanheatcheck = False
    elif(mess == "windopn"):
        window.open()
        windowcheck = True
    elif(mess == "windclos"):
        window.close()
        windowcheck = False
    elif(mess == "ledon"):
        rgb.setColor([a0['rgb1'], a0['rgb2'], a0['rgb3']])
        rgb.on()
        ledcheck = True
    elif(mess == "ledoff"):
        rgb.setColor([0, 0, 0])
        rgb.on()
        rgb.off()
        ledcheck = False
    elif(mess == "measre"):
        b1 = { "CO2":0, "SoilMoisture":0, "Light_0x5C":0, "Temperature":0, "Humidity":0}
        b1['CO2'] = int(co2.read())
        b1['SoilMoisture'] = int(soil.read())
        b1['Light_0x5C'] = int(light_in.read())
        b1['Temperature'], _, b1['Humidity'], _ = tphg_in.read()
        
        b = json.dumps(b1)
        res = b.encode('utf-8')
        c.send(res)
    else: continue 
        
    str = "done"
    a = str.encode('utf-8')
    c.send(a)
    c.close()

def timer(Timer):
    while True:
        c, addr = s.accept()
        print ('Got connection from', addr)
        try:
            a = c.recv(1024).decode('utf8')
            a0 = json.loads(a)
            mess = a0['mess']
            print(mess)
        except:
            str = "done"
            a = str.encode('utf-8')
            c.send(a)
            c.close()
            continue
        
        if(mess == "timer"):
            Timer = mess['timer']
        elif(mess == "check"):
            check = {"fancheck": True, "windowcheck": True, "fanheatcheck": True, "rgb1":0, "rgb2":0, "rgb3":0}
            rgbval = rgb.read()
            check['fancheck'] = fancheck; check['windowcheck'] = windowcheck; check['fanheatcheck'] = fanheatcheck
        
            if(ledcheck == True):
                check['rgb1'] = rgbval[0]; check['rgb2'] = rgbval[1]; check['rgb3'] = rgbval[2]
            else:
                check['rgb1'] = 0; check['rgb2'] = 0; check['rgb3'] = 0
            
            check00 = json.dumps(check)
            res1 = check00.encode('utf-8')
            c.send(res1)
        elif(mess == "fanon"):
            fan.on()
            fancheck = True
        elif(mess == "fanoff"):
            fan.off()
            fancheck = False
        elif(mess == "fanheaton"):
            heater.on()
            fanheatcheck = True
        elif(mess == "fanheatoff"):
            heater.off()
            fanheatcheck = False
        elif(mess == "windopn"):
            window.open()
            windowcheck = True
        elif(mess == "windclos"):
            window.close()
            windowcheck = False
        elif(mess == "ledon"):
            rgb.setColor([a0['rgb1'], a0['rgb2'], a0['rgb3']])
            rgb.on()
            ledcheck = True
        elif(mess == "ledoff"):
            rgb.setColor([0, 0, 0])
            rgb.on()
            rgb.off()
            ledcheck = False
        elif(mess == "measre"):
            b1 = { "CO2":0, "SoilMoisture":0, "Light_0x5C":0, "Temperature":0, "Humidity":0}
            b1['CO2'] = int(co2.read())
            b1['SoilMoisture'] = int(soil.read())
            b1['Light_0x5C'] = int(light_in.read())
            b1['Temperature'], _, b1['Humidity'], _ = tphg_in.read()
        
            b = json.dumps(b1)
            res = b.encode('utf-8')
            c.send(res)
        else: continue
            
    

def mess():
    pass