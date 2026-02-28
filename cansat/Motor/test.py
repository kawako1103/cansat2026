#cansat/Motor/test.py

# from gpiozero import PWMOutputDevice
# import time

# pin = PWMOutputDevice(27)
# pin.value = 1.0
# time.sleep(10)
# pin.value = 0

# from gpiozero import PWMOutputDevice, DigitalOutputDevice
# import time

# # DRV8835 IN1/IN2制御想定
# AIN1 = PWMOutputDevice(6)
# AIN2 = DigitalOutputDevice(5)

# BIN1 = PWMOutputDevice(17)
# BIN2 = DigitalOutputDevice(4)

# # 片側前進
# AIN2.off()
# AIN1.value = 1.0   # 100% PWM

# BIN2.off()
# BIN1.value = 1.0

# time.sleep(3)

# AIN1.value = 0
# BIN1.value = 0

# ####
# # これは動くがRobotなのでPWMをいじれない
# from gpiozero import Robot
# import time

# robot = Robot(left=(17, 4), right=(6, 5))

# # 右だけ回す
# robot.right_motor.forward(0.05)

# # time.sleep(0.05)

# # 左だけ回す
# robot.left_motor.forward(0.05)

# time.sleep(3)

# robot.stop()
# ####


# #### PWMをいじるための
# from gpiozero import PWMOutputDevice, DigitalOutputDevice
# import time

# AIN1 = PWMOutputDevice(6, frequency=8000)
# AIN2 = DigitalOutputDevice(5)

# BIN1 = PWMOutputDevice(17, frequency=8000)
# BIN2 = DigitalOutputDevice(4)

# # 右モータのみ
# AIN2.off()
# AIN1.value = 0.5

# time.sleep(3)

# AIN1.value = 0

####
#これなら動きそう
from gpiozero import PWMOutputDevice, DigitalOutputDevice
import time

# ---- 右モータ ----
R_IN1 = PWMOutputDevice(6, frequency=8000)
R_IN2 = DigitalOutputDevice(5)

# ---- 左モータ ----
L_IN1 = PWMOutputDevice(17, frequency=8000)
L_IN2 = DigitalOutputDevice(4)

# 前進設定（IN1=PWM, IN2=LOW）
R_IN2.off()
L_IN2.off()

#dutyを0.9だと死ぬ 0.8までなら落ちなさそう
R_IN1.value = 0.8

L_IN1.value = 0.8

time.sleep(3)

# 停止
R_IN1.value = 0
L_IN1.value = 0
####