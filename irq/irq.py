from machine import Pin

try:
    # 创建一个引脚对象p2，设置为输入模式并启用上拉电阻
    p2 = Pin(2, Pin.IN, Pin.PULL_UP)
    # 为p2引脚设置中断处理函数，当引脚电平由高变低时触发，并打印中断标志
    p2.irq(lambda pin: print("带标志的IRQ:", pin.irq().flags()), Pin.IRQ_FALLING)
except Exception as e:
    # 捕获并打印任何异常信息
    print(f"出现错误: {e}")