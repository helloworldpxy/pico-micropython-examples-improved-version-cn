'''
相较原代码改进：增加错误预警和处理机制。
'''
import time
import rp2
from machine import Pin

# 定义闪烁程序。它有一个GPIO在set指令上绑定，这是一个输出引脚。
# 使用大量延迟使闪烁可见。
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def blink():
    wrap_target()
    set(pins, 1)   [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    set(pins, 0)   [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    wrap()

try:
    # 使用闪烁程序以2000Hz的频率实例化状态机，设置绑定到Pin（25）（Raspberry PiPico板上的LED）
    sm = rp2.StateMachine(0, blink, freq=2000, set_base=Pin(25))

    # 运行状态机3秒。LED应闪烁。
    sm.active(1)
    time.sleep(3)
    sm.active(0)
except Exception as e:
    # 捕获并打印任何异常
    print(f"发生错误: {e}")