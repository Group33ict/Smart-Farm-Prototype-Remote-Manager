import sys
import math
import time
import _thread
import struct

from machine import Pin, ADC, I2C

if 0x4B in I2C(1).scan():
    SmartFarmMode = 'option'
else:
    SmartFarmMode = 'normal'

class PopThread(object):
    __thread_id = 0
    __running = False

    __callback_objects = []

    lock = _thread.allocate_lock()

    @classmethod
    def _run(cls):
        try:
            while PopThread.__running:
                PopThread.lock.acquire()
                for obj in PopThread.__callback_objects:
                    obj.run()
                PopThread.lock.release()
        except KeyboardInterrupt:
            pass
        finally:
            PopThread.lock.acquire()
            PopThread.__running = False
            PopThread.lock.release()

    @classmethod
    def _start(cls):
        if not PopThread.__running:
            PopThread.lock.acquire()
            PopThread.__running = True
            _thread.start_new_thread(PopThread._run, [])
            PopThread.lock.release()

    @classmethod
    def _stop(cls):
        if PopThread.__running:
            PopThread.lock.acquire()
            PopThread.__running = False
            PopThread.lock.release()

    @property
    def func(self):
        return self._func

    @func.setter
    def func(self, func):
        self._func = func

    @property
    def param(self):
        return self._param

    @param.setter
    def param(self, param):
        self._param = param

    def __init__(self):
        self._func = None
        self._params = None

    def __del__(self):
        self._stop()

    def run(self):
        if self.func:
            self.func(self.param)

    def start(self):
        self._start()
        if self not in PopThread.__callback_objects:
            PopThread.lock.acquire()
            PopThread.__callback_objects.append(self)
            PopThread.lock.release()

    def stop(self):
        if self in PopThread.__callback_objects:
            PopThread.lock.acquire()
            PopThread.__callback_objects.remove(self)
            PopThread.lock.release()

    def setCallback(self, func, param=None):
        if self._func and func is None:
            self.stop()
        else:
            self.start()

        self.func = func
        self.param = param

##################################################################
class Input(object):
    LOW = Pin.IRQ_LOW_LEVEL
    HIGH = Pin.IRQ_HIGH_LEVEL

    RISING = Pin.IRQ_RISING
    FALLING = Pin.IRQ_FALLING

    BOTH =  Pin.IRQ_RISING | Pin.IRQ_FALLING

    def __init__(self, pin, activeHigh=True):
        self._pin = pin
        self._activeHigh = activeHigh

        self._pin = Pin(pin, mode=Pin.IN)

    def read(self):
        level = self._pin()
        return level if self._activeHigh else not level

    def setCallback(self, func=None, param=None, type=FALLING):
        return self._pin.callback(type, func, param)

##################################################################
class Out(object):
    def __init__(self, pin):
        self._pin = Pin(pin, mode=Pin.OUT)

    def __del__(self):
        self._pin(0)

    def __call__(self):
        return self._pin()

    def on(self):
        self._pin(1)

    def off(self):
        self._pin(0)
    
    def toggle(self):
        self._pin.toggle()

##################################################################
class Fan(Out):
    def __init__(self, pin='P3'):
        super().__init__(pin)

    def __del__(self):
        super().__del__()

##################################################################
class WaterPump(Out):
    def __init__(self, pin='P22'):
        super().__init__(pin)
    
    def __del__(self):
        super().__del__()

