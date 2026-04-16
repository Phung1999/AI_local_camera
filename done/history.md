# AI Surveillance System - History

## Ngày bắt đầu: 2026-04-16

## Các bước đã thực hiện:

### Step 1: Tạo cấu trúc dự án + requirements.txt
- [x] Tạo thư mục: data/, modules/, desktop_app/
- [x] Tạo requirements.txt với các thư viện cần thiết
- [x] Tạo config.yaml với cấu hình mặc định
- [x] Tạo data/alerts.json (file rỗng)

### Step 2: Module camera.py (VideoCamera)
- [x] Class VideoCamera với thread đọc frame
- [x] Hỗ trợ webcam/RTSP
- [x] Resize 640x480
- [x] Methods: start(), read(), stop()
- [x] Hàm find_available_cameras() tìm camera tự động

### Step 3: Module detector.py (Motion + YOLO + Fire)
- [x] MotionDetector: MOG2 background subtraction
- [x] ObjectDetector: YOLOv8n detection (person, car, motorbike, dog, cat)
- [x] FireDetector: HSV color detection với flicker logic
- [x] Class Detector tổng hợp

### Step 4: Module zone.py (Shapely Polygon)
- [x] Class Zone với ray casting algorithm (không dùng shapely)
- [x] Method is_inside() kiểm tra điểm trong vùng
- [x] Methods set_polygon(), clear()

### Step 5: Module storage.py (AlertStorage)
- [x] Class AlertStorage với JSON file
- [x] Methods: save_alert(), load_alerts(), clear_alerts()
- [x] Auto-create file nếu chưa có

### Step 6: Module notifier.py (Telegram)
- [x] Class TelegramNotifier với urllib (không dùng telepot)
- [x] Cooldown riêng cho intrusion (20s) và fire (10s)
- [x] Methods: send_intrusion_alert(), send_fire_alert(), send_test()

### Step 7: Desktop App PyQt6 (desktop_app/app.py)
- [x] Giao diện chính với PyQt6
- [x] Camera Control: Start/Stop, nhập RTSP
- [x] Live View: Hiển thị video realtime (QLabel + OpenCV)
- [x] Zone Drawing: Click chuột tạo polygon
- [x] Alert Logs: Load từ alerts.json, nút Clear alerts
- [x] Log panel hiển thị trạng thái
- [x] Hỗ trợ nhiều camera cùng lúc (Multi-Camera)
- [x] Tự động sắp xếp grid theo số lượng camera (1x1, 1x2, 2x2, 2x3, 3x3)
- [x] Zone riêng cho mỗi camera
- [x] Alert ghi rõ camera nào phát hiện
- [x] Telegram: Nhập Token/Chat ID, nút Kết nối, Test
- [x] Quet QR code (webcam hoặc file)
- [x] ComboBox chọn loại camera: Webcam, Yoosee, Hikvision, Dahua, Imou, EZVIZ, RTSP
- [x] Form nhập riêng theo loại camera (IP, Port, User, Pass)

### Step 8-9: Core Loop + Anti-Spam Logic
- [x] Tích hợp trong SurveillanceApp
- [x] Flow: Camera → Motion Detection → YOLO → Fire Detect → Zone Check
- [x] Fire ưu tiên cao nhất
- [x] Intrusion cooldown 20s, Fire cooldown 10s

### Step 10-11: Integration + main.py
- [x] Tạo main.py entry point
- [x] Load config từ config.yaml
- [x] Kết nối tất cả modules

## Cấu trúc dự án hoàn chỉnh:
```
AI_local_camera/
├── main.py
├── config.yaml
├── requirements.txt
├── data/
│   ├── alerts.json
│   └── captures/
├── modules/
│   ├── __init__.py
│   ├── camera.py
│   ├── detector.py
│   ├── zone.py
│   ├── storage.py
│   └── notifier.py
└── desktop_app/
    ├── __init__.py
    ├── widgets.py      # CameraViewer, MultiCameraManager
    └── app.py          # SurveillanceApp (gọn hơn)
```

## Cách chạy:

### Với conda (khuyến nghị):
```bash
conda create -n ai_surveillance python=3.12 -y
conda activate ai_surveillance
pip install opencv-python ultralytics pyqt6 pyyaml
python main.py
```

### Hoặc sử dụng Python 3.10-3.12 trực tiếp:
```bash
pip install -r requirements.txt
python main.py
```

## Hoàn thành: 2026-04-16

## Ghi chú tương thích Python 3.15:
- zone.py: Viết lại không dùng shapely (dùng ray casting algorithm)
- notifier.py: Viết lại không dùng telepot (dùng urllib)
- requirements.txt: Loại bỏ shapely và telepot
- Python 3.15 alpha chưa có wheels cho numpy → cần dùng conda với Python 3.12
