'''
相较原代码改进：
1. 增加LED灯闪烁提示连接成功；
2. 增加异常处理，避免程序崩溃；
3. 增加超时时间，避免无限等待。
'''
# 此示例查找并连接到BLE温度传感器（例如在ble_temperature.py中的传感器）。

import bluetooth
import random
import struct
import time
import micropython
from ble_advertising import decode_services, decode_name
from micropython import const
from machine import Pin

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTS_READ_REQUEST = const(4)
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
_IRQ_PERIPHERAL_CONNECT = const(7)
_IRQ_PERIPHERAL_DISCONNECT = const(8)
_IRQ_GATTC_SERVICE_RESULT = const(9)
_IRQ_GATTC_SERVICE_DONE = const(10)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
_IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
_IRQ_GATTC_DESCRIPTOR_DONE = const(14)
_IRQ_GATTC_READ_RESULT = const(15)
_IRQ_GATTC_READ_DONE = const(16)
_IRQ_GATTC_WRITE_DONE = const(17)
_IRQ_GATTC_NOTIFY = const(18)
_IRQ_GATTC_INDICATE = const(19)

_ADV_IND = const(0x00)
_ADV_DIRECT_IND = const(0x01)
_ADV_SCAN_IND = const(0x02)
_ADV_NONCONN_IND = const(0x03)

# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
_TEMP_UUID = bluetooth.UUID(0x2A6E)
_TEMP_CHAR = (
    _TEMP_UUID,
    bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,
)
_ENV_SENSE_SERVICE = (
    _ENV_SENSE_UUID,
    (_TEMP_CHAR,),
)

