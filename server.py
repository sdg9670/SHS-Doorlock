import socket

ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
ssocket.bind(('localhost', 9671))
ssocket.listen(socket.SOMAXCONN)
while True:
    client, addr = ssocket.accept()
    if not client:
        continue
    print ('connected host: {0} port: {1}'.format(addr[0], addr[1]))
    while True:
        try:
            recvmsg = client.recv(1024)
            if not recvmsg or len(recvmsg) == 0:
                raise socket.error
        except:
            print('disconnected')
            break
        client.send(input('test: ').encode())
        print('From {0} Receive {1}'.format(addr, recvmsg.decode('utf-8')))

