# Nucleo-L152RE

Transferring the state of a physical device into an emulator after board
initialization.

### Purpose

This example shall show one of the core-features of avatar²: state transfers
between different targets.
Such a state transfer can either be made explicit or implicit by using the
orchestration plugin and both approaches are shown in this example.

Similarly to the qemu_uboot example, a corresponding avatar1 example can be
found
[here](https://github.com/avatarone/avatar-samples/tree/master/nucleo-l152re).
However, while the qemu_uboot examples tries to re-assemble the original
avatar-script, the example here will use new functionalities only present in
avatar²!


### Requirements
- A [Nucleo-L152RE](https://developer.mbed.org/platforms/ST-Nucleo-L152RE/)
  development board, flashed with the provided firmware.bin
- [avatar²-core](https://github.com/avatartwo/avatar2)
- [avatar²-qemu](https://github.com/avatartwo/avatar-qemu)

### Contents
- `nucleo_state_transfer.py` - the avatar²-script for this example
- `nucleo-l152re.cfg` - the openocd configuration file
- `firmware.bin` - binary version of the firmware used for this example, which is
  the nucleo_printf example, provided by and compiled with the mbed
  online compiler.
