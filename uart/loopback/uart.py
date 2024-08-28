'''
相较原代码改进：
1、原代码中每次读取一个字节，现在改为一次性读取所有可用数据，减少计算量；
2、删除了不必要的循环读取代码。

'''
from machine import UART, Pin
import time

try:
    uart1 = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
    uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

    txData = b'hello world\n\r'
    uart1.write(txData)
    time.sleep(0.1)  # 确保数据发送完毕

    if uart0.any():  # 检查是否有数据可读
        rxData = uart0.read()  # 一次性读取所有可用数据
        print(rxData.decode('utf-8'))
    else:
        print("无已接收的数据")
except Exception as e:
    print(f"出现错误: {e}")
