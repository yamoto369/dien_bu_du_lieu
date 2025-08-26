from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
import glob
import random
import traceback
from datetime import datetime

def create_report(success_files, failed_files):
    """
    Tạo file report thống kê kết quả xử lý files
    """
    try:
        # Lấy thời gian hiện tại để tạo tên file report
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"report_{current_time}.txt"
        
        # Tạo nội dung report
        report_content = []
        report_content.append("=== REPORT KẾT QUẢ XỬ LÝ FILE ===")
        report_content.append(f"Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        report_content.append(f"Tổng số file xử lý: {len(success_files) + len(failed_files)}")
        report_content.append(f"Số file thành công: {len(success_files)}")
        report_content.append(f"Số file thất bại: {len(failed_files)}")
        report_content.append("")
        
        report_content.append("== SUCCESS ==")
        if success_files:
            for file in success_files:
                report_content.append(file)
        else:
            report_content.append("Không có file nào được xử lý thành công")
        report_content.append("")
        
        report_content.append("== FAIL ==")
        if failed_files:
            for file in failed_files:
                report_content.append(file)
        else:
            report_content.append("Không có file nào thất bại")
        
        # Ghi file report
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_content))
        
        print(f"✅ Đã tạo file report: {report_filename}")
        print(f"📊 Thống kê: {len(success_files)} thành công, {len(failed_files)} thất bại")
        
    except Exception as e:
        print(f"❌ Lỗi khi tạo report: {e}")

def get_vessel_names_from_csv_files(csv_directory):
    """
    Lấy danh sách tên phương tiện từ các file CSV
    Tên phương tiện = các ký tự đầu tên file kết thúc bằng -TS
    """
    vessel_names = []
    
    try:
        # Tìm tất cả file CSV trong thư mục
        csv_files = glob.glob(os.path.join(csv_directory, "*.csv"))
        
        for csv_file in csv_files:
            filename = os.path.basename(csv_file)
            print(f"Đang xử lý file: {filename}")
            
            # Tìm phần tên kết thúc bằng -TS
            if "-TS" in filename:
                # Lấy phần từ đầu đến sau -TS (bao gồm cả -TS)
                ts_index = filename.find("-TS")
                vessel_name = filename[:ts_index + 3]  # +3 để lấy cả "-TS"
                if vessel_name and vessel_name not in vessel_names:
                    vessel_names.append(vessel_name)
                    print(f"✅ Tìm thấy tên phương tiện: {vessel_name}")
        
        print(f"Tổng cộng tìm thấy {len(vessel_names)} phương tiện từ {len(csv_files)} file CSV")
        return vessel_names
        
    except Exception as e:
        print(f"❌ Lỗi khi đọc file CSV: {e}")
        return []

def find_csv_file_for_vessel(csv_directory, vessel_name):
    """
    Tìm file CSV tương ứng với tên phương tiện
    """
    try:
        csv_files = glob.glob(os.path.join(csv_directory, "*.csv"))
        for csv_file in csv_files:
            if vessel_name in os.path.basename(csv_file):
                return csv_file
        return None
    except Exception as e:
        print(f"❌ Lỗi khi tìm file CSV cho {vessel_name}: {e}")
        return None

