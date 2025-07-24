#!/usr/bin/env python3
"""
Raw Socket FTP Implementation - Không dùng class wrapper, chỉ socket thô
"""

import socket
import re
import os
import logging

# Global variables để lưu trạng thái FTP connection
ftp_socket = None
ftp_host = None
ftp_port = 21
ftp_timeout = 60
ftp_passive_mode = True
ftp_encoding = 'utf-8'
ftp_last_response = None

# Exception classes
class FTPError(Exception):
    pass

class FTPPermError(FTPError):
    pass

class FTPTempError(FTPError):
    pass

class FTPProtoError(FTPError):
    pass

# Compatibility
all_errors = (FTPError, FTPPermError, FTPTempError, FTPProtoError, socket.error, OSError)
error_perm = FTPPermError
error_temp = FTPTempError
error_proto = FTPProtoError

def ftp_send_line(line):
    """Gửi một dòng lệnh tới FTP server"""
    global ftp_socket, ftp_encoding
    if not isinstance(line, bytes):
        line = line.encode(ftp_encoding)
    line += b'\r\n'
    ftp_socket.sendall(line)
    print(f">>> {line.decode(ftp_encoding).strip()}")

def ftp_recv_line():
    """Nhận một dòng phản hồi từ FTP server"""
    global ftp_socket, ftp_encoding
    line = b''
    while True:
        char = ftp_socket.recv(1)
        if not char:
            break
        line += char
        if line.endswith(b'\r\n'):
            break
    
    response = line.decode(ftp_encoding).rstrip('\r\n')
    print(f"<<< {response}")
    return response

def ftp_get_response():
    """Nhận phản hồi từ server và xử lý multi-line response"""
    global ftp_last_response
    
    resp = ftp_recv_line()
    ftp_last_response = resp
    
    # Xử lý multi-line response
    if len(resp) >= 4 and resp[3] == '-':
        code = resp[:3]
        while True:
            line = ftp_recv_line()
            if line.startswith(code + ' '):
                resp = line
                ftp_last_response = resp
                break
    
    # Kiểm tra lỗi
    if resp.startswith('4'):
        raise FTPTempError(resp)
    elif resp.startswith('5'):
        raise FTPPermError(resp)
    
    return resp

def ftp_send_command(cmd):
    """Gửi lệnh và nhận phản hồi"""
    ftp_send_line(cmd)
    return ftp_get_response()

def ftp_connect(host, port=21, timeout=60):
    """Kết nối tới FTP server"""
    global ftp_socket, ftp_host, ftp_port, ftp_timeout
    
    ftp_host = host
    ftp_port = port
    ftp_timeout = timeout
    
    try:
        ftp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ftp_socket.settimeout(timeout)
        ftp_socket.connect((host, port))
        
        # Đọc welcome message
        welcome = ftp_get_response()
        print(f"Connected to {host}:{port}")
        return welcome
        
    except socket.error as e:
        if ftp_socket:
            ftp_socket.close()
            ftp_socket = None
        raise FTPError(f"Cannot connect to {host}:{port} - {e}")

def ftp_login(user='anonymous', passwd='anonymous@'):
    """Đăng nhập FTP server"""
    resp = ftp_send_command(f'USER {user}')
    if resp.startswith('3'):  # Cần password
        resp = ftp_send_command(f'PASS {passwd}')
    return resp

def ftp_quit():
    """Thoát FTP session"""
    global ftp_socket
    try:
        resp = ftp_send_command('QUIT')
    except (FTPError, socket.error):
        resp = None
    finally:
        if ftp_socket:
            ftp_socket.close()
            ftp_socket = None
    return resp

def ftp_pwd():
    """Lấy thư mục hiện tại"""
    resp = ftp_send_command('PWD')
    # Trích xuất path từ response như '257 "/path" is current directory'
    match = re.search(r'"([^"]*)"', resp)
    if match:
        return match.group(1)
    return '/'

def ftp_cwd(dirname):
    """Thay đổi thư mục"""
    return ftp_send_command(f'CWD {dirname}')

