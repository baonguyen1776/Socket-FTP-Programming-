# 📁 Directory Operations – Quản lý thư mục trên FTP Server

do_ls(self, args) # Liệt kê các file và thư mục trong thư mục hiện tại trên FTP server.

do_cd(self, args) # Thay đổi thư mục hiện tại trên FTP server đến đường dẫn được chỉ định.

do_pwd(self, args) # In ra thư mục hiện tại trên FTP server.

do_mkdir(self, args) # Tạo thư mục mới trên FTP server tại đường dẫn chỉ định.

do_rmdir(self, args) # Xóa thư mục (rỗng) trên FTP server.

do_delete(self, args) # Xóa một file trên FTP server.

do_rename(self, args) # Đổi tên một file hoặc thư mục trên FTP server.

# ⬇️⬆️ File Transfer – Tải lên / tải xuống file

do_get(self, args) # Tải về 1 file từ FTP server về máy cục bộ.

do_recv(self, args) # Alias (bí danh) cho do_get – hoạt động giống hệt.

do_mget(self, args) # Tải về nhiều file từ FTP server, hỗ trợ wildcard (\*).

do_put(self, args) # Tải 1 file từ máy cục bộ lên FTP server (phải qua quét virus trước).

do_mput(self, args) # Tải nhiều file từ máy cục bộ lên FTP server, quét hết trước khi upload.

do_prompt(self, args) # Bật/tắt chế độ xác nhận khi dùng mget hoặc mput.

# 🛠️ Session Management – Quản lý phiên làm việc FTP

do_ascii(self, args) # Chuyển chế độ truyền file sang ASCII (text mode).

do_binary(self, args) # Chuyển chế độ truyền file sang binary (dạng nhị phân).

do_status(self, args) # Hiển thị trạng thái kết nối hiện tại và các chế độ truyền.

do_passive(self, args) # Bật/tắt chế độ passive FTP.

do_open(self, args) # Kết nối tới một FTP server bằng hostname/IP và port.

do_close(self, args) # Ngắt kết nối với FTP server.

do_quit(self, args) # Thoát khỏi chương trình client.

do_bye(self, args) # Alias của do_quit – cú pháp thân thiện hơn.

do_help(self, args) # Hiển thị danh sách lệnh và hướng dẫn sử dụng.

# 💻 Local Operations – Tác động lên máy cục bộ

do_lcd(self, args) # Thay đổi thư mục làm việc hiện tại của máy cục bộ. # Nếu không có đối số, in ra thư mục hiện tại.

# ⭐ Bonus Functions – Các hàm nâng cao (tùy chọn để cộng điểm)

do_putdir(self, args) # Tải lên toàn bộ một thư mục và các thư mục con lên FTP server (recursive upload).

do_getdir(self, args) # Tải về toàn bộ một thư mục và các thư mục con từ FTP server (recursive download).

log_event(self, msg) # Ghi log các hành động và sự kiện (upload, download, kết quả quét virus...) vào file log.

```sh
ftp_client/
├── __main__.py            # Điểm khởi chạy chính (gọi run)
├── client.py              # Lớp FTPClientApp chính
├── ftp_commands.py        # Các lệnh do_* (do_get, do_put, ...)
├── ftp_helpers.py         # Hàm helper (_download_file, _upload_file, _ftp_cmd)
├── virus_scan.py          # Kết nối ClamAV Agent (_connect_to_agent)
├── config.py              # Cấu hình (host, port, buffer size...)
└── utils.py               # Tiện ích phụ nếu cần
```

# 📁 Các Lệnh FTP Phổ Biến Trong Python (ftplib)

Dưới đây là tổng hợp các hàm thường dùng trong thư viện `ftplib` của Python khi làm việc với FTP server.

---

## 📚 Bảng Hàm và Công Dụng

| **Hàm**                    | **Công Dụng**                                                                        |
| -------------------------- | ------------------------------------------------------------------------------------ |
| `ftp.pwd()`                | Trả về **thư mục hiện tại** trên server FTP (giống lệnh `pwd` trong Unix).           |
| `ftp.cwd(path)`            | **Chuyển thư mục hiện tại** đến `path` trên server FTP.                              |
| `ftp.dir()`                | **Liệt kê chi tiết thông tin** về file/thư mục (giống `ls -l`).                      |
| `ftp.nlst()`               | Trả về **danh sách tên file/thư mục** trong thư mục hiện tại.                        |
| `ftp.retrbinary(cmd, f)`   | **Tải file nhị phân từ server.** Thường dùng: `ftp.retrbinary("RETR file", f.write)` |
| `ftp.storbinary(cmd, f)`   | **Gửi file nhị phân lên server.** Ví dụ: `ftp.storbinary("STOR file", f)`            |
| `ftp.delete(filename)`     | **Xoá một file** trên server.                                                        |
| `ftp.mkd(path)`            | **Tạo thư mục mới** trên server.                                                     |
| `ftp.rmd(path)`            | **Xoá thư mục rỗng** trên server.                                                    |
| `ftp.rename(from, to)`     | **Đổi tên** hoặc **di chuyển file** từ `from` sang `to`.                             |
| `ftp.quit()`               | **Đóng kết nối** FTP một cách lịch sự.                                               |
| `ftp.login(user, passwd)`  | Đăng nhập vào server FTP với tên người dùng và mật khẩu.                             |
| `ftp.connect(host, port)`  | Kết nối đến server FTP tại địa chỉ `host` và `port`.                                 |
| `ftp.set_pasv(True/False)` | Bật/tắt chế độ **Passive Mode** (nên dùng `True` với tường lửa/NAT).                 |

---

## 🔍 So Sánh Nhanh Một Số Hàm

| Hàm         | Trả về gì?               | Mục đích                  |
| ----------- | ------------------------ | ------------------------- |
| `pwd()`     | Chuỗi đường dẫn          | Xác định thư mục hiện tại |
| `cwd(path)` | Không trả về gì          | Đổi thư mục hiện tại      |
| `dir()`     | In ra thông tin chi tiết | Giống `ls -l`             |
| `nlst()`    | List tên file (chuỗi)    | Lấy danh sách đơn giản    |

---

## 🧪 Ví Dụ Cơ Bản

```python
from ftplib import FTP

ftp = FTP('ftp.example.com')
ftp.login('username', 'password')

print("Thư mục hiện tại:", ftp.pwd())  # /home/user

ftp.cwd('documents')                   # chuyển vào thư mục documents
print("Đang ở thư mục:", ftp.pwd())    # /home/user/documents

ftp.dir()                              # in thông tin chi tiết các file
file_list = ftp.nlst()                 # lấy danh sách tên file đơn giản
print("Danh sách file:", file_list)
```

\_**\_End\_\_**