##################################################################
class Adc(PopThread):
    _adc = ADC()

    MODE_INCLUSIVE = 1
    MODE_EXCLUSIVE = 2
    MODE_FULL = 3

    TYPE_NORMAL = 1
    TYPE_AVERAGE = 2

    REF_VOLTAG = 3.3
    ADC_MAX = 4096 - 1
    ATTENUATION = ADC.ATTN_11DB

    def __init__(self, pin):
        super().__init__()

        self._type = None
        self._mode = None
        self._min = None
        self._max = None

        self._adc = type(self)._adc.channel(pin=pin, attn=type(self).ATTENUATION)
        self.sample = 1

    def __del__(self):
        super().__del__()
        self._adc.deinit()

    @property
    def sample(self):
        return self._sample

    @sample.setter
    def sample(self, sample):
        self._sample = sample

    def read(self):
        return self._adc.value()

    def readAverage(self):
        val = 0.0

        for _ in range(self._sample):
            val += math.pow(self.read(), 2)

        return int(math.sqrt(val / self._sample))

    def readVolt(self, ref=REF_VOLTAG, adc_max=ADC_MAX):
        return ref * (self.read() / adc_max)

    def readVoltAverage(self, ref=REF_VOLTAG, adc_max=ADC_MAX):
        return ref * (self.readAverage() / adc_max)

    def run(self):
        if self._type == Adc.TYPE_NORMAL:
            val = self.read()
        else:
            val = self.readAverage()

        if self._mode == Adc.MODE_INCLUSIVE:
            if val >= self._min and val <= self._max:
                self._func(val, self._param)
        elif self._mode == Adc.MODE_EXCLUSIVE:
            if val < self._min or val > self._max:
                self._func(val, self._param)
        else:
            self._func(val, self._param)

    def setCallback(self, func, param=None, type=TYPE_AVERAGE, mode=MODE_FULL, min=0, max=ADC_MAX):
        if self.func and func is None:
            self.stop()
        else:
            self.start()

        self.func = func
        self.param = param
        self._type = type
        self._mode = mode
        self._min = min
        self._max = max

##################################################################
class SoilMoisture(Adc):
    def __init__(self, pin='P15', dried=0, watered=4095):
        super().__init__(pin)

        self._dried = dried
        self._watered = watered

    @property
    def dried(self):
        return self._dried

    @dried.setter
    def dried(self, value):
        if value < 0:
            self._dried = 0
        elif value > 4095:
            self._dried = 4095
        else:
            self._dried = value

    @property
    def watered(self):
        return self._watered

    @watered.setter
    def watered(self, value):
        if value < 0:
            self._watered = 0
        elif value > 4095:
            self._watered = 4095
        else:
            self._watered = value

    def calcSoilMoisture(self, value):
        raingedValue = self._dried - value
        raingedScale = self._dried - self._watered
        return 100-(abs(raingedValue/raingedScale) * 100)

##################################################################
class I2c():
    _i2c = I2C()

    def __init__(self, addr):
        super().__init__()
        self._sAddr = addr

    def read(self):
        ret = type(self)._i2c.readfrom(self._sAddr, 1)
        return ret[0]
    
    def reads(self,num):
        ret = type(self)._i2c.readfrom(self._sAddr, num)
        return ret

    def readByte(self, reg):
        ret = type(self)._i2c.readfrom_mem(self._sAddr, reg, 1)
        return ret[0]

    def readWord(self, reg):
        temp_ret = type(self)._i2c.readfrom_mem(self._sAddr, reg, 2)
        ret = []
        for r in temp_ret:
            ret.append(r)

        return ret

    def readBlock(self, reg, length):
        temp_ret = type(self)._i2c.readfrom_mem(self._sAddr, reg, length)
        ret = []
        for r in temp_ret:
            ret.append(r)

        return ret

    def write(self, data):
        data = bytes([data])
        return type(self)._i2c.writeto(self._sAddr, data)

    def writeByte(self, reg, data):
        data = bytes([data])
        return type(self)._i2c.writeto_mem(self._sAddr, reg, data)

    def writeWord(self, reg, data):
        data = bytes(data)
        return type(self)._i2c.writeto_mem(self._sAddr, reg, data)

    def writeBlock(self, reg, data):
        data = bytes(data)
        return type(self)._i2c.writeto_mem(self._sAddr, reg, data)

##################################################################
class Light(PopThread):
    def __init__(self, addr):
        super().__init__()
        self.i2c = I2c(addr)
        self.init()

    def init(self):
        # init
        self.i2c.write(0x01)
        self.i2c.write(0x07)

        # set cont H-mode2
        #self.i2c.write(0x11)
        time.sleep(0.180)
    
    def read(self):
        self.i2c.write(0x21)
        time.sleep(0.180)
        
        data = self.i2c.reads(2)

        return round((data[0] << 8 | data[1]) / (1.2 * 2)) 
  
