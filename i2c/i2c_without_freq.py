from machine import I2C

i2c = I2C(0)  # 默认为 SCL=Pin(9), SDA=Pin(8), freq=400000
