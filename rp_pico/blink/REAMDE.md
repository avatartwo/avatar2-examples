# Source of the used blink demo application

This is the source code used to produce the `blink.elf` firmware used by this Avatar2 example.

## Build

### Requirements:

* [Raspberry Pi Pico SDK](https://github.com/raspberrypi/pico-sdk) 
* Note: sometimes `libstdc++-arm-none-eabi-newlib` needs to be installed additionally

### Build instructions

```shell
$ mkdir build
$ cd build
build/ $ cmake ..
build/ $ make
```
