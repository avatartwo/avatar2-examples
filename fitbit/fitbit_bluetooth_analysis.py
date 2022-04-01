#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
########################
This work is done in context of a semester project at EURECOM 
in the digital security department.
#########################
author: Bechir Bouali
e-mail: bechir.bouali@eurecom.fr
#########################
"""

import IPython 
import telnetlib
import time

from os.path import abspath 
from avatar2 import *

def main():

    # Configure the location of various files
	firmware = abspath('./patched_firmware.bin')
	openocd_config = abspath('./fitbit.cfg')
	# Need to be changed 
	qemu_path = abspath("/root/EURECOM/projects/fitbit_project/avatar2/build/arm-softmmu/qemu-system-arm")
    # Initiate the avatar-object
	avatar = Avatar(arch=ARM_CORTEX_M3, output_directory='/tmp/avatar')
	# create openocd object and enabling gdbserver on port 3333
	fitbit = avatar.add_target(OpenOCDTarget,openocd_script=openocd_config,gdb_executable="arm-none-eabi-gdb")	
	# create qemu object to emulate 
	qemu = avatar.add_target(QemuTarget, executable=qemu_path,gdb_executable="arm-none-eabi-gdb", gdb_port=1236)
 	#Define the various memory ranges and store references to them
	rom  = avatar.add_memory_range(0x08000000, 0x40000, file=firmware)
	ram  = avatar.add_memory_range(0x20000000, 0x8000)
	mmio = avatar.add_memory_range(0x40000000, 0x1000000,forwarded=True, forwarded_to=fitbit)
	
	try:
		avatar.init_targets()
		# set hardware breakpoint at 0x0800EE62(get_bluetooth_id)
		fitbit.set_breakpoint(0x800ee62, hardware=True)
		print ("hardware breakpoint at 0x0800EE62")
		fitbit.cont()
		
		n = 0
		while True:
			time.sleep(3)	
			fitbit.wait()
			if fitbit.regs.pc == 0x0800EE62:
				n += 1
				print ("hit it %d times" % n)
				print ("My caller function at 0x%x" % fitbit.regs.lr)
			if n == 3:
				break
			print("waiting for the breakpoint")
			fitbit.cont()
		#Transfer the state from the physical device to the emulator
		avatar.transfer_state(fitbit, qemu, sync_regs=True,synced_ranges=[ram])
		print("State transfer finished, emulator $pc is: 0x%x" % qemu.regs.pc)
	except:
		print("error somewhere, shutdown avatar ")
		#shutting down avatar cleanly if there is an error
		avatar.shutdown()
	qemu.cont()
    # Further analysis could go here:
	IPython.embed()
    
	time.sleep(5)
	print("The End, shutdown avatar")
	avatar.shutdown()

if __name__ == '__main__':
	main()
