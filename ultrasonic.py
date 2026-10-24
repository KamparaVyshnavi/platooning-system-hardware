"""
Ultrasonic sensor helper for Raspberry Pi Pico (MicroPython).

Provides a light abstraction around the HC-SR04 sensor so it can be reused
across multiple modules (front, side, rear).  The measurement routine performs
basic timeout protection to avoid blocking when no echo is received and can
optionally average several samples for a smoother signal.
"""

from machine import Pin
import utime


class UltrasonicSensor:
    """HC-SR04 style ultrasonic sensor helper."""

    SPEED_OF_SOUND_CM_PER_US = 0.0343  # 343 m/s -> 0.0343 cm/us

    def __init__(self, trig_pin: int, echo_pin: int, timeout_us: int = 30000):
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.timeout_us = timeout_us

        # Ensure trigger is low before starting.
        self.trig.value(0)
        utime.sleep_ms(2)

    def read_distance_cm(self, samples: int = 3):
        """
        Return averaged distance in centimeters.

        :param samples: Number of measurements to average (ignored on failures)
        :return: Float distance in cm or None when every sample fails.
        """
        total = 0.0
        count = 0
        for _ in range(max(1, samples)):
            distance = self._single_measure()
            if distance is not None:
                total += distance
                count += 1
            utime.sleep_ms(5)

        if count == 0:
            return None
        return total / count

    def _single_measure(self):
        """Raw pulse measurement. Returns None when timed out."""
        self.trig.value(0)
        utime.sleep_us(2)
        self.trig.value(1)
        utime.sleep_us(10)
        self.trig.value(0)

        start_wait = utime.ticks_us()
        while self.echo.value() == 0:
            if utime.ticks_diff(utime.ticks_us(), start_wait) > self.timeout_us:
                return None

        pulse_start = utime.ticks_us()
        while self.echo.value() == 1:
            if utime.ticks_diff(utime.ticks_us(), pulse_start) > self.timeout_us:
                return None

        pulse_end = utime.ticks_us()
        pulse_duration = utime.ticks_diff(pulse_end, pulse_start)
        distance = (
            pulse_duration * UltrasonicSensor.SPEED_OF_SOUND_CM_PER_US / 2.0
        )
        return distance

