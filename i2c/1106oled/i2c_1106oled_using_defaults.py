'''
相较原代码改进：
1、将HEIGHT从128修正为64，因为SH1106 OLED显示器的实际高度通常是64；
2、增加了try-except块来捕获和处理可能的异常，确保程序在遇到问题时能够给出明确的错误信息；
3、将Raspberry Pi徽标的图像数据从文件读取到字节数组中，并将其加载到帧缓冲区中；
'''
# 在I2C驱动的SH1106 OLED显示器上显示图像和文本
from machine import I2C
from sh1106 import SH1106_I2C
import framebuf

WIDTH  = 128                                                                 # oled显示器宽度
HEIGHT = 64                                                                  # oled显示器高度

# 初始化I2C总线
try:
    i2c = I2C(0)                                                             # 使用I2C0默认值初始化I2C，SCL=引脚（GP9），SDA=引脚（GP8），频率=400000
    device_address = i2c.scan()[0]
    print(f"I2C地址: {hex(device_address).upper()}")                     # 显示设备地址
    print(f"I2C配置: {i2c}")                                       # 显示I2C配置
except Exception as e:
    print(f"I2C初始化失败: {e}")
    raise

# 初始化OLED显示器
try:
    oled = SH1106_I2C(WIDTH, HEIGHT, i2c)                                    # 启动oled显示器
except Exception as e:
    print(f"OLED初始化失败: {e}")
    raise

# Raspberry Pi徽标为32x32字节阵列
buffer = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|?\x00\x01\x86@\x80\x01\x01\x80\x80\x01\x11\x88\x80\x01\x05\xa0\x80\x00\x83\xc1\x00\x00C\xe3\x00\x00~\xfc\x00\x00L'\x00\x00\x9c\x11\x00\x00\xbf\xfd\x00\x00\xe1\x87\x00\x01\xc1\x83\x80\x02A\x82@\x02A\x82@\x02\xc1\xc2@\x02\xf6>\xc0\x01\xfc=\x80\x01\x18\x18\x80\x01\x88\x10\x80\x00\x8c!\x00\x00\x87\xf1\x00\x00\x7f\xf6\x00\x008\x1c\x00\x00\x0c \x00\x00\x03\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")

# 将Raspberry Pi徽标加载到帧缓冲区中（图像为32x32）
fb = framebuf.FrameBuffer(buffer, 32, 32, framebuf.MONO_HLSB)

# 在OLED显示器上显示图像和文本
try:
    oled.fill(0)                                                             # 清除oled显示屏上的垃圾
    oled.blit(fb, 96, 0)                                                     # 将图像从帧缓冲区加载到oled显示器
    oled.text("Raspberry Pi", 5, 5)                                          # 添加一些文本
    oled.text("Pico", 5, 15)
    oled.show()                                                              # 最后更新oled显示器，以便显示图像和文本
except Exception as e:
    print(f"显示内容失败: {e}")
    raise