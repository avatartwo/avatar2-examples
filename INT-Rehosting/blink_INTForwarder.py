from datetime import datetime

import IPython

from avatar2 import *

import util

VECTOR_TABLE_OFFSET_REG = 0xe000ed08

HARD_FAULT_ISR = 0x100001c4

IRQ_MAP = {
    0x100001f6: "<_reset_handler>",
    0x100001c0: "<isr_invalid>",
    0x100001c2: "<isr_nmi>",
    0x100001c4: "<isr_hardfault>",
    0x100001c6: "<isr_svcall>",
    0x100001c8: "<isr_pendsv>",
    0x100001ca: "<isr_systick>",
    0x100001cc: "<__unhandled_user_irq>",
    0x100012f0: "<hardware_alarm_irq_handler>",
    0x20041fff: "__END_OF_RAM__"
}

FIRMWARE = "./blink-uart.bin"
OPENOCD_CONFIG = "./pico-picoprobe.cfg"
AFTER_INIT_LOC = 0x1000037e  # end of loop


def main():
    # Configure the location of config and binary files
    firmware = abspath(FIRMWARE)
    bootrom = abspath('./pico_bootrom.bin')
    openocd_config = abspath(OPENOCD_CONFIG)

    # Initiate the avatar-object
    avatar = Avatar(arch=ARM_CORTEX_M3,
                    output_directory='/tmp/avatar', log_to_stdout=False)
    loggerAvatar, logger, _ = util.setup_loggers(emulated_logger=True)

    logger.info("Setting up targets")
    # Create the target-objects
    hardware = avatar.add_target(
        OpenOCDTarget, openocd_script=openocd_config, name='hardware')

    # Create controlled qemu instance
    qemu = avatar.add_target(QemuTarget, gdb_port=1236,
                             entry_address=0x1000000, name='qemu')

    logger.info("Loading interrupt plugins")
    avatar.load_plugin('arm.INTForwarder')
    avatar.load_plugin('assembler')
    avatar.load_plugin('disassembler')

    # Memory mapping from https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf#_address_map
    rom = avatar.add_memory_range(
        0x00000000, 0x00004000, file=bootrom, name='ROM')  # 16kB ROM with bootloader
    # 2MB Flash, Accessing using XIP with cache (most common)
    xip_cached = avatar.add_memory_range(
        0x10000000, 0x00200000, file=firmware, name='Flash (XIP) - cache')

    ram = avatar.add_memory_range(
        0x20000000, 0x00042000, name='RAM')  # 264kB of RAM
    # We will need the apb system registers, esp the timer
    apb_peripherals = avatar.add_memory_range(
        0x40000000, 0x00070000, name='APB', forwarded=True, forwarded_to=hardware)
    # To the USB registers are mapped in the 0x50 range
    usb_peripherals = avatar.add_memory_range(
        0x50100000, 0x00120000, name='USB', forwarded=True, forwarded_to=hardware)
    # To blink the LED we will need the SIO registers (contains GPIO registers)
    sio = avatar.add_memory_range(
        0xd0000000, 0x0000017c, name='SIO', forwarded=True, forwarded_to=hardware)  # SIO registers
    # Internal peripherals of the Cortex M0+, esp VTOR
    arm_peripherals = avatar.add_memory_range(0xe0000000, 0x00010000, name='Cortex Peripherals-1')

    # Initialize the targets
    logger.debug("Initializing targets")
    avatar.init_targets()

    # Set breakpoint right at the start of the loop
    hardware.set_breakpoint(AFTER_INIT_LOC, hardware=True)
    hardware.cont()
    hardware.wait()
    print("breakpoint hit")
    util.printVT(hardware, IRQ_MAP)
    vt_offset = util.getVTOR(hardware)

    logger.debug("Syncing targets")
    avatar.transfer_state(hardware, qemu, sync_regs=True, synced_ranges=[ram])

    ###############################################################################################
    # print("\n=================== Dropping in interactive session =========================\n")
    # IPython.embed()
    ###############################################################################################
    irq_trace = []

    def record_interrupt_enter(avatar, message, **kwargs):
        isr = message.interrupt_num
        isr_addr = message.isr_addr - 1
        irq = IRQ_MAP[isr_addr] if isr_addr in IRQ_MAP else 'unknown'
        logger.warning(f">>>>>>>>>>> ENTER IRQ-num={isr} irq={irq}")
        irq_trace.append(
            {'id': message.id, 'event': 'enter', 'isr': isr, 'irq': irq, 'timestamp': datetime.now().isoformat()})

    def record_interrupt_exit(avatar, message, **kwargs):
        isr = message.interrupt_num
        logger.warning(f">>>>>>>>>>> EXIT  IRQ-num={isr}")
        irq_trace.append(
            {'id': message.id, 'event': 'exit', 'isr': isr, 'irq': '__LAST_ENTER__',
             'timestamp': datetime.now().isoformat()})

    logger.debug("Registering interrupt handlers")
    avatar.watchmen.add_watchman('TargetInterruptEnter', 'after', record_interrupt_enter)
    avatar.watchmen.add_watchman('RemoteInterruptExit', 'after', record_interrupt_exit)

    logger.debug("Enabling interrupts")
    # NOTE: Here we can edit breakpoints in the hardware target without running into bug hell
    hardware.remove_breakpoint(0)  # Remove our initial breakpoint
    hardware.remove_breakpoint(1)  # Remove our initial breakpoint
    qemu.set_breakpoint(HARD_FAULT_ISR)  # Break on hardfault

    avatar.transfer_interrupt_state(hardware, qemu)
    avatar.enable_interrupt_forwarding(hardware, qemu)

    print("\n=================== Finished setting up interrupt rehosting =========================\n")
    STUB_LOC = hardware.protocols.interrupts._monitor_stub_isr
    # hardware.set_breakpoint(STUB_LOC)  # Break on stub
    IRQ_MAP[STUB_LOC] = "STUB"
    util.printVT(hardware, IRQ_MAP)

    print("\n=================== Continuing... =========================\n")
    print(f"HARDWARE: 0x{hardware.read_memory(VECTOR_TABLE_OFFSET_REG, 4):08x}")
    print(f"QEmu    : 0x{qemu.read_memory(VECTOR_TABLE_OFFSET_REG, 4):08x}")
    print()

    qemu.cont()
    sleep(2)
    hardware.cont()

    print("\n=================== Dropping in interactive session =========================\n")
    IPython.embed()
    # Executing `qemu.cont(); qemu.wait()` in the ipython shell, will cause the LED
    # to either turn on or off because we step from sleep() to sleep()

    print("=================== Done =========================")
    if hardware.state == TargetStates.RUNNING:
        hardware.stop()
    if qemu.state == TargetStates.RUNNING:
        qemu.stop()
    avatar.shutdown()
    return


if __name__ == '__main__':
    main()
