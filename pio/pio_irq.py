'''
相较原代码改进：
增加了try-except块来捕获并处理可能发生的异常，确保程序在遇到错误时不会崩溃，而是打印出错误信息。
'''
import time
import rp2

@rp2.asm_pio()
def irq_test():
    # 定义一个PIO汇编程序，用于测试中断
    wrap_target()
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    irq(0)         # 触发中断0
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    irq(1)         # 触发中断1
    wrap()

try:
    rp2.PIO(0).irq(lambda pio: print(pio.irq().flags()))  # 设置PIO0的中断处理函数，打印中断标志

    sm = rp2.StateMachine(0, irq_test, freq=2000)  # 创建并配置状态机0，运行irq_test程序，频率为2000Hz
    sm.active(1)  # 激活状态机0
    time.sleep(1)  # 等待1秒
    sm.active(0)  # 停用状态机0
except Exception as e:
    print(f"出现错误: {e}")
