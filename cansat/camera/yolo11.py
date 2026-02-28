# -*- coding: utf-8 -*-
# detector.py

import time
from ultralytics import YOLO

class ConeDetector:
    def __init__(self, model_path="cone_100epochs.pt"):
        """
        Initialize the YOLO model.
        :param model_path: Path to the trained YOLO model.
        """
        self.model = YOLO(model_path)

    def detect(self, image_path, show=False):
        """
        Run object detection on the given image.
        :param image_path: Path to the image file.
        :param show: Display the detection result image if True.
        :return: A dictionary containing detection results.
        """
        # Record start time
        inference_start_time = time.time()

        # Run inference
        results = self.model(image_path)

        # Record end time
        inference_end_time = time.time()

        boxes = results[0].boxes
        names = results[0].names

        detections = []

        # Process each detected object
        for i, box in enumerate(boxes):
            coords = box.xyxy[0]
            x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]

            # Calculate bounding box size
            width = x2 - x1
            height = y2 - y1

            # Calculate center coordinates
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            # Extract class and confidence
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = names[class_id]

            # Append result
            detections.append({
                "index": i + 1,
                "class_id": class_id,
                "class_name": class_name,
                "confidence": confidence,
                "bbox": {
                    "x1": float(x1),
                    "y1": float(y1),
                    "x2": float(x2),
                    "y2": float(y2),
                },
                "size": {
                    "width": float(width),
                    "height": float(height),
                },
                "center": {
                    "x": float(center_x),
                    "y": float(center_y),
                }
            })

        # Calculate total inference time
        inference_time = inference_end_time - inference_start_time

        # Optionally show the result image
        if show:
            results[0].show()

        # Return results as a dictionary
        return {
            "image_path": image_path,
            "num_objects": len(boxes),
            "detections": detections,
            "inference_time": inference_time
        }


# ==============================
# Allow script execution directly
# ==============================

if __name__ == "__main__":
    """
    If this script is executed directly, run a sample detection.
    Modify the paths below as needed.
    """
    
    # Example model and image paths
    # 必要に応じてパスを修正してください
    MODEL_PATH = "cone_100epochs.pt"
    IMAGE_PATH = "/home/cansat-stu/cansat/camera/picture/20251101170059.jpg"

    print("Running detection as standalone script...\n")

    # クラスのインスタンス化と実行
    try:
        detector = ConeDetector(MODEL_PATH)
        result = detector.detect(IMAGE_PATH, show=True)

        print(f"\n--- Detected {result['num_objects']} objects ---")
        for obj in result["detections"]:
            print(obj)
        
        print(f"Inference time: {result['inference_time']:.4f} sec")

    except Exception as e:
        print(f"An error occurred: {e}")