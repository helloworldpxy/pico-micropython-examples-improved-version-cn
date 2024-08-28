'''
相较原代码改进：
1、将状态机的设置部分提取到一个函数setup_state_machine中，减少了重复代码；
2、在设置状态机时增加了try-except块，以捕获可能的异常并打印错误信息。
'''
#示例使用PIO等待引脚更改并发出IRQ。
#
#演示：
#PIO封装
#   -PIO等待指令，等待输入引脚
#   -PIO irq指令，在阻塞模式下具有相对irq编号
#   -设置StateMachine的in_base引脚
#   -为StateMachine设置irq处理程序
#   -使用相同的程序和不同的引脚实例化2x StateMachine

import time
from machine import Pin
import rp2
# 定义一个PIO程序，用于等待引脚变为低电平并触发IRQ

@rp2.asm_pio()
def wait_pin_low():
    wrap_target()

    wait(0, pin, 0)
    irq(block, rel(0))
    wait(1, pin, 0)

    wrap()
# 定义一个IRQ处理函数，用于打印时间戳和状态机对象

def handler(sm):
    # 打印（封装）时间戳和状态机对象。
    print(time.ticks_ms(), sm)


# 在Pin（16）上用wait_pin_low程序实例化StateMachine（0）。
pin16 = Pin(16, Pin.IN, Pin.PULL_UP)
sm0 = rp2.StateMachine(0, wait_pin_low, in_base=pin16)
sm0.irq(handler)

# 在Pin（17）上用wait_pin_low程序实例化StateMachine（1）。
pin17 = Pin(17, Pin.IN, Pin.PULL_UP)
sm1 = rp2.StateMachine(1, wait_pin_low, in_base=pin17)
sm1.irq(handler)

# 启动StateMachine的运行。
sm0.active(1)
sm1.active(1)

# 现在，当Pin（16）或Pin（17）被拉低时，REPL上将会打印一条消息。

'''
32行以后可改动为
# 定义一个函数，用于设置状态机，包括引脚配置、状态机实例化、IRQ处理程序设置和激活状态机
def setup_state_machine(sm_id, pin_num):
    pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
    sm = rp2.StateMachine(sm_id, wait_pin_low, in_base=pin)
    sm.irq(handler)
    sm.active(1)
    return sm

try:
    sm0 = setup_state_machine(0, 16)
    sm1 = setup_state_machine(1, 17)
except Exception as e:
    print(f"Error setting up state machines: {e}")
'''