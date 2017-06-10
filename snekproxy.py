#!/bin/python2.7

import sys
import socket
import threading

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):

    try:
        server.bind(socket.AF_INET, socket.SOCK_STREAM)
    except:
        print "[!!] Failed to listen on %s:%d" % (local_host, local_port)
        print "[!!] Check for other listening sockets or correct permissions."
        sys.exit(0)

    print "[*] Listening on %s:%d" % (local_host,local_port)

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # print out local connection information
        print "[==>] Received incoming connection from %s:%d" % (addr[0],addr[1])

        # start thread to talk to remote host
        proxy_thread : threading.Thread(target=proxy_handler, args=(client_socket,
            remote_host, remote_port, receive_first))

        proxy_thread.start()


def proxy_hander(client_socket, remote_host, remote_port, receive_first):

    # connect to remote host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    # receive data from the remote end if necessary
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        # send it to our response handler
        remote_buffer = response_handler(remote_buffer)

        # if we have data to send to local client, send it
        if len(remote_buffer):
            print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
            client_socket.send(remote_buffer)
# TODO 


def main():
    if len(sys.argv[1:]) != 5:
        print "Usage: python2.7 snekproxy.py [localhost] [localport] \
                [remotehost] [remoteport] [receive_first]"
        print "Example: python2.7 snekproxy.py 127.0.0.1 9000 10.12.132.1 9000 True"
        sys.exit(0)

    # setup local listening params
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    # setup remote target params
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    # this tells the proxy to connect and receive data 
    # before sending to remote host 
    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    # spin up our listening socket
    server_loop(local_host, local_port, remote_host, receive_first)


main()
