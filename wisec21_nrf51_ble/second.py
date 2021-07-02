from avatar2 import Avatar
from avatar2.archs import ARM_CORTEX_M3
from avatar2.targets import OpenOCDTarget, QemuTarget

avatar = Avatar(arch=ARM_CORTEX_M3, output_directory='/tmp/avatar2')

# Specify Targets
nrf = avatar.add_target(OpenOCDTarget, openocd_script='/usr/share/openocd/scripts/board/nordic_nrf51_dk.cfg')
qemu = avatar.add_target(QemuTarget, gdb_port=1234)

# Add memory ranges

fw   = avatar.add_memory_range(0x000000000, 0x40000,
                               file='./firmware.bin')
ram  = avatar.add_memory_range(0x20000000, 0x10000)
mmio = avatar.add_memory_range(0x40000000, 0x20000000,
                               forwarded=True, forwarded_to=nrf)
ficr = avatar.add_memory_range(0x10000000, 0x2000,
                               forwarded=True, forwarded_to=nrf)

avatar.init_targets()

nrf.set_breakpoint(0x001dbac)
nrf.cont()
nrf.wait()

avatar.transfer_state(nrf, qemu, synced_ranges=[ram])
qemu.cont()
import time; time.sleep(2)



