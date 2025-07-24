#!/usr/bin/env python3
"""
ClamAV Agent Main Entry Point
Starts the ClamAV scanning agent server with graceful shutdown support
"""

import logging 
import sys
from sever_clam import ClamAVAgentServer

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

HOST = '0.0.0.0'
PORT = 9001

def main():
    """Main entry point for ClamAV Agent"""
    logging.info("Starting ClamAV Agent...")
    logging.info(f"Server will listen on {HOST}:{PORT}")
    
    agent_server = ClamAVAgentServer(HOST, PORT)
    
    try:
        agent_server.start()
    except KeyboardInterrupt:
        logging.info("Received KeyboardInterrupt signal, stopping server...")
    except Exception as e:
        logging.error(f"Unexpected error in main: {e}")
    finally:
        agent_server.stop()
        logging.info("ClamAV Agent shutdown complete")

if __name__ == "__main__":
    main()
