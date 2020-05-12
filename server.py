import socket
from threading import Timer
import threading
import time
from configparser import ConfigParser
from datetime import datetime

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
# Startup the Servers socket
server_address = ('localhost', 10000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

conf = ConfigParser()
conf.read("opt.conf", encoding='utf-8')

data = b'ignoreThisLongStringNamePlease:)'
client_data_ip = 123
has_been_run = False
too_many_packets = False
packets = []

# TODO: Make incrementing_number read the message number from the data then + 1


def log(conn, str):
    # "a" for append
    log = open("ServerLog.log", "a")
    log.write(f"[{conn}] {datetime.now()} {str}\n")
    log.close()


def read():
    global data, has_been_run, address, packets

    empty_packets_timer.start()
    print('\nServer startup complete\n')
    while True:
        print()
        # Wait for message from the Client
        data, address = sock.recvfrom(4096)
        has_been_run = False
        packets.append(data.decode())

        print('Packets received last second: '+str(len(packets))+'\n')

        time_thread.stop()

        # Print the message from the client
        print('Received {} bytes from {}'.format(len(data), address))
        print('Data: ' + str(data))

        if conf.getboolean('log', 'LogActive') is True:
            log(address, 'Incomming: '+str(data))


def main():
    # A number that we add up to see the message number
    incrementing_number = 1
    global has_been_run, too_many_packets

    while True:
        if get_too_many_packets() is True:
            print('\nToo many packets received last second\n'
                  'Ignoring incoming messages for 1 second')
            time.sleep(1)

        # If the IP is received
        if get_data()[:7] == b'com-0 1' and get_has_been_run() is False:
            incrementing_number = 1
            accept_message = 'com-0 accept ' + socket.gethostbyname(socket.gethostname())

            sock.sendto(accept_message.encode(), address)
            print('Sending: ' + str(accept_message))

            if conf.getboolean('log', 'LogActive') is True:
                log(address, 'Outgoing: ' + str(accept_message))

            global client_data_ip
            client_data_ip = data.split()[-1]

            has_been_run = True
            time_thread.start()

        # If an accept message is received
        if get_data()[:12] == b'com-0 accept' and get_has_been_run() is False:
            print('\nThe current active user is: ' + str(client_data_ip))

            has_been_run = True
            time_thread.start()

        # If a message is received
        if get_data()[:3] == b'msg' and get_has_been_run() is False:
            automated_message = 'res-' + str(incrementing_number) + '=I am server'
            incrementing_number += 2

            print('Sending: ' + automated_message)
            sock.sendto(automated_message.encode(), address)

            if conf.getboolean('log', 'LogActive') is True:
                log(address, 'Outgoing: ' + str(automated_message))

            has_been_run = True
            time_thread.start()

        if get_data()[:12] == b'con-res 0xFF' and get_has_been_run() is False:
            print('Client disconnected successfully')

            has_been_run = True

        if get_data() == b'ignoreThisLongStringNamePlease:)':
            time_thread.stop()

            has_been_run = True

        if get_data() == b'con-h 0x00' and get_has_been_run() is False:
            time_thread.stop()

            print('Client still alive\n')

            has_been_run = True


def kill_client():
    timeout_message = 'con-res 0xFE'
    print(str(client_data_ip) + ' Has been idle for more than 4 seconds\n'
                              'Timing out connection and sending: ' + timeout_message + '\n')

    sock.sendto(timeout_message.encode(), address)

    if conf.getboolean('log', 'LogActive') is True:
        log(address, 'Outgoing: '+str(timeout_message))

    time_thread.stop()


def empty_packets():
    packets.clear()


def get_packets():
    return len(packets)


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


if __name__ == '__main__':
    time_thread = RepeatedTimer(4, kill_client)
    empty_packets_timer = RepeatedTimer(1, empty_packets)
    t1 = threading.Thread(target=read).start()
    t2 = threading.Thread(target=main).start()
