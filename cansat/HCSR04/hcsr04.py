# -*- coding: utf-8 -*-
import gpiozero
import time
import numpy as np

# ピン設定 (phase4.pyでsetupが呼ばれていますが、gpiozeroは初期化時に設定します)
TRIG_PIN = 20
ECHO_PIN = 16


# グローバル変数としてセンサーを保持
sensor = None

def setup():
    """センサーの初期化"""
    global sensor
    if sensor is None:
        # gpiozeroのDistanceSensorを使用
        sensor = gpiozero.DistanceSensor(echo=ECHO_PIN, trigger=TRIG_PIN, max_distance=5.0)
        print("HC-SR04 Setup Complete")

def get_distance():
    """現在の距離をcm単位で返す (失敗時はNone)"""
    global sensor
    if sensor is None:
        setup()
    
    try:
        # gpiozeroは m 単位で返すので *100 で cm に変換
        val = sensor.distance
        if val is None:
            return None
        return val * 100
    except Exception as e:
        print(f"Sensor Error: {e}")
        return None

def get_stable_distance(
    sample_count=5,
    min_cm=5.0,
    max_cm=500.0,
    max_jump_cm=None,
    prev_distance=None,
):
    """安定した距離を取得し、異常値を除外して中央値を返す"""
    global sensor
    if sensor is None:
        setup()

    readings = []
    for _ in range(sample_count):
        d = get_distance()
        if d is None:
            time.sleep(0.05)
            continue

        # 範囲外は破棄
        if not (min_cm <= d <= max_cm):
            time.sleep(0.05)
            continue

        # 直前値からの急激なジャンプを除外（任意）
        if prev_distance is not None and max_jump_cm is not None:
            if abs(d - prev_distance) > max_jump_cm:
                time.sleep(0.05)
                continue

        readings.append(d)
        time.sleep(0.05)

    if not readings:
        return None

    # 中央値を採用してノイズを除去
    return float(np.median(readings))

if __name__ == '__main__':
    setup()
    try:
        while True:
            dist = get_distance()
            if dist:
                print(f"Distance: {dist:.1f} cm")
            time.sleep(1)
    except KeyboardInterrupt:
        pass
