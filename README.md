# Auto Web Test Project

Project này sử dụng Selenium để tự động hóa việc test web với IMEI từ file imeilist.txt.

## Cài đặt và chạy

### Cách 1: Chạy bằng file batch (Đơn giản nhất)
1. Double-click vào file `run_test.bat`
2. Chương trình sẽ tự động chạy với virtual environment

### Cách 2: Chạy thủ công
1. Mở PowerShell/Command Prompt trong thư mục project
2. Kích hoạt virtual environment:
   ```
   .venv\Scripts\activate
   ```
3. Chạy chương trình:
   ```
   python auto_web_test.py
   ```

## Cấu trúc project
- `auto_web_test.py`: File chính chứa code automation
- `imeilist.txt`: File chứa danh sách IMEI cần xử lý
- `requirements.txt`: Danh sách thư viện cần thiết
- `.venv/`: Thư mục virtual environment chứa tất cả thư viện
- `downloads/`: Thư mục lưu file CSV tải về
- `run_test.bat`: Script batch để chạy nhanh

## Chuyển sang máy khác
1. Copy toàn bộ thư mục project (bao gồm thư mục `.venv`)
2. Chạy trực tiếp file `run_test.bat` hoặc sử dụng lệnh thủ công như trên
3. Không cần cài đặt Python hay Selenium trên máy mới (chỉ cần có Python runtime)

## Lưu ý
- Đảm bảo file `imeilist.txt` có chứa các IMEI cần xử lý (mỗi IMEI một dòng)
- Chrome browser phải được cài đặt trên máy
- ChromeDriver sẽ được tự động tải về bởi Selenium
