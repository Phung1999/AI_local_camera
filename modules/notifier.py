import time
import io
import urllib.request
import urllib.parse
import urllib.error


class TelegramNotifier:
    def __init__(self, token=None, chat_id=None, cooldown_intrusion=20, cooldown_fire=10):
        self.token = token
        self.chat_id = chat_id
        self.cooldown_intrusion = cooldown_intrusion
        self.cooldown_fire = cooldown_fire
        self.last_sent = {
            "intrusion": 0,
            "fire": 0
        }
        self.api_url = None
        if token and chat_id:
            self._connect()

    def _connect(self):
        if self.token and self.token != "YOUR_TOKEN":
            self.api_url = f"https://api.telegram.org/bot{self.token}"

    def _can_send(self, alert_type):
        current_time = time.time()
        cooldown = self.cooldown_fire if alert_type == "fire" else self.cooldown_intrusion
        
        if current_time - self.last_sent.get(alert_type, 0) >= cooldown:
            self.last_sent[alert_type] = current_time
            return True
        return False

    def _send_request(self, method, data=None, files=None):
        if not self.api_url:
            print("Telegram chưa được cấu hình")
            return False
        
        try:
            url = f"{self.api_url}/{method}"
            
            if files:
                import multipart
                body, content_type = multipart.encode_multipart(data, files)
                req = urllib.request.Request(url, data=body)
                req.add_header('Content-Type', content_type)
            elif data:
                data = urllib.parse.urlencode(data).encode('utf-8')
                req = urllib.request.Request(url, data=data)
            else:
                req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = response.read().decode('utf-8')
                return True
                
        except Exception as e:
            print(f"Lỗi gửi Telegram: {e}")
            return False

    def _send_message(self, text, image=None):
        data = {
            'chat_id': self.chat_id,
            'text': text
        }
        
        if image is not None:
            try:
                import cv2
                import numpy as np
                
                if isinstance(image, np.ndarray):
                    is_success, buffer = cv2.imencode('.jpg', image)
                    if is_success:
                        image_bytes = buffer.tobytes()
                        return self._send_photo_with_caption(text, image_bytes)
                    return False
                else:
                    with open(image, 'rb') as f:
                        image_bytes = f.read()
                    return self._send_photo_with_caption(text, image_bytes)
            except Exception as e:
                print(f"Lỗi xử lý ảnh: {e}")
                return False
        else:
            return self._send_request('sendMessage', data)

    def _send_photo_with_caption(self, caption, image_bytes):
        try:
            boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
            
            body = f'--{boundary}\r\n'
            body += 'Content-Disposition: form-data; name="chat_id"\r\n\r\n'
            body += f'{self.chat_id}\r\n'
            
            body += f'--{boundary}\r\n'
            body += 'Content-Disposition: form-data; name="caption"\r\n\r\n'
            body += f'{caption}\r\n'
            
            body += f'--{boundary}\r\n'
            body += 'Content-Disposition: form-data; name="photo"; filename="alert.jpg"\r\n'
            body += 'Content-Type: image/jpeg\r\n\r\n'
            
            body_bytes = body.encode('utf-8')
            body_bytes += image_bytes
            body_bytes += f'\r\n--{boundary}--\r\n'.encode('utf-8')
            
            url = f"{self.api_url}/sendPhoto"
            req = urllib.request.Request(url, data=body_bytes)
            req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                response.read()
                return True
                
        except Exception as e:
            print(f"Lỗi gửi ảnh: {e}")
            return False

    def send_intrusion_alert(self, image, label):
        if not self._can_send("intrusion"):
            print("Cooldown intrusion - bỏ qua")
            return False
        
        text = f"⚠️ CẢNH BÁO XÂM NHẬP\nĐối tượng: {label}\nThời gian: {time.strftime('%H:%M:%S')}"
        return self._send_message(text, image)

    def send_fire_alert(self, image):
        if not self._can_send("fire"):
            print("Cooldown fire - bỏ qua")
            return False
        
        text = "🔥 CẢNH BÁO CHÁY\nPhát hiện dấu hiệu cháy/nổ!"
        return self._send_message(text, image)

    def send_test(self, image=None):
        text = f"🔔 Test tin nhắn\nThời gian: {time.strftime('%H:%M:%S')}"
        return self._send_message(text, image)

    def configure(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self._connect()


if __name__ == "__main__":
    notifier = TelegramNotifier()
    print("TelegramNotifier created.")
    print("Cần cấu hình token và chat_id để gửi tin.")
