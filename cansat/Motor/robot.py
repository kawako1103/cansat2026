#cansat/Motor/robot.py
from gpiozero import PWMOutputDevice, DigitalOutputDevice
import time

# ピン配置
"""
# メインは使わないのでコメントアウト
PIN_AIN1 = 6  # 右モータ PWM R_MAIN_IO1 GPIO6
PIN_AIN2 = 5  # 右モータ DIR R_MAIN_IO2 GPIO5
PIN_BIN1 = 17 # 左モータ PWM L_MAIN_IO1 GPIO17
PIN_BIN2 = 4  # 左モータ DIR L_MAIN_IO2 GPIO4
"""

# サブのDRV8835用のピン配置を使う
PIN_AIN1 = 19 # 右モータ R_SUB_IO1 GPIO19
PIN_AIN2 = 13 # 右モータ R_SUB_IO2 GPIO13
PIN_BIN1 = 22 # 左モータ L_SUB_IO1 GPIO22
PIN_BIN2 = 27 # 左モータ L_SUB_IO2 GPIO27

# グローバル変数の初期化
R_IN1 = None
R_IN2 = None
L_IN1 = None
L_IN2 = None

MAX_DUTY = 0.8  # モータ保護

# (LIN1,LIN2) = (1,0) で前進、(0,1) で後退、(1,1) でブレーキ、(0,0) で空転

# モータを初期化し、事前に開いているデバイスがあれば安全に閉じる
def initialize():
    global R_IN1, R_IN2, L_IN1, L_IN2
    
    # 既存のデバイスが開かれている場合は閉じる（二重エラー防止）
    if R_IN1 is not None:
        R_IN1.close()
        R_IN2.close()
        L_IN1.close()
        L_IN2.close()

    # 4本すべてをPWMOutputDeviceにする (PWM周波数 8000Hz)
    R_IN1 = PWMOutputDevice(PIN_AIN1, frequency=8000)
    R_IN2 = PWMOutputDevice(PIN_AIN2, frequency=8000)
    L_IN1 = PWMOutputDevice(PIN_BIN1, frequency=8000)
    L_IN2 = PWMOutputDevice(PIN_BIN2, frequency=8000)
    stop()

# --- モータ制御用のヘルパー関数 ---
# speedは -1.0〜1.0 で受け取り、0以上で前進・0未満で後退を表現
# --- 新しいモータ制御関数（両方ブレーキベース） ---
def set_right_motor(speed):
    speed = max(-1.0, min(1.0, speed))
    
    if speed >= 0:
        # 前進 (IN1を常にHIGHにし、IN2で反転PWMをかける)
        # 1.0と1.0でブレーキ、1.0と0.0で前進となる
        R_IN1.value = 1.0
        R_IN2.value = 1.0 - speed
    else:
        # 後退 (IN2を常にHIGHにし、IN1で反転PWMをかける)
        R_IN1.value = 1.0 - abs(speed)
        R_IN2.value = 1.0

def set_left_motor(speed):
    speed = max(-1.0, min(1.0, speed))
    
    if speed >= 0:
        # 前進
        L_IN1.value = 1.0
        L_IN2.value = 1.0 - speed
    else:
        # 後退
        L_IN1.value = 1.0 - abs(speed)
        L_IN2.value = 1.0

def stop():
    if R_IN1 is not None:
        # 停止時はすべて0（空転）にして完全に電源を落とす
        R_IN1.value = 0
        R_IN2.value = 0
        L_IN1.value = 0
        L_IN2.value = 0
# --------------------------------

def move(target_speed, mtime, speed=0.2, step=0.02, left_bias = 0.00,right_bias=0.00):
    # 目標速度まで滑らかに加速しつつ走行時間を消化（右モータに僅かな補正）
    while target_speed > speed and mtime > 0.0:
        speed += step
        mtime -= step

        left_speed = min(speed + left_bias, MAX_DUTY)*1.015
        right_speed = min(speed + right_bias, MAX_DUTY)

        set_left_motor(left_speed)
        set_right_motor(right_speed)

        time.sleep(step)

    time.sleep(abs(mtime))
    stop()
    return "00"

def turn(degree):
    # 正の値で右旋回、負の値で左旋回。degreeの大きさに応じて回転時間を計算
    mtime = abs(degree / 180.0)
    # turnの際の出力も MAX_DUTY=0.8 を適用する場合は 0.5 の部分を MAX_DUTY に置き換えて
    turn_speed = min(0.5, MAX_DUTY) 

    if degree > 0.0:
        # 右旋回: 左前進、右後退
        set_left_motor(turn_speed)
        set_right_motor(-turn_speed)
        time.sleep(mtime)
        stop()
        return "01"
    else:
        # 左旋回: 左後退、右前進
        set_left_motor(-turn_speed)
        set_right_motor(turn_speed)
        time.sleep(mtime)
        stop()
        return "10"

if __name__ == "__main__":
    initialize()  # ピンのセットアップを実行
    
    result = move(0.75, 3)
    print("Move result:", result)  
    time.sleep(1)  # 少し待ってから旋回
"""    
    result = turn(-90.0) # 左90度旋回
    print("Turn result:", result)  
    time.sleep(1)  # 少し待ってから次の旋回

    result = turn(90.0) # 右90度旋回
    print("Turn result:", result)  
    stop()
"""