'''
相较原代码改进：
1、原代码中使用了direction变量来控制duty的增减，优化后的代码直接使用range函数生成一个包含渐变和渐隐的序列，减少了额外的变量和逻辑判断；
2、原代码中对duty的边界检查和direction的更新是冗余的，优化后的代码通过range函数自动处理这些逻辑；
3、增加错误处理机制，使用try-except块捕获可能的异常，并打印错误信息。
'''
# 使用PWM使LED变暗的示例。

import time
from machine import Pin, PWM

try:
    # 创建PWM对象，LED连接在Pin(25)上
    pwm = PWM(Pin(25))

    # 设置PWM频率
    pwm.freq(1000)

    # 多次渐变LED的亮度
    for duty in range(0, 256) + range(255, -1, -1):
        pwm.duty_u16(duty * duty)
        time.sleep(0.001)
except Exception as e:
    print(f"出现错误: {e}")