from ftplib import FTP
import os

# ======== Cấu hình ========
FTP_HOST = "127.0.0.1"
FTP_PORT = 21
FTP_USER = "admin123"       # Thay bằng username bạn đã tạo
FTP_PASS = "12345" # Thay bằng password bạn đã đặt
LOCAL_FILE_PATH = r"D:\FZSever\test.txt"  # Đường dẫn tuyệt đối tới file
REMOTE_FILENAME = "text.txt"  # Tên file sẽ lưu trên server

# ======== Kết nối FTP và upload ========
try:
    # Kiểm tra file có tồn tại không
    if not os.path.isfile(LOCAL_FILE_PATH):
        raise FileNotFoundError(f"Không tìm thấy file: {LOCAL_FILE_PATH}")

    # Kết nối tới FTP server
    ftp = FTP()
    ftp.connect(FTP_HOST, FTP_PORT)
    ftp.login(FTP_USER, FTP_PASS)
    print(f"Đã đăng nhập FTP tại {FTP_HOST}:{FTP_PORT} dưới user '{FTP_USER}'")

    # Mở file và upload
    with open(LOCAL_FILE_PATH, "rb") as f:
        ftp.storbinary(f"STOR {REMOTE_FILENAME}", f)
        print(f"✅ Đã upload file: {REMOTE_FILENAME} lên server.")

    # Thoát FTP
    ftp.quit()

except Exception as e:
    print(f"❌ Lỗi: {e}")
