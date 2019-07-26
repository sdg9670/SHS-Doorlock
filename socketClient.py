import socket
import doorlockManager
from threading import Thread

HOST = 'simddong.ga'
PORT = 9670
'''
HOST = '127.0.0.1'
PORT = 9671
'''
class SocketClient():
    def __init__(self):
        self.c_name = '5'
        self.sock = None
        self.dm = doorlockManager.DoorLock(self)
        self.dm.start()
        
    def rcvMsg(self):
        while True:
            try:
                data = self.sock.recv(1024)
                if not data:
                    break
                string = data.decode()
                print('수신 ' + string)
                string = string.split()
                if string[1] == 'enroll':
                    self.dm.chageMode('enroll')
                elif string[1] == 'check':
                    self.dm.chageMode('check')
                elif string[1] == 'delete':
                    self.dm.deleteFingerprint(int(string[2]))
                elif string[1] == 'open':
                    self.dm.openDoor()

            except:
                pass
    
    def closeSocket(self):
        self.socket.close()
        
    def sndMsg(self, msg):
        self.sock.send(msg.encode())

    def runClient(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.sock.send(self.c_name.encode())
        self.rcvMsg()
