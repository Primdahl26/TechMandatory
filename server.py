import socket

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

incrementingNumber = 1

while True:
    print('\nWaiting to receive...')
    data, address = sock.recvfrom(4096)

    print('Received {} bytes from {}'.format(len(data), address))
    print('Data: '+str(data))

    if data[:7] == b'com-0 1':
        acceptMessage = 'com-0 accept ' + socket.gethostbyname(socket.gethostname())

        sent = sock.sendto(acceptMessage.encode(), address)
        print('Sending: '+str(acceptMessage))

        clientDataIP = data.split()[-1]

    if data[:3] == b'msg':
        automatedMessage = 'res-' + str(incrementingNumber) + '=I am server'
        incrementingNumber += 2

        print('Sending: '+automatedMessage)
        sent = sock.sendto(automatedMessage.encode(), address)

    if data[:12] == b'com-0 accept':

        print('\nThe current active user is: ' + str(clientDataIP))
