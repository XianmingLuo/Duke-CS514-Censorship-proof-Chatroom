import socket
import ssl
import threading
from ChatMessage import ChatMessage
class Client:
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.nickname = None
    def sendChatMessage(self, chatMessage):
        messageBytes = chatMessage.to_bytes()
        self.socket.send(messageBytes)
    def recvChatMessage(self):
        messageBytes = self.socket.recv(1024)
        return ChatMessage.from_bytes(messageBytes)
    def fetchNickname(self,):
        request = ChatMessage('NICK', False, None)
        self.sendChatMessage(request)
        response = self.recvChatMessage()
        assert(response.command == 'NICK' and response.isEncrypted == False)
        self.nickname = response.payload.decode('ascii')

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
        self.broadcastNotification("{} joined!".format(client.getNickname()))
        self.unicastNotification(client, 'Connected to server!')
        self.unicastNotification(client, 'Room Master is {}.'.format(self.roomMaster.getNickname()))
        handleThread = threading.Thread(target=self.handle, args=(client,))
        handleThread.start()
    def handle(self, client):
        while True:
            try:
                # Broadcasting Messages
                chatMessage = client.recvChatMessage()
                self.broadcast(chatMessage)
            except:
                # Removing And Closing Clients
                self.clients.remove(client)
                client.quit()
                self.broadcastNotification('{} left!'.format(client.getNickname()))
                if client == self.roomMaster:
                    if len(self.clients) > 0:
                        # Randomly assign a new room master for now
                        self.roomMaster = self.clients[0]
                        self.broadcastNotification('{} is the new room master!'.format(self.roomMaster.getNickname()))
                    else:
                        self.roomMaster = None

                break
    def broadcast(self, chatMessage):
        for client in self.clients:
            client.sendChatMessage(chatMessage)
    def broadcastNotification(self, notification: str):
        chatMessage = ChatMessage(None, False, notification.encode('ascii'))
        self.broadcast(chatMessage)
    def unicastNotification(self, client, notification: str):
        chatMessage = ChatMessage(None, False, notification.encode('ascii'))
        client.sendChatMessage(chatMessage)
if __name__ == '__main__':
    chatroom = Chatroom(host='127.0.0.1',port=55555)
    chatroom.start()
