from os.path import abspath
import IPython
from traitlets.config.loader import Config

from avatar2 import *
from avatar2.peripherals import AvatarPeripheral
import logging
import datetime


class PicoTimer(AvatarPeripheral):
    """Emulates the global timer peripheral of the rp2040
    __Note: Currently limited to the TIMERAWH and TIMERAWL register (read-only)__
    
    Based on https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf#section_timer
    """

    def dispatch_read(self, offset, size):
        print(
            f">>> PicoTimer handling read request at 0x{offset:x} of size 0x{size:x} <<<")
        if offset == 0x24:  # TIMERAWH register
            # elapsed micoseconds, upper 32 bits
            return (int((datetime.datetime.now() - self.init_time).total_seconds() * 1_000_000) & 0xffff_ffff_0000_0000) >> 32
        elif offset == 0x28:  # TIMERAWL register
            # elapsed micoseconds, lower 32 bits
            return int((datetime.datetime.now() - self.init_time).total_seconds() * 1_000_000) & 0xffff_ffff
        else:
            return 0x00

    def dispatch_write(self, offset, size, value):
        print(
            f">>> PicoTimer handling write request at 0x{offset:x} of size 0x{size:x} with value 0x{value:x} <<<")
        return False

    def __init__(self, name, address, size, **kwargs):
        super().__init__(name, address, size)
        self.read_handler[0:size] = self.dispatch_read
        self.write_handler[0:size] = self.dispatch_write

        self.init_time = datetime.datetime.now()

    def set_timer(self, low, high):
        delta = datetime.timedelta(microseconds=low + (high << 32))
        self.init_time = datetime.datetime.now() - delta


def main():

    # Configure the location of config and binary files
    firmware = abspath('./blink.bin')
    bootrom = abspath('./pico_bootrom.bin')
    openocd_config = abspath('./pico-picoprobe.cfg')

    # Initiate the avatar-object
    avatar = Avatar(arch=ARM_CORTEX_M3, output_directory='/tmp/avatar')
    logger = logging.getLogger('avatar')
    # logger.setLevel(logging.DEBUG)

    # Create the target-objects
    pico = avatar.add_target(OpenOCDTarget, openocd_script=openocd_config)

    # Create controlled qemu instance
    qemu = avatar.add_target(QemuTarget, gdb_port=1236,
                             entry_address=0x1000000)

    # Memory mapping from https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf#_address_map
    rom = avatar.add_memory_range(
        0x00000000, 0x00004000, file=bootrom, name='ROM')  # 16kB ROM with bootloader

    # We need the flash region because the code runs directly from flash memory
    # It does not need to be forwarded because there are no writes to it
    # For performance we can therefore map the blink.elf into this region, Accessing using XIP with cache region
    xip_cached = avatar.add_memory_range(
        0x10000000, 0x00048000, file=firmware, name='Flash (XIP) - cache')
    ram = avatar.add_memory_range(
        0x20000000, 0x00042000, name='RAM')  # 264kB of RAM

    # We will need the apb system registers
    apb_peripherals_1 = avatar.add_memory_range(
        0x40000000, 0x00054000, name='APB', forwarded=True, forwarded_to=pico)
    # The global timer is paused when the cores are halted, so we need to emualte it
    apb_timer: MemoryRange = avatar.add_memory_range(
        0x40054000, 0x44, emulate=PicoTimer)
    # Rest of the forwarded apb peripherals
    apb_peripherals_2 = avatar.add_memory_range(
        0x40058000, 0x4006c004 - 0x40058000, name='APB', forwarded=True, forwarded_to=pico)
    # To blink the LED we will need the SIO registers
    sio = avatar.add_memory_range(
        0xd0000000, 0x0000017c, name='SIO', forwarded=True, forwarded_to=pico)  # SIO registers

    # Initialize the targets
    avatar.init_targets()

    # Set breakpoint right at the start of the loop
    pico.set_breakpoint(0x10000366, hardware=True)
    pico.cont()
    pico.wait()
    print("Reached breakpoint")
    reg_pc = pico.read_register("pc")
    print(f"read pc reg from pico 0x{reg_pc:x} ({reg_pc})")
    # IPython.embed() # Entry to debug pico

    # Let the loop run once more
    pico.cont()
    pico.wait()

    print("Reached breakpoint")
    # Printing the state (xpsr) register to validate state transfer
    reg_xpsr = pico.read_register("xpsr")[0]
    print(
        f"Read xpsr reg from pico before transfer 0x{reg_xpsr:x} ({reg_xpsr})")

    reg_xpsr = qemu.read_register("xpsr")[0]
    print(
        f"Read xpsr reg from qemu before transfer 0x{reg_xpsr:x} ({reg_xpsr})")
    # Sync memory ranges from pico to qemu, sync registers, Flash (XIP) and SRAM
    # We only need to transfer one of the XIP ranges because they all point to the same flash, just with different caching strategies
    avatar.transfer_state(pico, qemu, sync_regs=True, synced_ranges=[ram])
    print("-------------- Transfer successful ---------------")

    reg_xpsr = qemu.read_register("xpsr")[0]
    print(
        f"Read xpsr reg from qemu after transfer 0x{reg_xpsr:x} ({reg_xpsr})")

    # From here on we want some more info on what's happening
    logger.setLevel(logging.DEBUG)
    # Transfer the timer peripheral state, we have to go through gdb because pico.read_memory will go to the emulated peripheral
    pico_gdb = pico.protocols.execution
    timer_H = pico_gdb.read_memory(0x40054024, 0x4)  # upper 32 bits of timer
    timer_L = pico_gdb.read_memory(0x40054028, 0x4)  # lower 32 bits of timer
    print(f"Timer state: TIMERAWH = 0x{timer_H:x}, TIMERAWL = 0x{timer_L:x}")
    picoTimer: PicoTimer = apb_timer.forwarded_to
    picoTimer.set_timer(timer_L, timer_H)
    print(
        f"Sanity-check: Elapsed time in emulated timer: 0x{picoTimer.dispatch_read(0x28, 4):x}" +
        " (__Should be close to TIMERAWL__)")

    # Location of the read-instruction from the TIMERAWL register at memory location 0x40054028 (0x28 offset)
    qemu.set_breakpoint(0x10001400)
    # Execute the emulation and wait for the breakpoint to get triggered
    qemu.cont()
    qemu.wait()
    IPython.embed()
    # Executing `qemu.cont(); qemu.wait()` in the ipython shell, will cause the LED
    # to either turn on or off because we step from sleep() to sleep()

    print("=================== Done =========================")

    avatar.shutdown()
    return


if __name__ == '__main__':
    main()
