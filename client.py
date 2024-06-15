from socket import *
import sys
import json

def main():
    if (len(sys.argv) != 6):
        print("Usage: client.py <server_address> <n_port> <req_code> <proto> <trace_to_send>")
        sys.exit(1)
    
    # take arguments
    server_address = sys.argv[1]
    n_port = int(sys.argv[2])
    req_code = int(sys.argv[3])
    proto = sys.argv[4]
    trace_to_send = sys.argv[5]

    # create socket and send message "UPLOAD <req_code> <proto>"
    udp_client_sock = socket(AF_INET, SOCK_DGRAM)
    message = f"UPLOAD {req_code} {proto}"
    udp_client_sock.sendto(message.encode(), (server_address, n_port))
    modified_message, _ = udp_client_sock.recvfrom(2048)
    r_port = int(modified_message.decode())

    udp_client_sock.close()

    # connect to the r_port provided by the server
    tcp_client_socket = socket(AF_INET, SOCK_STREAM)
    tcp_client_socket.connect((server_address, r_port))

    # --- SEND OVER JSON DATA TO SERVER ---
    # read the json trace file
    with open(trace_to_send, 'r') as file:
        trace_data = json.load(file)

    # send string of the trace file to the server
    tcp_client_socket.send(json.dumps(trace_data).encode())

    # send an eot code to the end of the string
    eot = '\x04'
    tcp_client_socket.send(eot.encode())

    if (proto != "TCP" and proto != "UDP" and proto != "TCPUDP"):
        print(f"Usage: invalid <proto>={proto}")
        sys.exit(1)

    # receive message from server
    tcp_message, _ = tcp_client_socket.recvfrom(2048) # count of packets
    packet_count = tcp_message.decode().split()
    tcp_packet_count = packet_count[0]
    udp_packet_count = packet_count[1]

    # print message on client side
    if (proto == "TCP"):
        print(f"{proto}={tcp_packet_count}")
    elif (proto == "UDP"):
        print(f"{proto}={udp_packet_count}")
    elif (proto == "TCPUDP"):
        print(f"TCP={tcp_packet_count}")
        print(f"UDP={udp_packet_count}")

    tcp_client_socket.close()

    return 0

if __name__ == "__main__":
    main()