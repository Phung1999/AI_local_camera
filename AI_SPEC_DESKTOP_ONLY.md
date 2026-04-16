# AI Surveillance System - Desktop Only Version (No API)

---

# GLOBAL RULE

* Mỗi STEP:

  1. Code xong
  2. Test ngay
  3. Chạy độc lập
* Code theo OOP
* Không phụ thuộc Flask / API

---

# PROJECT STRUCTURE

```bash
project/
│── main.py
│── config.yaml
│── data/
│    └── alerts.json
│── modules/
│    ├── camera.py
│    ├── detector.py
│    ├── zone.py
│    ├── notifier.py
│    ├── storage.py
│── desktop_app/
│    └── app.py
```

---

# STEP 1: Requirements

## requirements.txt

```txt
opencv-python
ultralytics
pyqt6
telepot
shapely
pyyaml
```

## Test

```bash
pip install -r requirements.txt
```

---

# STEP 2: Camera Module

## File: modules/camera.py

## Class: VideoCamera

### Features:

* Webcam / RTSP
* Thread đọc frame
* Resize 640x480

## Methods:

```python
start()
read()
stop()
```

## Test:

* Hiển thị camera bằng cv2.imshow

---

# STEP 3: AI Detection

## File: modules/detector.py

## Task:

* Load yolov8n.pt
* Detect:

  * person
  * dog
  * cat

## Output:

```python
[
  {
    "label": "person",
    "confidence": 0.92,
    "centroid": (x, y)
  }
]
```

## Test:

* Detect từ ảnh

---

# STEP 4: Zone Logic

## File: modules/zone.py

## Task:

* Dùng shapely:

```python
Polygon
Point
```

## Function:

```python
is_inside_zone(point, polygon)
```

## Test:

* Check điểm inside/outside

---

# STEP 5: Storage (JSON Local DB)

## File: modules/storage.py

## File lưu:

```bash
data/alerts.json
```

## Format:

```json
[
  {
    "time": "2026-01-01 10:00:00",
    "label": "person",
    "image": "data/img_001.jpg"
  }
]
```

## Class: AlertStorage

### Methods:

```python
save_alert(data)
load_alerts()
```

## Task:

* Nếu file chưa có → tự tạo
* Append dữ liệu mới

## Test:

* Ghi 1 alert → đọc lại được

---

# STEP 6: Telegram Notifier

## File: modules/notifier.py

## Class: TelegramNotifier

## Features:

* Gửi ảnh + text
* Cooldown (20s)
* Không spam

## Methods:

```python
send_alert(image, message)
```

## Config:

```yaml
telegram:
  token: "YOUR_TOKEN"
  chat_id: "YOUR_CHAT_ID"
  cooldown: 20
```

## Test:

* Gửi 1 ảnh thành công

---

# STEP 7: Desktop App (MAIN SYSTEM)

## File: desktop_app/app.py

## Tech:

* PyQt6

---

## UI Layout

```text
---------------------------------
| Camera Control | Live View    |
---------------------------------
| Zone Draw Area              |
---------------------------------
| Telegram Config             |
---------------------------------
| Alert Logs (JSON)           |
---------------------------------
```

---

## Features:

### 1. Camera Control

* Start / Stop camera
* Nhập RTSP

---

### 2. Live View

* Hiển thị video realtime (QLabel + OpenCV)

---

### 3. Zone Drawing

* Click chuột tạo polygon
* Lưu vào memory

---

### 4. Telegram Config

* Nhập token / chat_id
* Nút test gửi tin

---

### 5. Alert Logs

* Load từ alerts.json
* Hiển thị list + ảnh

---

# STEP 8: CORE LOOP (IMPORTANT)

## Flow:

```text
Camera → Detect → Check Zone
          ↓
      Intrusion?
          ↓ YES
   ┌───────────────┐
   │ Save JSON     │
   └───────────────┘
          ↓
   ┌───────────────┐
   │ Send Telegram │
   └───────────────┘
```

