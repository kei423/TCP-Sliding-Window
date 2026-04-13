import socket
import random
import matplotlib.pyplot as plt

# HOST = "127.0.0.1" # localhost
HOST = "172.20.10.5" # change this to hotspot ip address
PORT = 56700
# NUM_PACKETS = 1000000 # 1 mil
NUM_PACKETS = 500_000
MAX_ADVERTISED_WINDOW = 2 ** 8
MAX_SEQUENCE_NUMBER = MAX_ADVERTISED_WINDOW ** 2
DROP_CHANCE = 0.01

def send_packet(s, seq_num):
    # returns True if the packet has been successfully sent
    # returns False if the packet is dropped at a 1% chance
    if random.random() < DROP_CHANCE:
        return False
    s.sendall(str(seq_num).encode('utf8'))
    data = s.recv(1024)
    return True

def plot_data(time_axis, sender_window_over_time_axis, seq_received_times, seq_received_nums, seq_dropped_times, seq_dropped_nums):
    # plotting data stored once every 1000 packets sent
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    #1 TCP sender window size over time in the x-axis
    ax1.plot(time_axis, sender_window_over_time_axis, linewidth=0.8)
    ax1.axhline(y=MAX_ADVERTISED_WINDOW, color='r', linestyle='--', label='Max advertised window')
    ax1.set_ylabel("Window Size")
    ax1.set_title("TCP Sender Window Size Over Time")
    ax1.legend()

    #2 TCP sequence number received over time in x-axis
    ax2.scatter(seq_received_times, seq_received_nums, s=0.1, color='green')
    ax2.set_ylabel("Sequence Number")
    ax2.set_title("TCP Sequence Numbers Received Over Time")

    #3 TCP sequence number dropped over time in x-axis 
    ax3.scatter(seq_dropped_times, seq_dropped_nums, s=0.5, color='red')
    ax3.set_ylabel("Sequence Number")
    ax3.set_title("TCP Sequence Numbers Dropped Over Time")
    ax3.set_xlabel("Packets Sent")

    plt.tight_layout()
    plt.savefig("tcp_stats.png", dpi=150)
    plt.show()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    print(f"Connecting to IP Address {HOST} on Port {PORT}")
    data = s.recv(1024)
    print(data)

    current_sequence_number = 0
    dropped_sequence_numbers = []

    window_size = 1
    window_threshold = MAX_ADVERTISED_WINDOW
    # initial sliding window size rate
    # becomes False after reaching the max window limit or failing
    # if True, doubles upon success and halves upon failure
    # if False, +1 upon success and halves upon failure
    initial_rate = True

    packets_sent = 0
    packets_since_last_transmission = 0

    # tracking data for output graphs
    time_axis = []
    sender_window_over_time_axis = []
    seq_received_times = []
    seq_received_nums = []
    seq_dropped_times = []
    seq_dropped_nums = []

    # for tracking total packets sent
    num_retransmissions = 0

    # for table at the end of the doc
    retransmission_counts = {}

    while packets_sent < NUM_PACKETS:
        
        # check for packets that got dropped and retransmit every 100 packets
        if packets_since_last_transmission >= 100:
            successfully_resent_indices = []
            # tries to retransmit with a 1% failure rate
            for index, seq_num in enumerate(dropped_sequence_numbers):
                # increment the retransmission count
                num_retransmissions += 1
                retransmission_counts[seq_num] += 1
                if send_packet(s, seq_num):
                    # if retransmission is sucessful, mark to remove from list of
                    # dropped packets
                    successfully_resent_indices.append(index)
                    if packets_sent % 1000 == 0:
                        seq_received_times.append(packets_sent)
                        seq_received_nums.append(seq_num)
                else:
                    # window size halves upon failure
                    window_threshold = max(1, window_size // 2)
                    window_size = window_threshold
                    # intial rate = False after failing
                    initial_rate = False

                    if packets_sent % 1000 == 0:
                        seq_dropped_times.append(packets_sent)
                        seq_dropped_nums.append(seq_num)
            
            # remove successfully re-transmitted packets from the list of dropped packets
            for index in successfully_resent_indices[::-1]:
                dropped_sequence_numbers.pop(index)
            
            packets_since_last_transmission = 0
        
        # send a window's worth of new packets
        for _ in range(window_size):
            # for early termination
            if packets_sent >= NUM_PACKETS:
                break

            # sends packet
            delivery_successful = send_packet(s, current_sequence_number)

            if delivery_successful:
                # if sucessful, update the window size accordingly
                if packets_sent % 1000 == 0:
                    seq_received_times.append(packets_sent)
                    seq_received_nums.append(current_sequence_number)
                if initial_rate:
                    # window size doubles
                    window_size = min(window_size * 2, MAX_ADVERTISED_WINDOW)
                    # intial rate = False after reaching the max window size
                    if window_size >= window_threshold:
                        initial_rate = False
                else:
                    # window size += 1
                    window_size = min(window_size + 1, MAX_ADVERTISED_WINDOW)
            else:
                # if failure
                if current_sequence_number not in dropped_sequence_numbers:
                    dropped_sequence_numbers.append(current_sequence_number)
                # if seq num hasn't been dropped yet, set to 0
                retransmission_counts.setdefault(current_sequence_number, 0)
                # window size halves upon failure
                window_threshold = max(1, window_size // 2)
                window_size = window_threshold
                # intial rate = False after failing
                initial_rate = False
                
                if packets_sent % 1000 == 0:
                    seq_dropped_times.append(packets_sent)
                    seq_dropped_nums.append(current_sequence_number)

            if packets_sent % 1000 == 0:
                time_axis.append(packets_sent)
                sender_window_over_time_axis.append(window_size)

            # handles wraparound sequence number --> resets to 0 after
            # reaching the max sequence number
            current_sequence_number += 1
            if current_sequence_number > MAX_SEQUENCE_NUMBER:
                current_sequence_number = 0
            
            packets_sent += 1
            packets_since_last_transmission += 1
    
    # plotting data stored once every 1000 packets sent
    plot_data(time_axis, sender_window_over_time_axis, seq_received_times, seq_received_nums, seq_dropped_times, seq_dropped_nums)
    
    # retransmission table
    retransmission_tally = {}
    for count in retransmission_counts.values():
        retransmission_tally[count] = retransmission_tally.get(count, 0) + 1

    for n in sorted(retransmission_tally):
        print(f"{n} retransmissions: {retransmission_tally[n]} packets")
    
    print(f"Total packets sent: {packets_sent + num_retransmissions}")
