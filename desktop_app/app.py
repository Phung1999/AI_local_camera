import sys
import os
import cv2
import yaml
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.camera import VideoCamera, find_available_cameras
from modules.detector import Detector
from modules.zone import Zone
from modules.storage import AlertStorage
from modules.notifier import TelegramNotifier

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QPushButton, QTextEdit, QLineEdit, QGroupBox,
                              QListWidget, QListWidgetItem, QMessageBox, QGridLayout,
                              QSpinBox, QComboBox, QFileDialog)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap

from desktop_app.widgets import CameraViewer


class SurveillanceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Surveillance System - Multi Camera")
        self.setGeometry(50, 50, 1400, 900)
        
        self.camera_viewers = {}
        self.storage = AlertStorage()
        self.detector = Detector(
            classes=['person', 'car', 'motorbike', 'dog', 'cat'],
            motion_threshold=500
        )
        self.notifier = TelegramNotifier()
        self.running = False
        self.selected_camera_for_zone = None
        
        self._load_config()
        self._init_ui()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all_cameras)
        
        self.on_camera_type_changed()
    
    def _load_config(self):
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {
                'camera': {'width': 640, 'height': 480},
                'detection': {'classes': ['person', 'car', 'motorbike', 'dog', 'cat'], 'motion_threshold': 500},
                'telegram': {'token': 'YOUR_TOKEN', 'chat_id': 'YOUR_CHAT_ID', 'cooldown_intrusion': 20, 'cooldown_fire': 10}
            }
        
        self.notifier.configure(self.config['telegram']['token'], self.config['telegram']['chat_id'])
        
        if self.config['telegram']['token'] != 'YOUR_TOKEN':
            self.telegram_status.setText("Connected")
            self.telegram_status.setStyleSheet("color: green; font-weight: bold;")
    
    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        
        left_panel = QVBoxLayout()
        right_panel = QVBoxLayout()
        
        camera_control_group = QGroupBox("Camera List")
        camera_control_layout = QVBoxLayout()
        
        self.camera_list_widget = QListWidget()
        self.camera_list_widget.setMaximumHeight(100)
        camera_control_layout.addWidget(self.camera_list_widget)
        
        camera_type_layout = QHBoxLayout()
        camera_type_layout.addWidget(QLabel("Loai:"))
        self.camera_type_combo = QComboBox()
        self.camera_type_combo.addItems([
            "Webcam/Generic", "Yoosee", "Hikvision", "Dahua", "Imou", "EZVIZ", "RTSP URL"
        ])
        self.camera_type_combo.currentIndexChanged.connect(self.on_camera_type_changed)
        camera_type_layout.addWidget(self.camera_type_combo)
        camera_control_layout.addLayout(camera_type_layout)
        
        self.webcam_widget = QWidget()
        self.webcam_layout = QHBoxLayout()
        self.webcam_layout.addWidget(QLabel("Camera ID:"))
        self.camera_id_input = QSpinBox()
        self.camera_id_input.setRange(0, 10)
        self.camera_id_input.setValue(0)
        self.webcam_layout.addWidget(self.camera_id_input)
        self.webcam_widget.setLayout(self.webcam_layout)
        camera_control_layout.addWidget(self.webcam_widget)
        
        self.ip_widget = QWidget()
        ip_layout = QGridLayout()
        ip_layout.addWidget(QLabel("IP:"), 0, 0)
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("192.168.1.100")
        ip_layout.addWidget(self.ip_input, 0, 1)
        ip_layout.addWidget(QLabel("Port:"), 1, 0)
        self.port_input = QLineEdit("554")
        ip_layout.addWidget(self.port_input, 1, 1)
        ip_layout.addWidget(QLabel("User:"), 2, 0)
        self.user_input = QLineEdit("admin")
        ip_layout.addWidget(self.user_input, 2, 1)
        ip_layout.addWidget(QLabel("Pass:"), 3, 0)
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Mat khau")
        ip_layout.addWidget(self.pass_input, 3, 1)
        self.ip_widget.setLayout(ip_layout)
        camera_control_layout.addWidget(self.ip_widget)
        
        self.rtsp_widget = QWidget()
        rtsp_layout = QHBoxLayout()
        rtsp_layout.addWidget(QLabel("RTSP URL:"))
        self.rtsp_input = QLineEdit()
        self.rtsp_input.setPlaceholderText("rtsp://user:pass@ip:port/path")
        rtsp_layout.addWidget(self.rtsp_input)
        self.rtsp_widget.setLayout(rtsp_layout)
        camera_control_layout.addWidget(self.rtsp_widget)
        
        btn_layout = QHBoxLayout()
        btn_scan = QPushButton("Scan")
        btn_scan.clicked.connect(self.scan_cameras)
        btn_layout.addWidget(btn_scan)
        
        btn_add = QPushButton("Add Camera")
        btn_add.clicked.connect(self.add_camera)
        btn_layout.addWidget(btn_add)
        
        btn_remove = QPushButton("Remove")
        btn_remove.clicked.connect(self.remove_camera)
        btn_layout.addWidget(btn_remove)
        camera_control_layout.addLayout(btn_layout)
        
        camera_control_group.setLayout(camera_control_layout)
        left_panel.addWidget(camera_control_group)
        
        self.view_grid = QGridLayout()
        self.view_container = QWidget()
        self.view_container.setLayout(self.view_grid)
        self.view_container.setStyleSheet("background: #2a2a2a; border: 1px solid gray;")
        left_panel.addWidget(self.view_container)
        
        control_layout = QHBoxLayout()
        self.btn_start_all = QPushButton("Start All")
        self.btn_start_all.clicked.connect(self.start_all)
        control_layout.addWidget(self.btn_start_all)
        
        self.btn_stop_all = QPushButton("Stop All")
        self.btn_stop_all.clicked.connect(self.stop_all)
        self.btn_stop_all.setEnabled(False)
        control_layout.addWidget(self.btn_stop_all)
        left_panel.addLayout(control_layout)
        
        left_panel.setStretchFactor(self.view_container, 1)
        main_layout.addLayout(left_panel, 3)
        
        telegram_group = QGroupBox("Telegram")
        telegram_layout = QVBoxLayout()
        
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.telegram_status = QLabel("Disconnected")
        self.telegram_status.setStyleSheet("color: red; font-weight: bold;")
        status_layout.addWidget(self.telegram_status)
        telegram_layout.addLayout(status_layout)
        
        telegram_layout.addWidget(QLabel("Token:"))
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Nhap Telegram Bot Token")
        telegram_layout.addWidget(self.token_input)
        
        telegram_layout.addWidget(QLabel("Chat ID:"))
        self.chat_id_input = QLineEdit()
        self.chat_id_input.setPlaceholderText("Nhap Chat ID")
        telegram_layout.addWidget(self.chat_id_input)
        
        btn_connect_layout = QHBoxLayout()
        self.btn_connect = QPushButton("Ket Noi")
        self.btn_connect.clicked.connect(self.connect_telegram)
        btn_connect_layout.addWidget(self.btn_connect)
        
        self.btn_test = QPushButton("Test")
        self.btn_test.clicked.connect(self.test_telegram)
        self.btn_test.setEnabled(False)
        btn_connect_layout.addWidget(self.btn_test)
        telegram_layout.addLayout(btn_connect_layout)
        
        telegram_layout.addWidget(QLabel("Thong bao tu dong khi co canh bao"))
        
        telegram_group.setLayout(telegram_layout)
        right_panel.addWidget(telegram_group)
        
        alerts_group = QGroupBox("Alert Logs")
        alerts_layout = QVBoxLayout()
        self.alerts_list = QListWidget()
        alerts_layout.addWidget(self.alerts_list)
        
        alerts_btn_layout = QHBoxLayout()
        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.load_alerts)
        alerts_btn_layout.addWidget(btn_refresh)
        
        btn_clear_alerts = QPushButton("Clear")
        btn_clear_alerts.clicked.connect(self.clear_alerts)
        alerts_btn_layout.addWidget(btn_clear_alerts)
        alerts_layout.addLayout(alerts_btn_layout)
        
        alerts_group.setLayout(alerts_layout)
        right_panel.addWidget(alerts_group)
        
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        right_panel.addWidget(log_group)
        
        main_layout.addLayout(right_panel, 1)
    
    def _update_view_grid(self):
        while self.view_grid.count():
            item = self.view_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        count = len(self.camera_viewers)
        if count == 0:
            return
        
        if count == 1:
            rows, cols = 1, 1
        elif count == 2:
            rows, cols = 1, 2
        elif count <= 4:
            rows, cols = 2, 2
        elif count <= 6:
            rows, cols = 2, 3
        elif count <= 9:
            rows, cols = 3, 3
        else:
            rows, cols = 4, 3
        
        for i, (cam_id, viewer) in enumerate(self.camera_viewers.items()):
            r = i // cols
            c = i % cols
            self.view_grid.addWidget(viewer, r, c)
    
    def on_camera_type_changed(self):
        camera_type = self.camera_type_combo.currentText()
        
        self.webcam_widget.setVisible(camera_type == "Webcam/Generic")
        self.ip_widget.setVisible(camera_type in ["Yoosee", "Hikvision", "Dahua", "Imou", "EZVIZ"])
        self.rtsp_widget.setVisible(camera_type == "RTSP URL")
    
    def scan_cameras(self):
        self.log("Scanning cameras...")
        self.camera_list_widget.clear()
        
        cameras = find_available_cameras(max_check=10, timeout=1)
        
        if cameras:
            for cam in cameras:
                item = QListWidgetItem(f"[{cam['id']}] {cam['name']}")
                item.setData(Qt.ItemDataRole.UserRole, cam['id'])
                self.camera_list_widget.addItem(item)
            self.log(f"Found {len(cameras)} camera(s)")
        else:
            self.camera_list_widget.addItem("No cameras found")
            self.log("No cameras found")
    
    def add_camera(self):
        camera_type = self.camera_type_combo.currentText()
        source = None
        label = camera_type
        
        if camera_type == "Webcam/Generic":
            source = self.camera_id_input.value()
        elif camera_type == "RTSP URL":
            source = self.rtsp_input.text().strip()
            if not source:
                QMessageBox.warning(self, "Loi", "Nhap RTSP URL")
                return
        else:
            ip = self.ip_input.text().strip()
            if not ip:
                QMessageBox.warning(self, "Loi", "Nhap dia chi IP")
                return
            
            port = self.port_input.text().strip() or "554"
            user = self.user_input.text().strip() or "admin"
            pwd = self.pass_input.text().strip()
            
            paths = {
                "Yoosee": "/onvif1",
                "Hikvision": "/Streaming/Channels/101",
                "Dahua": "/cam/realmonitor?channel=1&subtype=0",
                "Imou": "/live",
                "EZVIZ": "/avstream/ch01/main/av_stream"
            }
            
            auth = f"{user}:{pwd}@" if pwd else f"{user}@"
            source = f"rtsp://{auth}{ip}:{port}{paths.get(camera_type, '')}"
        
        try:
            cam_id = len(self.camera_viewers) + 1
            source_int = int(source) if isinstance(source, int) or (isinstance(source, str) and source.isdigit()) else source
            
            cam = VideoCamera(source=source_int if isinstance(source_int, int) else source)
            cam.start()
            
            detector = Detector(
                classes=self.config['detection']['classes'],
                motion_threshold=self.config['detection']['motion_threshold']
            )
            
            viewer = CameraViewer(cam_id)
            viewer.clicked.connect(self.on_camera_clicked)
            
            self.camera_viewers[cam_id] = {
                'camera': cam,
                'detector': detector,
                'viewer': viewer,
                'zone': Zone(),
                'source': source,
                'frame': None,
                'frame_count': 0,
                'last_fire_alert': 0,
                'last_intrusion_alert': {}
            }
            
            self._update_view_grid()
            self.log(f"Added {label}: {str(source)[:50]}...")
            
        except Exception as e:
            QMessageBox.critical(self, "Loi", f"Khong the ket noi camera: {e}")
    
    def remove_camera(self):
        if not self.camera_viewers:
            return
        
        cam_id = max(self.camera_viewers.keys())
        self._remove_camera(cam_id)
    
    def _remove_camera(self, cam_id):
        if cam_id in self.camera_viewers:
            self.camera_viewers[cam_id]['camera'].stop()
            del self.camera_viewers[cam_id]
            self._update_view_grid()
            self.log(f"Removed camera {cam_id}")
    
    def on_camera_clicked(self, cam_id):
        self.selected_camera_for_zone = cam_id
        self.log(f"Selected camera {cam_id} for zone drawing")
    
    def start_all(self):
        if not self.camera_viewers:
            QMessageBox.warning(self, "Warning", "Add at least one camera first")
            return
        
        self.running = True
        self.btn_start_all.setEnabled(False)
        self.btn_stop_all.setEnabled(True)
        self.timer.start(30)
        self.log("Started all cameras")
    
    def stop_all(self):
        self.running = False
        self.timer.stop()
        self.btn_start_all.setEnabled(True)
        self.btn_stop_all.setEnabled(False)
        self.log("Stopped all cameras")
    
    def update_all_cameras(self):
        if not self.running:
            return
        
        for cam_id, data in self.camera_viewers.items():
            frame = data['camera'].read()
            data['frame'] = frame
            data['viewer'].setFrame(frame)
            
            if frame is not None:
                data['frame_count'] += 1
                
                if data['detector'].detect_motion(frame):
                    objects = data['detector'].detect_objects(frame)
                    
                    if data['detector'].detect_fire(frame):
                        self._handle_fire(cam_id, frame)
                    
                    for obj in objects:
                        if obj['label'] in self.config['detection']['classes']:
                            if data['zone'].is_inside(obj['centroid']):
                                self._handle_intrusion(cam_id, frame, obj)
    
    def _handle_fire(self, cam_id, frame):
        current_time = datetime.now().timestamp()
        last_fire = self.camera_viewers[cam_id].get('last_fire_alert', 0)
        
        if current_time - last_fire < self.config['telegram']['cooldown_fire']:
            return
        
        self.camera_viewers[cam_id]['last_fire_alert'] = current_time
        self.log(f"[Cam {cam_id}] PHAT HIEN CHAY!")
        
        img_path = self._save_image(frame, f"cam{cam_id}_fire")
        
        self.storage.save_alert({
            "camera": cam_id,
            "type": "fire",
            "label": "fire",
            "image": img_path
        })
        
        self.notifier.send_fire_alert(frame)
        self.load_alerts()
    
    def _handle_intrusion(self, cam_id, frame, obj):
        label = obj['label']
        
        last_alert = self.camera_viewers[cam_id]['last_intrusion_alert'].get(label, 0)
        if datetime.now().timestamp() - last_alert < self.config['telegram']['cooldown_intrusion']:
            return
        
        self.camera_viewers[cam_id]['last_intrusion_alert'][label] = datetime.now().timestamp()
        
        self.log(f"[Cam {cam_id}] XAM NHAP: {label}")
        
        img_path = self._save_image(frame, f"cam{cam_id}_{label}")
        
        self.storage.save_alert({
            "camera": cam_id,
            "type": "intrusion",
            "label": label,
            "image": img_path
        })
        
        self.notifier.send_intrusion_alert(frame, label)
        self.load_alerts()
    
    def _save_image(self, frame, label):
        os.makedirs("data/captures", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/captures/{label}_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        return filename
    
    def connect_telegram(self):
        token = self.token_input.text().strip()
        chat_id = self.chat_id_input.text().strip()
        
        if not token or not chat_id:
            QMessageBox.warning(self, "Loi", "Vui long nhap Token va Chat ID")
            return
        
        self.notifier.configure(token, chat_id)
        
        if self.notifier.send_test():
            self.telegram_status.setText("Connected")
            self.telegram_status.setStyleSheet("color: green; font-weight: bold;")
            self.btn_test.setEnabled(True)
            self.log("Telegram connected")
            QMessageBox.information(self, "Thanh cong", "Ket noi Telegram thanh cong!")
        else:
            self.telegram_status.setText("Disconnected")
            self.telegram_status.setStyleSheet("color: red; font-weight: bold;")
            self.btn_test.setEnabled(False)
            QMessageBox.warning(self, "Loi", "Khong the ket noi Telegram")
    
    def test_telegram(self):
        if self.notifier.send_test():
            QMessageBox.information(self, "Thanh cong", "Tin nhan test da duoc gui!")
        else:
            QMessageBox.warning(self, "Loi", "Khong the gui tin nhan")
    
    def load_alerts(self):
        self.alerts_list.clear()
        alerts = self.storage.load_alerts()
        for alert in reversed(alerts[-50:]):
            cam = alert.get('camera', '?')
            self.alerts_list.addItem(f"{alert['time']} [Cam{cam}] [{alert['type']}] {alert['label']}")
    
    def clear_alerts(self):
        self.storage.clear_alerts()
        self.alerts_list.clear()
        self.log("Da xoa tat ca alerts")
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def closeEvent(self, event):
        self.stop_all()
        for cam_id in list(self.camera_viewers.keys()):
            self._remove_camera(cam_id)
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = SurveillanceApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
