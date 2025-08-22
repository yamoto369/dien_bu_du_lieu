from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

def main():
    # Thiết lập Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    
    # Tạo driver Chrome (sử dụng driver mặc định trong system PATH)
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("Đang truy cập trang web...")
        driver.get("https://stram.viettel.io/")
        
        print("Chờ element 'Gửi bù sang TCTS' xuất hiện...")
        # Chờ đến khi element xuất hiện (tối đa 30 giây)
        wait = WebDriverWait(driver, 30)
        element = wait.until(
            EC.presence_of_element_located((By.XPATH, "//span[@class='sidebar-normal' and text()='Gửi bù sang TCTS']"))
        )
        
        print("Đã tìm thấy element 'Gửi bù sang TCTS'!")
        print("Element text:", element.text)
        
        # Giữ trình duyệt mở 5 giây để quan sát
        time.sleep(5)
        
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        print("Đóng trình duyệt...")
        driver.quit()

if __name__ == "__main__":
    main()
