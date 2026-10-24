# Smart Vehicle Platooning System using Raspberry Pi Pico

## Overview

This project implements a **Smart Vehicle Platooning Assistance System** using the Raspberry Pi Pico programmed in **MicroPython**.

The system continuously monitors the surrounding environment using three ultrasonic sensors placed at the **front**, **side**, and **rear** of the vehicle. Based on the measured distances, it estimates the relative velocity and acceleration of nearby vehicles, computes a dynamic safe following distance, and determines the appropriate driving state.

The current vehicle state and sensor measurements are displayed on a 16×2 LCD, while an audible buzzer alerts the driver whenever an unsafe situation is detected.

---

## Features

- Front, side and rear obstacle detection
- Dynamic safe following distance calculation
- Relative velocity estimation
- Relative acceleration estimation
- Lane availability detection
- Rear collision warning
- Overtake decision support
- LCD-based real-time telemetry
- Audible warning system
- Modular MicroPython implementation

---

## Hardware Components

| Component | Quantity |
|-----------|---------:|
| Raspberry Pi Pico | 1 |
| HC-SR04 Ultrasonic Sensor | 3 |
| LCD1602 I2C Display | 1 |
| Active/Passive Buzzer | 1 |
| Breadboard & Jumper Wires | As Required |

---

## Hardware Connections

### Ultrasonic Sensors

| Position | Trigger | Echo |
|----------|---------|------|
| Front | GP8 | GP9 |
| Side | GP6 | GP7 |
| Rear | GP10 | GP12 |

### Other Components

| Device | Pin |
|---------|----|
| Buzzer | GP15 |
| LCD SDA | GP0 |
| LCD SCL | GP1 |

LCD I2C Address

```
0x27
```

---

## Project Structure

```
platooning-system/
│
├── main.py
├── buzzer.py
├── lcd1602.py
├── ultrasonic.py
├── platoon_logic.py
└── __init__.py
```

---

## System Workflow

1. Initialize all hardware peripherals.
2. Read distances from front, side and rear ultrasonic sensors.
3. Estimate relative velocity.
4. Estimate relative acceleration.
5. Compute adaptive safe following distance.
6. Evaluate surrounding traffic conditions.
7. Decide vehicle state.
8. Display information on LCD.
9. Activate buzzer if required.
10. Repeat continuously.

---

# Platooning Logic

The controller estimates the relative motion of the vehicle ahead using consecutive ultrasonic sensor readings.

## Relative Velocity

The relative velocity is computed as

\[
v=\frac{d_{current}-d_{previous}}{\Delta t}
\]

where

- \(d_{current}\) = current front distance
- \(d_{previous}\) = previous front distance
- \(\Delta t\) = sampling interval

---

## Relative Acceleration

Acceleration is estimated using

\[
a=\frac{v_{current}-v_{previous}}{\Delta t}
\]

---

## Adaptive Safe Distance

Instead of using a fixed threshold, the controller dynamically adjusts the required following distance.

\[
D_{safe}=D_{min}+k|v|
\]

where

- \(D_{min}=10\) cm
- \(k=1.5\)

This allows the safe distance to increase automatically as the relative speed increases.

---

## Decision States

The controller can output the following states.

| State | Description |
|--------|-------------|
| CRUISE | Normal driving |
| FOLLOW | Maintain safe following distance |
| STOP | Immediate braking required |
| OVERTAKE | Lane clear for overtaking |
| WAIT-LANE | Adjacent lane occupied |
| WAIT-REAR | Rear vehicle too close |
| BACK ALERT | Fast approaching rear vehicle |
| FRONT SENSOR? | Front sensor unavailable |

---

## Safety Conditions

The controller generates warnings when

- Front distance falls below the minimum safe distance
- Rapid closing speed is detected
- Sudden braking is observed
- Rear vehicle approaches rapidly
- Sensor failures occur

Whenever an unsafe condition is detected, the buzzer is activated.

---

## LCD Display

The LCD alternates between two display modes.

### Screen 1

```
F:120 S:80 B:95
OVERTAKE
```

### Screen 2

```
F:120 S:80 B:95
v:+12.5 a:-8.4
```

where

- F = Front distance
- S = Side distance
- B = Rear distance
- v = Relative velocity
- a = Relative acceleration

---

## Software Requirements

- Raspberry Pi Pico
- MicroPython
- Thonny IDE (recommended)

---

## Running the Project

1. Flash MicroPython firmware to Raspberry Pi Pico.
2. Copy all project files to the Pico.
3. Execute

```python
main.py
```

The controller continuously monitors the environment and updates the display and warning system in real time.

---

## Future Improvements

- Bluetooth communication between vehicles
- Vehicle-to-Vehicle (V2V) communication
- GPS integration
- Camera-based lane detection
- Machine learning for driving behavior prediction
- Automatic motor control
- Cloud-based telemetry logging

