"""
Smart platooning demo for Raspberry Pi Pico (MicroPython).

Hardware (default pins map to GP numbers on the Pico):
    - Front HC-SR04:  TRIG GP8  | ECHO GP9
    - Side  HC-SR04:  TRIG GP6  | ECHO GP7
    - Back  HC-SR04:  TRIG GP10 | ECHO GP12
    - Buzzer:         GP15 (change to match your wiring)
    - LCD1602 I2C:    SDA GP0, SCL GP1 (bus 0, addr 0x27)
"""

from machine import Pin, I2C
import utime

from pico_platoon.ultrasonic import UltrasonicSensor
from pico_platoon.buzzer import Buzzer
from pico_platoon.lcd1602 import Lcd1602
from pico_platoon.platoon_logic import PlatoonController


# Pin map (update if your wiring differs)
TRIG_FRONT = 8
ECHO_FRONT = 9

TRIG_SIDE = 6
ECHO_SIDE = 7

TRIG_BACK = 10
ECHO_BACK = 12

BUZZER_PIN = 15

LCD_I2C_ID = 0
LCD_SDA = 0
LCD_SCL = 1
LCD_ADDR = 0x27


def init_hardware():
    i2c = I2C(LCD_I2C_ID, sda=Pin(LCD_SDA), scl=Pin(LCD_SCL), freq=400000)
    lcd = Lcd1602(i2c, address=LCD_ADDR)
    lcd.clear()
    lcd.putstr("Platoon Booting")
    buzzer = Buzzer(BUZZER_PIN, frequency=1800)
    sensors = {
        "front": UltrasonicSensor(TRIG_FRONT, ECHO_FRONT),
        "side": UltrasonicSensor(TRIG_SIDE, ECHO_SIDE),
        "back": UltrasonicSensor(TRIG_BACK, ECHO_BACK),
    }
    return lcd, buzzer, sensors


def fmt_distance(value):
    if value is None:
        return "---"
    return f"{int(value):>3}"


def fmt_signed(value):
    return f"{value:+05.1f}"


def update_lcd(lcd, telemetry, flip=False):
    lcd.clear()
    distances = telemetry.distances
    line1 = f"F:{fmt_distance(distances['front'])} "
    line1 += f"S:{fmt_distance(distances['side'])} "
    line1 += f"B:{fmt_distance(distances['back'])}"

    if flip:
        line2 = f"v:{fmt_signed(telemetry.velocity)}"
        line2 += f" a:{fmt_signed(telemetry.acceleration)}"
    else:
        line2 = telemetry.state[:16]

    lcd.move_to(0, 0)
    lcd.putstr(line1[:16])
    lcd.move_to(0, 1)
    lcd.putstr(line2[:16])


def log_console(telemetry):
    dist = telemetry.distances
    print(
        "F:{:>6}cm S:{:>6}cm B:{:>6}cm | v:{:+6.2f}cm/s a:{:+6.2f}cm/s^2 | {}".format(
            f"{dist['front']:.1f}" if dist["front"] else "---",
            f"{dist['side']:.1f}" if dist["side"] else "---",
            f"{dist['back']:.1f}" if dist["back"] else "---",
            telemetry.velocity,
            telemetry.acceleration,
            telemetry.state,
        )
    )


def main():
    lcd, buzzer, sensors = init_hardware()
    controller = PlatoonController()
    flip = False

    try:
        while True:
            front = sensors["front"].read_distance_cm()
            side = sensors["side"].read_distance_cm()
            back = sensors["back"].read_distance_cm()

            telemetry = controller.update(front, side, back)

            if telemetry.alert:
                buzzer.on()
            else:
                buzzer.off()

            update_lcd(lcd, telemetry, flip)
            log_console(telemetry)
            flip = not flip

            utime.sleep_ms(250)
    except KeyboardInterrupt:
        pass
    finally:
        buzzer.off()
        lcd.clear()
        lcd.putstr("System halted")


if __name__ == "__main__":
    main()

