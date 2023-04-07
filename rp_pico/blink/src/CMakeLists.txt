# Add blink example
add_executable(blink
        blink.c
        )

# pull in common dependencies
target_link_libraries(blink pico_stdlib)

# Communications setup
pico_enable_stdio_usb(blink 0) # No serial over USb
pico_enable_stdio_uart(blink 1) # Serial over uart0

# create map/bin/hex file etc.
pico_add_extra_outputs(blink)
