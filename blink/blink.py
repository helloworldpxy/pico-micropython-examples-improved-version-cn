'''
相较原代码改进：
1、在回调函数tick时，led变量不再需要声明为全局变量，去除全局变量亦可直接使用；
2、使用try-except语句捕获定时器初始化失败的异常，并打印错误信息。
'''
from machine import Pin, Timer

# 初始化LED引脚为输出模式
led = Pin("LED", Pin.OUT)

# 定义定时器回调函数，用于切换LED的状态
def tick(timer):
    led.toggle()

try:
    # 创建一个定时器对象并初始化，设置频率为2.5Hz，模式为周期性，并绑定回调函数tick
    tim = Timer()
    tim.init(freq=2.5, mode=Timer.PERIODIC, callback=tick)

except Exception as e:
    print(f"定时器初始化失败: {e}")
