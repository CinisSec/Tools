#!/opt/local/bin/python2.7

import sys
import socket
import getopt
import threading
import subprocess


# global variables
listen              = False
command             = False
upload              = False
execute             = ""
target              = ""
upload_destination  = ""
port                = 0

def usage():
    print "Netbat Net Tool"
    print
    print "Usage: netbat.py -t target_host -p port"
    print "-l --listen              - listen on [host]:[port] for"
    print "-e --execute=file        - execute file upon receiving a connection"
    print "-c --command             - initialize a command shell"
    print "-u --upload=destination  - upon receiving connection upload a file \
                                      and write to [destination]"
    print
    print
    print "Examples: "
    print "netbat.py -t 192.168.0.1 -p 5555 -l -c"
    print "netbat.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe"
    print "netbat.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\""
    print "echo 'ABCDEFGHI' | ./netbat.py -t 192.168.11.12 -p 135"
    sys.exit(0)

def main():
    global listen
    global port
    global command
    global execute
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    # read CLI options
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hle:t:p:cu",["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"
    
    # listen or just send data from stdin?
    if not listen and len(target) and port > 0:

        # read in buffer from CLI
        # this will block, so send CTRL-D if not sending input
        # to CLI
        buffer = sys.stdin.read()

        # send data off
        client_sender(buffer)

    # listen and potentially upload, execute commands, drop shell back
    # depending on the CLI options
    if listen:
        server_loop()

def client_sender(buffer):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connect to target
        client.connect((target, port))

        if len(buffer):
            
            client.send(buffer)

        while True:

            #wait for data response
            recv_len = 1
            response = ""

            while recv_len:

                data        = client.recv(4096)
                recv_len    = len(data)
                response   += data

                if recv_len < 4096:
                    break

            print response

            # wait for more input
            buffer  = raw_input("")
            buffer += "\n"

            # send buffer
            client.send(buffer)
    except:

        print "[*] Exception! Exiting."

        # close connection
        client.close()

def server_loop():
    global target
    global port

    # if no target is definded, we listen on all interfaces
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # spin off a thread to handle new client
        client_thread = threading.Thread(target=client_handler,args=(client_socket,))
        client_thread.start()


def run_command(command):
    # trim new line
    command = command.rstrip()

    # run cmd and get output
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"

    # send output to client
    return output


def client_handler(client_socket):
    global upload
    global execute
    global command

    # check for upload
    if len(upload_destination):
        
        # read in all of the bytes and write to our destination
        file_buffer = ""

        # keep reading data until none is available
        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        # now we take bytes and try to write them out
        try:
            file_descriptor = open(upload_destination,"wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            # ack if we wrote file
            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)
    # check for cmd exec
    if len(execute):

        # run cmd
        output = run_command(execute)

        client_socket.send(output)

    # go into other loop if cmd shell was requested
    if command:

        while True:
            # show a simple prompt
            client_socket.send("<Netbat:#> ")

            # now we receive until linefeed (enter key)
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                md_buffer += client_socket.recv(1024)

            # send back to cmd output
            response = run_command(cmd_buffer)

            # send back the response
            client_socket.send(response)



main()