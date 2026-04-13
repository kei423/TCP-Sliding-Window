import socket
import matplotlib.pyplot as plt

HOST = "127.0.0.1" # localhost
PORT = 56700
ADVERTISED_WINDOW = 2 ** 8
MAX_SEQUENCE_NUMBER = ADVERTISED_WINDOW ** 2

num_received_packets = 0
received_packets = []
goodput = []
prev_seq_num = -1
# keeps track of missing seq nums within the 10k batch
missing_seq_nums = []
# keeps track of all missing seq nums
missing_total = []

# function to find missing sequence numbers between received received sequence numbers
def find_missing_seq(seq_num):
    global prev_seq_num
    global missing_seq_nums
    global missing_total

    # if there is/are dropped packets, the sequence number not be +1 of the previous sequence number
    # or 0 if the previous sequence number was the max number
    if not ((seq_num == prev_seq_num+1) or (prev_seq_num == MAX_SEQUENCE_NUMBER and seq_num == 0)):
        for i in range(prev_seq_num+1, seq_num):
            missing_seq_nums.append(i)
            missing_total.append(i)
    prev_seq_num = seq_num


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    connection, address = s.accept()
    with connection:
        # Prints sender and receiver IP
        print(f"Sender IP Address: {address[0]}")
        receiver_ip, receiver_port = connection.getsockname()
        print(f'Receiver IP Address: {receiver_ip}')
        while True:
            data = connection.recv(1024)
            if not data:
                break

            seq_num = int(data.decode('utf8'))
            num_received_packets += 1
            received_packets.append(seq_num)
            # checks if a seq num is retransmitted
            if seq_num in missing_total:
                # removes packet if retransmission is successful
                missing_total.remove(seq_num)
            else:
                # checks for missing sequences if not retransmission
                find_missing_seq(seq_num)

            # for every 10k packets, calculate goodput (received / (received + attempted missing packets))
            if num_received_packets%10000 == 0 and num_received_packets != 0:
                goodput.append(num_received_packets/(num_received_packets + len(missing_seq_nums)))
                missing_seq_nums = []

            connection.sendall(data)

# output for goodput for every 10k packets, final average goodput, and number of packets received
print('Goodput Every 10k Packets:')
print(goodput)
print('Average Goodput:', sum(goodput)/len(goodput))
print('Number of Packets Received:', num_received_packets)