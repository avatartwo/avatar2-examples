# Rehosting the Raspberry Pi Pico with the blink example

This example was developed to enable rehosting of the rp2040 chip of the Raspberry Pi Pico
development board.

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
- [Avatar²-core](https://github.com/avatartwo/avatar2)
- [OpenOCD](http://openocd.org/)
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
