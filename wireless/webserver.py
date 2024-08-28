'''
相较原代码改进：
1、在等待网络连接时，直接检查wlan.status()是否等于3（已连接状态）；
2、在处理请求时，使用in关键字来检查请求中是否包含特定字符串，而不是使用find方法；
3、合并了LED状态的判断逻辑，减少了重复代码；
4、增加了对一般异常的处理，以便在发生未预见的错误时也能关闭连接并打印错误信息。
'''
import network
import socket
import time

from machine import Pin

# 初始化LED引脚
led = Pin(15, Pin.OUT)

# 设置网络名称和密码
ssid = '你的网络名称'
password = '你的网络密码'

# 初始化并激活WLAN接口
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# HTML模板
html = """<!DOCTYPE html>
<html>
    <head> <title>Pico W</title> </head>
    <body> <h1>Pico W</h1>
        <p>%s</p>
    </body>
</html>
"""

# 等待连接到网络
max_wait = 10
while max_wait > 0:
    if wlan.status() == 3:  # 直接检查是否已连接
        break
    max_wait -= 1
    print('正在等待连接……')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('网络连接失败')
else:
    print('已连接')
    status = wlan.ifconfig()
    print('ip = ' + status[0])

# 获取套接字地址信息
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

# 创建并配置套接字
s = socket.socket()
s.bind(addr)
s.listen(1)

print('正在监听', addr)

# 监听客户端连接
while True:
    try:
        cl, addr = s.accept()
        print('客户端已连接', addr)
        request = cl.recv(1024).decode('utf-8')  # 直接解码为字符串
        print(request)

        led_on = '/light/on' in request
        led_off = '/light/off' in request

        if led_on:
            print("LED开启")
            led.value(1)
            stateis = "LED is ON"
        elif led_off:
            print("LED关闭")
            led.value(0)
            stateis = "LED is OFF"
        else:
            stateis = "未知请求"

        response = html % stateis

        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()

    except OSError as e:
        cl.close()
        print('连接关闭')
    except Exception as e:
        print(f'发生错误: {e}')
        cl.close()
        print('连接关闭')
