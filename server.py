import socket
import matplotlib.pyplot as plt

HOST = "127.0.0.1" # localhost
PORT = 56700
ADVERTISED_WINDOW = 2 ** 8
MAX_SEQUENCE_NUMBER = ADVERTISED_WINDOW ** 2
num_received_packets = 0
received_packets = []
throughput = []
prev_seq_num = -1
missing_seq_nums = []
missing_total = []

def find_missing_seq(seq_num):
    global prev_seq_num
    global missing_seq_nums
    global missing_total

    if not ((seq_num == prev_seq_num+1) or (prev_seq_num == MAX_SEQUENCE_NUMBER and seq_num == 0)):
        #print(prev_seq_num, seq_num)
        for i in range(prev_seq_num+1, seq_num):
            missing_seq_nums.append(i)
            missing_total.append(i)
    prev_seq_num = seq_num


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

            seq_num = int(data.decode('utf8'))
            num_received_packets += 1
            received_packets.append(seq_num)
            if seq_num in missing_total:
                missing_total.remove(seq_num)
            else:
                find_missing_seq(seq_num)

            if num_received_packets%10000 == 0 and num_received_packets != 0:
                throughput.append(num_received_packets/(num_received_packets + len(missing_seq_nums)))
                missing_seq_nums = []

            connection.sendall(data)

print('Goodput Every 10k Packets:')
print(throughput)
print('Average Goodput:', sum(throughput)/len(throughput))
print('Number of Packets Received:', num_received_packets)