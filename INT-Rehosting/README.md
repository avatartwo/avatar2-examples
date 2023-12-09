# Rehosting the Raspberry Pi Pico blink example with timer interrupts active
This example is an addition to the original Raspberry Pi Pico example with added interrupt forwarding capabilities.

### Purpose

This example shows the following additional concepts of the avatar² framework:
* Orchestrating interrupts during rehosting
  * Interrupt state transfers
  * Interrupt forwarding
* Interrupt state and event introspection

### Requirements
- Two [Raspberry Pi Picos](https://www.raspberrypi.com/products/raspberry-pi-pico/)
  , one flashed with the provided blink.elf, the other one setup as a picoprobe debugger for the first one
- [Avatar²-core](https://github.com/avatartwo/avatar2) (at least December 2023)
- [OpenOCD](http://openocd.org/) (Requires at least OpenOCD version 12.0)
- [Avatar²-qemu](https://github.com/avatartwo/avatar-qemu) (at least December 2023)

### Contents
- `blink_INTForwarder.py` - the avatar²-script for rehosting using the INTForwarder plugin and QEmu
- `blink-int.bin` - Dump of the flash of the pico for quicker state transfer
- `blink-int.elf` - Compiled firmware (with debug symbols) for flashing and debugging
- `pico_bootrom.bin` - Dumped image of the Picos bootrom (v2.0)
- `pico-picoprobe.cfg` - the OpenOCD configuration file for the pico-picoprobe combination
- `util.py` - Utility functions for logging
