from os.path import abspath
from time import sleep

from avatar2 import *

# Change to control whether the state transfer should be explicit or implicit
USE_ORCHESTRATION = 0


def main():

    # Configure the location of various files
    firmware = abspath('./firmware.bin')

    openocd_config = abspath('./nucleo-l152re.cfg')

    # Adjust me!
    qemu_path = ("/home/nsr/avatar2/avatar/targets/build/qemu/arm-softmmu/"
                 "qemu-system-arm")

    # Initiate the avatar-object
    avatar = Avatar(arch=ARM_CORTEX_M3, output_directory='/tmp/avatar')

    # Create the target-objects
    nucleo = avatar.add_target(OpenOCDTarget, openocd_script=openocd_config,
                               gdb_executable="arm-none-eabi-gdb")

    qemu = avatar.add_target(QemuTarget, executable=qemu_path,
                             gdb_executable="arm-none-eabi-gdb", gdb_port=1236)

    # Define the various memory ranges and store references to them
    rom  = avatar.add_memory_range(0x08000000, 0x1000000, 'rom', file=firmware)
    ram  = avatar.add_memory_range(0x20000000, 0x14000, 'ram')
    mmio = avatar.add_memory_range(0x40000000, 0x1000000, 'peripherals',
                                   forwarded=True, forwarded_to=nucleo)

    # Initialize the targets
    avatar.init_targets()

    if not USE_ORCHESTRATION:
        # This branch shows explicit state transferring using avatar

        # 1) Set the breakpoint on the physical device and execute up to there
        nucleo.set_breakpoint(0x8005104)
        nucleo.cont()
        nucleo.wait()

        # 2) Transfer the state from the physical device to the emulator
        avatar.transfer_state(nucleo, qemu, synched_ranges=[ram])

        print("State transfer finished, emulator $pc is: 0x%x" % qemu.regs.pc)
    else:
        # This shows implicit state transferring using the orchestration plugin

        # 1) Load the plugin
        avatar.load_plugin('orchestrator')

        # 2) Specify the first target of the analysis
        avatar.start_target = nucleo

        # 3) Configure transitions
        #    Here, only one transition is defined. Note that 'stop=True' forces
        #    the orchestration to stop once the transition has occurred.
        avatar.add_transition(0x8005104, nucleo, qemu, synched_ranges=[ram],
                              stop=True)

        # 4) Start the orchestration!
        avatar.start_orchestration()

        print("State transfer finished, emulator $pc is: 0x%x" % qemu.regs.pc)

    # Continue execution in the emulator.
    # Due due to the forwarded mmio, output on the serial port of the physical
    # device (/dev/ttyACMx) can be observed, although solely the emulator
    # is executing.
    qemu.cont()

    # Further analysis could go here:
    # import IPython; IPython.embed()

    # Let this example run for a bit before shutting down avatar cleanly
    sleep(5)
    avatar.shutdown()


if __name__ == '__main__':
    main()
