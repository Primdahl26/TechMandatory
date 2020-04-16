import socket
import time

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
# Startup the Servers socket
server_address = ('localhost', 10000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)


def main():
    # A number that we add up to see the message number
    incrementingNumber = 1

    # Make sure that the time if statement runs only once
    hasBeenRun = False

    # A number that keeps track of how many packages was received
    packageCounter = 0

    # Time to handle the tolerance
    currentTime = time.time()
    timeoutTime = currentTime + 4
    total_seconds = round(currentTime - timeoutTime).__str__()

    while True:
        # Wait for message from the Client
        print('\nWaiting to receive...')

        data, address = sock.recvfrom(4096)

        if hasBeenRun is False:
            print('Time until timeout: ' + str(total_seconds[1:])+' seconds')

        print('Received {} bytes from {}'.format(len(data), address))
        print('Data: ' + str(data))

        # If the IP is received
        if data[:7] == b'com-0 1':
            acceptMessage = 'com-0 accept ' + socket.gethostbyname(socket.gethostname())

            sent = sock.sendto(acceptMessage.encode(), address)
            print('Sending: ' + str(acceptMessage))

            clientDataIP = data.split()[-1]

        # If a message is received
        if data[:3] == b'msg':
            timeoutTime = currentTime + 4

            automatedMessage = 'res-' + str(incrementingNumber) + '=I am server'
            incrementingNumber += 2

            print('Sending: ' + automatedMessage)
            sent = sock.sendto(automatedMessage.encode(), address)

        # If an accept message is received=
        if data[:12] == b'com-0 accept':
            print('\nThe current active user is: ' + str(clientDataIP))

        # If time is greater than 4 seconds
        if time.time() > timeoutTime and hasBeenRun is False:
            timeoutMessage = 'con-res 0xFE'
            print('\n' + clientDataIP.decode() + ' Has been idle for more than 4 seconds\n'
                                                 'Timing out connection and sending: ' + timeoutMessage)

            sent = sock.sendto(timeoutMessage.encode(), address)

            hasBeenRun = True

        if data[:12] == b'con-res 0xFF':

            print('\nRestarting server...')
            main()


main()
