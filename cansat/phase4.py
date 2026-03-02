#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import os
from Motor import robot

robot.initialize()

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
        camera = None  # finally で安全に参照するため初期化
        camera_available = True
        sensor_available = True

        # カメラセットアップ
        try:
            camera = Camera()
        except Exception as e:
            camera_available = False
            log_message(f"Camera init failed -> vision disabled ({e})")

        # 超音波センサセットアップ
        try:
            hcsr04_setup()
        except Exception as e:
            sensor_available = False
            log_message(f"HCSR04 init failed -> distance sensor disabled ({e})")

        # YOLOモデルのロード
        model_path = "/home/cansat-stu/cansat/camera/cone_100epochs.pt" 
        log_message(f"Loading YOLO model from {model_path}...")
        detector = ConeDetector(model_path)

        # パラメータ設定
        IMG_WIDTH = 2592
        CENTER_THRESHOLD = 400
        GOAL_DISTANCE_CM = 40.0
        GOAL_BBOX_AREA = 200000.0  # 距離センサ無し時の代替停止条件
        MIN_CONFIDENCE = 0.5
        ALLOWED_CLASS_IDS = None  # 例: {0} にするとクラス0のみ許可
        MAX_RUNTIME_SEC = 180
        NO_DETECTION_LIMIT = 5
        NO_PROGRESS_LIMIT = 8
        MIN_PROGRESS_CM = 5.0
        TURN_DURATION_SEC = 0.2
        SEARCH_TURN_SEC = 0.3

        img_center_x = IMG_WIDTH / 2
        threshold_left_limit = img_center_x - CENTER_THRESHOLD
        threshold_right_limit = img_center_x + CENTER_THRESHOLD

        start_time = time.time()
        last_distance = None
        no_detection_streak = 0
        no_progress_streak = 0

        while True:
            log_message("--- Start Loop ---")

            if time.time() - start_time > MAX_RUNTIME_SEC:
                log_message("Fail-safe: max runtime reached -> stopping")
                break

            target_cone = None
            direction = "none_cone"
            bbox_area = None

            if camera_available:
                try:
                    image_path = camera.capture_and_save()
                except Exception as e:
                    camera_available = False
                    log_message(f"Camera capture failed -> disabling vision ({e})")
                    image_path = None

                if not image_path:
                    log_message("Failed to capture image.")
                else:
                    # --- AI検出 ---
                    try:
                        result = detector.detect(image_path, show=False)
                        detections = result["detections"]
                        filtered = [
                            d for d in detections
                            if d.get("confidence", 0) >= MIN_CONFIDENCE
                            and (ALLOWED_CLASS_IDS is None or d.get("class_id") in ALLOWED_CLASS_IDS)
                        ]
                        if len(filtered) > 0:
                            target_cone = max(filtered, key=lambda x: x["size"]["width"] * x["size"]["height"])
                            bbox_area = target_cone["size"]["width"] * target_cone["size"]["height"]
                            log_message(f"Cone Detected! Confidence: {target_cone['confidence']:.2f} Area: {bbox_area:.0f}")
                            no_detection_streak = 0
                        else:
                            log_message("No cone detected.")
                            no_detection_streak += 1
                    except Exception as e:
                        camera_available = False
                        log_message(f"Detection failed -> disabling vision ({e})")
                        target_cone = None
                        bbox_area = None
            else:
                log_message("Vision disabled -> skipping detection")
                no_detection_streak += 1

            # --- 方向判定 ---
            if target_cone is not None:
                cx = target_cone["center"]["x"]
                log_message(f"Cone Center X: {cx:.1f}")

                if cx < threshold_left_limit:
                    direction = "Left"
                elif cx > threshold_right_limit:
                    direction = "Right"
                else:
                    direction = "Center"
            elif not camera_available and sensor_available:
                # 視覚が無い場合は距離センサで直進のみを試行
                direction = "ForwardBlind"

            # --- ロボット制御ロジック ---
            
            if direction == "Right": 
                # カメラ逆のため左旋回(要実機確認)
                log_message("Cone is Right -> Turning Left (Adjust)") 
                #robot.turn(-5)
                robot.turn(5)
                time.sleep(TURN_DURATION_SEC)
                robot.stop()
                time.sleep(0.5)

            elif direction == "Left":
                # カメラ逆のため右旋回(要実機確認)
                log_message("Cone is Left -> Turning Right (Adjust)")
                #robot.turn(5)
                robot.turn(-8)
                time.sleep(TURN_DURATION_SEC)
                robot.stop()
                time.sleep(0.5)

            elif direction == "none_cone":
                log_message("Searching mode (None_cone)")
                # 検出が続かない場合は長めに探索旋回
                spin_time = SEARCH_TURN_SEC if no_detection_streak >= NO_DETECTION_LIMIT else TURN_DURATION_SEC
                robot.turn(10) # 探索旋回
                time.sleep(spin_time)
                robot.stop()
                time.sleep(0.5)

            elif direction == "ForwardBlind":
                log_message("Vision disabled, distance sensor only -> moving forward cautiously")
                if sensor_available:
                    current_distance = get_stable_distance(
                        sample_count=3,
                        min_cm=5.0,
                        max_cm=500.0,
                        max_jump_cm=150.0,
                        prev_distance=last_distance,
                    )
                    if current_distance is not None and current_distance <= GOAL_DISTANCE_CM:
                        log_message("Distance goal reached (blind mode)")
                        robot.stop()
                        break
                    robot.move(0.5, 0.5)
                    time.sleep(0.5)
                    robot.stop()
                    time.sleep(0.5)
                    last_distance = current_distance if current_distance is not None else last_distance
                else:
                    log_message("No sensors available -> stopping")
                    robot.stop()
                    break

            elif direction == "Center":
                log_message("Cone is Center -> Checking Distance...")

                # 3. 安全ロジック: 動く前にまず距離を測る
                # 2. get_stable_distance を使用 (3回測定して中央値をとる)
                if sensor_available:
                    current_distance = get_stable_distance(
                        sample_count=3,
                        min_cm=5.0,
                        max_cm=500.0,
                        max_jump_cm=150.0,
                        prev_distance=last_distance,
                    )
                else:
                    current_distance = None

                if current_distance is None and sensor_available:
                    # センサエラー時は視覚の近接判定にフォールバック
                    log_message("Distance measurement failed -> fallback to vision-only close check")
                elif current_distance is None and not sensor_available:
                    log_message("Distance sensor unavailable -> vision-only close check")

                if current_distance is not None:
                    log_message(f"Distance to cone: {current_distance:.1f} cm")
                    if last_distance is not None and current_distance >= last_distance - MIN_PROGRESS_CM:
                        no_progress_streak += 1
                    else:
                        no_progress_streak = 0

                    # ゴール判定 (距離センサ使用)
                    if current_distance <= GOAL_DISTANCE_CM:
                        log_message("Target Close! Finishing Approach.")
                        robot.move(0.8, 0.8)
                        time.sleep(0.2)
                        robot.stop()
                        log_message("GOAL REACHED!")
                        break

                    # まだ遠いので前進する
                    log_message("Approaching Target...")
                    step_time = min(0.6, max(0.2, current_distance / 200.0))
                    robot.move(0.8, 0.8)
                    time.sleep(step_time)
                    robot.stop()
                    time.sleep(0.5)
                    last_distance = current_distance
                else:
                    # 距離センサなし: バウンディングボックス面積で近接判定
                    if bbox_area is not None and bbox_area >= GOAL_BBOX_AREA:
                        log_message("BBox area goal reached (vision-only)")
                        robot.move(0.6, 0.6)
                        time.sleep(0.5)
                        robot.stop()
                        break
                    log_message("Vision-only approach...")
                    robot.move(0.7, 0.7)
                    time.sleep(0.5)
                    robot.stop()
                    time.sleep(0.5)
                    no_progress_streak = 0  # 面積利用時はリセット

                # 進まない/計測に異常が続く場合は再探索へ戻す
                if no_progress_streak >= NO_PROGRESS_LIMIT:
                    log_message("Fail-safe: no progress -> back to search spin")
                    robot.turn(40)
                    time.sleep(SEARCH_TURN_SEC)
                    robot.stop()
                    no_progress_streak = 0

            # 連続未検出が続いたら探索に戻る（方向に関係なく）
            if no_detection_streak >= NO_DETECTION_LIMIT and direction != "none_cone":
                log_message("Fail-safe: forcing search spin after long no-detection")
                robot.turn(40)
                time.sleep(SEARCH_TURN_SEC)
                robot.stop()
                no_detection_streak = 0

            # ループ末尾の待機
            time.sleep(0.01)

    except KeyboardInterrupt:
        log_message("Interrupted by User")
    except Exception as e:
        log_message(f"Critical Error: {e}")
        import traceback
        log_message(traceback.format_exc()) # エラー詳細をログに残す
    finally:
        # 終了処理
        try:
            if camera:
                camera.stop_camera()
        except Exception:
            pass
        try:
            robot.stop()
        except Exception:
            pass
        log_message("Phase 4 completed.")
        # ファイルを閉じる
        if log_file:
            log_file.close()

if __name__ == "__main__":
    phase4()
