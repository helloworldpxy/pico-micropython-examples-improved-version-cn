'''
相较原代码改进：
1.、增加了异常处理，避免程序崩溃。
'''
# 使用PIO进行PWM和降低LED亮度的示例

from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
from time import sleep


@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_prog():
    pull(noblock) .side(0)
    mov(x, osr) # 将最新的拉取数据保存在X中，供noblock回收
    mov(y, isr) # ISR必须预加载PWM计数最大值
    label("pwmloop")
    jmp(x_not_y, "skip")
    nop()         .side(1)
    label("skip")
    jmp(y_dec, "pwmloop")


class PIOPWM:
    def __init__(self, sm_id, pin, max_count, count_freq):
        self._sm = StateMachine(sm_id, pwm_prog, freq=2 * count_freq, sideset_base=Pin(pin))
        # 使用exec（）将最大计数加载到ISR中
        self._sm.put(max_count)
        self._sm.exec("pull()")
        self._sm.exec("mov(isr, osr)")
        self._sm.active(1)
        self._max_count = max_count

    def set(self, value):
        # 最小值为-1（完全关闭），0实际上仍会产生窄脉冲
        value = max(value, -1)
        value = min(value, self._max_count)
        self._sm.put(value)


# 在Raspberry Pi主板上的Pin 25
try:
    pwm = PIOPWM(0, 25, max_count=(1 << 16) - 1, count_freq=10_000_000)
except Exception as e:
    print(f"PWM初始化失败: {e}")

while True:
    try:
        for i in range(256):
            pwm.set(i ** 2)
            sleep(0.01)
    except Exception as e:
        print(f"循环中出现错误: {e}")
        break
