| Thành phần      | Trách nhiệm chính                           |
| --------------- | ------------------------------------------- |
| `ClamAVScanner` | Thực hiện quét virus bằng `clamscan`        |
| `FileHandler`   | Nhận và lưu file tạm từ client              |
| `ClamAVServer`  | Khởi chạy socket SSL server và xử lý client |
| `ClientHandler` | Đại diện cho một phiên làm việc với client  |

# ClamAV Agent

Đây là một chương trình ClamAV Agent được viết bằng Python, có chức năng nhận file qua socket, quét virus bằng `clamscan` (ClamAV) và trả về kết quả cho client.

## Cấu trúc dự án

- `clamav_agent.py`: Chương trình chính của ClamAV Agent.

## Yêu cầu hệ thống

- Python 3.x
- ClamAV và `clamav-daemon` (đã cài đặt và cập nhật cơ sở dữ liệu virus)

## Hướng dẫn sử dụng

### 1. Khởi động ClamAV Agent

Chạy chương trình `clamav_agent.py` trên máy chủ hoặc một terminal riêng:

```bash
python3 clamav_agent.py
```

Agent sẽ lắng nghe trên địa chỉ `0.0.0.0` (tất cả các interface) và cổng `65432`.

### 2. Kiểm tra ClamAV Agent (sử dụng `clamav_client.py`)

Bạn có thể sử dụng `clamav_client.py` để kiểm tra chức năng của Agent. Đảm bảo rằng `clamav_client.py` được cấu hình để kết nối đến địa chỉ IP và cổng của máy chủ đang chạy `clamav_agent.py`.

**Tạo file test:**

Để kiểm tra file bị nhiễm, bạn có thể tạo một file EICAR test virus:

```bash
echo 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*' > eicar.txt
```

Để kiểm tra file sạch:

```bash
echo 'This is a clean file for testing.' > clean_file.txt
```

**Chạy client:**

```bash
python3 clamav_client.py
```

Chương trình client sẽ gửi `eicar.txt` và `clean_file.txt` đến agent để quét và in ra kết quả.

## Thiết kế

Chương trình được thiết kế theo hướng đối tượng (OOP) với các lớp chính:

- `ClamAVScanner`: Chịu trách nhiệm thực hiện lệnh `clamscan` để quét virus trên một file cụ thể.
- `ClientHandler`: Xử lý kết nối từ mỗi client trong một thread riêng biệt. Nó nhận tên file, nội dung file, gọi `ClamAVScanner` để quét, và gửi kết quả trở lại client.
- `ClamAVAgentServer`: Lớp server chính, lắng nghe các kết nối đến và tạo ra một `ClientHandler` mới cho mỗi kết nối.

## Lưu ý

- Thư mục tạm `temp_scan_files` sẽ được tạo để lưu trữ các file nhận được trước khi quét. Các file này sẽ được xóa sau khi quét xong.
- Logging được cấu hình để ghi lại các thông tin quan trọng về hoạt động của agent.
- Để sử dụng trong môi trường thực tế, cần cân nhắc thêm về bảo mật (ví dụ: TLS/SSL cho giao tiếp socket), xử lý lỗi mạnh mẽ hơn, và quản lý tài nguyên hiệu quả hơn.
