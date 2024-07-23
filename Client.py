import socket
import time

server_address = ('127.0.0.1', 65432)
client_id = None

def register():
    global client_id
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(server_address)
        s.sendall(b'01')
        data = s.recv(1024)
        client_id = data.decode('utf-8')[2:]
        print(f"Registered with ID: {client_id}")

def connect():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(server_address)
        s.sendall(f"03{client_id}".encode('utf-8'))
        while True:
            data = s.recv(1024)
            if not data:
                break
            print(f"Received: {data.decode('utf-8')}")

def send_message(dst, message):
    timestamp = str(int(time.time()))
    msg = f"05{client_id}{dst}{timestamp}{message}"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(server_address)
        s.sendall(msg.encode('utf-8'))

def read_confirmation(src, timestamp):
    msg = f"08{src}{timestamp}"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(server_address)
        s.sendall(msg.encode('utf-8'))

def create_group(members):
    timestamp = str(int(time.time()))
    members_str = ''.join(members)
    msg = f"10{client_id}{timestamp}{members_str}"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(server_address)
        s.sendall(msg.encode('utf-8'))

if __name__ == "__main__":
    register()
    connect()
    # Example usage:
    # send_message('destination_id', 'Hello World')
    # create_group(['member1_id', 'member2_id'])