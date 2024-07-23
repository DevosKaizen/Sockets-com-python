import socket
import threading
import time

clients = {}
pending_messages = {}

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode('utf-8')
            handle_message(message, conn)

def handle_message(message, conn):
    code = message[:2]
    if code == '01':
        register_client(conn)
    elif code == '03':
        client_id = message[2:15]
        connect_client(client_id, conn)
    elif code == '05':
        handle_send_message(message, conn)
    elif code == '08':
        handle_read_confirmation(message, conn)
    elif code == '10':
        handle_create_group(message, conn)

def register_client(conn):
    client_id = generate_unique_id()
    clients[client_id] = conn
    conn.sendall(f"02{client_id}".encode('utf-8'))

def generate_unique_id():
    return str(int(time.time() * 1000000))[-13:]

def connect_client(client_id, conn):
    clients[client_id] = conn
    if client_id in pending_messages:
        for message in pending_messages[client_id]:
            conn.sendall(message.encode('utf-8'))
        del pending_messages[client_id]

def handle_send_message(message, conn):
    src = message[2:15]
    dst = message[15:28]
    timestamp = message[28:38]
    data = message[38:]
    if dst in clients:
        clients[dst].sendall(f"06{message}".encode('utf-8'))
        conn.sendall(f"07{dst}{timestamp}".encode('utf-8'))
    else:
        if dst not in pending_messages:
            pending_messages[dst] = []
        pending_messages[dst].append(message)
        conn.sendall(f"07{dst}{timestamp}".encode('utf-8'))

def handle_read_confirmation(message, conn):
    src = message[2:15]
    timestamp = message[15:25]
    for client_id, messages in pending_messages.items():
        messages[:] = [msg for msg in messages if msg[2:15] != src or msg[28:38] > timestamp]
    conn.sendall(f"09{src}{timestamp}".encode('utf-8'))

def handle_create_group(message, conn):
    group_id = generate_unique_id()
    creator = message[2:15]
    timestamp = message[15:25]
    members = [message[i:i+13] for i in range(25, len(message), 13)]
    group_message = f"11{group_id}{timestamp}{''.join(members + [creator])}"
    for member in members + [creator]:
        if member in clients:
            clients[member].sendall(group_message.encode('utf-8'))
        else:
            if member not in pending_messages:
                pending_messages[member] = []
            pending_messages[member].append(group_message)

def start_server():
    host = '127.0.0.1'
    port = 65432
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print("Server started, waiting for connections...")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    start_server()