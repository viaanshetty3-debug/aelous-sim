"""Unit and functional tests for AEOLUS tabletop hardware control logic.

Validates the state machine transitions, PWM duty ramps, vorticity reduction
calculations, and safety triggers defined in main.ino and HARDWARE_PLAN.md.
"""

import pytest


class AeolusHardwareController:
    """Python reference simulator for the Arduino Mega firmware logic."""

    INTERVENTION_DURATION = 30000  # ms
    POST_DECAY_DURATION = 40000    # ms
    COOL_DOWN_DURATION = 30000     # ms

    def __init__(self):
        self.state = "IDLE"
        self.state_enter_time = 0
        self.exhaust_pwm = 0
        self.vacuum_pwm = 0
        self.heater_pwm = 0
        self.circulation_pwm = 0
        self.chamber_temp = 25.0
        self.heater_temps = [25.0] * 5
        self.vacuum_pressure = 0  # Pa
        self.vorticity_reduction = 0.0
        self.alarm_triggered = False
        self.alarm_message = ""
        self.main_relay = False

    def start_pressed(self, current_time=0):
        if self.state == "IDLE":
            self.state = "INITIALIZATION"
            self.state_enter_time = current_time
            self.main_relay = True

    def stop_pressed(self):
        self.all_systems_off()
        self.state = "IDLE"

    def all_systems_off(self):
        self.exhaust_pwm = 0
        self.vacuum_pwm = 0
        self.heater_pwm = 0
        self.circulation_pwm = 0
        self.main_relay = False

    def trigger_alarm(self, message):
        self.alarm_triggered = True
        self.alarm_message = message
        self.all_systems_off()
        self.state = "SHUTDOWN"

    def update_sensor_readings(self, chamber_temp=None, heater_temp=None, vacuum_pressure=None):
        if chamber_temp is not None:
            self.chamber_temp = chamber_temp
        if heater_temp is not None:
            self.heater_temps[0] = heater_temp
        if vacuum_pressure is not None:
            self.vacuum_pressure = vacuum_pressure

    def compute_vorticity_reduction(self):
        red = 100.0
        if self.vacuum_pressure < -100:
            eff = (self.vacuum_pressure - (-100)) / (-250 - (-100))
            red += 25.0 * eff
        if self.heater_temps[0] > 30.0:
            eff = (self.heater_temps[0] - 25.0) / 10.0
            red += 20.0 * eff
        self.vorticity_reduction = red
        return red

    def update(self, current_time):
        time_in_state = current_time - self.state_enter_time

        # Safety Checks
        if self.chamber_temp > 80.0:
            self.trigger_alarm("OVER-TEMPERATURE")
            return

        if self.state == "INITIALIZATION":
            if self.chamber_temp > 50.0:
                self.trigger_alarm("CHAMBER TOO HOT")
                return
            if time_in_state < 2000:
                self.exhaust_pwm = 51   # 20%
                self.vacuum_pwm = 25
            else:
                self.state = "PRE_VORTEX"
                self.state_enter_time = current_time

        elif self.state == "PRE_VORTEX":
            if time_in_state < 10000:
                ramp = time_in_state / 10000.0
                self.exhaust_pwm = int(192 * ramp)  # Ramp to 75%
                self.vacuum_pwm = int(50 + 25 * ramp)
            else:
                self.state = "INTERVENTION"
                self.state_enter_time = current_time

        elif self.state == "INTERVENTION":
            if time_in_state < self.INTERVENTION_DURATION:
                # Thermal ramp 0-5s, then hold 100%
                if time_in_state < 5000:
                    t_ramp = time_in_state / 5000.0
                else:
                    t_ramp = 1.0
                self.heater_pwm = int(255 * t_ramp)

                # Vacuum ramp 0-5s to 150 duty (~ -250 Pa)
                v_ramp = time_in_state / 5000.0 if time_in_state < 5000 else 1.0
                self.vacuum_pwm = int(150 * v_ramp)

                # Steady exhaust fan at 75%
                self.exhaust_pwm = 192

                # Decay phase in the final 5s of intervention (25s - 30s)
                if time_in_state > 25000:
                    decay = (time_in_state - 25000) / 5000.0
                    self.heater_pwm = int(255 * (1.0 - 0.7 * decay))
                    self.vacuum_pwm = int(150 * (1.0 - 0.4 * decay))

                self.compute_vorticity_reduction()
            else:
                self.state = "POST_DECAY"
                self.state_enter_time = current_time

        elif self.state == "POST_DECAY":
            if time_in_state < self.POST_DECAY_DURATION:
                self.heater_pwm = 76    # 30% hold
                self.vacuum_pwm = 90    # -150 Pa hold
                ramp = 1.0 - (0.25 * (time_in_state / self.POST_DECAY_DURATION))
                self.exhaust_pwm = int(192 * ramp)
                self.compute_vorticity_reduction()
            else:
                self.state = "COOL_DOWN"
                self.state_enter_time = current_time

        elif self.state == "COOL_DOWN":
            if time_in_state < self.COOL_DOWN_DURATION:
                ramp = 1.0 - (time_in_state / self.COOL_DOWN_DURATION)
                self.heater_pwm = int(76 * ramp)
                self.exhaust_pwm = int(128 * ramp)
                self.vacuum_pwm = 0
            else:
                self.state = "SHUTDOWN"
                self.all_systems_off()


