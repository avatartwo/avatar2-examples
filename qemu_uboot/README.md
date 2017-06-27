# Qemu U-Boot

Connecting avatar² to a qemu-instance running u-boot.

### Purpose
This example has three purposes: 
First and foremost, it is designed as easy accessible example without any
further hardware requirements - all which is need to run this example is the 
[avatar²-core](https://github.com/avatartwo/avatar2) and the 
[avatar²-qemu](https://github.com/avatartwo/avatar-qemu).

Second, this example shall stress the differences between avatar1 and
avatar² - the very same example is also available for the original
implementation of avatar 
[here](https://github.com/avatarone/avatar-samples/tree/master/qemu_uboot).

Last but not least, the concept of forwarded memory is shown in this example.

### Requirements
- [avatar²-core](https://github.com/avatartwo/avatar2)
- [avatar²-qemu](https://github.com/avatartwo/avatar-qemu)

### Contents

- `qemu_uboot_avatar2.py` - the exemplary avatar²-script
- `u-boot` - ELF executable of U-Boot, suitable for Qemu's versatilePB plattform
- `u-boot.bin` - Binary dump of U-Boot after it has been loaded to qemu


