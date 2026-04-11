import socket

HOST = "127.0.0.1" # change this to hotspot ip address
PORT = 56700
ADVERTISED_WINDOW = 1
MAX_ADVERTISED_WINDOW = 2 ** 8
missing_seq_nums = []

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    connection, address = s.accept()
    with connection:
        print(f"Connected by {address}")
        while True:
            data = connection.recv(1024)
            if not data:
                break
            print(int(data.decode('utf8')))
            connection.sendall(data)