##################################################################
class PwmController():
    PCA9685_REG_MODE1 = 0x00
    PCA9685_REG_MODE2 = 0x01
    PCA9685_REG_PRESCALE = 0xFE
    PCA9685_REG_LED0_ON_L = 0x06
    PCA9685_REG_LED0_ON_H = 0x07
    PCA9685_REG_LED0_OFF_L = 0x08
    PCA9685_REG_LED0_OFF_H = 0x09
    PCA9685_REG_ALL_ON_L = 0xFA
    PCA9685_REG_ALL_ON_H = 0xFB
    PCA9685_REG_ALL_OFF_L = 0xFC
    PCA9685_REG_ALL_OFF_H = 0xFD

    RESTART = 1<<7
    AI = 1<<5
    SLEEP = 1<<4
    ALLCALL	= 1<<0
    OCH = 1<<3
    OUTDRV = 1<<2
    INVRT = 1<<4

    def __init__(self, addr=0x5e):
        self.i2c = I2c(addr)
        self.init()

        self._curChannel = -1

    def init(self):
        buf = self.AI | self.ALLCALL
        self.i2c.writeByte(self.PCA9685_REG_MODE1,buf)
        buf = self.OCH | self.OUTDRV
        self.i2c.writeByte(self.PCA9685_REG_MODE2,buf)
        time.sleep(0.05)
        recv = self.i2c.readByte(self.PCA9685_REG_MODE1)
        buf = recv & (~self.SLEEP)
        self.i2c.writeByte(self.PCA9685_REG_MODE1,buf)

    def setChannel(self, ch):
        self._curChannel = ch

    def setDuty(self, percent, scale):
        step = int(round(percent * (4096.0 / scale)))
        if step <= 0:
            on = 0
            off = 4096
        elif step >= 4095:
            on = 4096
            off = 0
        else:
            on = 0
            off = step

        on_l = on&0xff
        on_h = on>>8
        off_l = off&0xff
        off_h = off>>8
        if self._curChannel >= 0:
            self.i2c.writeByte(self.PCA9685_REG_LED0_ON_L+4*self._curChannel,on_l)
            self.i2c.writeByte(self.PCA9685_REG_LED0_ON_H+4*self._curChannel,on_h)
            self.i2c.writeByte(self.PCA9685_REG_LED0_OFF_L+4*self._curChannel,off_l)
            self.i2c.writeByte(self.PCA9685_REG_LED0_OFF_H+4*self._curChannel,off_h)
        elif self._curChannel == -1:
            self.i2c.writeByte(self.PCA9685_REG_ALL_ON_L,on_l)
            self.i2c.writeByte(self.PCA9685_REG_ALL_ON_H,on_h)
            self.i2c.writeByte(self.PCA9685_REG_ALL_OFF_L,off_l)
            self.i2c.writeByte(self.PCA9685_REG_ALL_OFF_H,off_h)

    def setFreq(self, freq):
        prescale = int(round(25000000/(4096*freq))-1)
        if prescale < 3:
            prescale = 3
        elif prescale > 255:
            prescale = 255

        recv = self.i2c.readByte(self.PCA9685_REG_MODE1)
        buf = (recv &(~self.SLEEP))|self.SLEEP
        self.i2c.writeByte(self.PCA9685_REG_MODE1,buf)
        self.i2c.writeByte(self.PCA9685_REG_PRESCALE,prescale)
        self.i2c.writeByte(self.PCA9685_REG_MODE1,recv)
        time.sleep(0.05)
        buf = recv | self.RESTART
        self.i2c.writeByte(self.PCA9685_REG_MODE1,buf)

    def setInvertPulse(self):
        recv = self.i2c.readByte(self.PCA9685_REG_MODE2)
        buf = recv | self.INVRT
        self.i2c.writeByte(self.PCA9685_REG_MODE2,buf)
        time.sleep(0.05)

