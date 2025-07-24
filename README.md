# Secure FTP Client with Virus Scanning via ClamAV Agent

This project implements a secure FTP client that integrates with a ClamAV agent for virus scanning before file uploads. It consists of two main components: an FTP Client and a ClamAV Agent.

## Components

1.  **FTP Client**: A custom FTP client application that interacts with an FTP server and the ClamAV Agent. It supports various FTP commands, including file and directory operations, and ensures files are scanned for viruses before being uploaded.
2.  **ClamAV Agent**: A server-side component that receives files from the FTP Client, scans them using the `clamscan` utility (part of ClamAV), and returns the scan result (OK or INFECTED) back to the client.

## System Requirements

To run this project, you will need:

- Python 3.x
- `tkinter` library (usually included with Python installations, but may need to be installed separately on some systems)
- `pyftpdlib` (for the FTP server, if you choose to use it)
- ClamAV antivirus engine (including `clamscan` utility)
- An FTP Server (e.g., FileZilla Server, vsftpd)

## Setup Instructions

### 1. ClamAV Installation and Configuration

ClamAV is an open-source antivirus engine. You need to install it on the machine where the `ClamAV Agent` will run.

**On Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install clamav clamav-daemon
```

**On macOS (using Homebrew):**

```bash
brew install clamav
```

After installation, ensure the ClamAV daemon is running and update the virus definitions:

```bash
sudo freshclam
sudo systemctl start clamav-freshclam
sudo systemctl enable clamav-freshclam
sudo systemctl start clamav-daemon
sudo systemctl enable clamav-daemon
```

### 2. FTP Server Setup

You can use any FTP server software. Here are instructions for a couple of popular choices:

#### a. FileZilla Server (Windows)

1.  Download and install FileZilla Server from [https://filezilla-project.org/](https://filezilla-project.org/)
2.  Launch FileZilla Server Interface.
3.  Go to `Edit > Users` and add a new user. Set a password and add a shared folder (this will be the root directory for your FTP client).
4.  Ensure the server is running and accessible from the machine where your FTP client will run.

#### b. vsftpd (Linux)

1.  Install vsftpd:
    ```bash
    sudo apt install vsftpd
    ```
2.  Configure vsftpd (edit `/etc/vsftpd.conf`). A minimal setup might involve:
    ```
    anonymous_enable=NO
    local_enable=YES
    write_enable=YES
    chroot_local_user=YES
    ```
3.  Restart vsftpd:
    ```bash
    sudo systemctl restart vsftpd
    ```
4.  Create an FTP user and set permissions for their home directory.

### 3. Project Dependencies (Python)

Navigate to the `Client` and `ClamAvAgent` directories and install any required Python packages. Based on the code, `tkinter` is a standard library, but `pyftpdlib` might be needed if you're running a Python-based FTP server for testing.

```bash
pip install pyftpdlib # If you plan to use a Python FTP server for testing
```

## Running the Programs

This project involves three main entities running on potentially separate machines (or different terminal windows/ports on the same machine):

1.  **FTP Client**
2.  **ClamAV Agent**
3.  **FTP Server** (third-party software)

### 1. Start the ClamAV Agent

Open a terminal and navigate to the `ClamAvAgent` directory:

```bash
cd ClamAvAgent
python3 main.py
```

The agent will start listening for connections on `0.0.0.0:9001` (default, configurable in `main.py`). You should see log messages indicating it's running.

### 2. Start the FTP Server

Ensure your chosen FTP server (FileZilla, vsftpd, etc.) is running and configured with a user account that the FTP client can use.

### 3. Start the FTP Client

Open a new terminal and navigate to the `Client` directory:

```bash
cd Client
python3 main.py
```

This will launch a graphical login window. Enter the FTP server details (host, port, username, password) and the ClamAV Agent details (host, port). The default ClamAV Agent port is `9001`.

## Sample Commands and Expected Outputs

Once connected via the FTP Client GUI, you can perform various FTP operations. The client will automatically send files to the ClamAV Agent for scanning before `put` or `mput` operations.

### Example: Uploading a Clean File

1.  Ensure ClamAV Agent is running.
2.  Connect FTP Client to your FTP server.
3.  In the FTP Client GUI, use the `put` command (or the upload button) to upload a clean file (e.g., a simple text file).

    **Expected Output (ClamAV Agent Terminal):**

    ```
    [Timestamp] - INFO - Received file for scanning: /tmp/temp_file_name.txt
    [Timestamp] - INFO - Scan result for /tmp/temp_file_name.txt: OK
    ```

    **Expected Output (FTP Client GUI/Logs):**
    The file should be successfully uploaded to the FTP server.

### Example: Uploading an Infected File

To test with an infected file, you can use the EICAR test file, which is a harmless file detected as a virus by antivirus software.

1.  Create a file named `eicar.txt` with the following content:
    ```
    X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*
    ```
2.  Attempt to upload `eicar.txt` using the FTP Client.

    **Expected Output (ClamAV Agent Terminal):**

    ```
    [Timestamp] - INFO - Received file for scanning: /tmp/eicar.txt
    [Timestamp] - INFO - Scan result for /tmp/eicar.txt: INFECTED
    ```

    **Expected Output (FTP Client GUI/Logs):**
    The upload should be aborted, and a warning message should be displayed, indicating that the file is infected and cannot be uploaded.

### Other FTP Commands

The client supports standard FTP commands. You can type them into the command input field in the GUI:

- `ls`: List files and directories on the FTP server.
- `cd <directory>`: Change directory on the FTP server.
- `pwd`: Print working directory on the FTP server.
- `mkdir <directory_name>`: Create a new directory on the FTP server.
- `rmdir <directory_name>`: Remove a directory on the FTP server.
- `delete <file_name>`: Delete a file on the FTP server.
- `rename <old_name> <new_name>`: Rename a file on the FTP server.
- `get <file_name>`: Download a file from the FTP server.
- `mput <wildcard>`: Upload multiple files (e.g., `mput *.txt`). Each file will be scanned.
- `mget <wildcard>`: Download multiple files.
- `quit` or `bye`: Exit the FTP client.
- `help` or `?`: Display help information.

## Project Structure

```
Socket-FTP-Programming-/
├── ClamAvAgent/
│   ├── handler.py
│   ├── main.py
│   ├── scanner.py
│   └── sever_clam.py
├── Client/
│   ├── client.py
│   ├── config.py
│   ├── ftp_command.py
│   ├── ftp_gui.py
│   ├── ftp_helpers.py
│   ├── login_window.py
│   ├── main.py
│   ├── utils.py
│   └── virus_scan.py
└── tests/
    ├── ... (test files)
```
