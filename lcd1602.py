"""
Minimal I2C 16x2 LCD helper based on the PCF8574 backpack.

Tested on Raspberry Pi Pico running MicroPython 1.20+.
"""

from machine import I2C
import utime


class Lcd1602:
    """16x2 HD44780 LCD using an I2C backpack."""

    # Commands
    LCD_CLR = 0x01
    LCD_HOME = 0x02
    LCD_ENTRY_MODE = 0x04
    LCD_DISPLAY_ON = 0x0C
    LCD_FUNCTION_SET = 0x28
    LCD_SET_DDRAM = 0x80

    # Backlight bit
    BACKLIGHT = 0x08

    ENABLE = 0x04

    def __init__(self, i2c: I2C, address: int = 0x27, cols: int = 16, rows: int = 2):
        self.i2c = i2c
        self.address = address
        self.cols = cols
        self.rows = rows
        self._backlight = Lcd1602.BACKLIGHT

        utime.sleep_ms(20)
        self._write(0x03 << 4)
        utime.sleep_ms(5)
        self._write(0x03 << 4)
        utime.sleep_us(120)
        self._write(0x03 << 4)
        self._write(0x02 << 4)

        self.command(Lcd1602.LCD_FUNCTION_SET)
        self.command(Lcd1602.LCD_DISPLAY_ON)
        self.command(Lcd1602.LCD_CLR)
        self.command(Lcd1602.LCD_ENTRY_MODE | 0x02)

    def _write(self, data):
        self.i2c.writeto(self.address, bytes([data | self._backlight]))

    def _pulse(self, data):
        self._write(data | Lcd1602.ENABLE)
        utime.sleep_us(1)
        self._write(data & ~Lcd1602.ENABLE)
        utime.sleep_us(50)

    def command(self, cmd):
        self._send(cmd, mode=0)

    def write_char(self, char_val):
        self._send(char_val, mode=1)

    def _send(self, data, mode):
        high = (data & 0xF0) | mode
        low = ((data << 4) & 0xF0) | mode
        self._pulse(high)
        self._pulse(low)

    def clear(self):
        self.command(Lcd1602.LCD_CLR)
        utime.sleep_ms(2)

    def move_to(self, col, row):
        row = max(0, min(self.rows - 1, row))
        addr = Lcd1602.LCD_SET_DDRAM + col + (0x40 * row)
        self.command(addr)

    def putstr(self, text: str):
        for ch in text:
            if ch == "\n":
                # Move to next row
                self.move_to(0, 1)
                continue
            self.write_char(ord(ch))

    def set_backlight(self, enabled: bool):
        self._backlight = Lcd1602.BACKLIGHT if enabled else 0x00
        self._write(0)  # Update latch

