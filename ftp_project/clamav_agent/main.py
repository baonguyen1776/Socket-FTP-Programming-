import logging 
from sever_clam import ClamAVAgentServer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HOST = '0.0.0.0'
PORT = 9001

if __name__ == "__main__":
    agent_server = ClamAVAgentServer(HOST, PORT)
    try:
        agent_server.start()
    except KeyboardInterrupt:
        logging.info("Received KeyboardInterrupt signal, stopping server...")
    finally:
        agent_server.stop()