##################################################################
class RgbLedBar():

    def __init__(self, addr=0x5E, channels=[2,1,0]):
        self.pwmcontroller = PwmController(addr)

        self.pwmcontroller.setFreq(60)
        self.channels = channels

        self._state = False
        self.setColor(0x000000)

    def setColor(self, color):
        rgb = [0] * 3

        try:
            iter(color)
            isIter = True
        except:
            isIter = False
        
        if not isIter:
            rgb[0] = color >> 16 & 0xFF
            rgb[1] = color >> 8  & 0xFF
            rgb[2] = color >> 0  & 0xFF
        elif len(color) == 3:
            rgb = color
        for i in range(3):
            rgb[i] = rgb[i] & 0xFF

        self.color = rgb

        if self._state:
            for channel, value in zip(self.channels, self.color):
                self.pwmcontroller.setChannel(channel)
                self.pwmcontroller.setDuty(value, 255)

    def read(self, *args):
        ret = []

        if len(args) > 0:
            for arg in args:
                if arg.lower() == "r":
                    ret.append(self.color[0])
                if arg.lower() == "g":
                    ret.append(self.color[1])
                if arg.lower() == "b":
                    ret.append(self.color[2])
        else:
            ret = self.color

        if len(ret) == 1: ret = ret[0]

        return ret

    def on(self):
        if not self._state:
            self._state = True
            for channel, value in zip(self.channels, self.color):
                self.pwmcontroller.setChannel(channel)
                self.pwmcontroller.setDuty(value, 255)

    def off(self):
        if self._state:
            self._state = False
            for channel, value in zip(self.channels, [0, 0, 0]):
                self.pwmcontroller.setChannel(channel)
                self.pwmcontroller.setDuty(value, 255)

##################################################################
class Window():

    def __init__(self, addr=0x40):
        self.pwmcontroller = PwmController(addr)
        self.power = Out('P21')
        self.power.on()

        self.pwmcontroller.setChannel(0)
        self.pwmcontroller.setFreq(50)
        self.pwmcontroller.setDuty(0, 4095)
        self.close()
    
    def open(self, step = None):
        self.power.on()
        if step == 1:
            self._angle(15)
        elif step == 2:
            self._angle(30)
        elif step == 3:
            self._angle(45)
        elif step == 4:
            self._angle(60)
        elif step == 5:
            self._angle(75)
        else:
            self._angle(90)

    def close(self):        
        self._angle(0)        
        self.power.off()        
    
    def _angle(self, angle):
        self.pwmcontroller.setDuty(int(497-(angle*2.38)), 4095)  
        time.sleep(1)      

