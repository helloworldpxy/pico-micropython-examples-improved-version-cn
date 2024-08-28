'''
相较原代码：
1、优化注释和代码逻辑；
2、简化代码，去除冗余代码。
'''
#此示例演示了一个简单的温度传感器外围设备。
#传感器的本地值如果被更新，它将通知
#每10秒连接一个中枢。

import bluetooth
import random
import struct
import time
import machine
import ubinascii
from ble_advertising import advertising_payload
from micropython import const
from machine import Pin

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_INDICATE_DONE = const(20)

_FLAG_READ = const(0x0002)
_FLAG_NOTIFY = const(0x0010)
_FLAG_INDICATE = const(0x0020)

# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
_TEMP_CHAR = (
    bluetooth.UUID(0x2A6E),
    _FLAG_READ | _FLAG_NOTIFY | _FLAG_INDICATE,
)
_ENV_SENSE_SERVICE = (
    _ENV_SENSE_UUID,
    (_TEMP_CHAR,),
)

# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)

# 定义一个BLE温度传感器类
class BLETemperature:
    # 初始化方法，设置BLE设备和温度传感器
    def __init__(self, ble, name=""):
        self._sensor_temp = machine.ADC(4)
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle,),) = self._ble.gatts_register_services((_ENV_SENSE_SERVICE,))
        self._connections = set()
        if len(name) == 0:
            name = 'Pico %s' % ubinascii.hexlify(self._ble.config('mac')[1],':').decode().upper()
        print('传感器名称 %s' % name)
        self._payload = advertising_payload(
            name=name, services=[_ENV_SENSE_UUID]
        )
        self._advertise()

    # BLE事件处理方法
    def _irq(self, event, data):
        # 跟踪连接，以便我们发送通知。
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            # 再次开始广告以允许新的连接。
            self._advertise()
        elif event == _IRQ_GATTS_INDICATE_DONE:
            conn_handle, value_handle, status = data

    # 更新温度值并通知或指示连接的中枢
    def update_temperature(self, notify=False, indicate=False):
        # 写下本地值，准备中枢读取。
        temp_deg_c = self._get_temp()
        print("写入温度 %.2f 摄氏度" % temp_deg_c);
        self._ble.gatts_write(self._handle, struct.pack("<h", int(temp_deg_c * 100)))
        if notify or indicate:
            for conn_handle in self._connections:
                if notify:
                    # 通知连接的中枢。
                    self._ble.gatts_notify(conn_handle, self._handle)
                if indicate:
                    # 指示连接的中枢。
                    self._ble.gatts_indicate(conn_handle, self._handle)

    # 开始广告
    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    # 获取温度值
    def _get_temp(self):
        conversion_factor = 3.3 / (65535)
        reading = self._sensor_temp.read_u16() * conversion_factor

        #温度传感器测量连接到第ADC通道5的偏置双极二极管的Vbe电压
        #通常，在27摄氏度时，Vbe=0.706V，斜率为每度-1.721mV（0.001721）。
        return 27 - (reading - 0.706) / 0.001721

# 演示函数，初始化BLE和温度传感器，并定期更新温度值
def demo():
    ble = bluetooth.BLE()
    temp = BLETemperature(ble)
    counter = 0
    led = Pin('LED', Pin.OUT)
    while True:
        if counter % 10 == 0:
            temp.update_temperature(notify=True, indicate=False)
        led.toggle()
        time.sleep_ms(1000)
        counter += 1

if __name__ == "__main__":
    demo()