# BLE温度传感器中心类，用于扫描、连接和读取BLE温度传感器的数据。
class BLETemperatureCentral:
    def __init__(self, ble):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        self._reset()
        self._led = Pin('LED', Pin.OUT)

    def _reset(self):
        # 已成功扫描的缓存名称和地址。
        self._name = None
        self._addr_type = None
        self._addr = None

        # 缓存值（如果有）
        self._value = None

        # 完成各种操作的回调。
        # 这些在被调用后重置为None。
        self._scan_callback = None
        self._conn_callback = None
        self._read_callback = None

        # 当设备通知新数据时的持久回调。
        self._notify_callback = None

        # 已连接设备。
        self._conn_handle = None
        self._start_handle = None
        self._end_handle = None
        self._value_handle = None

    def _irq(self, event, data):
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            if adv_type in (_ADV_IND, _ADV_DIRECT_IND):
                type_list = decode_services(adv_data)
                if _ENV_SENSE_UUID in type_list:
                    # 找到一个变压装置，记住它并停止扫描。
                    self._addr_type = addr_type
                    self._addr = bytes(addr)  # 注意：缓存地址缓冲区归调用者所有，因此需要复制它。
                    self._name = decode_name(adv_data) or "?"
                    self._ble.gap_scan(None)

        elif event == _IRQ_SCAN_DONE:
            if self._scan_callback:
                if self._addr:
                    # 在扫描过程中检测到设备（扫描已明确停止）。
                    self._scan_callback(self._addr_type, self._addr, self._name)
                    self._scan_callback = None
                else:
                    # 扫描超时。
                    self._scan_callback(None, None, None)

        elif event == _IRQ_PERIPHERAL_CONNECT:
            # 连接成功。
            conn_handle, addr_type, addr = data
            if addr_type == self._addr_type and addr == self._addr:
                self._conn_handle = conn_handle
                self._ble.gattc_discover_services(self._conn_handle)

        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            # 断开连接（由我们或远程端发起）。
            conn_handle, _, _ = data
            if conn_handle == self._conn_handle:
                # 如果它是由我们发起的，它已经被重置了。
                self._reset()

        elif event == _IRQ_GATTC_SERVICE_RESULT:
            # 已连接的设备返回了服务。
            conn_handle, start_handle, end_handle, uuid = data
            if conn_handle == self._conn_handle and uuid == _ENV_SENSE_UUID:
                self._start_handle, self._end_handle = start_handle, end_handle

        elif event == _IRQ_GATTC_SERVICE_DONE:
            # 服务查询完成。
            if self._start_handle and self._end_handle:
                self._ble.gattc_discover_characteristics(
                    self._conn_handle, self._start_handle, self._end_handle
                )
            else:
                print("找不到环境感应服务。")

        elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
            # 连接的设备返回了一个特征。
            conn_handle, def_handle, value_handle, properties, uuid = data
            if conn_handle == self._conn_handle and uuid == _TEMP_UUID:
                self._value_handle = value_handle

        elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
            # 特征查询完成。
            if self._value_handle:
                # 我们已完成连接和发现设备，启动连接回调。
                if self._conn_callback:
                    self._conn_callback()
            else:
                print("未能找到温度特性。")

        elif event == _IRQ_GATTC_READ_RESULT:
            # 读取已成功完成。
            conn_handle, value_handle, char_data = data
            if conn_handle == self._conn_handle and value_handle == self._value_handle:
                self._update_value(char_data)
                if self._read_callback:
                    self._read_callback(self._value)
                    self._read_callback = None

        elif event == _IRQ_GATTC_READ_DONE:
            # 读取已完成（无操作）。
            conn_handle, value_handle, status = data

        elif event == _IRQ_GATTC_NOTIFY:
            # ble_temperature.py演示会定期通知其值。
            conn_handle, value_handle, notify_data = data
            if conn_handle == self._conn_handle and value_handle == self._value_handle:
                self._update_value(notify_data)
                if self._notify_callback:
                    self._notify_callback(self._value)

    # 如果我们已成功连接并发现特征，则会返回true。
    def is_connected(self):
        return self._conn_handle is not None and self._value_handle is not None

    # 查找公布环境传感器服务的设备。
    def scan(self, callback=None):
        self._addr_type = None
        self._addr = None
        self._scan_callback = callback
        self._ble.gap_scan(2000, 30000, 30000)

    # 连接到指定的设备（否则使用扫描中的缓存地址）。
    def connect(self, addr_type=None, addr=None, callback=None):
        self._addr_type = addr_type or self._addr_type
        self._addr = addr or self._addr
        self._conn_callback = callback
        if self._addr_type is None or self._addr is None:
            return False
        self._ble.gap_connect(self._addr_type, self._addr)
        return True

    # 断开与当前设备的连接。
    def disconnect(self):
        if not self._conn_handle:
            return
        self._ble.gap_disconnect(self._conn_handle)
        self._reset()

    # 发出（异步）读取，将调用带有数据的回调。
    def read(self, callback):
        if not self.is_connected():
            return
        self._read_callback = callback
        try:
            self._ble.gattc_read(self._conn_handle, self._value_handle)
        except OSError as error:
            print(error)

    # 设置设备通知我们时调用的回调。
    def on_notify(self, callback):
        self._notify_callback = callback

    def _update_value(self, data):
        # 数据以摄氏度为单位，分辨率为0.01摄氏度。
        try:
            self._value = struct.unpack("<h", data)[0] / 100
        except OSError as error:
            print(error)

    def value(self):
        return self._value

# 闪烁LED灯的方法，用于指示状态。
def sleep_ms_flash_led(self, flash_count, delay_ms):
    self._led.off()
    while(delay_ms > 0):
        for i in range(flash_count):
            self._led.on()
            time.sleep_ms(100)
            self._led.off()
            time.sleep_ms(100)
            delay_ms -= 200
        time.sleep_ms(1000)
        delay_ms -= 1000

# 打印温度结果的方法。
def print_temp(result):
    print("读取温度: %.2f 摄氏度" % result)

# 演示方法，用于扫描、连接和读取温度传感器的数据。
def demo(ble, central):
    not_found = False

    def on_scan(addr_type, addr, name):
        if addr_type is not None:
            print("找到传感器: %s" % name)
            central.connect()
        else:
            nonlocal not_found
            not_found = True
            print("未找到传感器")

    central.scan(callback=on_scan)

    # 等待连接……
    while not central.is_connected():
        time.sleep_ms(100)
        if not_found:
            return

    print("已连接")

    # 明确问题如下
    while central.is_connected():
        central.read(callback=print_temp)
        sleep_ms_flash_led(central, 2, 2000)

    print("未连接")

# 主程序入口，初始化BLE并运行演示。
if __name__ == "__main__":
    ble = bluetooth.BLE()
    central = BLETemperatureCentral(ble)
    while(True):
        demo(ble, central)
        sleep_ms_flash_led(central, 1, 10000)