##################################################################
class Tphg(PopThread):
    def __init__(self, addr):
        super().__init__()
        self.i2c = I2c(addr)

        self.i2c.writeByte(0xE0,0xB6)
        time.sleep(0.01)        
        
        # set calibration data
        calibration = self.i2c.readBlock(0x89, 25)
        calibration += self.i2c.readBlock(0xE1, 16)   
        
        calibration = list(struct.unpack("<hbBHhbBhhbbHhhBBBHbbbBbHhbb", bytes(calibration[1:39])))
        calibration = [float(i) for i in calibration]

        self._temp_calibration = [calibration[x] for x in [23, 0, 1]]
        self._pressure_calibration = [calibration[x] for x in [3, 4, 5, 7, 8, 10, 9, 12, 13, 14]]
        self._humidity_calibration = [calibration[x] for x in [17, 16, 18, 19, 20, 21, 22]]
        self._humidity_calibration[0] /= 16 # flip around H1 & H2
        self._humidity_calibration[1] *= 16
        self._humidity_calibration[1] += self._humidity_calibration[0] % 16
        self._sw_err = (self.i2c.readBlock(0x04,1)[0] & 0xF0) / 16

        self.i2c.writeByte(0x5A, 0x73)  #res_heat_0 (320 Celsius. ref: datasheet 3.3.5(21pg)) 
        self.i2c.writeByte(0x64, 0x65)  #gas_wait_0 (b01 100101 = 4 x 37 = 148ms))   

        self.i2c.writeByte(0x75, 0b010 << 2)
        self.i2c.writeByte(0x74, (0b100 << 5) | (0b011 << 2))  
        self.i2c.writeByte(0x72, 0b010)
        self.i2c.writeByte(0x71, 0x10)  
        
        self._t_fine = None
        self._adc_pres = None
        self._adc_hum = None
        self._adc_gas = None
        self._gas_range = None
        
    def _temperature(self):
        calc_temp = ((self._t_fine * 5) + 128) / 256
        return calc_temp / 100

    def _pressure(self):
        var1 = (self._t_fine / 2) - 64000
        var2 = ((var1 / 4) * (var1 / 4)) / 2048
        var2 = (var2 * self._pressure_calibration[5]) / 4
        var2 = var2 + (var1 * self._pressure_calibration[4] * 2)
        var2 = (var2 / 4) + (self._pressure_calibration[3] * 65536)
        var1 = ((((var1 / 4) * (var1 / 4)) / 8192) * (self._pressure_calibration[2] * 32) / 8) + ((self._pressure_calibration[1] * var1) / 2)
        var1 = var1 / 262144
        var1 = ((32768 + var1) * self._pressure_calibration[0]) / 32768
        calc_pres = 1048576 - self._adc_pres
        calc_pres = (calc_pres - (var2 / 4096)) * 3125
        calc_pres = (calc_pres / var1) * 2
        var1 = (self._pressure_calibration[8] * (((calc_pres / 8) * (calc_pres / 8)) / 8192)) / 4096
        var2 = ((calc_pres / 4) * self._pressure_calibration[7]) / 8192
        var3 = (((calc_pres / 256) ** 3) * self._pressure_calibration[9]) / 131072
        calc_pres += (var1 + var2 + var3 + (self._pressure_calibration[6] * 128)) / 16
        return calc_pres / 100

    def _humidity(self):
        temp_scaled = ((self._t_fine * 5) + 128) / 256
        var1 = (self._adc_hum - (self._humidity_calibration[0] * 16)) - ((temp_scaled * self._humidity_calibration[2]) / 200)
        var2 = (self._humidity_calibration[1] * (((temp_scaled * self._humidity_calibration[3]) / 100) + 
                (((temp_scaled * ((temp_scaled * self._humidity_calibration[4]) / 100)) / 64) / 100) + 16384)) / 1024
        var3 = var1 * var2
        var4 = self._humidity_calibration[5] * 128
        var4 = (var4 + ((temp_scaled * self._humidity_calibration[6]) / 100)) / 16
        var5 = ((var3 / 16384) * (var3 / 16384)) / 1024
        var6 = (var4 * var5) / 2
        calc_hum = (((var3 + var6) / 1024) * 1000) / 4096
        calc_hum /= 1000 
        return 100 if calc_hum > 100 else 0 if calc_hum < 0 else calc_hum

    def _gas(self):
        LOOKUP_TABLE_1 = (2147483647.0, 2147483647.0, 2147483647.0, 2147483647.0, 2147483647.0, 2126008810.0, 2147483647.0, 
            2130303777.0, 2147483647.0, 2147483647.0, 2143188679.0, 2136746228.0, 2147483647.0, 2126008810.0, 2147483647.0, 2147483647.0)

        LOOKUP_TABLE_2 = (4096000000.0, 2048000000.0, 1024000000.0, 512000000.0, 255744255.0, 127110228.0,
            64000000.0, 32258064.0, 16016016.0, 8000000.0, 4000000.0, 2000000.0, 1000000.0, 500000.0, 250000.0, 125000.0)

        var1 = ((1340 + (5 * self._sw_err)) * (LOOKUP_TABLE_1[self._gas_range])) / 65536
        var2 = ((self._adc_gas * 32768) - 16777216) + var1
        var3 = (LOOKUP_TABLE_2[self._gas_range] * var1) / 512
        calc_gas_res = (var3 + (var2 / 2)) / var2
        return int(calc_gas_res)
    
    def _perform_reading(self):        
        ctrl = self.i2c.readBlock(0x74,1)[0] #ctrl_meas
        ctrl = (ctrl & 0xFC) | 0x01  # ctrl_meas, mode<1:0>
        self.i2c.writeByte(0x74, ctrl) #ctrl_temp
                
        new_data = False
        while not new_data:
            data = self.i2c.readBlock(0x1D, 15) #meas_status_0
            new_data = data[0] & 0x80 != 0
            time.sleep(0.005)
        
        self._adc_pres = ((data[2] * 4096) + (data[3] * 16) + (data[4] / 16))
        _adc_temp = ((data[5] * 4096) + (data[6] * 16) + (data[7] / 16))
        self._adc_hum = struct.unpack(">H", bytes(data[8:10]))[0]
        self._adc_gas = int(struct.unpack(">H", bytes(data[13:15]))[0] / 64)
        self._gas_range = data[14] & 0x0F

        var1 = (_adc_temp / 8) - (self._temp_calibration[0] * 2)
        var2 = (var1 * self._temp_calibration[1]) / 2048
        var3 = ((var1 / 2) * (var1 / 2)) / 4096
        var3 = (var3 * self._temp_calibration[2] * 16) / 16384
        self._t_fine = int(var2 + var3)
           
    def read(self):
        self._perform_reading()
        return round(self._temperature(), 2), round(self._pressure(), 2), round(self._humidity(), 2), self._gas() 

    def sealevel(self, altitude):
        self._perform_reading()
        press = self._pressure()
        return press / pow((1-altitude/44330), 5.255), press
    
    def altitude(self, sealevel): 
        self._perform_reading()
        press = self._pressure()
        return 44330 * (1.0-pow(press/sealevel,0.1903)), press        

