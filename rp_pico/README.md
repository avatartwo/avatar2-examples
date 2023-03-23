# Rehosting the Raspberry Pi Pico with the blink example

This example was developed to enable rehosting of the rp2040 chip of the Raspberry Pi Pico
development board.

### Notes on state register

During development of this example, an inconsistency in the handling of the Cortex-M state register (xPSR) between the various Avatar² targets was found.
Therefore this example requires the most recent Avatar² (March 2023) version and an OpenOCD build which includes their changes to the `xpsr` register naming from January 2023.

__In more detail:__  
The `xpsr` register encodes the different state registers for the Cortex-M family, in the Cortex-A family this is called `cpsr`.
QEmu reuses the `cpsr` register from the Cortex-M family to encode the state bits in the Cortex-M simulation.
This can lead to undefined behavior in combination with Avatar²s' handling of registers through the gdb connection.
In particular a write to `xPSR` causes a write to a different register than a write to `xpsr` which causes a hard fault in the simulated cortex.

For the PANDA target this is different, as it does not support the `xpsr` register to begin with but uses a translated `cpsr` register in its place.

### Purpose

This example shows important concepts of the avatar² framework:
* Orchestrating a single embedded device
* Memory mapping multiple memory regions
* State transfer from the device to QEmu or PANDA (special focus on the state registers)
* Development of a python peripheral
* Manual state transfer from the physical peripheral into the python peripheral for emulation

### Requirements
- Two [Raspberry Pi Picos](https://www.raspberrypi.com/products/raspberry-pi-pico/)
  , one flashed with the provided blink.elf, the other one setup as a picoprobe debugger for the first one
- [Avatar²-core](https://github.com/avatartwo/avatar2) (at least March 2023)
- [OpenOCD](http://openocd.org/) (at least Feb 2023)
- [Avatar²-qemu](https://github.com/avatartwo/avatar-qemu) (Only for the QEmu example)
- [PANDA](https://github.com/panda-re/panda) (Only for the PANDA example)

### Contents
- `pico-blink.py` - the avatar²-script for rehosting using QEmu
- `pico-blink-PANDA.py` - the avatar²-script for rehosting using PANDA
- `pico-picoprobe.cfg` - the OpenOCD configuration file for the pico-picoprobe combination
- `blink.bin` - Dump of the flash of the pico for quicker state transfer
- `blink.elf` - Compiled firmware (with debug symbols) for flashing and debugging
- `pico_bootrom.bin` - Dumped image of the Picos bootrom (v2.0)
- `blink/` - Files to compile the  `blink.elf` file
