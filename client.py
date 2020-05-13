import os
from threading import *
import socket
import threading
from configparser import ConfigParser
import time
import sys
import re

# For making printing with threads
# not screw up the text layout
screen_lock = Semaphore(value=1)

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 10000)

# To read from the opt.conf file
conf = ConfigParser()
conf.read("opt.conf", encoding='utf-8')

# Bind the socket to the port
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

# The message that the user writes
self_written_message = ''

# Data
data = b''

# A flag see if a piece of code has been executed
# This is present since the program is threaded, and the main method
# needs to only execute the if statement once - and then again when the read
# message gets new data - then the value is set to False again
has_been_run = False


# TODO: Make incrementing_number read the message number from the data then + 1


# While loop that reads messages
def read():
    global data, server, has_been_run
    # Send ip address to get accepted
    ip_message = b'com-0 ' + ip_address.encode()
    sock.sendto('com-0 '.encode() + ip_address.encode(), server_address)

    screen_lock.acquire()
    print('\n<<Trying to access server>>\n\nSending IP...\nSending: {!r}'.format(ip_message))
    screen_lock.release()

    while True:
        # Start up the client socket, and wait for a message
        data, server = sock.recvfrom(4096)

        screen_lock.acquire()
        print('\nReceived {} bytes from {}'.format(len(data), server))
        print('Data: ' + str(data))
        screen_lock.release()

        # Setting has_been_run to false, since a new message was just received
        has_been_run = False

        # For performance
        time.sleep(0.1)


# Method that handles the messages that read() has read
def main():
    # A number that we add up to see the message number
    global has_been_run

    try:
        while True:
            # If a normal message is received
            if get_data()[:3] == b'res' and has_been_run is False:

                try:
                    # Set the server message number to the first int
                    server_message_number = int(re.search(r"\d+", get_data().decode()).group())

                    # Set the client message number the the servers + 1
                    client_message_number = server_message_number + 1

                    screen_lock.acquire()
                    print('Server message number: ' + str(server_message_number))
                    screen_lock.release()

                except IndexError as e:
                    print('IndexError:" ' + str(e))
                    break

                # If the opt.conf file AutomateMessages is false, then the user
                # needs to write the message
                if conf.getboolean("settings", "AutomateMessages") is False:

                    screen_lock.acquire()
                    print('Enter message: ')
                    screen_lock.release()

                    write()

                    final_message = 'msg-' + str(client_message_number) + '=' + get_self_written_message()

                    # Send message back
                    sock.sendto(final_message.encode(), server_address)

                    screen_lock.acquire()
                    print('Sending: ' + final_message)
                    screen_lock.release()

                    # The code has been executed, so we make has been run true,
                    # so that we dont execute the same code multiple times
                    has_been_run = True

                # Else the client will write a ok_message itself
                else:
                    ok_message = 'msg-' + str(client_message_number) + '=Ok, good to know'

                    # Send message back
                    sock.sendto(ok_message.encode(), server_address)

                    screen_lock.acquire()
                    print('Sending: ' + ok_message)
                    screen_lock.release()

                    # The code has been executed, so we make has been run true,
                    # so that we dont execute the same code multiple times
                    has_been_run = True

            # If accept message is received
            if get_data()[:12] == b'com-0 accept' and has_been_run is False:
                acceptMessage = 'com-0 accept'

                # Send message back
                sock.sendto(acceptMessage.encode(), server_address)

                screen_lock.acquire()
                print('Sending: ' + acceptMessage)
                screen_lock.release()

                # First message is always msg-0
                first_message = 'msg-0=Hello, i am new user'

                # Send message back
                sock.sendto(first_message.encode(), server_address)

                screen_lock.acquire()
                print('Sending: ' + first_message)
                screen_lock.release()

                # The code has been executed, so we make has been run true,
                # so that we dont execute the same code multiple times
                has_been_run = True

    # If the loop is broken, close the socket
    finally:
        screen_lock.acquire()
        print('Reached finally block-\nClosing socket...')
        screen_lock.release()

        sock.close()


# Method so the user can write input
def write():
    global self_written_message
    self_written_message = input()

    # If QUIT is typed it sends to server that it has quit, and quits
    if self_written_message == 'QUIT':
        sock.sendto(b'con-res 0xFF', server_address)

        screen_lock.acquire()
        print('You chose to quit\nSending: con-res 0xFF')
        screen_lock.release()

        sys.stdout.flush()
        os._exit(0)


# Method that checks if the message is con-res 0xFE
# If this is the case, then shut down the client
def check_heartbeat():
    while True:
        if get_data()[:12] == b'con-res 0xFE':
            close_message = 'con-res 0xFF'

            # Send to server that the client has received the order to close down
            # Answer is: con-res 0xFF
            sock.sendto(close_message.encode(), server_address)

            screen_lock.acquire()
            print('Idle for more than 4 seconds\nClosing down connection with following message: ' + close_message)
            screen_lock.release()

            sys.stdout.flush()
            os._exit(0)

        if get_data()[:12] == b'con-res 0xFU':
            close_message = 'con-res 0xFF'

            # Send to server that the client has received the order to close down
            # Answer is: con-res 0xFF
            sock.sendto(close_message.encode(), server_address)

            screen_lock.acquire()
            print('Asked by server to disconnect\nClosing down connection with following message: ' + close_message)
            screen_lock.release()

            sys.stdout.flush()
            os._exit(0)


# A thread keeps running this, so that the server does not
# kick the client due to inactivity
def keep_alive():
    heartbeat_message = b'con-h 0x00'
    try:
        # If the KeepALive setting in opt.conf is True
        if conf.getboolean("settings", "KeepALive"):
            while True:
                # Wait the seconds and repeat sending the message
                # so that the server does not kick us out
                time.sleep(3)
                # print('Sending heartbeat to server\nSending: ' + str(heartbeat_message)+'\n')
                sock.sendto(heartbeat_message, server_address)

    except Exception as e:
        screen_lock.acquire()
        print('Reading error: '.format(str(e)))
        screen_lock.release()


# Method that sends a message to the Server that is meant to disrupt it
def hack():
    time.sleep(5)
    try:
        # While the HackActive setting in opt.conf is True
        while conf.getboolean("hack", "HackActive"):
            sock.sendto(b'What you gonna do about this message?', server_address)

            screen_lock.acquire()
            print('Sending hack message: What you gonna do about this message?')
            screen_lock.release()

            time.sleep(0.1)

    except Exception as e:
        print('Reading error: '.format(str(e)))


def get_self_written_message():
    return self_written_message


def get_data():
    return data


# Startup the threads
if __name__ == '__main__':
    threading.Thread(target=read).start()
    threading.Thread(target=main).start()
    threading.Thread(target=check_heartbeat).start()
    threading.Thread(target=keep_alive).start()
    threading.Thread(target=hack).start()
