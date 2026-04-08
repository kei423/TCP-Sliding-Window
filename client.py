import socket
import random

HOST = "127.0.0.1" # localhost
PORT = 56700
NUM_PACKETS = 10000000 # 10 mil
ADVERTISED_WINDOW = 2 ** 8
MAX_SEQUENCE_NUMBER = ADVERTISED_WINDOW ** 2
DROP_CHANCE = 0.01

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    current_sequence_numnber = 0
    dropped_sequence_numbers = []
    for _ in range(NUM_PACKETS // 100):
        for _ in range(100):
            if random.random() > DROP_CHANCE:
                s.sendall(str(current_sequence_numnber).encode('utf8'))
                data = s.recv(1024)

                print(f"Received: {data!r}")
            else:
                if current_sequence_numnber not in dropped_sequence_numbers:
                    dropped_sequence_numbers.append(current_sequence_numnber)

            current_sequence_numnber += 1
            if current_sequence_numnber > MAX_SEQUENCE_NUMBER:
                current_sequence_numnber = 0
        
        # check for packets that got dropped
        successfully_resent_sequence_number_indices = []
        for index, sequence_number in enumerate(dropped_sequence_numbers):
            if random.random() > DROP_CHANCE:
                s.sendall(str(sequence_number).encode('utf8'))
                data = s.recv(1024)

                print(f"Resent received: {data!r}")
                successfully_resent_sequence_number_indices.append(index)
        
        for index in successfully_resent_sequence_number_indices[::-1]:
            dropped_sequence_numbers.pop(index)
