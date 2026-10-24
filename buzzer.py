"""
Buzzer helper for Raspberry Pi Pico.

Supports both active buzzers (digital on/off) and passive ones driven with a
basic square wave generated through PWM.  For this project we mostly need a
simple alert interface, but an optional pulsing method is provided to create
distinct warning patterns for various platoon states.
"""

from machine import Pin, PWM
import utime


class Buzzer:
    """Simple PWM-enabled buzzer abstraction."""

    def __init__(self, pin: int, frequency: int = 2000, duty: int = 512):
        self.pin = pin
        self.frequency = frequency
        self.duty = duty
        self._pwm = PWM(Pin(pin))
        self._pwm.deinit()  # start silent
        self._active = False

    def on(self):
        if self._active:
            return
        self._pwm = PWM(Pin(self.pin))
        self._pwm.freq(self.frequency)
        self._pwm.duty_u16(self.duty)
        self._active = True

    def off(self):
        if not self._active:
            return
        self._pwm.deinit()
        self._active = False

    def pulse(self, duration_ms: int = 250, pause_ms: int = 150, count: int = 2):
        """
        Emit a pulsed alert pattern without blocking the main logic for too long.
        """
        for _ in range(count):
            self.on()
            utime.sleep_ms(duration_ms)
            self.off()
            utime.sleep_ms(pause_ms)

