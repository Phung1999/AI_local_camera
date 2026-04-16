import cv2
import socket
import requests

def test_camera_connection(ip="192.168.0.100", port=554):
    print(f"Testing camera at {ip}:{port}")
    print("-" * 50)
    
    # Test 1: RTSP
    print("\n1. Testing RTSP...")
    rtsp_urls = [
        f"rtsp://{ip}:{port}/onvif1",
        f"rtsp://{ip}:{port}/onvif2",
        f"rtsp://{ip}:{port}/11",
        f"rtsp://{ip}:{port}/live.sdp",
        f"rtsp://{ip}:{port}/0",
        f"rtsp://admin:admin@{ip}:{port}/onvif1",
        f"rtsp://admin:123@{ip}:{port}/onvif1",
        f"rtsp://admin:@{ip}:{port}/onvif1",
    ]
    
    for url in rtsp_urls:
        print(f"  Trying: {url}")
        cap = cv2.VideoCapture(url)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"  SUCCESS! Connected with: {url}")
                cap.release()
                return url
        cap.release()
    
    # Test 2: HTTP snapshot
    print("\n2. Testing HTTP snapshot...")
    http_urls = [
        f"http://{ip}/snapshot.jpg",
        f"http://{ip}/cgi-bin/snapshot.cgi",
        f"http://{ip}/snap.jpg",
        f"http://{ip}/image.jpg",
        f"http://{ip}:88/cgi-bin/snapshot.cgi",
    ]
    
    for url in http_urls:
        print(f"  Trying: {url}")
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                print(f"  SUCCESS! HTTP snapshot accessible: {url}")
                return url
        except:
            pass
    
    # Test 3: ONVIF
    print("\n3. Testing ONVIF...")
    onvif_url = f"http://{ip}:8899/onvif/device_service"
    print(f"  ONVIF service: {onvif_url}")
    
    # Test 4: Port scan
    print("\n4. Scanning common ports...")
    ports = [554, 80, 88, 8080, 8899, 34567]
    for p in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, p))
        if result == 0:
            print(f"  Port {p}: OPEN")
        sock.close()
    
    print("\n" + "=" * 50)
    print("Test complete. Check results above.")

if __name__ == "__main__":
    test_camera_connection("192.168.0.100")
