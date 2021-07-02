from avatar2 import Avatar
from avatar2.archs import ARM_CORTEX_M3
from avatar2.targets import OpenOCDTarget, QemuTarget
from avatar2.peripherals import AvatarPeripheral

class nrf51UART(AvatarPeripheral):
    def dispatch_read(self, offset, size):

        if offset == 0x11c:
            return self.txdone

        return 0x00

    def dispatch_write(self, offset, size, value):
        if offset == 0x11c:
            self.txdone = value
        elif offset == 0x51c:
            print(f">>>> {chr(value)} <<<<")
            self.txdone=1
        return True


    def __init__(self, name, address, size, **kwargs):
        super().__init__(name, address, size)
        self.read_handler[0:size] = self.dispatch_read
        self.write_handler[0:size] = self.dispatch_write

        self.txdone = 0



avatar = Avatar(arch=ARM_CORTEX_M3, output_directory='/tmp/avatar2')

# Specify Targets
nrf = avatar.add_target(OpenOCDTarget, openocd_script='/usr/share/openocd/scripts/board/nordic_nrf51_dk.cfg')
qemu = avatar.add_target(QemuTarget, gdb_port=1234)

# Add memory ranges

fw   = avatar.add_memory_range(0x000000000, 0x40000,
                               file='./firmware.bin')
ram  = avatar.add_memory_range(0x20000000, 0x10000)
mmio = avatar.add_memory_range(0x40000000, 0x2000,
                               forwarded=True, forwarded_to=nrf)

uart = avatar.add_memory_range(0x40002000, 0x1000,
                               emulate=nrf51UART)

mmio2 = avatar.add_memory_range(0x40003000, 0x20000000-0x3000,
                               forwarded=True, forwarded_to=nrf)
ficr = avatar.add_memory_range(0x10000000, 0x2000,
                               forwarded=True, forwarded_to=nrf)

avatar.init_targets()

nrf.set_breakpoint(0x001dbac)
nrf.cont()
nrf.wait()

avatar.transfer_state(nrf, qemu, synced_ranges=[ram])
qemu.write_memory(0x20002274, 4, 0x00)
qemu.cont()
import time; time.sleep(2)



