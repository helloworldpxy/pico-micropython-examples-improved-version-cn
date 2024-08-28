'''
相较原代码改进：
1、使用extend方法替代+=，减少中间变量的创建；
2、简化_append函数的实现，去除冗余代码；
3、在decode_field和demo函数中增加了异常处理。
'''

# 帮助生成BLE广告有效载荷。

from micropython import const
import struct
import bluetooth

# 广告有效载荷是以下形式的重复数据包：
# 1字节数据长度（N+1）
# 1字节（见下面的常量）
# N字节特点类型的数据

_ADV_TYPE_FLAGS = const(0x01)
_ADV_TYPE_NAME = const(0x09)
_ADV_TYPE_UUID16_COMPLETE = const(0x03)
_ADV_TYPE_UUID32_COMPLETE = const(0x05)
_ADV_TYPE_UUID128_COMPLETE = const(0x07)
_ADV_TYPE_UUID16_MORE = const(0x02)
_ADV_TYPE_UUID32_MORE = const(0x04)
_ADV_TYPE_UUID128_MORE = const(0x06)
_ADV_TYPE_APPEARANCE = const(0x19)

# 生成要传递给gap_advertise的有效载荷（adv_data=…）。
def advertising_payload(limited_disc=False, br_edr=False, name=None, services=None, appearance=0):
    payload = bytearray()

    def _append(adv_type, value):
        payload.extend(struct.pack("BB", len(value) + 1, adv_type))
        payload.extend(value)

    _append(
        _ADV_TYPE_FLAGS,
        struct.pack("B", (0x01 if limited_disc else 0x02) + (0x18 if br_edr else 0x04)),
    )

    if name:
        _append(_ADV_TYPE_NAME, name.encode('utf-8'))

    if services:
        for uuid in services:
            b = uuid.to_bytes(16, 'big')
            if len(b) == 2:
                _append(_ADV_TYPE_UUID16_COMPLETE, b)
            elif len(b) == 4:
                _append(_ADV_TYPE_UUID32_COMPLETE, b)
            elif len(b) == 16:
                _append(_ADV_TYPE_UUID128_COMPLETE, b)

    if appearance:
        _append(_ADV_TYPE_APPEARANCE, struct.pack("<h", appearance))

    return payload

# 从有效载荷中解码特定类型的字段。
def decode_field(payload, adv_type):
    result = []
    i = 0
    try:
        while i + 1 < len(payload):
            if payload[i + 1] == adv_type:
                result.append(payload[i + 2: i + payload[i] + 1])
            i += 1 + payload[i]
    except IndexError:
        print("解码字段时出错：索引超出范围")
    return result

# 从有效载荷中解码设备名称。
def decode_name(payload):
    n = decode_field(payload, _ADV_TYPE_NAME)
    return n[0].decode('utf-8') if n else ""

# 从有效载荷中解码服务UUID。
def decode_services(payload):
    services = []
    for u in decode_field(payload, _ADV_TYPE_UUID16_COMPLETE):
        services.append(bluetooth.UUID(struct.unpack("<h", u)[0]))
    for u in decode_field(payload, _ADV_TYPE_UUID32_COMPLETE):
        services.append(bluetooth.UUID(struct.unpack("<d", u)[0]))
    for u in decode_field(payload, _ADV_TYPE_UUID128_COMPLETE):
        services.append(bluetooth.UUID(u))
    return services

# 演示如何使用上述函数生成和解码BLE广告有效载荷。
def demo():
    try:
        payload = advertising_payload(
            name="micropython",
            services=[bluetooth.UUID(0x181A), bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")],
        )
        print(payload)
        print(decode_name(payload))
        print(decode_services(payload))
    except Exception as e:
        print(f"演示失败: {e}")

# 如果此脚本作为主程序运行，则执行演示函数。
if __name__ == "__main__":
    demo()