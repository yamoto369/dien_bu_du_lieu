from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os
import glob
import shutil

def clear_tmp_directory(tmp_dir):
    """
    Xóa tất cả file trong thư mục TMP
    """
    try:
        files = glob.glob(os.path.join(tmp_dir, "*"))
        if files:
            for file in files:
                os.remove(file)
    except Exception as e:
        print(f"⚠️  Lỗi khi xóa file trong TMP: {e}")

def check_and_move_file_from_tmp(tmp_dir, final_dir, timeout=10):
    """
    Kiểm tra có file nào trong thư mục TMP và move sang thư mục downloads chính
    Returns: (success, filename) - success: True/False, filename: tên file được move hoặc None
    """
    for i in range(timeout):
        time.sleep(1)
        files = glob.glob(os.path.join(tmp_dir, "*"))
        
        if files:
            # Có file, lấy file đầu tiên
            file_path = files[0]
            filename = os.path.basename(file_path)
            final_path = os.path.join(final_dir, filename)
            
            try:
                # Move file từ TMP sang thư mục chính
                shutil.move(file_path, final_path)
                return True, filename
            except Exception as e:
                print(f"⚠️  Lỗi khi move file {filename}: {e}")
                return False, filename
        
        print(f"Kiểm tra lần {i+1}/{timeout}...")
    
    return False, None

def main():
    # Danh sách thống kê IMEI tải thất bại và thành công
    failed_imei_list = []
    success_files = []
    
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
    tmp_dir = os.path.join(download_dir, "TMP")
    
    # Tạo thư mục downloads và TMP nếu chưa tồn tại
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    
    print(f"Thư mục tải chính: {download_dir}")
    print(f"Thư mục tải tạm: {tmp_dir}")
    
    prefs = {
        "download.default_directory": tmp_dir,  # Tải về thư mục TMP trước
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
        time.sleep(3)
        
        tong_cuc_thuy_san = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//p[text()='Tổng cục thủy sản']"))
        )
        tong_cuc_thuy_san.click()
               
        element = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@class='sidebar-normal' and text()='Gửi bù sang TCTS']"))
        )
        element.click()
        
        date_from = wait.until(
            EC.presence_of_element_located((By.ID, "date_timepicker_start"))
        )
        driver.execute_script("arguments[0].value = '19/08/2025 18:00';", date_from)
        
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
            
            # Xóa hết file trong thư mục TMP trước khi tải
            clear_tmp_directory(tmp_dir)
            
            print("Click nút tải CSV...")
            csv_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-danger' and @onclick='createBanTinBuCsv()']"))
            )
            csv_btn.click()
            
            # Kiểm tra và move file từ TMP
            success, filename = check_and_move_file_from_tmp(tmp_dir, download_dir, 10)
            
            if success:
                print(f"✅ IMEI {imei} - Tải và move file thành công: {filename}")
                success_files.append({"imei": imei, "filename": filename})
            else:
                print(f"❌ IMEI {imei} - Tải file thất bại")
                failed_imei_list.append(imei)
            
            print(f"Hoàn thành xử lý IMEI {imei}")

        print(f"\n=== Đã hoàn thành xử lý tất cả {len(imei_list)} IMEI ===")
        
        # Báo cáo thống kê chi tiết
        print(f"\n📊 === BÁO CÁO THỐNG KÊ ===")
        print(f"Tổng số IMEI xử lý: {len(imei_list)}")
        print(f"Số IMEI tải thành công: {len(success_files)}")
        print(f"Số IMEI tải thất bại: {len(failed_imei_list)}")
        
        # Hiển thị danh sách file thành công
        if success_files:
            print(f"\n✅ Danh sách IMEI tải thành công:")
            for idx, item in enumerate(success_files, 1):
                print(f"  {idx}. IMEI: {item['imei']} → File: {item['filename']}")
        
        # Hiển thị danh sách IMEI thất bại
        if failed_imei_list:
            print(f"\n❌ Danh sách IMEI tải thất bại:")
            for idx, failed_imei in enumerate(failed_imei_list, 1):
                print(f"  {idx}. {failed_imei}")
                
            # Ghi danh sách IMEI thất bại vào file
            failed_file_path = os.path.join(os.path.dirname(__file__), "failed_imei.txt")
            try:
                with open(failed_file_path, 'w', encoding='utf-8') as f:
                    for failed_imei in failed_imei_list:
                        f.write(f"{failed_imei}\n")
                print(f"\n💾 Đã lưu danh sách IMEI thất bại vào file: {failed_file_path}")
            except Exception as e:
                print(f"⚠️  Lỗi khi ghi file IMEI thất bại: {e}")
        else:
            print(f"\n🎉 Tất cả IMEI đều tải thành công!")
        
        # Làm sạch thư mục TMP (xóa các file còn lại nếu có)
        try:
            remaining_files = glob.glob(os.path.join(tmp_dir, "*"))
            if remaining_files:
                print(f"\n🧹 Đang dọn dẹp {len(remaining_files)} file còn lại trong thư mục TMP...")
                for file in remaining_files:
                    os.remove(file)
                print("✅ Đã dọn dẹp thư mục TMP")
        except Exception as e:
            print(f"⚠️  Lỗi khi dọn dẹp thư mục TMP: {e}")

        # Giữ trình duyệt mở 60 giây để quan sát kết quả
        time.sleep(60)
        
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        print("Đóng trình duyệt...")
        driver.quit()

if __name__ == "__main__":
    main()
