#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import os
from datetime import datetime
from picamera2 import Picamera2
from libcamera import Transform

class Camera:
    def __init__(self, save_dir="/home/cansat-stu/cansat/camera/picture", resolution=(2592, 1944)):
        self.save_dir = save_dir
        self.resolution = resolution
        self.picam2 = None
        self.setup_camera()

    def setup_camera(self):
        """カメラの初期化を一度だけ行う"""
        try:
            print("Initializing Camera...")
            self.picam2 = Picamera2()
            # ﾂ嘉ｱﾂ転ﾂ設津ｨ (rotation=180)
            config = self.picam2.create_still_configuration(
                main={"size": self.resolution},
                transform=Transform(rotation=180)
            )
            self.picam2.configure(config)
            self.picam2.start()
            print("Camera Initialized.")
            # ﾂ露ﾂ出ﾂ暗ﾂ津ｨﾂのつｽﾂめの待機
            time.sleep(2) 
        except Exception as e:
            print(f"Camera Init Error: {e}")

    def capture_and_save(self):
        """画像を撮影して保存し、ファイルパスを返す"""
        try:
            os.makedirs(self.save_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}.jpg"
            full_path = os.path.join(self.save_dir, filename)

            if self.picam2:
                # capture_file ﾂは画像ﾂづｰﾂフﾂァﾂイﾂδ仰に保堕ｶ
                self.picam2.capture_file(full_path)
                print(f"Saved: {filename}")
                return full_path
            else:
                print("Camera not initialized.")
                return None
        except Exception as e:
            print(f"Capture Error: {e}")
            return None

    def stop_camera(self):
        if self.picam2:
            self.picam2.stop()
            print("Camera Stopped.")

if __name__ == "__main__":
    cam = Camera()
    cam.capture_and_save()
    cam.stop_camera()