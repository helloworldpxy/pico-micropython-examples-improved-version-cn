'''
相较原代码改进如下：
1、改动部分注释，使之更加明确；
2、在read_blocking方法中使用列表推导式，减少了代码行数，提高了可读性；
3、在__init__方法中增加了断言，确保cpha和cpol参数为False，并在断言失败时提供更明确的错误信息；
4、在write_blocking方法中添加了self参数，使其符合类方法的定义。
'''
import rp2
from machine import Pin

@rp2.asm_pio(out_shiftdir=0, autopull=True, pull_thresh=8, autopush=True, push_thresh=8, sideset_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_HIGH), out_init=rp2.PIO.OUT_LOW)
def spi_cpha0():
    # 注意X必须在第一个字节之前由设置代码预先初始化，我们在发送每个字节后重新加载
    # 通常会通过exec（）执行此操作，但在这种情况下，它位于指令内存中，只运行一次
    set(x, 6)
    # 实际程序如下
    wrap_target()
    pull(ifempty)            .side(0x2)   [1]
    label("bitloop")
    out(pins, 1)             .side(0x0)   [1]
    in_(pins, 1)             .side(0x1)
    jmp(x_dec, "bitloop")    .side(0x1)

    out(pins, 1)             .side(0x0)
    set(x, 6)                .side(0x0) # 请注意，对于可编程帧大小，这可以用mov x，y代替
    in_(pins, 1)             .side(0x1)
    jmp(not_osre, "bitloop") .side(0x1) # TXF空时失效

    nop()                    .side(0x0)   [1] # CSn后肩
    wrap()

class PIOSPI:
    # 定义一个使用PIO进行SPI通信的类

    def __init__(self, sm_id, pin_mosi, pin_miso, pin_sck, cpha=False, cpol=False, freq=1000000):
        # 初始化PIO SPI通信，设置状态机和引脚
        assert(not(cpol or cpha)), "CPHA and CPOL must be False"
        self._sm = rp2.StateMachine(sm_id, spi_cpha0, freq=4*freq, sideset_base=Pin(pin_sck), out_base=Pin(pin_mosi), in_base=Pin(pin_sck))
        self._sm.active(1)

    def write_blocking(self, wdata):
        # 阻塞式写数据到SPI总线
        for b in wdata:
            self._sm.put(b << 24)

    def read_blocking(self, n):
        # 从SPI总线阻塞式读取n字节数据
        return [self._sm.get() & 0xff for _ in range(n)]

    def write_read_blocking(self, wdata):
        # 阻塞式写数据到SPI总线并读取响应
        rdata = []
        for b in wdata:
            self._sm.put(b << 24)
            rdata.append(self._sm.get() & 0xff)
        return rdata