##################################################################   
class Switch(Input):  
    def __init__(self, pin):
        super().__init__(pin, activeHigh=True)
        
    def __del__(self):
        super().__del__()         
      
################################################################c##
class Textlcd():
    # LCD_WIDTH = 16		
    LCD_WIDTH = 20
    LCD_CMD = 0x00
    LCD_CHR = 0x01
    LCD_LINE1 = 0x00
    LCD_LINE2 = 0x40
    LCD_LINE3 = 0x14
    LCD_LINE4 = 0x54

    LCD_CLEAR = 0x01
    LCD_HOME = 0x02
    LCD_DISPLAY = 0x04
    LCD_CURSOR = 0x02
    LCD_BLINKING = 0x01
    LCD_DISPLAY_SHIFT_R = 0x1C
    LCD_DISPLAY_SHIFT_L = 0x18
    LCD_CURSOR_SHIFT_R = 0x14
    LCD_CURSOR_SHIFT_L = 0x10
    LCD_ENTRY_MODE_SET = 0x06
    LCD_BACKLIGHT = 0x08
    ENABLE = 0x04
    E_PULSE = 500
    E_DELAY = 500

    def __init__(self, addr=0x27):
        self.i2c = I2c(addr)
        self._x = 0
        self._y = 0
        
        self.command(0x33)
        self.command(0x32)

        self.command(0x28)
        self.command(0x0F)
        self.command(0x06)
        self.command(0x01)
        time.sleep(0.1)

        self.display_status = 0x0F

        self.returnHome()

    def __del__(self):
        self.display_status = 0x00
        self.clear()

    def _byte(self, byte, mode):
        high_bit = mode | (byte & 0xF0) | self.LCD_BACKLIGHT
        low_bit = mode | ((byte << 4) & 0xF0) | self.LCD_BACKLIGHT
        self._enable(high_bit)
        self._enable(low_bit)

    def _enable(self, byte):
        time.sleep_us(200)
        self.i2c.write(byte | self.ENABLE)
        time.sleep_us(200)
        self.i2c.write(byte & ~self.ENABLE)
        
    def command(self, command):
        self._byte(command,self.LCD_CMD)

    def clear(self):
        self.command(self.LCD_CLEAR)

    def returnHome(self):
        self._x = 0
        self._y = 0
        self.command(self.LCD_HOME)

    def displayOn(self):
        self.display_status = self.display_status | self.LCD_DISPLAY
        self.command(self.display_status)

    def displayOff(self):
        self.display_status = self.display_status & ~self.LCD_DISPLAY
        self.command(self.display_status)

    def displayShiftR(self):
        self.command(self.LCD_DISPLAY_SHIFT_R)

    def displayShiftL(self):
        self.command(self.LCD_DISPLAY_SHIFT_L)

    def cursorOn(self, blinking):
        self.display_status = self.display_status | self.LCD_CURSOR
        if blinking == 1:
            self.display_status = self.display_status | self.LCD_BLINKING
        else:
            self.display_status = self.display_status & ~self.LCD_BLINKING

        self.command(self.display_status)

    def cursorOff(self):
        self.display_status = self.display_status & ~self.LCD_CURSOR
        self.display_status = self.display_status & ~self.LCD_BLINKING
        self.command(self.display_status)

    def cursorShiftR(self):
        self.command(self.LCD_CURSOR_SHIFT_R)

    def cursorShiftL(self):
        self.command(self.LCD_CURSOR_SHIFT_L)

    def entryModeSet(self):
        self.command(self.LCD_ENTRY_MODE_SET)

    def setCursor(self, x, y):
        self._x = x
        self._y = y
        if x > 19:
            x = 19
        if y == 1:
            y = self.LCD_LINE2
        elif y == 2:
            y = self.LCD_LINE3
        elif y == 3:
            y = self.LCD_LINE4
        self.command(0x80 | (x+y))

    def data(self, data):
        self._byte(data, self.LCD_CHR)

    def print(self, string, x=0 , y=0, line=-1):
        self._x = x
        self._y = y
        if line >= 0:
            self._x = 0
            self._y = line
        self.setCursor(self._x, self._y)
        for c in string:
            if self._x == 20:
                self._y = self._y + 1
                if self._y > 3:
                    self.setCursor(19, 3)
                    break
                self.setCursor(0, self._y)
            self._x = self._x + 1
            self.data(ord(c))
        
    def x(self):
        return self._x
    def y(self):
        return self._y


