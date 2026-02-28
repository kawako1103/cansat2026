import threading
from gpiozero import PWMOutputDevice
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

# Motor Pin
PIN_AIN1 = 27
PIN_AIN2 = 22
PIN_BIN1 = 13
PIN_BIN2 = 19

dcm_pins = {
    "right_backward": PIN_AIN2,
    "right_forward": PIN_AIN1,
    "left_backward": PIN_BIN2,
    "left_forward": PIN_BIN1,
}


class MotorPWM:
    def __init__(
        self, forward_pin, backward_pin, pwm_frequency=16000, pin_factory=None
    ):
        self.forward = PWMOutputDevice(
            forward_pin, frequency=pwm_frequency, pin_factory=pin_factory
        )
        self.backward = PWMOutputDevice(
            backward_pin, frequency=pwm_frequency, pin_factory=pin_factory
        )
        # Initialize _value
        self._value = 0.0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, speed):
        self._value = speed
        if speed > 0:
            self.forward.value = speed
            self.backward.value = 0
        elif speed < 0:
            self.forward.value = 0
            self.backward.value = -speed
        else:
            self.forward.value = 0
            self.backward.value = 0


def smooth_transition(
    motor_left,
    motor_right,
    target_value_left,
    target_value_right,
    step=0.01,
    delay=0.02,
):
    current_value_left = motor_left.value
    current_value_right = motor_right.value

    while (
        current_value_left != target_value_left
        or current_value_right != target_value_right
    ):
        if current_value_left < target_value_left:
            current_value_left = min(current_value_left + step, target_value_left)
        else:
            current_value_left = max(current_value_left - step, target_value_left)

        if current_value_right < target_value_right:
            current_value_right = min(current_value_right + step, target_value_right)
        else:
            current_value_right = max(current_value_right - step, target_value_right)

        thread_left = threading.Thread(
            target=set_motor_values, args=(motor_left, current_value_left)
        )
        thread_right = threading.Thread(
            target=set_motor_values, args=(motor_right, current_value_right)
        )

        thread_left.start()
        thread_right.start()

        thread_left.join()
        thread_right.join()

        sleep(delay)


def set_motor_values(motor, value):
    motor.value = value


# motor's max duty is "duty" and motor will rotate for "time" seconds in this method, motor won't stop.
def move(left_duty, right_duty, time):
    factory = PiGPIOFactory()
    motor_left = MotorPWM(
        forward_pin=dcm_pins["left_forward"],
        backward_pin=dcm_pins["left_backward"],
        pin_factory=factory,
    )
    motor_right = MotorPWM(
        forward_pin=dcm_pins["right_forward"],
        backward_pin=dcm_pins["right_backward"],
        pin_factory=factory,
    )

    # motor will be rotated when duty is more than 0.5
    # therefore if you input the duty, motor should rotate absolutely
    # ex:if you input duty = 0 or duty = 0.5 or duty = 1.0, duty ratio is 0.5, 0.75, 1 respectively.
    left_duty_ratio = 0.5 * (1 + left_duty)
    right_duty_ratio = 0.5 * (1 + right_duty)

    try:
        print("Top Speed Rotation")
        smooth_transition(
            motor_left, motor_right, 1.0 * left_duty_ratio, 1.0 * right_duty_ratio
        )  # previous 1,0
        # smooth_transition(motor_right, 1.0 * duty_ratio)
        sleep(time)

    except KeyboardInterrupt:
        print("stop")
        motor_left.value = 0.0
        motor_right.value = 0.0


def stop():
    factory = PiGPIOFactory()
    motor_left = MotorPWM(
        forward_pin=dcm_pins["left_forward"],
        backward_pin=dcm_pins["left_backward"],
        pin_factory=factory,
    )
    motor_right = MotorPWM(
        forward_pin=dcm_pins["right_forward"],
        backward_pin=dcm_pins["right_backward"],
        pin_factory=factory,
    )

    try:
        print("Reverse Rotation 2s")
        smooth_transition(motor_left, motor_right, -0.5, -0.5)
        # smooth_transition(motor_right, -0.5)
        sleep(0.2)

        print("Nothing 5s")
        smooth_transition(motor_left, motor_right, 0.0, 0.0)
        # smooth_transition(motor_right, 0.0)
        sleep(0.5)

    except KeyboardInterrupt:
        print("stop")
        motor_left.value = 0.0
        motor_right.value = 0.0


if __name__ == "__main__":
    # move_forward should be used with motor_stop()
    # move_forward(duty, time)
    move(0.75, 0.74, 6.0)  # left + 0.01 # 4 m or less or more
    move(1.0, 0.7, 3.0)
    # stop
    print("stop")
    stop()
