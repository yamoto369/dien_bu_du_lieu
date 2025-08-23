from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os

def main():
    # Đọc danh sách IMEI từ file
    imei_file_path = os.path.join(os.path.dirname(__file__), "imeilist.txt")
    try:
        with open(imei_file_path, 'r', encoding='utf-8') as f:
            imei_list = [line.strip() for line in f.readlines() if line.strip()]
        print(f"Đã đọc {len(imei_list)} IMEI từ file imeilist.txt")
    except FileNotFoundError:
        print("Không tìm thấy file imeilist.txt!")
        return
    except Exception as e:
        print(f"Lỗi đọc file imeilist.txt: {e}")
        return

    # Thiết lập Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    
    # Thiết lập thư mục download tự động
    download_dir = os.path.join(os.getcwd(), "downloads")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Tạo driver Chrome (sử dụng driver mặc định trong system PATH)
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("Đang truy cập trang web...")
        driver.get("https://stram.viettel.io/")
        
        print("Chờ element sidebar-wrapper xuất hiện...")
        # Chờ đến khi element xuất hiện (tối đa 60 giây)
        wait = WebDriverWait(driver, 60)
        
        # Chờ element sidebar-wrapper xuất hiện
        sidebar_element = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='sidebar-wrapper ps-container ps-theme-default ps-active-y']"))
        )
        print("Đã tìm thấy element sidebar-wrapper!")
        
        print("Chờ thêm 3 giây...")
        time.sleep(3)
        
        print("Click vào element 'Tổng cục thủy sản'...")
        tong_cuc_thuy_san = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//p[text()='Tổng cục thủy sản']"))
        )
        tong_cuc_thuy_san.click()
        print("Đã click vào 'Tổng cục thủy sản'!")
        
        print("Chờ element 'Gửi bù sang TCTS' xuất hiện...")
        # Chờ đến khi element xuất hiện (tối đa 60 giây)
        
        element = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@class='sidebar-normal' and text()='Gửi bù sang TCTS']"))
        )
        
        
        print("Click vào element 'Gửi bù sang TCTS'!")
        element.click()
        
        print("Chờ element date_timepicker_start xuất hiện...")
        date_from = wait.until(
            EC.presence_of_element_located((By.ID, "date_timepicker_start"))
        )        
        
        print("Điền ngày bắt đầu...")
        driver.execute_script("arguments[0].value = '19/08/2025 18:00';", date_from)
        
        print("Điền ngày kết thúc...")
        date_to = driver.find_element(By.ID, "date_timepicker_end")
        driver.execute_script("arguments[0].value = '20/08/2025 03:00';", date_to)
        
        # Bắt đầu vòng lặp xử lý từng IMEI
        for i, imei in enumerate(imei_list, 1):
            print(f"\n=== Xử lý IMEI {i}/{len(imei_list)}: {imei} ===")
            imei_input = driver.find_element(By.ID, "imeiDevice")
            imei_input.clear()
            imei_input.send_keys(imei)

            print("Click nút Tìm kiếm...")
            search_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[@class='btn btn-primary btn-fill' and @onclick='searchHistoryDevice()']"))
            )
            search_btn.click()
            
            print("Chờ thêm 5 giây trước khi click nút tải file...")
            time.sleep(5)
            
            print("Click nút tải CSV...")
            csv_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-danger' and @onclick='createBanTinBuCsv()']"))
            )
            csv_btn.click()
            
            print(f"Đã click nút tải CSV cho IMEI {imei}! File sẽ được tải về tự động...")
            
            # Chờ một chút để file được tải về
            print("Chờ file tải về hoàn tất...")
            time.sleep(5)
            
            print(f"Hoàn thành xử lý IMEI {imei}")

        print(f"\n=== Đã hoàn thành xử lý tất cả {len(imei_list)} IMEI ===")

        # Giữ trình duyệt mở 60 giây để quan sát kết quả
        time.sleep(60)
        
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        print("Đóng trình duyệt...")
        driver.quit()

if __name__ == "__main__":
    main()
