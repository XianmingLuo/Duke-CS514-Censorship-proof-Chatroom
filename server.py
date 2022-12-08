import socket
import ssl
import threading
from ChatMessage import ChatMessage
class Client:
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.nickname = None
        self.keyServer = None
        self.publicKey = None
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
    def connectKeyServer(self):
        # TODO: Not using TLS for now
        self.keyServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.keyServer.connect((self.address[0], self.address[1]+1))
    def requestEncryptedSymmetricKey(self, requester_pk: bytes):
        self.keyServer.send(requester_pk)
        encryptedKey = self.keyServer.recv(1024)
        return encryptedKey
    def requestPublicKey(self):
        request = ChatMessage('KEY', False, None)
        self.socket.send(request.to_bytes())
        response = ChatMessage.from_bytes(self.socket.recv(1024))
        self.publicKey = response.payload
        print("Public Key is {}".format(self.publicKey))
        return self.publicKey
    def appointRoomMaster(self):
        leaderAppointment = ChatMessage('MASTER', False, None)
        self.sendChatMessage(leaderAppointment)
        self.connectKeyServer()
    def getNickname(self,):
        return self.nickname
    def quit(self,):
        self.socket.close()
        if self.keyServer:
            self.keyServer.close()
        
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
            # Inform the client its room master identity
            # So that it will generate a symmetric key to distribute
            client.appointRoomMaster()
            self.roomMaster = client

            # TODO: do we need to ack master appointment?
            print("Room Master is {}".format(self.roomMaster.getNickname()))
        else:
            # Request public key from the new client
            publicKey = client.requestPublicKey()
            # Get Encrypted Symmetric key 
            encryptedKey = self.roomMaster.requestEncryptedSymmetricKey(publicKey)
            print("[RoomMaster] Key is {}".format(encryptedKey))
            response = ChatMessage('DISTRIBUTE', 'False', encryptedKey)
            # send the encrypted symmetric key to the new participant
            client.sendChatMessage(response)
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
                print(chatMessage.payload.decode('ascii'))
                self.broadcast(chatMessage)
            except:
                # Removing And Closing Clients
                self.clients.remove(client)
                client.quit()
                self.broadcastNotification('{} left!'.format(client.getNickname()))
                if client == self.roomMaster:
                    if len(self.clients) > 0:
                        # Randomly assign a new room master for now
                        # Appoint a new Room Master
                        # TODO: Lock needed?
                        self.clients[0].appointRoomMaster()
                        self.roomMaster = self.clients[0]
                        # TODO: Ack needed?
                        self.broadcastNotification('{} is the new room master!'.format(self.roomMaster.getNickname()))
                    else:
                        # No clients left
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
