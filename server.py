from socket import *
import sys
import json


def main():
    req_code = sys.argv[1]
    
    ### --- CREATE A NEGOTIATION PORT ---
    udp_server_port = 12000

    # keep looping until we find an available port
    while True:
        try:
            udp_server_socket = socket(AF_INET, SOCK_DGRAM)
            udp_server_socket.bind(('', udp_server_port))
            n_port = udp_server_socket.getsockname()[1]
            break
        except error as e:
            udp_server_port += 1

    print(f"SERVER_PORT={n_port}")


    while True:
        message, client_address = udp_server_socket.recvfrom(2048)
        tokens = message.decode().split()

        # need to check using the <req_code> if a client is supposed to be connecting to the server
        if len(tokens) != 3 or tokens[0] != 'UPLOAD' or tokens[1] != req_code:
            udp_server_socket.sendto('0'.encode(), client_address) # responds with a 0 if failed
            continue

        # else create a tcp socket
        else:
            tcp_server_port = 12001

            # keep looping until a free port is found
            while True:
                try:
                    tcp_server_socket = socket(AF_INET, SOCK_STREAM)
                    tcp_server_socket.bind(('', tcp_server_port))
                    tcp_server_socket.listen(1)
                    r_port = tcp_server_socket.getsockname()[1]
                    break
                except error as e:
                    tcp_server_port += 1

            r_port_bytes = str(r_port).encode()
            udp_server_socket.sendto(r_port_bytes, client_address)

            # transaction to send packet count back to client with helper function, tcp_transaction
            proto = tokens[2]
            tcp_transaction(tcp_server_socket, proto)

def tcp_transaction(tcp_server_socket, proto):
    tcp_socket_connection, tcp_addr_connection = tcp_server_socket.accept()

    data = ""
    while True:

        # receive trace data in 2048 byte-chunks
        trace_chunk = tcp_socket_connection.recv(2048).decode()
        
        # check if chunk ends in EOT, and break from loop if so
        if trace_chunk.endswith('\x04'):

            # remove EOT character from trace data
            data += trace_chunk[:-1]
            break

        data += trace_chunk
    
    # convert trace data string into JSON
    trace_json = json.loads(data)

    tcp_packet_count = get_tcp_packets(trace_json)
    udp_packet_count = get_udp_packets(trace_json)
        
    # send (tcp, udp) as a string, separated by a whitespace
    packet_count = str(tcp_packet_count) + " " + str(udp_packet_count)
    tcp_socket_connection.sendto(packet_count.encode(), tcp_addr_connection) 
    tcp_socket_connection.close()

def get_tcp_packets(data):
    tcp_packet_count = 0

    for packet in data:
        layers = packet.get("_source", {}).get("layers", {})
        if "tcp" in layers:
            tcp_packet_count += 1

    return tcp_packet_count

def get_udp_packets(data):
    udp_packet_count = 0

    for packet in data:
        layers = packet.get("_source", {}).get("layers", {})
        if "udp" in layers:
            udp_packet_count += 1

    return udp_packet_count

if __name__ == "__main__":
    main()