'''
相较原代码改进：
1、在创建StateMachine时增加了异常处理，以捕获初始化失败的情况；
2、在发送数据和打印消息时增加了异常处理，以捕获数据发送和消息打印失败的情况。
'''
# 使用PIO创建UART TX接口的示例

from machine import Pin
from rp2 import PIO, StateMachine, asm_pio

UART_BAUD = 115200
PIN_BASE = 10
NUM_UARTS = 8


@asm_pio(sideset_init=PIO.OUT_HIGH, out_init=PIO.OUT_HIGH, out_shiftdir=PIO.SHIFT_RIGHT)
def uart_tx():
    # 在数据可用之前，禁用TX阻止
    pull()
    # 初始化位计数器，生效起始位8个周期
    set(x, 7)  .side(0)       [7]
    # 移出8个数据比特，每比特8个执行周期
    label("bitloop")
    out(pins, 1)              [6]
    jmp(x_dec, "bitloop")
    # 生效停止位共8个循环（包括1个用于pull()）
    nop()      .side(1)       [6]


# 现在我们在引脚10到17上添加8个UART TX。对所有这些设备使用相同的传输速率。
uarts = []
for i in range(NUM_UARTS):
    try:
        sm = StateMachine(
            i, uart_tx, freq=8 * UART_BAUD, sideset_base=Pin(PIN_BASE + i), out_base=Pin(PIN_BASE + i)
        )
        sm.active(1)
        uarts.append(sm)
    except Exception as e:
        print(f"Failed to initialize UART {i}: {e}")

# 我们可以通过将字符推送到TX FIFO来打印每个UART中的字符
def pio_uart_print(sm, s):
    try:
        for c in s:
            sm.put(ord(c))
    except Exception as e:
        print(f"Failed to send data to UART: {e}")


# 从每个UART打印不同的消息
for i, u in enumerate(uarts):
    try:
        pio_uart_print(u, f"Hello from UART {i}!\n")
    except Exception as e:
        print(f"Failed to print message on UART {i}: {e}")