if 0x62 in I2C(0).scan():
    
    class CO2(PopThread):    
        CO2_address = 0x62
        co2_val=0
        def __init__(self, addr=CO2_address): 
            super().__init__()
            self.i2c = I2C(0)

            self._status = False
            self.stopPeriodicMeasurement()
            
            _thread.start_new_thread(self.thread_read,())
            time.sleep(6.5)
        def __del__(self):
            self.stopPeriodicMeasurement()
            self.setCallback(None)
            
        def stopPeriodicMeasurement(self):
            self.i2c.writeto(0x62, bytes([0x3F,0x86])) #stop
            self._status = False
            time.sleep(1)
        
        def getSerialNumber(self):        
            if self._status != False:
                self.stopPeriodicMeasurement()
            
            self.i2c.writeto(0x62, bytes([0x36,0x82])) #get serialnum
            data = self.i2c.readfrom(0x62,9)  
            serial0 = ((int(data[0])<<8) + int(data[1]))
            serial1 = ((int(data[3])<<8) + int(data[4]))
            serial2 = ((int(data[6])<<8) + int(data[7]))        
            return [hex(serial0), hex(serial1), hex(serial2)]
        
        def startPeriodicMeasurement(self):
            self.i2c.writeto(0x62, bytes([0x21,0xB1])) #start
            self._status = True
            time.sleep(5)
        
        def thread_read(self):
            while True:        
                if self._status != True:
                    self.startPeriodicMeasurement()
                else:
                    time.sleep(5)           

                self.i2c.writeto(0x62, bytes([0xEC,0x05])) #read co2, temp, humi        
                data = self.i2c.readfrom(0x62,9)
                self.stopPeriodicMeasurement()

                self.co2_val = ((int(data[0])<<8) + int(data[1]))
            
        def read(self):
            return self.co2_val
    
else:   
    class CO2(PopThread):
    
        CO2_address = 0x31
        
        def __init__(self, addr=CO2_address): 
            super().__init__()
            self.i2c = I2c(addr)
        
        def read(self):
            value = self.i2c.readBlock(0x52, 7)      
            return ((value[1] <<8) | (value[2]))

class WaterLevel(Input):  
    def __init__(self):
        super().__init__('P18', activeHigh=True)
        
    def __del__(self):
        super().__del__()    
        
class pcf8574():
    def __init__(self, ch):
        self.i2c = I2c(0x25)
        self.on_ch = 0xFF - (0x01<<ch)
        self.off_ch = 0x01<<ch
        self.state = False
    
    def on(self):
        data = (self.i2c.read()) & (self.on_ch)
        self.i2c.write(data)
        self.state = True
        time.sleep(0.05)

    def off(self):
        data = (self.i2c.read()) | (self.off_ch)
        self.i2c.write(data)  
        self.state = False
        time.sleep(0.05)
    
    def toggle(self):
        if self.state is True:
            self.off()
        else:
            self.on()  

