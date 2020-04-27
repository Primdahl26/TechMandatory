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
ipAddress = socket.gethostbyname(hostname)
selfWrittenMessage = ''

data = b''
hasBeenRun = False


def main():
    incrementingNumber = 0
    global hasBeenRun

    try:
        while True:
            # If a normal message is received
            if get_data()[:3] == b'res' and hasBeenRun is False:
                incrementingNumber += 2
                okMessage = 'msg-' + str(incrementingNumber) + '=Ok, good to know'
                print('Enter message: ')

                write()

                finalMessage = 'msg-' + str(incrementingNumber) + '=' + get_self_written_message()

                print('Sending: ' + finalMessage)
                sock.sendto(finalMessage.encode(), server_address)

                hasBeenRun = True

            # If accept message is received
            if get_data()[:12] == b'com-0 accept' and hasBeenRun is False:
                acceptMessage = 'com-' + str(incrementingNumber) + ' accept'

                print('Sending: ' + acceptMessage)
                sock.sendto(acceptMessage.encode(), server_address)

                firstMessage = 'msg-' + str(incrementingNumber) + '=Hello, i am new user'

                print('Sending: ' + firstMessage)
                sock.sendto(firstMessage.encode(), server_address)

                hasBeenRun = True

    finally:
        print('\nReached finally block\nClosing socket...')
        sock.close()


def read():
    global data, server, hasBeenRun
    # Send ip address to get accepted
    print('Sending IP...\nSending: {!r}'.format(ipAddress))
    sock.sendto('com-0 '.encode() + ipAddress.encode(), server_address)
    while True:
        print()
        # Start up the client socket, and wait for a message
        data, server = sock.recvfrom(4096)
        print('Received {} bytes from {}'.format(len(data), server))
        print('Data: ' + str(data))

        hasBeenRun = False


def write():
    global selfWrittenMessage
    selfWrittenMessage = input()


def check_heartbeat():
    while True:
        if get_data()[:12] == b'con-res 0xFE':
            closeMessage = 'con-res 0xFF'

            sock.sendto(closeMessage.encode(), server_address)
            print('Idle for more than 4 seconds\nClosing down connection with following message: ' + closeMessage)

            sys.stdout.flush()
            os._exit(0)


def keep_alive():
    heartbeatMessage = b'con-h 0x00'
    try:
        if conf.getboolean("settings", "KeepALive"):
            while True:
                time.sleep(3)
                print('Sending heartbeat to server\nSending: ' + str(heartbeatMessage)+'\n')
                sock.sendto(heartbeatMessage, server_address)

    finally:
        print('Something went wrong')


def get_self_written_message():
    return selfWrittenMessage


def get_data():
    return data


if __name__ == '__main__':
    threading.Thread(target=read).start()
    threading.Thread(target=main).start()
    threading.Thread(target=check_heartbeat).start()
    threading.Thread(target=keep_alive).start()
