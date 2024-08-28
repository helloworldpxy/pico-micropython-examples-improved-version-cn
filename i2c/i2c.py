
from machine import Pin, I2C

def i2c_operations(i2c_bus, i2c_address):
    try:
        # 扫描I2C总线上的设备
        devices = i2c_bus.scan()
        print(f"在总线上发现的设备 {i2c_bus}: {devices}")

        # 向地址为i2c_address的设备写入数据b'123'
        i2c_bus.writeto(i2c_address, b'123')
        print(f"写入设备地址的数据 {i2c_address}")

        # 从地址为i2c_address的设备读取4字节数据
        data = i2c_bus.readfrom(i2c_address, 4)
        print(f"从设备地址读取的数据 {i2c_address}: {data}")

        # 向地址为i2c_address的设备的内存地址6写入数据b'456'
        i2c_bus.writeto_mem(i2c_address, 6, b'456')
        print(f"写入设备存储器地址6的数据 {i2c_address}")

        # 从地址为i2c_address的设备的内存地址6读取4字节数据
        mem_data = i2c_bus.readfrom_mem(i2c_address, 6, 4)
        print(f"从设备的存储器地址6读取的数据 {i2c_address}: {mem_data}")
    except OSError as e:
        print(f"I2C操作失败: {e}")

# 初始化I2C总线0，设置时钟引脚为Pin(9)，数据引脚为Pin(8)，频率为100000Hz
i2c0 = I2C(0, scl=Pin(9), sda=Pin(8), freq=100000)
i2c_operations(i2c0, 76)

# 初始化I2C总线1，设置时钟引脚为Pin(7)，数据引脚为Pin(6)，频率为100000Hz
i2c1 = I2C(1, scl=Pin(7), sda=Pin(6), freq=100000)
i2c_operations(i2c1, 76)