---

## Pseudo Code:

```python
frame = camera.read()

objects = detector.detect(frame)

for obj in objects:
    if zone.is_inside(obj["centroid"]):
        
        save image
        
        storage.save_alert(...)
        
        notifier.send_alert(...)
```

---

# STEP 9: Optimization

## Task:

* Detect mỗi 2–3 frame
* Thread riêng:

  * Camera
  * AI
  * UI

---

# STEP 10: Run System

## Run:

```bash
python desktop_app/app.py
```

---

# FINAL NOTE FOR AI

* Không dùng Flask
* Không dùng API
* Tất cả chạy local
* UI điều khiển trực tiếp module
* Code phải chạy được từng STEP
* Không viết 1 lần quá nhiều

---
# STEP 3: Motion + AI Detection (UPDATED)

## File: modules/detector.py

## Strategy:

* Không detect mọi frame
* Chỉ detect khi có CHUYỂN ĐỘNG

---

## 1. Motion Detection (OpenCV)

### Tech:

* Background Subtraction (MOG2)

```python
fgbg = cv2.createBackgroundSubtractorMOG2()
```

### Logic:

```python
mask = fgbg.apply(frame)

# lọc nhiễu
_, thresh = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)

# tìm contour
contours, _ = cv2.findContours(thresh, ...)

# nếu có vùng lớn → có chuyển động
```

---

## 2. Trigger YOLO (chỉ khi có motion)

## Detect các class:

```python
["person", "car", "motorbike", "dog", "cat"]
```

---

## Output:

```python
[
  {
    "label": "person",
    "confidence": 0.91,
    "centroid": (x, y),
    "box": [x1, y1, x2, y2]
  }
]
```

---

## Rule:

* Không có motion → bỏ qua YOLO
* Có motion → chạy YOLO

---

## Test:

* Đứng yên → không detect
* Di chuyển → detect

---

# STEP 8: CORE LOOP (UPDATED)

## Flow:

```text
Camera → Motion Detection
          ↓
      Có chuyển động?
          ↓ NO → BỎ QUA
          ↓ YES
     YOLO Detect
          ↓
     Lọc object cần thiết
          ↓
     Check Zone
          ↓
     Nếu vi phạm:
        → Save JSON
        → Save Image
        → Send Telegram
```

---

## Pseudo Code:

```python
frame = camera.read()

motion = detector.detect_motion(frame)

if motion:

    objects = detector.detect_objects(frame)

    for obj in objects:

        if obj["label"] in ["person", "car", "motorbike", "dog", "cat"]:

            if zone.is_inside(obj["centroid"]):

                image_path = save_frame(frame)

                storage.save_alert({
                    "time": now(),
                    "label": obj["label"],
                    "image": image_path
                })

                notifier.send_alert(frame, obj["label"])
```

---

# STEP 9: Anti-Spam Logic (IMPORTANT)

## Rule:

* Cùng 1 object → không spam liên tục

## Simple solution:

* Cooldown theo label:

```python
last_sent = {
  "person": 0,
  "car": 0
}
```

---

# PERFORMANCE TIPS

* YOLO chỉ chạy khi có motion → tăng FPS x3
* Resize frame trước detect
* Bỏ qua contour nhỏ (< 500 px)

---
Nâng cấp cực mạnh (nếu bạn muốn pro hơn)
Tracking ID (DeepSORT) → biết “cùng 1 người”
Phân biệt:
Người đứng lâu vs người đi ngang
Chỉ alert khi:
Ở trong vùng > 2s


# STEP 3: Motion + AI Detection + Fire Detection (FINAL)

## File: modules/detector.py

---

## 1. Motion Detection (giữ nguyên)

* Dùng MOG2
* Chỉ trigger khi có chuyển động

---

## 2. Object Detection (YOLO)

## Classes:

```python
["person", "car", "motorbike", "dog", "cat"]
```