# ============================================================
# TEST SUITE
# ============================================================

class TestAeolusHardwareLogic:
    """Test suite validating firmware state machine & actuation formulas."""

    def test_initial_state_idle(self):
        controller = AeolusHardwareController()
        assert controller.state == "IDLE"
        assert controller.exhaust_pwm == 0
        assert controller.heater_pwm == 0
        assert controller.vacuum_pwm == 0
        assert not controller.main_relay

    def test_startup_and_initialization(self):
        controller = AeolusHardwareController()
        controller.start_pressed(current_time=0)
        assert controller.state == "INITIALIZATION"
        assert controller.main_relay is True

        controller.update(current_time=1000)
        assert controller.exhaust_pwm == 51
        assert controller.vacuum_pwm == 25

        # After 2000ms, transitions to PRE_VORTEX
        controller.update(current_time=2000)
        assert controller.state == "PRE_VORTEX"

    def test_prevortex_fan_ramp(self):
        controller = AeolusHardwareController()
        controller.start_pressed(0)
        controller.update(2000)  # Enter PRE_VORTEX at t=2000ms

        controller.update(7000)
        assert controller.state == "PRE_VORTEX"
        assert 90 <= controller.exhaust_pwm <= 100

        controller.update(12000)
        assert controller.state == "INTERVENTION"

    def test_intervention_dual_activation_and_decay(self):
        controller = AeolusHardwareController()
        controller.state = "INTERVENTION"
        controller.state_enter_time = 0

        controller.update(2500)
        assert 120 <= controller.heater_pwm <= 135
        assert 70 <= controller.vacuum_pwm <= 80

        controller.update(10000)
        assert controller.heater_pwm == 255
        assert controller.vacuum_pwm == 150
        assert controller.exhaust_pwm == 192

        controller.update(27500)
        assert controller.heater_pwm < 255
        assert controller.vacuum_pwm < 150

        controller.update(30000)
        assert controller.state == "POST_DECAY"

    def test_vorticity_reduction_formula(self):
        controller = AeolusHardwareController()
        
        controller.update_sensor_readings(heater_temp=25.0, vacuum_pressure=0)
        red = controller.compute_vorticity_reduction()
        assert red == 100.0

        controller.update_sensor_readings(heater_temp=28.5, vacuum_pressure=-250)
        red = controller.compute_vorticity_reduction()
        assert red == pytest.approx(125.0, abs=0.1)

        controller.update_sensor_readings(heater_temp=25.0, vacuum_pressure=-203.8)
        red = controller.compute_vorticity_reduction()
        assert red == pytest.approx(117.3, abs=0.2)

    def test_emergency_overtemp_cutoff(self):
        controller = AeolusHardwareController()
        controller.start_pressed(0)
        controller.update(1000)

        controller.update_sensor_readings(chamber_temp=85.0)
        controller.update(1500)

        assert controller.alarm_triggered is True
        assert controller.state == "SHUTDOWN"
        assert controller.exhaust_pwm == 0
        assert controller.heater_pwm == 0
        assert controller.vacuum_pwm == 0
        assert controller.main_relay is False
        assert "OVER-TEMPERATURE" in controller.alarm_message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
