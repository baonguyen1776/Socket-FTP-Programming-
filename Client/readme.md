Giải thích code:

- Thứ nhất là ta cần import các thư viện cần dùng như:
  - ftplib: để làm việc với protocol FTP
  - os: Để làm việc với hệ thống tập tin
  - socket: Để làm việc với kết nối mạng
  - sys: Để làm việc với các tham số dòng lệnh
  - struct: Để làm việc với cấu trúc dữ liệu nhị phân
  - glob: Để tìm kiếm các tập tin theo mẫu
  - shlex: Để làm việc với các tập tin nén
  - readline: Để đọc dữ liệu từ tập tin
  - logging: Để ghi lại các thông tin log

Thứ hai các dòng lệnh từ dòng 12 đến dòng 16 là các dòng code để thiết lập địa chỉ host CLAMAV hay Port cũng như SIZE mà đối tương Agent thiết lập

Từ dòng 19-21 là lệnh để log các thông tin ra terminal ví dụ như: đã kết nối tệp thành công hay lỗi rồi

Trong `Class FTPClientApp` thì bao gồm các hàm `__init__` (constructer) - `_connect_to_agent_` xử lý kết nối với agent (self chứa post và host của CLAMAV)
