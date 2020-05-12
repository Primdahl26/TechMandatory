import socket
import threading
from threading import *
import time
from configparser import ConfigParser
from datetime import datetime

# For making printing with threads
# not screw up the text layout
screen_lock = Semaphore(value=1)

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
# Startup the Servers socket
server_address = ('localhost', 10000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# To read from the opt.conf file
conf = ConfigParser()
conf.read("opt.conf", encoding='utf-8')

# Data
data = b'default_message'

# A value to see if a piece of code has been executed
# This is present since the program is threaded, and the main method
# needs to only execute the if statement once - and then again when the read
# message gets new data - then the value is set to False again
has_been_run = False

# A boolean value to see if too many packets were received
too_many_packets = False

# A list to hold the packets received the last second
packets = []

# IP-Address
ip = 'default_ip'

# Variable too see if it is the first time the client runs on the server
first_run = True


# Method to log messages to the ServerLog.log file
def log_server(conn, message):
    # "a" for append
    log = open("ServerLog.log", "a")
    log.write(f"[{conn}] {datetime.now()} {message}\n")
    log.close()


# While loop that reads messages
def read():
    global data, has_been_run, address, packets, ip, first_run

    # Startup the thread that empties the packet every 1 second
    empty_packets_timer.start()

    screen_lock.acquire()
    print('\nServer startup complete')
    screen_lock.release()

    while True:
        # Wait for message from the Client
        data, address = sock.recvfrom(4096)

        # Setting has_been_run to false, since a new message was just received
        has_been_run = False

        # Put the data into the packet
        packets.append(data.decode())

        screen_lock.acquire()
        print('\nPackets received last second: ' + str(len(packets)))
        screen_lock.release()

        # Since a message was received, we stop the timer
        # that would kill the client, if more than 4 seconds passed
        time_thread.stop()

        # If this is the first run on the server
        # then we take the IP, and change it so its not the first run anymore
        if first_run is True:
            ip = get_data().decode().split(' ')[1]
            first_run = False

        # Print the message from the client
        screen_lock.acquire()
        print('Received {} bytes from {}'.format(len(data), address))
        print('Data: ' + str(data))
        screen_lock.release()

        # TODO: Make incrementing_number read the message number from the data then + 1

        try:
            current_incremented_number = get_data().decode()[get_data().decode().index('-'):]
            print(current_incremented_number)
        except IndexError:
            pass

        # If LogActive is true, then log the message
        if conf.getboolean('log', 'LogActive') is True:
            log_server(address, 'Incomming: ' + str(data))

        # To make the threads not screw up
        time.sleep(0.1)


# Method that handles the messages that read() has read
def main():
    # A number that we add up to see the message number
    incrementing_number = 1

    global has_been_run, too_many_packets, ip, connected_ip

    while True:
        # If too many packets have been received the last 1 second
        # then we pause handling the messages for a second
        if get_too_many_packets() is True:

            screen_lock.acquire()
            print('Too many packets received last second-\n'
                  'Ignoring incoming messages for 1 second')
            screen_lock.release()

            time.sleep(1)

        # If the IP is received, and the IP is valid
        if is_good_ipv4(get_ip()) and get_has_been_run() is False:
            incrementing_number = 1
            accept_message = 'com-0 accept ' + socket.gethostbyname(socket.gethostname())

            # Send message back
            sock.sendto(accept_message.encode(), address)

            screen_lock.acquire()
            print('Sending: ' + str(accept_message))
            screen_lock.release()

            # If LogActive is true, then log the message
            if conf.getboolean('log', 'LogActive') is True:
                log_server(address, 'Outgoing: ' + str(accept_message))

            # The code has been executed, so we make has been run true,
            # so that we dont execute the same code multiple times
            has_been_run = True

            # We make a variable to hold the ip address
            connected_ip = ip

            # Change the ip to a not valid ip
            ip = 'default_ip'

            # Start the time_thread again, so kill_client will be called
            # if more than 4 seconds pass without any message
            time_thread.start()

        # If an accept message is received
        if get_data()[:12] == b'com-0 accept' and get_has_been_run() is False:

            screen_lock.acquire()
            print('\nHandshake completed')
            screen_lock.release()

            # If LogActive is true, then log the message
            if conf.getboolean('log', 'LogActive') is True:
                log_server(address, 'Handshake completed')

            # The code has been executed, so we make has been run true,
            # so that we dont execute the same code multiple times
            has_been_run = True

            # Start the time_thread again, so kill_client will be called
            # if more than 4 seconds pass without any message
            time_thread.start()

        # If a message is received
        if get_data()[:3] == b'msg' and get_has_been_run() is False:
            automated_message = 'res-' + str(incrementing_number) + '=I am server'
            incrementing_number += 2

            sock.sendto(automated_message.encode(), address)

            screen_lock.acquire()
            print('Sending: ' + automated_message)
            screen_lock.release()

            # If LogActive is true, then log the message
            if conf.getboolean('log', 'LogActive') is True:
                log_server(address, 'Outgoing: ' + str(automated_message))

            # The code has been executed, so we make has been run true,
            # so that we dont execute the same code multiple times
            has_been_run = True

            # Start the time_thread again, so kill_client will be called
            # if more than 4 seconds pass without any message
            time_thread.start()

            # If the message is QUIT then kill the client
            if get_data().decode().split('=')[1] == 'QUIT':
                kill_client()

        # Message that the client successfully disconnected
        if get_data()[:12] == b'con-res 0xFF' and get_has_been_run() is False:
            screen_lock.acquire()
            print('Client disconnected successfully')
            screen_lock.release()

            # The code has been executed, so we make has been run true,
            # so that we dont execute the same code multiple times
            has_been_run = True

        # If the data is the first default message
        if get_data() == b'default_message':
            # The code has been executed, so we make has been run true,
            # so that we dont execute the same code multiple times
            has_been_run = True

            # Start the time_thread again, so kill_client will be called
            # if more than 4 seconds pass without any message
            time_thread.stop()

        # If the message is a heartbeat message
        if get_data() == b'con-h 0x00' and get_has_been_run() is False:
            screen_lock.acquire()
            print('Client still alive')
            screen_lock.release()

            # The code has been executed, so we make has been run true,
            # so that we dont execute the same code multiple times
            has_been_run = True

            # Start the time_thread again, so kill_client will be called
            # if more than 4 seconds pass without any message
            time_thread.stop()


# Method to kill the client
def kill_client():
    global first_run

    timeout_message = 'con-res 0xFE'

    sock.sendto(timeout_message.encode(), address)

    screen_lock.acquire()
    print('\n' + connected_ip + ' Has been idle for more than 4 seconds-\n'
                                'Timing out connection and sending: ' + timeout_message)
    screen_lock.release()

    # If LogActive is true, then log the message
    if conf.getboolean('log', 'LogActive') is True:
        log_server(address, 'Outgoing: ' + str(timeout_message))

    # Stop the TimeThread, and make it first_run true,
    # since a clients run would be the first again
    time_thread.stop()

    # since client disconnected,
    # it will be first
    first_run = True


# Clears the packets
def empty_packets():
    packets.clear()


# Returns the number of items in packets
def get_packets():
    return len(packets)


def get_ip():
    return ip


# Looks at the IP-address and determines if it is a valid IPv-4 format
def is_good_ipv4(s):
    pieces = s.split('.')
    if len(pieces) != 4:
        return False
    try:
        return all(0 <= int(p) < 256 for p in pieces)
    except ValueError:
        return False


# Loops up in the opt.conf file, too see if too many packages was received
def get_too_many_packets():
    if get_packets() >= conf.getint("settings", "MaxPackages"):
        return True
    else:
        return False


def get_data():
    return data


def get_address():
    return address


def get_has_been_run():
    return has_been_run


# Class to be able to make a RepeatedTimer Thread
# Takes a second as argument, and a method
# Will execute the method after the given time
class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


# Startup the threads
if __name__ == '__main__':
    time_thread = RepeatedTimer(4, kill_client)
    empty_packets_timer = RepeatedTimer(1, empty_packets)
    threading.Thread(target=read).start()
    threading.Thread(target=main).start()
