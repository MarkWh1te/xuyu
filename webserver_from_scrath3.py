# coding:utf-8


import socket
import time

# server address contains host and port
SERVER_ADDRESS = (HOST, PORT) = '',8888
REQUEST_QUEUE_SIZE = 6

socket_family = socket.AF_INET
socket_type = socket.SOCK_STREAM


def handle_request(client_connection):
    request = client_connection.recv(1024)
    print(request)
    print(request.decode())
    http_response = b"""\
HTTP/1.1 200 OK

Hello, World!
"""
    client_connection.sendall(http_response)
    time.sleep(50)


def serve_forever():
    listen_socket = socket.socket(socket_family,socket_type)
    listen_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
    listen_socket.bind(SERVER_ADDRESS)
    listen_socket.listen(REQUEST_QUEUE_SIZE)
    print("serving HTTP service on {port} ".format(port=PORT))
    while 1:
        client_connection, client_address = listen_socket.accept()
        handle_request(client_connection)
        client_connection.close()

if __name__ == '__main__':
    serve_forever()
