# WiSec'21 Tutorial

This example was developed as part of the tutorial on avatar2 presented at the
ACM Conference on Security and Privacy in Wireless and Mobile Networks (WiSec)
2021. The full video of the tutorial is avaible as [VOD on Youtube](https://www.youtube.com/watch?v=uyAPi663NP4&t=5707s).

### Purpose

This example shows important concepts of the avatar² framework:
* Orchestrating a single embedded device
* State transfer from the device to qemu.
* Development of a python peripheral

The examples are thoroughly explained in the tutorial, and it is recommended to
follow along with the recording.


### Requirements
- A [NRF51-DK](https://www.nordicsemi.com/Products/Development-hardware/nRF51-DK)
  development board, flashed with the provided firmware.bin
- [avatar²-core](https://github.com/avatartwo/avatar2)
- [avatar²-qemu](https://github.com/avatartwo/avatar-qemu)
- [openocd](http://openocd.org/)

### Contents
- `first.py` - avatar²-script for connecting to the nrf51 and spawning an IPython shell.
- `second.py` - avatar²-script for transfering state from the nrf51 to qemu when data uart data is received via BLE.
- `third.py` - avatar²-script containing a python peripheral to print received uart data on the orchestration shell.
- `firmware.bin` - binary version of the firmware used for this example
  (ble_uart_app, provided by and compiled with the Nordic SDK v12.3.0.)
