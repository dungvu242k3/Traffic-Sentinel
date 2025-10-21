# Hanoi Traffic Sentinel 🚦

---

## Giới thiệu

**Hanoi Traffic Sentinel** là một dự án ứng dụng trí tuệ nhân tạo (AI) để phân tích luồng video từ camera giao thông, tự động phát hiện các vi phạm như vượt đèn đỏ, đi sai làn (dự kiến), nhận dạng biển số (dự kiến), và cung cấp giao diện web dashboard để theo dõi, quản lý.

Mục tiêu là xây dựng một hệ thống mạnh mẽ, dễ mở rộng, giúp nâng cao ý thức tham gia giao thông và hỗ trợ cơ quan chức năng trong việc xử lý vi phạm.

---

## Tính năng chính ✨

* **Phát hiện Vượt đèn đỏ:** Sử dụng model YOLO để xác định trạng thái đèn tín hiệu và theo dõi phương tiện.
* **Giao diện Dashboard:** Hiển thị trực tiếp các luồng camera, thống kê vi phạm, quản lý camera. (FE/BE)
* **Kiến trúc Microservices:** Tách biệt logic xử lý AI (`ai-service`) và logic nghiệp vụ/API (`backend-api`) để dễ dàng mở rộng và bảo trì.
* **Kiến trúc Clean Architecture:** Áp dụng cho `backend-api` giúp code rõ ràng, dễ kiểm thử.
* **Xử lý Bất đồng bộ:** Sử dụng FastAPI và `asyncio` cho hiệu năng cao.
* **Thông báo Real-time (Dự kiến):** Sử dụng Message Queue (RabbitMQ) và WebSockets để cập nhật vi phạm gần như tức thì.

---

## Kiến trúc Hệ thống 🏗️

Hệ thống được xây dựng dựa trên kiến trúc Microservices, bao gồm các thành phần chính:

1.  **Front-end (FE):** Giao diện người dùng dựa trên nền web (HTML, CSS, Vanilla JavaScript) để hiển thị dashboard và quản lý.
2.  **Back-end API (BE):** Dịch vụ FastAPI (Python) quản lý logic nghiệp vụ, API, kết nối database (PostgreSQL), và lắng nghe tin nhắn từ AI. Áp dụng Clean Architecture.
3.  **AI Service:** Dịch vụ Python độc lập, sử dụng OpenCV và YOLO (Ultralytics) để xử lý video, phát hiện vi phạm và gửi kết quả vào Message Queue (RabbitMQ).
4.  **Database:** PostgreSQL để lưu trữ thông tin camera và vi phạm.
5.  **Message Queue:** RabbitMQ làm trung gian giao tiếp bất đồng bộ giữa AI Service và Back-end API.



---

## Công nghệ sử dụng 💻

* **Back-end:** Python, FastAPI, SQLAlchemy (Async), Pydantic, Pika (RabbitMQ client)
* **AI:** Python, Ultralytics YOLO, OpenCV
* **Front-end:** HTML, TailwindCSS, Vanilla JavaScript
* **Database:** PostgreSQL
* **Message Queue:** RabbitMQ
* **Khác:** Docker (dự kiến), Streamlink/yt-dlp (để lấy stream)

---

## Cài đặt và Chạy thử nghiệm 🚀

*(Phần này bạn cần chi tiết hóa dựa trên dự án của mình)*

1.  **Clone Repository:**
    ```bash
    git clone [https://github.com/your-username/hanoi-traffic-sentinel.git](https://github.com/your-username/hanoi-traffic-sentinel.git)
    cd hanoi-traffic-sentinel
    ```

2.  **Thiết lập Môi trường:**
    * Cài đặt Python 3.10+
    * Cài đặt PostgreSQL và tạo database (ví dụ: `traffic_db`).
    * Cài đặt RabbitMQ (khuyến nghị dùng Docker).
    * Tạo môi trường ảo và cài đặt thư viện cho BE và AI:
        ```bash
        # Trong thư mục BE (hoặc backend-api)
        python -m venv venv
        source venv/bin/activate # Hoặc venv\Scripts\activate trên Windows
        pip install -r requirements.txt # (Bạn cần tạo file requirements.txt)

        # Trong thư mục AI_service
        python -m venv venv
        source venv/bin/activate # Hoặc venv\Scripts\activate trên Windows
        pip install -r requirements.txt # (Bạn cần tạo file requirements.txt)
        ```

3.  **Cấu hình:**
    * Tạo file `.env` trong thư mục `BE` theo mẫu và điền thông tin kết nối database.

4.  **Chạy các Dịch vụ (mỗi lệnh trong một terminal riêng):**
    * **Chạy Back-end API:**
        ```bash
        cd BE
        uvicorn app.main:app --reload
        ```
    * **Chạy Consumer:**
        ```bash
        cd BE
        python run_consumer.py
        ```
    * **Chạy AI Service:**
        ```bash
        python -m AI_service.main
        ```
    * **Chạy Front-end:** Mở file `FE/html/index.html` bằng Live Server trong VS Code.

---

## Demo (Screenshots) 📸

*(Thêm các ảnh chụp màn hình giao diện Dashboard, trang Quản lý Camera, trang Vi phạm ở đây)*



