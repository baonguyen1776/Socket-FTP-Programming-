"""
Main entry point for FTP Client
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_gui():
    """Run GUI client"""
    try:
        from client.ui.main import FTPClientApp
        app = FTPClientApp()
        app.start()
    except ImportError as e:
        print(f"Error importing GUI components: {e}")
        print("Make sure tkinter is installed")
        sys.exit(1)

def run_cli():
    """Run command line client"""
    from client.core.ftp_command import FTPCommands
    from client.core.raw_socket_ftp import FTP
    
    ftp = FTP()
    client = FTPCommands(ftp)
    client.cmdloop()

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--cli":
            run_cli()
        elif sys.argv[1] == "--gui":
            run_gui()
        else:
            print("Usage: python run_client.py [--cli|--gui]")
            print("  --cli: Run command line interface")
            print("  --gui: Run graphical interface")
            sys.exit(1)
    else:
        # Default to CLI
        print("Starting FTP Client (CLI mode)")
        print("Use --gui for graphical interface")
        run_cli()

if __name__ == "__main__":
    main()