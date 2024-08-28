'''
相较原代码改进：
1、初始化SPI时，只设置一次即可，不需要重复设置；
2、使用try-except块来捕获可能的异常，并打印错误信息；
3、在write和write_readinto方法中，明确使用bytes类型数据，避免潜在的类型错误。
'''
from machine import SPI

try:
    # 初始化SPI，只设置一次
    spi = SPI(0, 100_000, polarity=1, phase=1)
    
    # 写入数据
    spi.write(b'test')
    
    # 读取数据
    data = spi.read(5)
    print(data)
    
    # 写入并读取数据
    buf = bytearray(3)
    spi.write_readinto(b'out', buf)
    print(buf)
except Exception as e:
    print(f"出现错误: {e}")
