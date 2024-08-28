'''
相较原代码改进：
1、在计算 r 和 b 时，使用位运算 & 0xFF 来确保值在有效范围内；
2、增加错误处理机制，确保程序在遇到错误时不会崩溃。
'''
# 使用PIO驱动一组WS2812 LED的示例。

import array, time
from machine import Pin
import rp2

# 配置WS2812 LED的数量。
NUM_LEDS = 8

# 定义用于驱动WS2812 LED的PIO程序
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
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

try:
    # 创建状态机，使用ws2812程序，输出在Pin(22)
    sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(22))

    # 启动状态机，它将等待其FIFO上的数据
    sm.active(1)

    # 通过LED RGB值的数组显示LED上的图案
    ar = array.array("I", [0 for _ in range(NUM_LEDS)])

    # 循环颜色
    for i in range(4 * NUM_LEDS):
        for j in range(NUM_LEDS):
            r = (j * 100 // (NUM_LEDS - 1)) & 0xFF
            b = (100 - j * 100 // (NUM_LEDS - 1)) & 0xFF
            if j != i % NUM_LEDS:
                r >>= 3
                b >>= 3
            ar[j] = (r << 16) | b
        sm.put(ar, 8)
        time.sleep_ms(50)

    # 淡出
    for _ in range(24):
        for j in range(NUM_LEDS):
            ar[j] >>= 1
        sm.put(ar, 8)
        time.sleep_ms(50)

except Exception as e:
    print(f"发生错误: {e}")