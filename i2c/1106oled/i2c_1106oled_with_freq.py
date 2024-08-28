'''
相较原代码改进：
1、增加I2C的频率参数，默认频率为100kHz，可以根据实际情况调整。
2、调整代码逻辑，提升容错能力。
'''
# 在I2C驱动的ssd1306 OLED显示器上显示图像和文本
from machine import Pin, I2C
from sh1106 import SH1106_I2C
import framebuf

WIDTH  = 128                                                   # oled显示宽度
HEIGHT = 32                                                    # oled显示高度

try:
    # 使用引脚GP8和GP9（默认I2C0引脚）启动I2C
    i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=200000)
    # 显示设备地址
    print("I2C地址: " + hex(i2c.scan()[0]).upper())
    # 显示I2C配置
    print("I2C配置: " + str(i2c))

    # 启动oled显示器
    oled = SH1106_I2C(WIDTH, HEIGHT, i2c)

    # Raspberry Pi徽标为32x32字节阵列
    buffer = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|?\x00\x01\x86@\x80\x01\x01\x80\x80\x01\x11\x88\x80\x01\x05\xa0\x80\x00\x83\xc1\x00\x00C\xe3\x00\x00~\xfc\x00\x00L'\x00\x00\x9c\x11\x00\x00\xbf\xfd\x00\x00\xe1\x87\x00\x01\xc1\x83\x80\x02A\x82@\x02A\x82@\x02\xc1\xc2@\x02\xf6>\xc0\x01\xfc=\x80\x01\x18\x18\x80\x01\x88\x10\x80\x00\x8c!\x00\x00\x87\xf1\x00\x00\x7f\xf6\x00\x008\x1c\x00\x00\x0c \x00\x00\x03\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")

    # 将Raspberry Pi徽标加载到帧缓冲区中（图像为32x32）
    fb = framebuf.FrameBuffer(buffer, 32, 32, framebuf.MONO_HLSB)

    # 清除oled显示屏上的垃圾。
    oled.fill(0)

    # 将图像从帧缓冲区闪烁到oled显示器
    oled.blit(fb, 96, 0)

    # 添加一些文本
    oled.text("Raspberry Pi", 5, 5)
    oled.text("Pico", 5, 15)

    # 最后更新oled显示器，以便显示图像和文本
    oled.show()
except Exception as e:
    # 出现错误时打印错误信息
    print(f"出现错误: {e}")