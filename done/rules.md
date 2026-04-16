Khi giao việc cho AI "vibe code" để xây dựng hệ thống giám sát, bạn cần lưu ý một số "luật" ngầm về kỹ thuật, logic xử lý và đạo đức/pháp lý để đảm bảo sản phẩm chạy ổn định và an toàn:
1. Luật về Cấu trúc và Môi trường (Kỹ thuật)
Explicit is better than implicit (Rõ ràng tốt hơn ngầm định): Hãy yêu cầu AI xác định rõ môi trường làm việc thông qua Virtual Environment (venv) để tách biệt các phụ thuộc của dự án, tránh xung đột với hệ thống
.
Chia để trị (Modularization): Đừng yêu cầu AI viết toàn bộ app trong một file. Hãy chia nhỏ thành các Class (lập trình hướng đối tượng) riêng biệt: module đọc camera, module nhận diện YOLO, module gửi Telegram và module giao diện
.
Tận dụng thư viện có sẵn: Luôn nhắc AI sử dụng các thư viện mạnh mẽ như OpenCV để xử lý phần cứng và Ultralytics (YOLOv8) cho phần AI để đạt hiệu suất cao nhất
.
2. Luật về Logic Giám sát (Tránh báo động giả)
Vùng cấm (ROI - Region of Interest): AI phải thiết lập logic cho phép vẽ đa giác (polygon) để xác định vùng cần bảo vệ
.
Xác định tâm đối tượng (Centroid): Thay vì cảnh báo ngay khi đối tượng chạm vào khung hình, hãy tính toán điểm trung tâm (centroid) của người hoặc vật. Chỉ khi cái tâm này nằm trong vùng cấm mới kích hoạt cảnh báo
.
Cơ chế chống spam (Cooldown): Thiết lập một khoảng thời gian chờ (ví dụ: ít nhất 15 giây hoặc lâu hơn) giữa các lần gửi thông báo để tránh việc Telegram bị "ngập" tin nhắn khi đối tượng di chuyển liên tục
.
3. Luật về Bảo mật và Quyền riêng tư
Tuyệt đối bảo mật Token: Các mã Telegram Bot Token hoặc mật khẩu API phải được AI lưu trữ trong file cấu hình riêng (như .ini hoặc .env) và không được chia sẻ công khai
.
Quyền riêng tư (Privacy): Khi xây dựng hệ thống giám sát, cần lưu ý đến quyền riêng tư cá nhân và các quy định pháp lý về việc quay phim tại khu vực công cộng hoặc nơi làm việc
. Nếu gửi dữ liệu qua Internet, hãy đảm bảo luồng stream được mã hóa (encryption)
.
Tuân thủ luật chống Spam: Nếu hệ thống có tính năng gửi email, bạn phải đảm bảo có sự đồng ý của người nhận để tuân thủ các quy định như GDPR
.
4. Luật về Tối ưu hóa
Bỏ qua khung hình (Frame Skipping): Để app chạy mượt trên máy cấu hình yếu, hãy yêu cầu AI lập trình sao cho chỉ xử lý 1 trong mỗi 3-5 khung hình (giảm tải cho CPU/GPU)
.
Xử lý đa luồng (Parallel Processing): Việc đọc camera, nhận diện AI và gửi tin nhắn Telegram nên chạy trên các luồng (thread) độc lập để luồng video không bị đứng (lag) khi đang gửi dữ liệu đi
.
Mẹo nhỏ cho bạn: Khi AI code xong, hãy yêu cầu nó kiểm tra lại bằng các lệnh assert để xác nhận logic hoạt động đúng như mong đợi trước khi triển khai thực tế
.