class pHPump():
    def __init__(self):
        self.up_pump = pcf8574(ch=0)
        self.down_pump = pcf8574(ch=1)
        
    def up(self):
        self.up_pump.on()
        self.down_pump.off()
    
    def down(self):
        self.up_pump.off()
        self.down_pump.on()
    
    def stop(self):
        self.up_pump.off()
        self.down_pump.off()
        
class NutrientPump():
    def __init__(self):
        self.nutrient_Pump = pcf8574(ch=2)
    
    def on(self):
        self.nutrient_Pump.on()

    def off(self):
        self.nutrient_Pump.off()
    
    def toggle(self):
        self.nutrient_Pump.toggle()

class NutrientSolutionPump():
    def __init__(self):
        self.nutrient_solution_Pump = pcf8574(ch=3)
    
    def on(self):
        self.nutrient_solution_Pump.on()

    def off(self):
        self.nutrient_solution_Pump.off()
    
    def toggle(self):
        self.nutrient_solution_Pump.toggle()

class CO2Pump(pcf8574):
    def __init__(self):
        self.co2_Pump = pcf8574(ch=4)
    
    def on(self):
        self.co2_Pump.on()

    def off(self):
        self.co2_Pump.off()
    
    def toggle(self):
        self.co2_Pump.toggle()

class Cooler(pcf8574):
    def __init__(self):
        self.cooler = pcf8574(ch=6)
    
    def on(self):
        self.cooler.on()

    def off(self):
        self.cooler.off()
    
    def toggle(self):
        self.cooler.toggle()

class Heater(pcf8574):
    def __init__(self):
        self.heater = pcf8574(ch=7)
    
    def on(self):
        self.heater.on()

    def off(self):
        self.heater.off()
    
    def toggle(self):
        self.heater.toggle()

class ADS7828():
    def __init__(self, ch):
        self.i2c = I2c(0x4B)
        self.channels = [0x00, 0x40, 0x10, 0x50, 0x20, 0x60, 0x30, 0x70]
        self.ch = (self.channels[ch])| 0x80
    
    def read(self):
        self.i2c.write(self.ch)
        data = self.i2c.reads(2)
        return round(data[0] << 8 | data[1])
    
    def readVoltage(self):
        self.i2c.write(self.ch)
        data = self.i2c.reads(2)
        data = round(data[0] << 8 | data[1])        
        return data*5/4095

class NutrientLevel(PopThread):
    def __init__(self):
        super().__init__()
        self.asd7828 = ADS7828(2)
        
    def read(self):
        data = self.asd7828.readVoltage()
        
        if data>2:
            data=1
        else:
            data=0      
        
        return data

class TDS(PopThread):
    def __init__(self):
        super().__init__()
        self.asd7828 = ADS7828(0)
        self.tphg = Tphg(0x76)
    def readPPM(self):
        data = [0,0,0,0,0,0,0,0,0,0]
        for i in range(10):
            data[i] = self.asd7828.readVoltage()
            time.sleep(0.01)

        for i in range(9):
            for j in range(10):
                if data[i] > data[j]:
                    temp = data[i]
                    data[i] = data[j]
                    data[j] = temp
        
        averageVoltage = (data[5] + data[4]) / 2        
        temperature = self.tphg.read()[0]
        compensationCoefficient=1.0+0.02*(temperature-25.0)
        compensationVolatge=averageVoltage/compensationCoefficient
        tdsValue=(133.42*compensationVolatge*compensationVolatge*compensationVolatge - 255.86*compensationVolatge*compensationVolatge + 857.39*compensationVolatge)*0.5
        return tdsValue
    
    def readEC(self):
        return self.readPPM()/640

class pH(PopThread):
    def __init__(self):
        super().__init__()
        self.asd7828 = ADS7828(1)
        
    def readVoltage(self):
        return self.asd7828.readVoltage()
    
    def read(self):
        data = [0,0,0,0,0,0,0,0,0,0]
        for i in range(10):
            data[i] = self.asd7828.readVoltage()
            time.sleep(0.01)

        for i in range(9):
            for j in range(10):
                if data[i] > data[j]:
                    temp = data[i]
                    data[i] = data[j]
                    data[j] = temp
        
        avgValue = 0
        for i in range(2,8):
            avgValue = avgValue + data[i]

        #return -5.7*(avgValue / 6)+21.34   
        return ((avgValue / 6)-1)*10