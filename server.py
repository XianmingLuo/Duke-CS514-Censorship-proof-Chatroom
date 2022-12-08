import socket
import ssl
import threading

class Client:
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.nickname = None
    def send(self, message):
        self.socket.send(message.encode('ascii'))
    def recv(self,):
        message = self.socket.recv()
        return message.decode('ascii')
    def fetchNickname(self,):
        self.send('NICK')
        self.nickname = self.recv()
    def getNickname(self,):
        return self.nickname
    def quit(self,):
        self.socket.close()
        
class Chatroom:
    def __init__(self, host, port):
        self.clients = []
        self.roomMaster = None
        # SSL Context
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain(certfile='.ssh/cert.pem', keyfile='.ssh/key.pem')
        self.context.verify_mode = ssl.CERT_NONE
        # Starting Server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = self.context.wrap_socket(self.server, server_side = True)
        self.server.bind((host, port))
        self.server.listen()
        
    def start(self):
        while True:
        # Accept Connection
            socket, address = self.server.accept()
            client = Client(socket, address)
            print("Connected with {}".format(str(address))) 
            # Start Handling Thread For Client
            handshakeThread = threading.Thread(target=self.handshake, args=(client,))
            handshakeThread.start()
    def handshake(self, client):
        client.fetchNickname()
        if not self.roomMaster:
            self.roomMaster = client
            print("Room Master is {}".format(self.roomMaster.getNickname()))
        else:
            #No handshake fornow
            #client.recv(client_public_key)
            #client_pk.append(client_public_key) thread-safe
            #roomMaster.send(client_public_key)
            #roomMaster.recv(encrypted_symmetric_chatroom_key)
            #client.send(encrypted_symmetric_chatroom_key)
            pass
        self.clients.append(client)
        self.broadcast("{} joined!".format(client.getNickname()))
        client.send('Connected to server!')
        client.send('Room Master is {}.'.format(self.roomMaster.getNickname()))
        handleThread = threading.Thread(target=self.handle, args=(client,))
        handleThread.start()
    def handle(self, client):
        while True:
            try:
                # Broadcasting Messages
                message = client.recv()
                self.broadcast(message)
            except:
                # Removing And Closing Clients
                self.clients.remove(client)
                client.quit()
                self.broadcast('{} left!'.format(client.getNickname()))
                break
    def broadcast(self, message):
        print(message)
        for client in self.clients:
            client.send(message)
if __name__ == '__main__':
    chatroom = Chatroom(host='127.0.0.1',port=55555)
    chatroom.start()