---

## 3. Fire / Smoke Detection (NEW)

## OPTION A (RECOMMENDED):

* Dùng model YOLO custom:

  * fire
  * smoke

Ví dụ:

```python
model_fire = YOLO("fire_model.pt")
```

---

## OPTION B (Fallback nhẹ):

* Detect màu (HSV)

### Fire color range:

```python
lower = (0, 120, 200)
upper = (50, 255, 255)
```

### Logic:

* Nếu vùng màu lớn + flicker → nghi cháy

---

## Output chuẩn:

```python
[
  {
    "label": "person",
    "confidence": 0.9,
    "centroid": (x, y)
  },
  {
    "label": "fire",
    "confidence": 0.95,
    "centroid": (x, y)
  }
]
```

---

# STEP 6: Telegram Notifier (UPDATED)

## File: modules/notifier.py

## Class: TelegramNotifier

---

## Features:

* Gửi ảnh + text
* Cooldown riêng cho:

  * intrusion
  * fire

---

## Methods:

```python
send_intrusion_alert(image, label)

send_fire_alert(image)
```

---

## Message Format:

### Intrusion:

```text
🚨 CẢNH BÁO XÂM NHẬP
Đối tượng: person
Thời gian: 12:30
```

### Fire:

```text
🔥 CẢNH BÁO CHÁY
Phát hiện dấu hiệu cháy/nổ!
```

---

## Anti-Spam:

```python
cooldown = {
  "intrusion": 20,
  "fire": 10
}
```

---

# STEP 8: CORE LOOP (FINAL)

## Flow:

```text
Camera → Motion
          ↓
     Có chuyển động?
          ↓ NO → SKIP
          ↓ YES
   ┌───────────────┐
   │ YOLO Detect   │
   └───────────────┘
          ↓
   ┌───────────────┐
   │ Fire Detect   │
   └───────────────┘
          ↓
   ┌───────────────┐
   │ Zone Check    │
   └───────────────┘
```

---

## Logic chi tiết:

```python
frame = camera.read()

if detector.detect_motion(frame):

    objects = detector.detect_objects(frame)
    fire = detector.detect_fire(frame)

    # --- FIRE ưu tiên cao ---
    if fire:
        image_path = save_frame(frame)

        storage.save_alert({
            "time": now(),
            "label": "fire",
            "image": image_path
        })

        notifier.send_fire_alert(frame)

    # --- INTRUSION ---
    for obj in objects:

        if obj["label"] in ["person", "car", "motorbike", "dog", "cat"]:

            if zone.is_inside(obj["centroid"]):

                image_path = save_frame(frame)

                storage.save_alert({
                    "time": now(),
                    "label": obj["label"],
                    "image": image_path
                })

                notifier.send_intrusion_alert(frame, obj["label"])
```

---

# STEP 11: Alert JSON (UPDATED)

## File: data/alerts.json

```json
[
  {
    "time": "2026-01-01 10:00:00",
    "type": "intrusion",
    "label": "person",
    "image": "data/img1.jpg"
  },
  {
    "time": "2026-01-01 10:05:00",
    "type": "fire",
    "label": "fire",
    "image": "data/fire1.jpg"
  }
]
```

---

# PRIORITY RULE (IMPORTANT)

1. FIRE luôn ưu tiên cao nhất
2. Fire → gửi ngay (cooldown ngắn)
3. Intrusion → gửi sau (cooldown dài hơn)

---

# PERFORMANCE

* Motion → giảm load
* Fire detect → chạy song song
* YOLO → chỉ chạy khi cần

---

# FINAL RESULT

Hệ thống sẽ:

✅ Phát hiện chuyển động
✅ Nhận diện:

* Người
* Xe máy
* Ô tô
* Động vật

✅ Phát hiện cháy / khói
✅ Gửi cảnh báo Telegram realtime
✅ Lưu lịch sử JSON

---
