'''
相较源代码改进：
1、将conversion_factor的计算结果直接用于读取传感器数据，减少计算量；
2、将温度读取和计算逻辑封装到一个函数中，使代码更简洁；
3、增加异常处理，避免程序崩溃。
'''
import machine
import utime

# 初始化温度传感器，使用ADC通道4
sensor_temp = machine.ADC(4)
# 计算电压转换因子
conversion_factor = 3.3 / 65535

def read_temperature():
    try:
        # 读取传感器数据并转换为电压
        reading = sensor_temp.read_u16() * conversion_factor
        # 根据电压计算温度
        #温度传感器测量连接到ADC通道5的偏置双极二极管的Vbe电压
        #通常，在27摄氏度时，Vbe=0.706V，斜率为每度-1.721mV（0.001721）。
        temperature = 27 - (reading - 0.706) / 0.001721
        return temperature
    except Exception as e:
        print(f"读取温度时发生错误: {e}")
        return None

while True:
    temperature = read_temperature()
    if temperature is not None:
        print(temperature)
    utime.sleep(2)