def wait_for_api_response(driver, target_url="sendFileCsvToTcts", timeout=30):
    """
    Chờ và theo dõi response từ API
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Lấy network logs
            logs = driver.get_log('performance')
            for log in logs:
                message = log.get('message', '')
                if 'Network.responseReceived' in message:
                    try:
                        import json
                        log_data = json.loads(message)
                        if 'params' in log_data:
                            response_data = log_data['params']['response']
                            url = response_data.get('url', '')
                            
                            if target_url in url:
                                
                                # Lấy response body
                                request_id = log_data['params']['requestId']
                                try:
                                    response_body = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                                    body_content = response_body.get('body', '')
                                    
                                    if body_content:
                                        response_json = json.loads(body_content)
                                        
                                        success = response_json.get('success', False)
                                        result_text = response_json.get('resultText', '')
                                        
                                        if success:
                                            return True
                                        else:
                                            return False
                                except Exception as body_error:
                                    print(f"Không thể đọc response body: {body_error}")
                                    
                    except Exception as parse_error:
                        continue
            
            time.sleep(1)
            
        except Exception as e:
            time.sleep(1)
    
    print(f"❌ Timeout sau {timeout} giây, không nhận được response")
    return False

def sync_test():
    """
    Script test cho tính năng đồng bộ trên trang https://stramtest.innoway.vn
    """
    print("=== BẮT ĐẦU TEST TÍNH NĂNG ĐỒNG BỘ ===")
    
    # Khởi tạo danh sách để tracking kết quả
    success_files = []
    failed_files = []
    
    # Đường dẫn đến thư mục chứa file CSV (folder DS trong cùng thư mục với script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_directory = os.path.join(script_dir, "DS")
    
    print(f"Đường dẫn thư mục CSV: {csv_directory}")
    
    # Kiểm tra xem thư mục DS có tồn tại không
    if not os.path.exists(csv_directory):
        print(f"❌ Không tìm thấy thư mục DS tại: {csv_directory}")
        print("Vui lòng tạo thư mục 'DS' và đặt các file CSV vào đó.")
        return
    
    # Thiết lập Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--log-level=0")
    
    # Tạo driver Chrome
    driver = webdriver.Chrome(options=chrome_options)
    
    # Bật DevTools để theo dõi network requests
    driver.execute_cdp_cmd('Network.enable', {})
    
    try:
        # Bước 1: Truy cập trang web
        print("Bước 1: Đang truy cập trang web https://stramtest.innoway.vn...")
        driver.get("https://stramtest.innoway.vn")
        
        # Bước 2: Chờ cho đến khi hiển thị nút Tổng cục thủy sản ở menu bar bên trái
        print("Bước 2: Chờ hiển thị nút 'Tổng cục thủy sản' ở menu bar bên trái...")
        wait = WebDriverWait(driver, 60)
        
        # Chờ sidebar xuất hiện trước
        sidebar_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar-wrapper"))
        )
        print("✅ Sidebar đã xuất hiện")
        
        # Chờ nút "Tổng cục thủy sản" xuất hiện
        tong_cuc_thuy_san = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//p[contains(text(), 'Tổng cục thủy sản')]"))
        )
        print("✅ Nút 'Tổng cục thủy sản' đã hiển thị")
        
        # Bước 3: Nhấn vào Tổng cục thủy sản
        print("Bước 3: Nhấn vào 'Tổng cục thủy sản'...")
        tong_cuc_thuy_san.click()
        print("✅ Đã click vào 'Tổng cục thủy sản'")
        
        # Chờ menu con mở ra
        time.sleep(2)
        
        # Bước 4: Nhấn chọn Gửi Bù Sang TCTS
        print("Bước 4: Nhấn chọn 'Gửi Bù Sang TCTS'...")
        gui_bu_sang_tcts = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Gửi bù sang TCTS')]"))
        )
        gui_bu_sang_tcts.click()
        print("✅ Đã click vào 'Gửi Bù Sang TCTS'")
        
        # Chờ trang tải
        time.sleep(3)
        
        # Bước 5: Nhấn nút GỬI BÙ FILE
        print("Bước 5: Nhấn nút 'GỬI BÙ FILE'...")
        gui_bu_file_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.btn-success"))
        )
        gui_bu_file_btn.click()
        print("✅ Đã click nút 'GỬI BÙ FILE'")
        
        # Chờ form nhập thông tin xuất hiện
        time.sleep(3)
        
        # Bước 6: Thực hiện gửi lần lượt từng phương tiện với thông tin chi tiết
        print("Bước 6: Thực hiện gửi lần lượt từng file CSV...")
        
        # Lấy danh sách tất cả file CSV trong thư mục DS
        csv_files = glob.glob(os.path.join(csv_directory, "*.csv"))
        print(f"Tìm thấy {len(csv_files)} file CSV để xử lý")
        
        # Lặp qua từng file CSV
        for i, csv_file_path in enumerate(csv_files[:5], 1):  # Giới hạn 5 file đầu tiên để test
            filename = os.path.basename(csv_file_path)
            print(f"\n--- Xử lý file {i}: {filename} ---")
            
            try:
                # Split tên file bởi dấu "_", lấy phần đầu tiên là tên thiết bị
                device_name = filename.split("_")[0]
                
                # 1. Điền tên thiết bị vào input deviceNameList
                try:
                    device_input = wait.until(
                        EC.element_to_be_clickable((By.ID, "deviceNameList"))
                    )
                    device_input.clear()
                    device_input.send_keys(device_name)
                except Exception as e:
                    print(f"❌ Lỗi khi điền tên thiết bị: {e}")
                    failed_files.append(filename)
                    continue
                
                time.sleep(1)
                
                # 2. Dùng JavaScript điền ngày bắt đầu và kết thúc
                try:
                    # Điền ngày bắt đầu: 19/08/2025
                    driver.execute_script("""
                        document.getElementById('dateFrom').value = '19/08/2025';
                        document.getElementById('dateFrom').dispatchEvent(new Event('change'));
                    """)
                    
                    # Điền ngày kết thúc: 20/08/2025  
                    driver.execute_script("""
                        document.getElementById('dateTo').value = '20/08/2025';
                        document.getElementById('dateTo').dispatchEvent(new Event('change'));
                    """)
                except Exception as e:
                    print(f"❌ Lỗi khi điền ngày bằng JavaScript: {e}")
                    failed_files.append(filename)
                    continue
                
                time.sleep(1)
                
                # 3. Điền ID phản hồi
                try:
                    id_response_input = wait.until(
                        EC.element_to_be_clickable((By.ID, "idRespon"))
                    )
                    id_response_input.clear()
                    id_response_input.send_keys("test")
                except Exception as e:
                    print(f"❌ Lỗi khi điền ID phản hồi: {e}")
                    failed_files.append(filename)
                    continue
                
                time.sleep(1)
                
                # 4. Load file vào input file
                print("Đang load file CSV...")
                try:
                    file_input = wait.until(
                        EC.presence_of_element_located((By.ID, "files"))
                    )
                    file_input.send_keys(csv_file_path)
                except Exception as e:
                    print(f"❌ Lỗi khi load file: {e}")
                    failed_files.append(filename)
                    continue
                
                time.sleep(2)
                
                # 5. Nhấn nút "Gửi file"
                print("Đang nhấn nút 'Gửi file'...")
                try:
                    send_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@onclick='sendFileCsvToTcts()']"))
                    )
                    
                    # Scroll đến nút nếu cần
                    driver.execute_script("arguments[0].scrollIntoView();", send_button)
                    time.sleep(0.5)
                    
                    send_button.click()
                    
                    # Chờ và kiểm tra response từ API
                    response_success = wait_for_api_response(driver, "sendFileCsvToTcts", 60)                    
                   
                    # Quyết định có tiếp tục không
                    if response_success:
                        print("✅ Xử lý file thành công, sẽ tiếp tục với file tiếp theo")
                        success_files.append(filename)
                    else:
                        print("⚠️ Xử lý file không thành công, nhưng sẽ tiếp tục với file tiếp theo")
                        failed_files.append(filename)
                        
                except Exception as e:
                    print(f"❌ Lỗi khi nhấn nút 'Gửi file': {e}")
                    failed_files.append(filename)
                    continue
                
                print(f"✅ Hoàn thành xử lý file: {filename}")
                
                # Chờ trước khi xử lý file tiếp theo
                if i < len(csv_files[:5]):
                    print("Chờ 3 giây trước khi xử lý file tiếp theo...")
                    time.sleep(3)
                    
                    # Reset form để chuẩn bị cho file tiếp theo (nếu cần)
                    try:
                        # Clear các input field
                        driver.execute_script("""
                            document.getElementById('deviceNameList').value = '';
                            document.getElementById('dateFrom').value = '';
                            document.getElementById('dateTo').value = '';
                            document.getElementById('idRespon').value = '';
                            document.getElementById('files').value = '';
                        """)
                        time.sleep(1)
                    except:
                        pass
                    
            except Exception as file_error:
                print(f"❌ Lỗi khi xử lý file {filename}: {file_error}")
                failed_files.append(filename)
                continue
        
        # Chờ để quan sát kết quả
        print(f"\n🎉 HOÀN THÀNH XỬ LÝ {len(csv_files[:5])} FILE CSV!")
        print("Chờ 15 giây để quan sát kết quả...")
        time.sleep(15)
        
        print("=== TEST TÍNH NĂNG ĐỒNG BỘ HOÀN THÀNH ===")
        
    except Exception as e:
        print(f"❌ Lỗi trong quá trình test: {e}")
        print("Có thể các selector đã thay đổi hoặc trang web chưa tải đầy đủ")
    
    finally:
        # Tạo report kết quả
        try:
            create_report(success_files, failed_files)
        except:
            print("❌ Không thể tạo file report")
            
        # Giữ trình duyệt mở thêm 60 giây để kiểm tra thủ công nếu cần
        print("Giữ trình duyệt mở thêm 60 giây để kiểm tra...")
        time.sleep(60)
        print("Đóng trình duyệt...")
        driver.quit()

def main():
    """
    Hàm chính để chạy test
    """
    try:
        sync_test()
    except KeyboardInterrupt:
        print("\n⚠️ Test bị dừng bởi người dùng")
    except Exception as e:
        print(f"❌ Lỗi không mong muốn: {e}")

if __name__ == "__main__":
    main()
