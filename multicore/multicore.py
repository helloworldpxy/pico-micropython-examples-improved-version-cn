'''
相较原代码改进：
1、在for循环中使用_作为循环变量，表示这个变量在循环体内不会被使用，可以提高代码的可读性。
'''
import time, _thread, machine

# 定义一个任务函数，该函数控制LED灯闪烁n次，每次闪烁的间隔时间为delay秒
def task(n, delay):
    try:
        led = machine.Pin("LED", machine.Pin.OUT)
        for _ in range(n):
            led.high()
            time.sleep(delay)
            led.low()
            time.sleep(delay)
        print('完成')
    except Exception as e:
        print(f"出现错误: {e}")

try:
    # 启动一个新的线程来执行task函数，参数为闪烁次数10和每次闪烁的间隔时间0.5秒
    _thread.start_new_thread(task, (10, 0.5))
except Exception as e:
    print(f"启动线程失败: {e}")