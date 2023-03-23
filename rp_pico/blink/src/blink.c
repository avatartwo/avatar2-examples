/**
 * Based on the official Blink example by Raspberry Pi
 */

#include "pico/stdlib.h"

#ifndef PICO_DEFAULT_LED_PIN
#error "This blink example requires a board with a regular LED"
#else
#define LED_PIN PICO_DEFAULT_LED_PIN
#endif

int main()
{
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    while (true)
    {
        gpio_put(LED_PIN, 1);
        busy_wait_ms(500); // Using busy wait to avoid interrupts
        gpio_put(LED_PIN, 0);
        busy_wait_ms(500); // Using busy wait to avoid interrupts
    }
    return 0;
}