def ftp_mkd(dirname):
    """Tạo thư mục"""
    resp = ftp_send_command(f'MKD {dirname}')
    match = re.search(r'"([^"]*)"', resp)
    if match:
        return match.group(1)
    return dirname

def ftp_rmd(dirname):
    """Xóa thư mục"""
    return ftp_send_command(f'RMD {dirname}')

def ftp_delete(filename):
    """Xóa file"""
    return ftp_send_command(f'DELE {filename}')

def ftp_rename(fromname, toname):
    """Đổi tên file"""
    resp = ftp_send_command(f'RNFR {fromname}')
    if resp.startswith('3'):
        return ftp_send_command(f'RNTO {toname}')
    return resp

def ftp_size(filename):
    """Lấy kích thước file"""
    resp = ftp_send_command(f'SIZE {filename}')
    try:
        return int(resp.split()[1])
    except (IndexError, ValueError):
        raise FTPProtoError(f"Invalid SIZE response: {resp}")

def ftp_set_pasv(passive):
    """Đặt chế độ passive"""
    global ftp_passive_mode
    ftp_passive_mode = passive

def ftp_make_pasv():
    """Tạo kết nối passive mode"""
    global ftp_timeout
    
    resp = ftp_send_command('PASV')
    # Parse PASV response như '227 Entering Passive Mode (192,168,1,1,20,21)'
    match = re.search(r'\((\d+),(\d+),(\d+),(\d+),(\d+),(\d+)\)', resp)
    if not match:
        raise FTPProtoError(f"Invalid PASV response: {resp}")
    
    nums = [int(x) for x in match.groups()]
    host = '.'.join(map(str, nums[:4]))
    port = nums[4] * 256 + nums[5]
    
    # Tạo data connection
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.settimeout(ftp_timeout)
    data_socket.connect((host, port))
    return data_socket

