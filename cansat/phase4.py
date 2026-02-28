#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import os
from Motor import robot

# 1. ディレクトリ構成に合わせたインポート
# フォルダ構成:
#   phase4.py
#   camera/
#     camera.py
#     yolo11.py
#   HCSR04/
#     hcsr04.py
try:
    from camera.camera import Camera
    from camera.yolo11 import ConeDetector
    # 2. get_stable_distance をインポートに追加
    from HCSR04.hcsr04 import get_stable_distance, setup as hcsr04_setup
except ImportError as e:
    print(f"Import Error: {e}")
    print("ディレクトリ構成やファイル名が正しいか確認してください。")
    # テスト用にパスが見つからない場合のフォールバックが必要ならここに記述
    raise

def phase4():
    # ログファイル名の生成
    log_filename = os.path.join(os.path.dirname(__file__), f"phase4_{time.strftime('%Y%m%d')}.log")
    
    # 4. ログファイルを一度だけ開き、最後に閉じるように変更
    # 'buffering=1' で行ごとにバッファリング（書き込み漏れ防止）
    log_file = open(log_filename, "a", buffering=1)

    def log_message(message):
        """内部関数: 開いているファイルにログを書き込む"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        full_msg = f"{timestamp} - {message}"
        print(message)
        try:
            log_file.write(full_msg + "\n")
            log_file.flush() # 強制書き込み（突然の電源断対策）
        except Exception as e:
            print(f"Log Write Error: {e}")

    log_message("Initializing Phase 4...")

    # 各モジュールの初期化
    try:
        # カメラセットアップ
        camera = Camera()

        # 超音波センサセットアップ
        hcsr04_setup()

        # YOLOモデルのロード
        model_path = "cone_100epochs.pt" 
        log_message(f"Loading YOLO model from {model_path}...")
        detector = ConeDetector(model_path)

        # パラメータ設定
        IMG_WIDTH = 2592
        CENTER_THRESHOLD = 400 
        img_center_x = IMG_WIDTH / 2
        threshold_left_limit = img_center_x - CENTER_THRESHOLD
        threshold_right_limit = img_center_x + CENTER_THRESHOLD

        while True:
            log_message("--- Start Loop ---")

            # --- 撮影 ---
            image_path = camera.capture_and_save()
            if not image_path:
                log_message("Failed to capture image.")
                continue

            # --- AI検出 ---
            result = detector.detect(image_path, show=False)
            detections = result["detections"]
            target_cone = None

            if len(detections) > 0:
                # 一番大きく写っているコーンをターゲットにする
                target_cone = max(detections, key=lambda x: x["size"]["width"] * x["size"]["height"])
                log_message(f"Cone Detected! Confidence: {target_cone['confidence']:.2f}")
            else:
                log_message("No cone detected.")

            # --- 方向判定 ---
            if target_cone is None:
                direction = "none_cone"
            else:
                cx = target_cone["center"]["x"]
                log_message(f"Cone Center X: {cx:.1f}")

                if cx < threshold_left_limit:
                    direction = "Left"
                elif cx > threshold_right_limit:
                    direction = "Right"
                else:
                    direction = "Center"

            # --- ロボット制御ロジック ---
            
            if direction == "Right": 
                # カメラ逆のため左旋回(要実機確認)
                log_message("Cone is Right -> Turning Left (Adjust)") 
                robot.turn(-20) 
                time.sleep(0.5)
                robot.stop()
                time.sleep(1)

            elif direction == "Left":
                # カメラ逆のため右旋回(要実機確認)
                log_message("Cone is Left -> Turning Right (Adjust)")
                robot.turn(15) 
                time.sleep(0.5)
                robot.stop()
                time.sleep(1)

            elif direction == "none_cone":
                log_message("Searching mode (None_cone)")
                robot.turn(40) # 探索旋回
                time.sleep(0.5)
                robot.stop()
                time.sleep(1)

            elif direction == "Center":
                log_message("Cone is Center -> Checking Distance...")

                # 3. 安全ロジック: 動く前にまず距離を測る
                # 2. get_stable_distance を使用 (3回測定して中央値をとる)
                current_distance = get_stable_distance(sample_count=3)

                if current_distance is None:
                    # センサエラー時は進まない
                    log_message("Distance measurement failed/timeout -> SKIP moving")
                    robot.stop()
                    # 必要であれば少し待機
                    time.sleep(0.5)
                    continue

                log_message(f"Distance to cone: {current_distance:.1f} cm")

                # ゴール判定 (40cm以下)
                if current_distance <= 40.0:
                    log_message("Target Close! Finishing Approach.")
                    
                    # 最後の詰め
                    robot.move(0.8, 0.8)
                    time.sleep(1)
                    robot.stop()

                    log_message("GOAL REACHED!")
                    break # ループを抜ける
                
                else:
                    # まだ遠いので前進する
                    log_message("Approaching Target...")
                    robot.move(0.8, 0.8)
                    time.sleep(1) # 距離に応じて調整してください
                    robot.stop()
                    time.sleep(1)

            # ループ末尾の待機
            time.sleep(1)

    except KeyboardInterrupt:
        log_message("Interrupted by User")
    except Exception as e:
        log_message(f"Critical Error: {e}")
        import traceback
        log_message(traceback.format_exc()) # エラー詳細をログに残す
    finally:
        # 終了処理
        camera.stop_camera()
        robot.stop()
        log_message("Phase 4 completed.")
        # ファイルを閉じる
        if log_file:
            log_file.close()

if __name__ == "__main__":
    phase4()