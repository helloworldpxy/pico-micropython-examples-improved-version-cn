'''
相较原代码改进：
1、在创建StateMachine时增加了错误处理机制，以捕获并报告初始化失败的情况；
2、在pixels_fill函数中，直接计算颜色值并赋值给数组，减少了重复计算；
3、在pixels_show函数中，直接使用enumerate来遍历数组，减少了不必要的索引计算。
'''
# 使用PIO驱动一组WS2812 LED的示例。

import array, time
from machine import Pin
import rp2

# 配置WS2812 LED的数量。
NUM_LEDS = 16
PIN_NUM = 6
brightness = 0.2

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    # 定义PIO程序，用于控制WS2812 LED
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()

# 使用ws2812程序创建StateMachine，在引脚上输出
try:
    sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))
    sm.active(1)
except Exception as e:
    print(f"初始化StateMachine失败: {e}")
    raise

# 通过LED RGB值阵列在LED上显示图案。
ar = array.array("I", [0 for _ in range(NUM_LEDS)])

def pixels_show():
    # 显示当前LED阵列的颜色
    dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
    for i, c in enumerate(ar):
        r = int(((c >> 8) & 0xFF) * brightness)
        g = int(((c >> 16) & 0xFF) * brightness)
        b = int((c & 0xFF) * brightness)
        dimmer_ar[i] = (g << 16) + (r << 8) + b
    sm.put(dimmer_ar, 8)
    time.sleep_ms(10)

def pixels_set(i, color):
    # 设置单个LED的颜色
    ar[i] = (color[1] << 16) + (color[0] << 8) + color[2]

def pixels_fill(color):
    # 填充所有LED为同一颜色
    color_value = (color[1] << 16) + (color[0] << 8) + color[2]
    for i in range(len(ar)):
        ar[i] = color_value

def color_chase(color, wait):
    # 逐个点亮LED，形成颜色追逐效果
    for i in range(NUM_LEDS):
        pixels_set(i, color)
        time.sleep(wait)
        pixels_show()
    time.sleep(0.2)

def wheel(pos):
    # 根据位置生成RGB颜色
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

def rainbow_cycle(wait):
    # 生成彩虹循环效果
    for j in range(255):
        for i in range(NUM_LEDS):
            rc_index = (i * 256 // NUM_LEDS) + j
            pixels_set(i, wheel(rc_index & 255))
        pixels_show()
        time.sleep(wait)

BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
COLORS = (BLACK, RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE)

print("fills")
for color in COLORS:
    pixels_fill(color)
    pixels_show()
    time.sleep(0.2)

print("chases")
for color in COLORS:
    color_chase(color, 0.01)

print("rainbow")
rainbow_cycle(0)