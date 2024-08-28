'''
相较原代码改进：
1、将重复的代码封装到toggle_led函数中，减少冗余代码。
3、在toggle_led函数中添加了try-except块，以处理可能发生的异常。
3、将睡眠时间作为参数传递给toggle_led函数，增加了代码的灵活性。
'''
# 示例使用PIO通过显式执行打开LED。
#
# 演示：
#   - 使用set_init和set_base
#   - 使用StateMachine.exec

import time
from machine import Pin
import rp2

# 定义一个使用单个固定引脚的空程序。
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def prog():
    pass

# 切换LED状态的函数，包含错误处理机制。
def toggle_led(state_machine, duration=0.5):
    """
    切换LED状态的函数，包含错误处理机制。
    :param state_machine: StateMachine对象
    :param duration: 持续时间，默认为0.5秒
    """
    try:
        state_machine.exec("set(pins, 1)")  # 打开设置引脚
        time.sleep(duration)  # 睡眠指定时间
        state_machine.exec("set(pins, 0)")  # 关闭设置引脚
    except Exception as e:
        print(f"执行过程中发生错误: {e}")

# 构建StateMachine，将引脚25绑定到设定引脚。
sm = rp2.StateMachine(0, prog, set_base=Pin(25))

# 调用toggle_led函数来控制LED
toggle_led(sm)