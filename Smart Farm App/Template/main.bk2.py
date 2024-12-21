import sys
import time
import pop
import json


print("run")

#co2 = pop.CO2()
#soil = pop.SoilMoisture()
#light_in = pop.Light(0x5C)
#tphg_in = pop.Tphg(0x76)

#fan = pop.Fan()
#rgb = pop.RgbLedBar()
##window = pop.Window()
#textlcd = pop.Textlcd()

#fan.off()
##b1 = { "CO2":0, "SoilMoisture":0, "Light_0x5C":0, "Temperature":0, "Humidity":0}
#b = json.loads(b)
#print(b1)
'''
b1.co2val = pop.CO2().read()
b1.soilval = pop.SoilMoisture().read()
b1.light_inval = light_in.read()
b1.tempin, _, b1.humiin, _ = tphg_in.read()'''

#b = '{ "co2val":0, "soilval":0, "light_inval":0, "tempin":0, "humiin":0}'
#b1 = json.loads(b)
"""
b1['CO2'] = co2.read()
b1['SoilMoisture'] = soil.read()
b1['Light_0x5C'] = light_in.read()
b1['Temperature'], _, b1['Humidity'], _ = tphg_in.read()

print(b1)

a, b, c, d = tphg_in.read()
print(a, b, c, d)
"""


#from pop import Cooler 
#cooler= Cooler() 
#cooler.on() 
#time.sleep(3) 
'''
from pop import Heater 
heater = Heater()
heater.off()
'''
#fan.off()

#window.close()

'''
pump = pop.WaterPump()
pump.on()
time.sleep(8)
pump.off()
'''

'''
from pop import Switch
switchup = Switch('P8')
switchdown = Switch('P23')

def switchup_func(param):
    print(param.read())
    time.sleep_ms(1)
    
def switchdown_func(param):
    print(param.read())
    time.sleep_ms(1)

switchup.setCallback(func=switchup_func, param=switchup, type=switchup.BOTH)

switchdown.setCallback(func=switchdown_func, param=switchdown, type=switchdown.BOTH)

time.sleep(10)

switchup.setCallback(None)
switchdown.setCallback(None)
'''

co2 = pop.CO2()

for i in range (10): 
    print(int(co2.read()))
    time.sleep(1)


