import socket
import os
import re
import logging
from utils import Utils

class FTPError(Exception):
    """Base FTP exception"""
    pass

class FTPPermError(FTPError):
    """FTP permission error (5xx responses)"""
    pass

class FTPTempError(FTPError):
    """FTP temporary error (4xx responses)"""
    pass

class FTPProtoError(FTPError):
    """FTP protocol error"""
    pass

# For compatibility with existing code
all_errors = (FTPError, FTPPermError, FTPTempError, FTPProtoError, socket.error, OSError)
error_perm = FTPPermError
error_temp = FTPTempError
error_proto = FTPProtoError

class CustomFTP:
    """Custom FTP client implementation using sockets"""
    
    def __init__(self):
        self.sock = None
        self.host = None
        self.port = 21
        self.timeout = 60
        self.passive_mode = True
        self.encoding = 'utf-8'
        self.welcome = None
        self.lastresp = None
        
    def connect(self, host, port=21, timeout=60):
        """Connect to FTP server"""
        self.host = host
        self.port = port
        self.timeout = timeout
        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(timeout)
            self.sock.connect((host, port))
            
            # Read welcome message
            self.welcome = self._getresp()
            Utils.log_event(f"Connected to {host}:{port} - {self.welcome}")
            return self.welcome
            
        except socket.error as e:
            if self.sock:
                self.sock.close()
                self.sock = None
            raise FTPError(f"Cannot connect to {host}:{port} - {e}")
    
    def _putline(self, line):
        """Send a line to the server"""
        if not isinstance(line, bytes):
            line = line.encode(self.encoding)
        line += b'\r\n'
        self.sock.sendall(line)
        Utils.log_event(f"FTP CMD: {line.decode(self.encoding).strip()}", level=logging.DEBUG)
    
    def _getline(self):
        """Get a line from the server"""
        line = b''
        while True:
            char = self.sock.recv(1)
            if not char:
                break
            line += char
            if line.endswith(b'\r\n'):
                break
        
        response = line.decode(self.encoding).rstrip('\r\n')
        Utils.log_event(f"FTP RESP: {response}", level=logging.DEBUG)
        return response
    
    def _getresp(self):
        """Get a response from the server"""
        resp = self._getline()
        self.lastresp = resp
        
        # Handle multi-line responses
        if len(resp) >= 4 and resp[3] == '-':
            code = resp[:3]
            while True:
                line = self._getline()
                if line.startswith(code + ' '):
                    resp = line
                    self.lastresp = resp
                    break
        
        # Check for error responses
        if resp.startswith('4'):
            raise FTPTempError(resp)
        elif resp.startswith('5'):
            raise FTPPermError(resp)
        
        return resp
    
    def _sendcmd(self, cmd):
        """Send a command and return the response"""
        self._putline(cmd)
        return self._getresp()
    
    def voidcmd(self, cmd):
        """Send a command and return the response"""
        return self._sendcmd(cmd)
    
    def login(self, user='anonymous', passwd='anonymous@'):
        """Login to the FTP server"""
        resp = self._sendcmd(f'USER {user}')
        if resp.startswith('3'):  # Need password
            resp = self._sendcmd(f'PASS {passwd}')
        return resp
    
    def quit(self):
        """Quit the FTP session"""
        try:
            resp = self._sendcmd('QUIT')
        except (FTPError, socket.error):
            resp = None
        finally:
            if self.sock:
                self.sock.close()
                self.sock = None
        return resp
    
    def pwd(self):
        """Get current working directory"""
        resp = self._sendcmd('PWD')
        # Extract path from response like '257 "/path" is current directory'
        match = re.search(r'"([^"]*)"', resp)
        if match:
            return match.group(1)
        return '/'
    
    def cwd(self, dirname):
        """Change working directory"""
        return self._sendcmd(f'CWD {dirname}')
    
    def mkd(self, dirname):
        """Create directory"""
        resp = self._sendcmd(f'MKD {dirname}')
        # Extract created directory from response
        match = re.search(r'"([^"]*)"', resp)
        if match:
            return match.group(1)
        return dirname
    
    def rmd(self, dirname):
        """Remove directory"""
        return self._sendcmd(f'RMD {dirname}')
    
    def delete(self, filename):
        """Delete file"""
        return self._sendcmd(f'DELE {filename}')
    
    def rename(self, fromname, toname):
        """Rename file"""
        resp = self._sendcmd(f'RNFR {fromname}')
        if resp.startswith('3'):  # Ready for destination
            return self._sendcmd(f'RNTO {toname}')
        return resp
    
    def size(self, filename):
        """Get file size"""
        resp = self._sendcmd(f'SIZE {filename}')
        # Extract size from response like '213 1234'
        try:
            return int(resp.split()[1])
        except (IndexError, ValueError):
            raise FTPProtoError(f"Invalid SIZE response: {resp}")
    
    def set_pasv(self, passive):
        """Set passive mode"""
        self.passive_mode = passive
    
    def _makepasv(self):
        """Enter passive mode and return data socket"""
        resp = self._sendcmd('PASV')
        # Parse PASV response like '227 Entering Passive Mode (192,168,1,1,20,21)'
        match = re.search(r'\((\d+),(\d+),(\d+),(\d+),(\d+),(\d+)\)', resp)
        if not match:
            raise FTPProtoError(f"Invalid PASV response: {resp}")
        
        nums = [int(x) for x in match.groups()]
        host = '.'.join(map(str, nums[:4]))
        port = nums[4] * 256 + nums[5]
        
        # Create data connection
        data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_sock.settimeout(self.timeout)
        data_sock.connect((host, port))
        return data_sock
    
    def _makeport(self):
        """Enter active mode and return data socket"""
        # Create listening socket
        data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_sock.bind(('', 0))  # Bind to any available port
        data_sock.listen(1)
        
        # Get local IP and port
        host, port = data_sock.getsockname()
        # Convert IP to comma-separated format
        hbytes = host.split('.')
        pbytes = [str(port // 256), str(port % 256)]
        
        # Send PORT command
        port_cmd = f"PORT {','.join(hbytes + pbytes)}"
        self._sendcmd(port_cmd)
        
        return data_sock
    
    def _transfercmd(self, cmd):
        """Setup data transfer connection"""
        if self.passive_mode:
            data_sock = self._makepasv()
            self._sendcmd(cmd)
            return data_sock
        else:
            data_sock = self._makeport()
            self._sendcmd(cmd)
            conn, addr = data_sock.accept()
            data_sock.close()
            return conn
    
    def nlst(self, *args):
        """Get name list"""
        cmd = 'NLST'
        if args:
            cmd += ' ' + ' '.join(args)
        
        data_sock = self._transfercmd(cmd)
        
        try:
            data = b''
            while True:
                chunk = data_sock.recv(8192)
                if not chunk:
                    break
                data += chunk
        finally:
            data_sock.close()
            self._getresp()  # Get transfer completion response
        
        if not data:
            return []
        
        # Split by lines and filter empty lines
        files = data.decode(self.encoding).strip().split('\n')
        return [f.strip() for f in files if f.strip()]
    
    def dir(self, *args, **kwargs):
        """Get directory listing"""
        cmd = 'LIST'
        if args and not callable(args[0]):
            cmd += ' ' + ' '.join(args)
        
        callback = None
        if args and callable(args[0]):
            callback = args[0]
        elif 'callback' in kwargs:
            callback = kwargs['callback']
        
        data_sock = self._transfercmd(cmd)
        
        try:
            data = b''
            while True:
                chunk = data_sock.recv(8192)
                if not chunk:
                    break
                data += chunk
        finally:
            data_sock.close()
            self._getresp()  # Get transfer completion response
        
        if data:
            lines = data.decode(self.encoding).strip().split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    if callback:
                        callback(line)
                    else:
                        print(line)
    
    def retrbinary(self, cmd, callback, blocksize=8192):
        """Retrieve file in binary mode"""
        data_sock = self._transfercmd(cmd)
        
        try:
            while True:
                data = data_sock.recv(blocksize)
                if not data:
                    break
                callback(data)
        finally:
            data_sock.close()
            self._getresp()  # Get transfer completion response
    
    def retrlines(self, cmd, callback=None):
        """Retrieve file in ASCII mode"""
        data_sock = self._transfercmd(cmd)
        
        try:
            data = b''
            while True:
                chunk = data_sock.recv(8192)
                if not chunk:
                    break
                data += chunk
        finally:
            data_sock.close()
            self._getresp()  # Get transfer completion response
        
        if data:
            lines = data.decode(self.encoding).split('\n')
            for line in lines:
                line = line.rstrip('\r')
                if callback:
                    callback(line)
                else:
                    print(line)
    
    def storbinary(self, cmd, file, blocksize=8192):
        """Store file in binary mode"""
        data_sock = self._transfercmd(cmd)
        
        try:
            while True:
                data = file.read(blocksize)
                if not data:
                    break
                if isinstance(data, str):
                    data = data.encode(self.encoding)
                data_sock.sendall(data)
        finally:
            data_sock.close()
            self._getresp()  # Get transfer completion response
    
    def storlines(self, cmd, lines):
        """Store file in ASCII mode"""
        data_sock = self._transfercmd(cmd)
        
        try:
            for line in lines:
                if isinstance(line, str):
                    line = line.encode(self.encoding)
                if not line.endswith(b'\r\n'):
                    line += b'\r\n'
                data_sock.sendall(line)
        finally:
            data_sock.close()
            self._getresp()  # Get transfer completion response

# Alias for compatibility
FTP = CustomFTP