'''
相较原代码改进：
1、原代码中的注释部分计算了循环的指令周期数，这些计算在实际运行中并不需要，因此删除；
2、使用try-except块来捕获可能的异常，并打印错误信息。
'''
# 使用PIO闪烁LED并以1Hz提高IRQ的示例。

import time
from machine import Pin
import rp2

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def blink_1hz():
    # 定义一个PIO程序，用于以1Hz的频率闪烁LED，并在每次闪烁时触发IRQ。
    irq(rel(0))
    set(pins, 1)
    set(x, 31) [5]
    label("高延迟")
    nop() [29]
    jmp(x_dec, "高延迟")

    set(pins, 0)
    set(x, 31) [6]
    label("低延迟")
    nop() [29]
    jmp(x_dec, "低延迟")

try:
    # 使用blink_1hz程序创建StateMachine，并在Pin（25）上输出。
    sm = rp2.StateMachine(0, blink_1hz, freq=2000, set_base=Pin(25))

    # 设置IRQ处理程序以打印毫秒时间戳。
    sm.irq(lambda p: print(time.ticks_ms()))

    # 启动 StateMachine
    sm.active(1)
except Exception as e:
    # 捕获并打印任何发生的错误。
    print(f"发生错误: {e}")