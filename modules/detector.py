import cv2
import numpy as np
from ultralytics import YOLO


class MotionDetector:
    def __init__(self, threshold=500):
        self.fgbg = cv2.createBackgroundSubtractorMOG2()
        self.threshold = threshold

    def detect(self, frame):
        if frame is None:
            return False
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = self.fgbg.apply(gray)
        _, thresh = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        total_area = sum(cv2.contourArea(c) for c in contours if cv2.contourArea(c) > 100)
        
        return total_area > self.threshold


class ObjectDetector:
    def __init__(self, classes=None):
        if classes is None:
            classes = ["person", "car", "motorbike", "dog", "cat"]
        self.classes = classes
        self.model = YOLO("yolov8n.pt")

    def detect(self, frame):
        if frame is None:
            return []
        
        results = self.model(frame, verbose=False)[0]
        detections = []
        
        for box in results.boxes:
            cls_id = int(box.cls[0])
            label = self.model.names[cls_id]
            
            if label in self.classes:
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                
                detections.append({
                    "label": label,
                    "confidence": round(conf, 2),
                    "centroid": (cx, cy),
                    "box": [x1, y1, x2, y2]
                })
        
        return detections


class FireDetector:
    def __init__(self):
        self.lower_hsv = np.array([0, 120, 200])
        self.upper_hsv = np.array([50, 255, 255])
        self.min_area = 1000
        self.flicker_count = 0
        self.prev_motion = False
        self.motion_frames = 0

    def detect(self, frame):
        if frame is None:
            return False
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_hsv, self.upper_hsv)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        has_fire = False
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > self.min_area:
                has_fire = True
                break
        
        if has_fire != self.prev_motion:
            self.flicker_count += 1
        else:
            self.flicker_count = 0
        
        self.prev_motion = has_fire
        
        if has_fire:
            self.motion_frames += 1
        else:
            self.motion_frames = 0
        
        return has_fire and self.flicker_count >= 3 and self.motion_frames >= 2


class Detector:
    def __init__(self, classes=None, motion_threshold=500):
        self.motion = MotionDetector(threshold=motion_threshold)
        self.object = ObjectDetector(classes=classes)
        self.fire = FireDetector()
        self.last_motion = False

    def detect_motion(self, frame):
        self.last_motion = self.motion.detect(frame)
        return self.last_motion

    def detect_objects(self, frame):
        return self.object.detect(frame)

    def detect_fire(self, frame):
        return self.fire.detect(frame)


if __name__ == "__main__":
    import sys
    
    detector = Detector()
    
    img_path = sys.argv[1] if len(sys.argv) > 1 else "data/test.jpg"
    
    frame = cv2.imread(img_path)
    if frame is None:
        print(f"Không tìm thấy ảnh: {img_path}")
        print("Test với frame trắng...")
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    objects = detector.detect_objects(frame)
    print(f"Objects detected: {len(objects)}")
    for obj in objects:
        print(f"  - {obj['label']}: {obj['confidence']} at {obj['centroid']}")
    
    fire = detector.detect_fire(frame)
    print(f"Fire detected: {fire}")
