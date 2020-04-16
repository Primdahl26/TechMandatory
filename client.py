import socket
import  time

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 10000)
message = 'Message from client'

hostname = socket.gethostname()
ipAddress = socket.gethostbyname(hostname)


def main():
    incrementingNumber = 0

    try:
        # Send ip address to get accepted
        print('Sending IP...\nSending: {!r}'.format(ipAddress))
        sent = sock.sendto('com-0 '.encode() + ipAddress.encode(), server_address)

        while True:
            # Start up the client socket, and wait for a message
            print('\nWaiting to receive...')
            data, server = sock.recvfrom(4096)
            print('Received {} bytes from {}'.format(len(data), server))
            print('Data: ' + str(data))

            # If a normal message is received
            if data[:3] == b'res':
                incrementingNumber += 2
                okMessage = 'msg-' + str(incrementingNumber) + '=Ok, good to know'

                print('Sending: ' + okMessage)
                sock.sendto(okMessage.encode(), server_address)

                time.sleep(8)

            # If accept message is received
            if data[:12] == b'com-0 accept':
                acceptMessage = 'com-' + str(incrementingNumber) + ' accept'

                print('Sending: ' + acceptMessage)
                sent = sock.sendto(acceptMessage.encode(), server_address)

                firstMessage = 'msg-' + str(incrementingNumber) + '=Hello, i am new user'

                print('Sending: ' + firstMessage)
                sent = sock.sendto(firstMessage.encode(), server_address)

            # If it is asked to shut down
            if data[:12] == b'con-res 0xFE':
                closeMessage = 'con-res 0xFF'
                print('\nIdle for more than 4 seconds\nClosing down connection with following message: ' + closeMessage)

                sent = sock.sendto(closeMessage.encode(), server_address)
                break

    finally:
        print('\nReached finally block\nClosing socket...')
        sock.close()


main()
