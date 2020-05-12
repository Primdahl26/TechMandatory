import os
import socket
import threading
from configparser import ConfigParser
import time
import sys

conf = ConfigParser()
conf.read("opt.conf", encoding='utf-8')

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 10000)

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
self_written_message = ''

data = b''
has_been_run = False

# TODO: Make incrementing_number read the message number from the data then + 1


def main():
    incrementing_number = 0
    global has_been_run

    try:
        while True:
            # If a normal message is received
            if get_data()[:3] == b'res' and has_been_run is False:
                if conf.getboolean("settings", "AutomateMessages") is False:
                    incrementing_number += 2
                    print('Enter message: ')
                    write()
                    final_message = 'msg-' + str(incrementing_number) + '=' + get_self_written_message()

                    print('Sending: ' + final_message)
                    sock.sendto(final_message.encode(), server_address)

                    has_been_run = True
                else:
                    incrementing_number += 2
                    ok_message = 'msg-' + str(incrementing_number) + '=Ok, good to know'

                    print('Sending: ' + ok_message)
                    sock.sendto(ok_message.encode(), server_address)

                    has_been_run = True
            # If accept message is received
            if get_data()[:12] == b'com-0 accept' and has_been_run is False:
                acceptMessage = 'com-' + str(incrementing_number) + ' accept'

                print('Sending: ' + acceptMessage)
                sock.sendto(acceptMessage.encode(), server_address)

                first_message = 'msg-' + str(incrementing_number) + '=Hello, i am new user'

                print('Sending: ' + first_message)
                sock.sendto(first_message.encode(), server_address)

                has_been_run = True

    finally:
        print('\nReached finally block\nClosing socket...')
        sock.close()


def read():
    global data, server, has_been_run
    # Send ip address to get accepted
    ipMessage = b'com-0 '+ip_address.encode()
    print('Sending IP...\nSending: {!r}'.format(ip_address))
    sock.sendto('com-0 '.encode() + ip_address.encode(), server_address)
    while True:
        print()
        # Start up the client socket, and wait for a message
        data, server = sock.recvfrom(4096)
        print('Received {} bytes from {}'.format(len(data), server))
        print('Data: ' + str(data))

        has_been_run = False


def write():
    global self_written_message
    self_written_message = input()


def check_heartbeat():
    while True:
        if get_data()[:12] == b'con-res 0xFE':
            close_message = 'con-res 0xFF'

            sock.sendto(close_message.encode(), server_address)
            print('Idle for more than 4 seconds\nClosing down connection with following message: ' + close_message)

            sys.stdout.flush()
            os._exit(0)


def keep_alive():
    heartbeat_message = b'con-h 0x00'
    try:
        if conf.getboolean("settings", "KeepALive"):
            while True:
                time.sleep(3)
                print('Sending heartbeat to server\nSending: ' + str(heartbeat_message)+'\n')
                sock.sendto(heartbeat_message, server_address)

    except Exception as e:
        print('Reading error: '.format(str(e)))


def hack():
    try:
        while conf.getboolean("hack", "HackActive"):
            sock.sendto(b'What you gonna do about this message?', server_address)
            print('\nSending hack message: What you gonna do about this message?\n')
            time.sleep(1)

    except Exception as e:
        print('Reading error: '.format(str(e)))


def get_self_written_message():
    return self_written_message


def get_data():
    return data


if __name__ == '__main__':
    threading.Thread(target=read).start()
    threading.Thread(target=main).start()
    threading.Thread(target=check_heartbeat).start()
    threading.Thread(target=keep_alive).start()
    threading.Thread(target=hack).start()
