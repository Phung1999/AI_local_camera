import cv2
import threading
import time


def find_available_cameras(max_check=10, timeout=2):
    available = []
    for i in range(max_check):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                available.append({
                    "id": i,
                    "name": f"Camera {i}",
                    "backend": cap.getBackendName()
                })
            cap.release()
    return available


class VideoCamera:
    def __init__(self, source=0, width=640, height=480):
        self.source = source
        self.width = width
        self.height = height
        self.cap = None
        self.running = False
        self.current_frame = None
        self.lock = threading.Lock()
        self.thread = None

    def start(self):
        if self.running:
            return
        
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise RuntimeError(f"Không thể mở camera: {self.source}")
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (self.width, self.height))
                with self.lock:
                    self.current_frame = frame
            else:
                time.sleep(0.01)

    def read(self):
        with self.lock:
            return self.current_frame.copy() if self.current_frame is not None else None

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        if self.cap:
            self.cap.release()
            self.cap = None


if __name__ == "__main__":
    cam = VideoCamera(source=0)
    cam.start()
    
    print("Camera started. Press 'q' to quit.")
    while True:
        frame = cam.read()
        if frame is not None:
            cv2.imshow("Camera Test", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    
    cam.stop()
    cv2.destroyAllWindows()