def ftp_make_port():
    """Tạo kết nối active mode"""
    global ftp_timeout
    
    # Tạo listening socket
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.bind(('', 0))
    data_socket.listen(1)
    
    # Lấy local IP và port
    host, port = data_socket.getsockname()
    hbytes = host.split('.')
    pbytes = [str(port // 256), str(port % 256)]
    
    # Gửi lệnh PORT
    port_cmd = f"PORT {','.join(hbytes + pbytes)}"
    ftp_send_command(port_cmd)
    
    return data_socket

def ftp_transfer_cmd(cmd):
    """Thiết lập kết nối truyền dữ liệu"""
    global ftp_passive_mode
    
    if ftp_passive_mode:
        data_socket = ftp_make_pasv()
        ftp_send_command(cmd)
        return data_socket
    else:
        data_socket = ftp_make_port()
        ftp_send_command(cmd)
        conn, addr = data_socket.accept()
        data_socket.close()
        return conn

def ftp_nlst(*args):
    """Lấy danh sách tên file"""
    global ftp_encoding
    
    cmd = 'NLST'
    if args:
        cmd += ' ' + ' '.join(args)
    
    data_socket = ftp_transfer_cmd(cmd)
    
    try:
        data = b''
        while True:
            chunk = data_socket.recv(8192)
            if not chunk:
                break
            data += chunk
    finally:
        data_socket.close()
        ftp_get_response()  # Nhận phản hồi hoàn thành
    
    if not data:
        return []
    
    files = data.decode(ftp_encoding).strip().split('\n')
    return [f.strip() for f in files if f.strip()]

def ftp_dir(path=None, callback=None):
    """Lấy danh sách chi tiết thư mục"""
    global ftp_encoding
    
    cmd = 'LIST'
    if path:
        cmd += f' {path}'
    
    data_socket = ftp_transfer_cmd(cmd)
    
    try:
        data = b''
        while True:
            chunk = data_socket.recv(8192)
            if not chunk:
                break
            data += chunk
    finally:
        data_socket.close()
        ftp_get_response()  # Nhận phản hồi hoàn thành
    
    if data:
        lines = data.decode(ftp_encoding).strip().split('\n')
        for line in lines:
            line = line.strip()
            if line:
                if callback:
                    callback(line)
                else:
                    print(line)

def ftp_retrbinary(cmd, callback, blocksize=8192):
    """Tải file ở chế độ binary"""
    data_socket = ftp_transfer_cmd(cmd)
    
    try:
        while True:
            data = data_socket.recv(blocksize)
            if not data:
                break
            callback(data)
    finally:
        data_socket.close()
        ftp_get_response()

def ftp_retrlines(cmd, callback=None):
    """Tải file ở chế độ ASCII"""
    global ftp_encoding
    
    data_socket = ftp_transfer_cmd(cmd)
    
    try:
        data = b''
        while True:
            chunk = data_socket.recv(8192)
            if not chunk:
                break
            data += chunk
    finally:
        data_socket.close()
        ftp_get_response()
    
    if data:
        lines = data.decode(ftp_encoding).split('\n')
        for line in lines:
            line = line.rstrip('\r')
            if callback:
                callback(line)
            else:
                print(line)

def ftp_storbinary(cmd, file_obj, blocksize=8192):
    """Upload file ở chế độ binary"""
    global ftp_encoding
    
    data_socket = ftp_transfer_cmd(cmd)
    
    try:
        while True:
            data = file_obj.read(blocksize)
            if not data:
                break
            if isinstance(data, str):
                data = data.encode(ftp_encoding)
            data_socket.sendall(data)
    finally:
        data_socket.close()
        ftp_get_response()

def ftp_storlines(cmd, lines):
    """Upload file ở chế độ ASCII"""
    global ftp_encoding
    
    data_socket = ftp_transfer_cmd(cmd)
    
    try:
        for line in lines:
            if isinstance(line, str):
                line = line.encode(ftp_encoding)
            if not line.endswith(b'\r\n'):
                line += b'\r\n'
            data_socket.sendall(line)
    finally:
        data_socket.close()
        ftp_get_response()

def ftp_voidcmd(cmd):
    """Gửi lệnh và trả về phản hồi"""
    return ftp_send_command(cmd)

# Wrapper class để tương thích với code cũ
class FTP:
    """Wrapper class sử dụng raw socket functions"""
    
    def __init__(self):
        self.host = None
        self.port = 21
        
    def connect(self, host, port=21, timeout=60):
        self.host = host
        self.port = port
        return ftp_connect(host, port, timeout)
        
    def login(self, user='anonymous', passwd='anonymous@'):
        return ftp_login(user, passwd)
        
    def quit(self):
        return ftp_quit()
        
    def pwd(self):
        return ftp_pwd()
        
    def cwd(self, dirname):
        return ftp_cwd(dirname)
        
    def mkd(self, dirname):
        return ftp_mkd(dirname)
        
    def rmd(self, dirname):
        return ftp_rmd(dirname)
        
    def delete(self, filename):
        return ftp_delete(filename)
        
    def rename(self, fromname, toname):
        return ftp_rename(fromname, toname)
        
    def size(self, filename):
        return ftp_size(filename)
        
    def set_pasv(self, passive):
        return ftp_set_pasv(passive)
        
    def nlst(self, *args):
        return ftp_nlst(*args)
        
    def dir(self, *args, **kwargs):
        path = None
        callback = None
        
        if args:
            if callable(args[0]):
                callback = args[0]
            else:
                path = args[0]
                if len(args) > 1 and callable(args[1]):
                    callback = args[1]
        
        return ftp_dir(path, callback)
        
    def retrbinary(self, cmd, callback, blocksize=8192):
        return ftp_retrbinary(cmd, callback, blocksize)
        
    def retrlines(self, cmd, callback=None):
        return ftp_retrlines(cmd, callback)
        
    def storbinary(self, cmd, file_obj, blocksize=8192):
        return ftp_storbinary(cmd, file_obj, blocksize)
        
    def storlines(self, cmd, lines):
        return ftp_storlines(cmd, lines)
        
    def voidcmd(self, cmd):
        return ftp_voidcmd(cmd)