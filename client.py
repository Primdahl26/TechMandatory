import socket

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 10000)
message = 'Message from client'

hostname = socket.gethostname()
ipAddress = socket.gethostbyname(hostname).encode()

incrementingNumber = 0

try:
    # Send ip address to get accepted
    print('Sending IP...\nSending: {!r}'.format(ipAddress))
    sent = sock.sendto(ipAddress, server_address)

    while True:
        print('\nWaiting to receive...')
        data, server = sock.recvfrom(4096)
        print('Received {} bytes from {}'.format(len(data), server))
        print('Data: ' + str(data))

        if data[:3] == b'com':
            acceptMessage = 'com-' + str(incrementingNumber) + ' accept'

            print('Sending: ' + acceptMessage)
            sent = sock.sendto(acceptMessage.encode(), server_address)

            incrementingNumber += 2
            firstMessage = 'msg-' + str(incrementingNumber) + '=Hello, i am new user'

            print('Sending: ' + firstMessage)
            sent = sock.sendto(firstMessage.encode(), server_address)

        if data[:3] == b'res':
            incrementingNumber += 2
            okMessage = 'msg-' + str(incrementingNumber) + '=Ok, good to know'

            print('Sending: ' + okMessage)
            sock.sendto(okMessage.encode(), server_address)


finally:
    print('\nReached finally block\nClosing socket...')
    sock.close()
