import cv2
import numpy as np
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QImage, QPixmap

from modules.zone import Zone


class CameraViewer(QWidget):
    clicked = pyqtSignal(int)
    
    def __init__(self, camera_id, parent=None):
        super().__init__(parent)
        self.camera_id = camera_id
        self.zone = Zone()
        self.zone_points = []
        self.setStyleSheet("border: 1px solid gray; background: #1a1a1a;")
        self.setMinimumSize(320, 240)
        
    def setFrame(self, frame):
        if frame is None:
            return
        
        display = frame.copy()
        
        if self.zone.polygon:
            poly = self.zone.polygon
            pts = np.array(poly.exterior.coords, dtype=np.int32)
            cv2.polylines(display, [pts], True, (0, 255, 0), 2)
        
        rgb_frame = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        qt_image = QImage(rgb_frame.data, w, h, ch * w, QImage.Format.Format_RGB888)
        scaled = qt_image.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
        self.setPixmap(QPixmap.fromImage(scaled))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.zone_points.append(QPoint(int(event.position().x()), int(event.position().y())))
            self.update()
            self.clicked.emit(self.camera_id)
        elif event.button() == Qt.MouseButton.RightButton:
            self.zone_points = []
            self.zone.clear()
            self.update()
    
    def paintEvent(self, event):
        if self.pixmap():
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self.pixmap())
            
            painter.setPen(QPen(Qt.GlobalColor.red, 2))
            if len(self.zone_points) > 1:
                for i in range(len(self.zone_points) - 1):
                    painter.drawLine(self.zone_points[i], self.zone_points[i + 1])
            if len(self.zone_points) > 2:
                painter.drawLine(self.zone_points[-1], self.zone_points[0])
            
            painter.setPen(QPen(Qt.GlobalColor.yellow, 6))
            for pt in self.zone_points:
                painter.drawPoint(pt)


class MultiCameraManager:
    def __init__(self):
        self.cameras = {}
        self.detector = None
        self.notifier = None
        self.storage = None
        self.config = None
        self.running = False
        self.lock = threading.Lock()
    
    def add_camera(self, cam_id, source, detector, notifier, storage, config):
        if cam_id in self.cameras:
            return False
        
        try:
            cam = VideoCamera(source=source)
            cam.start()
            
            self.cameras[cam_id] = {
                'camera': cam,
                'detector': detector,
                'notifier': notifier,
                'storage': storage,
                'config': config,
                'frame': None,
                'source': source,
                'frame_count': 0,
                'last_alert': 0
            }
            return True
        except Exception as e:
            print(f"Error adding camera {cam_id}: {e}")
            return False
    
    def remove_camera(self, cam_id):
        if cam_id in self.cameras:
            self.cameras[cam_id]['camera'].stop()
            del self.cameras[cam_id]
    
    def read_frames(self):
        with self.lock:
            for cam_id, data in self.cameras.items():
                frame = data['camera'].read()
                data['frame'] = frame
    
    def get_frame(self, cam_id):
        with self.lock:
            if cam_id in self.cameras:
                return self.cameras[cam_id]['frame']
        return None
    
    def stop_all(self):
        for cam_id in list(self.cameras.keys()):
            self.remove_camera(cam_id)


import threading
from modules.camera import VideoCamera
