#cansat/Motor/robot.py
from gpiozero import PWMOutputDevice, DigitalOutputDevice
import threading
import time

# ピン配置
PIN_AIN1 = 6  # 右モータ PWM
PIN_AIN2 = 5  # 右モータ DIR
PIN_BIN1 = 17 # 左モータ PWM
PIN_BIN2 = 4  # 左モータ DIR

# グローバル変数の初期化
R_IN1 = None
R_IN2 = None
L_IN1 = None
L_IN2 = None

MAX_DUTY = 0.8  # モータ保護

def initialize():
    global R_IN1, R_IN2, L_IN1, L_IN2
    
    # 既存のデバイスが開かれている場合は閉じる（二重エラー防止）
    if R_IN1 is not None:
        R_IN1.close()
        R_IN2.close()
        L_IN1.close()
        L_IN2.close()

    # test.py の設定を反映 (PWM周波数 8000Hz)
    R_IN1 = PWMOutputDevice(PIN_AIN1, frequency=8000)
    R_IN2 = DigitalOutputDevice(PIN_AIN2)
    L_IN1 = PWMOutputDevice(PIN_BIN1, frequency=8000)
    L_IN2 = DigitalOutputDevice(PIN_BIN2)
    
    stop()

# --- モータ制御用のヘルパー関数 ---
def set_right_motor(speed):
    """ 右モータの出力設定 (DRV8835 IN/IN制御想定) """
    # speedを -1.0 〜 1.0 の範囲に制限
    speed = max(-1.0, min(1.0, speed))
    
    if speed >= 0:
        # 前進
        R_IN2.off()
        R_IN1.value = speed
    else:
        # 後退 (IN2をHIGHにし、IN1(PWM)を反転させることで擬似的に後退PWMを作る)
        R_IN2.on()
        R_IN1.value = 1.0 + speed  # speedがマイナスなので実質 1.0 - abs(speed)

def set_left_motor(speed):
    """ 左モータの出力設定 (DRV8835 IN/IN制御想定) """
    # speedを -1.0 〜 1.0 の範囲に制限
    speed = max(-1.0, min(1.0, speed))
    
    if speed >= 0:
        # 前進
        L_IN2.off()
        L_IN1.value = speed
    else:
        # 後退
        L_IN2.on()
        L_IN1.value = 1.0 + speed

# --------------------------------

def move(target_speed, mtime, speed=0.2, step=0.02, right_bias=0.04):
    while target_speed > speed and mtime > 0.0:
        speed += step
        mtime -= step

        left_speed = min(speed, MAX_DUTY)
        right_speed = min(speed + right_bias, MAX_DUTY)

        set_left_motor(left_speed)
        set_right_motor(right_speed)

        time.sleep(step)

    time.sleep(abs(mtime))
    stop()
    return "00"

def turn(degree):
    mtime = abs(degree / 180.0)
    # turnの際の出力も MAX_DUTY=0.8 を適用する場合は 0.5 の部分を MAX_DUTY に置き換えて
    turn_speed = min(0.4, MAX_DUTY) 

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

def stop():
    if R_IN1 is not None:
        R_IN2.off()
        R_IN1.value = 0
        L_IN2.off()
        L_IN1.value = 0

if __name__ == "__main__":
    initialize()  # ピンのセットアップを実行
    
    # result = turn(100.0)
    
    result = move(0.75, 3)  
    print("Move result:", result)  
    
    result = stop()
    time.sleep(1)
    
    #result = turn(-90.0 / 5)
    result = turn(-90.0)
    print("Turn result:", result)  
    
    result = stop()
    time.sleep(1)
    
    #result = turn(-90.0 / 5)
    result = turn(90.0)
    print("Turn result:", result)  
    
    
    stop()
