import socket
from threading import Timer
import threading

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
# Startup the Servers socket
server_address = ('localhost', 10000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

data = b'ignoreThisLongStringNamePlease:)'
clientDataIP = 123
hasBeenRun = False


def read():
    global data, hasBeenRun, address

    print('\nServer startup complete\n')
    while True:
        print()
        # Wait for message from the Client
        data, address = sock.recvfrom(4096)

        timeThread.stop()

        # Print the message from the client
        print('Received {} bytes from {}'.format(len(data), address))
        print('Data: ' + str(data))

        hasBeenRun = False


def main():
    # A number that we add up to see the message number
    incrementingNumber = 1
    global hasBeenRun

    while True:
        # If the IP is received
        if get_data()[:7] == b'com-0 1' and get_has_been_run() is False:
            incrementingNumber = 1
            acceptMessage = 'com-0 accept ' + socket.gethostbyname(socket.gethostname())

            sock.sendto(acceptMessage.encode(), address)
            print('Sending: ' + str(acceptMessage))

            global clientDataIP
            clientDataIP = data.split()[-1]

            hasBeenRun = True
            timeThread.start()

        # If an accept message is received
        if get_data()[:12] == b'com-0 accept' and get_has_been_run() is False:
            print('\nThe current active user is: ' + str(clientDataIP))

            hasBeenRun = True
            timeThread.start()

        # If a message is received
        if get_data()[:3] == b'msg' and get_has_been_run() is False:
            automatedMessage = 'res-' + str(incrementingNumber) + '=I am server'
            incrementingNumber += 2

            print('Sending: ' + automatedMessage)
            sock.sendto(automatedMessage.encode(), address)

            hasBeenRun = True
            timeThread.start()

        if get_data()[:12] == b'con-res 0xFF' and get_has_been_run() is False:
            print('Client disconnected successfully')

            hasBeenRun = True

        if get_data() == b'ignoreThisLongStringNamePlease:)':
            timeThread.stop()

            hasBeenRun = True

        if get_data() == b'con-h 0x00' and get_has_been_run() is False:
            timeThread.stop()

            print('Client still alive')

            hasBeenRun = True


def kill_client():
    timeoutMessage = 'con-res 0xFE'
    print(str(clientDataIP) + ' Has been idle for more than 4 seconds\n'
                              'Timing out connection and sending: ' + timeoutMessage + '\n')

    sock.sendto(timeoutMessage.encode(), address)

    timeThread.stop()


def get_data():
    return data


def get_address():
    return address


def get_has_been_run():
    return hasBeenRun


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
    timeThread = RepeatedTimer(4, kill_client)
    threading.Thread(target=read).start()
    threading.Thread(target=main).start()
