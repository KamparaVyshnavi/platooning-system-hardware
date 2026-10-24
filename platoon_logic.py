"""
Core platooning logic shared by the main script and potential simulators.

Encapsulates:
    - distance smoothing
    - velocity / acceleration estimation
    - adaptive safe distance
    - state decision (STOP, FOLLOW, OVERTAKE, WAIT, BACK_ALERT)
"""

import utime


class PlatoonState:
    """Lightweight container for telemetry + decision outputs."""

    def __init__(
        self,
        timestamp_ms,
        distances,
        velocity,
        acceleration,
        state,
        alert,
    ):
        self.timestamp_ms = timestamp_ms
        self.distances = distances
        self.velocity = velocity
        self.acceleration = acceleration
        self.state = state
        self.alert = alert


class PlatoonController:
    def __init__(
        self,
        dmin_cm=10.0,
        gain=1.5,
        lane_clear_cm=30.0,
        back_clear_cm=35.0,
        back_alert_cm=20.0,
    ):
        self.dmin_cm = dmin_cm
        self.gain = gain
        self.lane_clear_cm = lane_clear_cm
        self.back_clear_cm = back_clear_cm
        self.back_alert_cm = back_alert_cm

        self._prev_time_ms = None
        self._prev_front = None
        self._prev_back = None
        self._prev_velocity = 0.0

    def _delta_t(self, now_ms):
        if self._prev_time_ms is None:
            self._prev_time_ms = now_ms
            return 0.1
        delta = (now_ms - self._prev_time_ms) / 1000.0
        self._prev_time_ms = now_ms
        return max(delta, 0.02)

    def update(self, front_cm, side_cm, back_cm):
        now_ms = utime.ticks_ms()
        dt = self._delta_t(now_ms)

        velocity = self._estimate_velocity(front_cm, dt)
        acceleration = self._estimate_acceleration(velocity, dt)

        safe_distance = self.dmin_cm + self.gain * abs(velocity)

        state, alert = self._decide_state(
            front_cm, side_cm, back_cm, velocity, acceleration, safe_distance, dt
        )

        return PlatoonState(
            now_ms,
            {"front": front_cm, "side": side_cm, "back": back_cm},
            velocity,
            acceleration,
            state,
            alert,
        )

    def _estimate_velocity(self, front_cm, dt):
        if front_cm is None or self._prev_front is None:
            self._prev_front = front_cm
            return 0.0
        velocity = (front_cm - self._prev_front) / dt
        self._prev_front = front_cm
        return velocity

    def _estimate_acceleration(self, velocity, dt):
        acceleration = (velocity - self._prev_velocity) / dt
        self._prev_velocity = velocity
        return acceleration

    def _back_velocity(self, back_cm, dt):
        if back_cm is None or self._prev_back is None:
            self._prev_back = back_cm
            return 0.0
        v = (back_cm - self._prev_back) / dt
        self._prev_back = back_cm
        return v

    def _decide_state(
        self, front_cm, side_cm, back_cm, velocity, acceleration, safe_distance, dt
    ):
        state = "CRUISE"
        alert = False

        if front_cm is None:
            return "FRONT SENSOR?", True

        front_close = front_cm < safe_distance
        approaching_fast = velocity < -8.0
        hard_brake = acceleration < -30.0

        if front_cm < self.dmin_cm + 3 or (front_close and (approaching_fast or hard_brake)):
            return "STOP", True

        if front_close:
            return "FOLLOW", False

        back_velocity = self._back_velocity(back_cm, dt)
        if back_cm is not None and (
            back_cm < self.back_alert_cm or back_velocity < -10.0
        ):
            return "BACK ALERT", True

        if side_cm is None:
            return "WAIT-SIDE?", True

        if side_cm < self.lane_clear_cm:
            state = "WAIT-LANE"
            alert = False
        else:
            if back_cm is not None and back_cm < self.back_clear_cm:
                state = "WAIT-REAR"
            else:
                state = "OVERTAKE"

        return state, alert

