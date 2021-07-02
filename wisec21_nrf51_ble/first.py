from avatar2 import Avatar
from avatar2.archs import ARM_CORTEX_M3
from avatar2.targets import OpenOCDTarget

avatar = Avatar(arch=ARM_CORTEX_M3, output_directory='/tmp/avatar2')

# Specify Targets
nrf = avatar.add_target(OpenOCDTarget, openocd_script='/usr/share/openocd/scripts/board/nordic_nrf51_dk.cfg')

# Add memory ranges
# skip for now

avatar.init_targets()

nrf.set_breakpoint(0x0001da94)
nrf.cont()
nrf.wait()

import IPython; IPython.embed()
'''
The following commands where executed in the interactive IPython shell to
change the BLE identifier:
    nrf.write_memory(0x20002000, 20, b"WiSec_UART", raw=True)
    nrf.regs.r1 = 0x20002000
    nrf.cont()

Later on, the firmware was dumped from the device via:
    nrf.stop() 
    fw_data = nrf.read_memory(0x00, 0x40000, raw=True)
    with open("firmware.bin", "wb") as f:
        f.write(fw_data)
'''


