from avatar2 import *

import threading
import subprocess
import os


# The TargetLauncher is ripped from the avatar1-example
# It is used to spawn and stop a qemu instance which is independent of avatar2.
class TargetLauncher(object):
    def __init__(self, cmd):
        self._cmd = cmd
        self._process = None
        self._thread = threading.Thread(target=self.run)
        self._thread.start()

    def stop(self):
        if self._process:
            print(self._process.kill())

    def run(self):
        print("TargetLauncher is starting process %s" %
              " ".join(['"%s"' % x for x in self._cmd]))
        self._process = subprocess.Popen(self._cmd)


def main():

    # Adjust me!
    qemu_path = ("/home/avatar2/avatar2/targets/build/qemu/arm-softmmu/"
                 "qemu-system-arm")

    # Let's start the qemu-instance which is not controlled by avatar2
    target_runner = TargetLauncher([qemu_path,
                                    "-M",  "versatilepb",
                                    "-m", "20M",
                                    "-gdb", "tcp:127.0.0.1:1234",
                                    "-serial",
                                    "tcp:127.0.0.1:2000,server,nowait",
                                    "-kernel", "u-boot",
                                    "-S", "-nographic",
                                    "-monitor",
                                    "telnet:127.0.0.1:2001,server,nowait"
                                    ])

    # Creation of the avatar-object
    avatar = Avatar(arch=ARM, output_directory='/tmp/myavatar')

    # Define a GDBTarget as first target - this will be used to connect to
    # the qemu-instance which is not controlled by avatar2
    gdb = avatar.add_target(GDBTarget,
                            gdb_executable="arm-none-eabi-gdb", gdb_port=1234)

    # Define a QemuTarget as second target, which will be used to emulate the
    # first target.
    qemu = avatar.add_target(QemuTarget,
                             gdb_executable="arm-none-eabi-gdb",
                             executable=qemu_path,
                             gdb_port=1236,
                             entry_address=0x1000000)

    # Redirect the serial connection of the qemu-target to a tcp-connection
    qemu.additional_args = ["-serial", "tcp::2002,server,nowait"]

    # Definition of memory ranges, corresponding to the definitions of the
    # avatar1 example, including forwarded, emulated and file-backed ranges
    avatar.add_memory_range(0x00000000, 0x001000, name='interrupts')

    avatar.add_memory_range(0x00001000, 0xfdc000, name='before_code',
                            forwarded=True, forwarded_to=gdb)
    avatar.add_memory_range(0x00fdd000, 0x01000, name='init_mem')
    avatar.add_memory_range(0x00fde000, 0x22000, name='heap')

    avatar.add_memory_range(0x01000000, 0x019000, name='text_data_bss',
                            file='%s/u-boot.bin' % os.getcwd())

    avatar.add_memory_range(0x01019000, 0x101f1000-0x01019000, 
                            name='after_code', 
                            forwarded=True, forwarded_to=gdb)

    avatar.add_memory_range(0x101f1000, 0x1000, name='serial',
                            qemu_name='pl011',
                            qemu_properties={'type': 'serial',
                                             'name': 'chardev',
                                             'value': 0})

    avatar.add_memory_range(0x101f2000, 0x100000000-0x101f2000, 
                            name='after_serial',
                            forwarded=True, forwarded_to=gdb)

    # Initiliaze the targets
    avatar.init_targets()

    # Run until clear_bss
    qemu.set_breakpoint(0x010000b4)
    qemu.cont()
    qemu.wait()
    print("================== Arrived at clear_bss =========================")

    # Run until the main-loop - this will take a while as a lot of
    # memory accesses will be forwarded
    # Note that due to the emulated pl011-serial device, some output of
    # the u-boot initilization will be printed on 127.0.0.1:2002
    qemu.set_breakpoint(0x0100af34)
    qemu.cont()
    qemu.wait()
    print("Arrived at main loop, demo is over")

    # Additional code for analyses or playing around could go here, e.g.:
    # import IPython; IPython.embed()

    # Shutdown avatar and the external qemu-instance
    avatar.shutdown()
    target_runner.stop()


if __name__ == '__main__':
    main()
